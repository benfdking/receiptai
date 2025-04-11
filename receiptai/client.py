from typing import Optional
from contextlib import AsyncExitStack, asynccontextmanager
import logging
import json

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from langchain_mcp_adapters.client import MultiServerMCPClient, StdioConnection
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
from templates import EMAIL_SEARCH_TEMPLATE

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()


# FastAPI models
class Query(BaseModel):
    text: str


class EmailDetails(BaseModel):
    sender: str
    recipient: str
    subject: str
    date: str
    body: str


class QueryResponse(BaseModel):
    count: str
    results: list[EmailDetails]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global langgraph_client, server_script_path

    # Get server script path from environment variable or use a default
    server_script_path = os.environ.get('MCP_SERVER_SCRIPT')
    if not server_script_path:
        logger.error("MCP_SERVER_SCRIPT environment variable not set. Server won't start.")
        yield
        return

    logger.info('Initialising LangGraph client with server script: %s', server_script_path)
    langgraph_client = LangGraphClient()
    try:
        # Initialise the client synchronously to ensure it's ready before serving requests
        await langgraph_client.connect_to_server(server_script_path)
        logger.info('LangGraph client successfully initialised')
    except Exception as e:
        logger.error('Error initialising LangGraph client: %s', str(e))

    yield  # FastAPI will now process requests

    if langgraph_client is not None:
        await langgraph_client.cleanup()
        logger.info('LangGraph client cleaned up successfully')


class LangGraphClient:
    def __init__(self):
        self.session: Optional[MultiServerMCPClient] = None
        self.exit_stack = AsyncExitStack()
        self.model = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            temperature=0,
            timeout=None,
            max_retries=2,
            stop=["end_turn"]
        )
        self.mcpClient = None
        self.agent = None
        self.initialised = False

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script
        """
        GmailMcpOpts: StdioConnection = {
                "command": "python",
                "args": [server_script_path],
                "transport": "stdio",
                "env": None,
                "cwd": None,
                "encoding_error_handler": "strict",
                "session_kwargs": None,
                "encoding": "utf-8"
            }

        TimeMcpOpts: StdioConnection = {
                "command": "python",
                "args": ["receiptai/time_mcp.py"],
                "transport": "stdio",
                "env": None,
                "cwd": None,
                "encoding_error_handler": "strict",
                "session_kwargs": None,
                "encoding": "utf-8"
            }

        client = await self.exit_stack.enter_async_context(
            MultiServerMCPClient({
                "gmail": GmailMcpOpts,
                "time": TimeMcpOpts
            })
        )

        self.session = client
        response = client.get_tools()
        self.agent = create_react_agent(self.model, client.get_tools())

        # self.session is guaranteed to be non-None at this point
        assert self.session is not None, 'Session should be initialised'

        logger.info('Connected to server with tools: %s', [tool.name for tool in response])

        self.initialised = True

    async def process_query(self, query: str) -> str:
            """Process a query using LangGraph agent and available tools"""
            if not self.initialised:
                raise ValueError('LangGraph Client is not initialised yet')

            assert self.session is not None, 'Session should be initialised when client is initialised'
            assert self.agent is not None, 'Agent should be initialised when client is initialised'

            prompt = f"{EMAIL_SEARCH_TEMPLATE} \n Here is the user's query: {query}"

            # Call the agent
            agent_response = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            # Extract the final response text from the agent response
            # The last message contains the AIMessage object
            ai_message = agent_response["messages"][-1]

            # Handle different content formats
            final_response = ""
            if hasattr(ai_message, "content"):
                content = ai_message.content
                # Check if content is a string
                if isinstance(content, str):
                    final_response = content
                # Check if content is a list of content blocks
                elif isinstance(content, list):
                    # Concatenate text blocks
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            final_response += block.get("text", "")

                # If the response is not JSON, try to extract JSON from it
                if not final_response.startswith('{'):
                    # Try to find JSON in the response
                    import re
                    json_match = re.search(r'({.*})', final_response, re.DOTALL)
                    if json_match:
                        final_response = json_match.group(1)
            else:
                # Fallback: try to access content as a property or method
                try:
                    if callable(getattr(ai_message, "text", None)):
                        final_response = ai_message.text()
                    elif hasattr(ai_message, "text"):
                        final_response = ai_message.text
                    else:
                        logger.warning("Unexpected response format, trying to convert to string")
                        final_response = str(ai_message)
                except Exception as e:
                    logger.error(f"Error extracting content from response: {e}")
                    final_response = str(ai_message)

            return final_response



    async def cleanup(self):
        """Clean up resources"""
        if self.initialised:
            await self.exit_stack.aclose()
            self.session = None
            self.agent = None
            self.initialised = False


app = FastAPI(title='LangGraph MCP Client API', lifespan=lifespan)

langgraph_client: LangGraphClient | None = None
server_script_path: str | None = None


async def get_langchain_client():
    global langgraph_client, server_script_path
    if langgraph_client is None:
        raise HTTPException(status_code=503, detail='LangGraph Client not initialised')
    if not langgraph_client.initialised:
        raise HTTPException(status_code=503, detail='LangGraph Client initialisation in progress')
    return langgraph_client


# API endpoints
@app.post('/query', response_model=QueryResponse)
async def handle_query(query: Query, langgraph_client: LangGraphClient = Depends(get_langchain_client)):
    try:
        response = await langgraph_client.process_query(query.text)
        # Attempt to parse the response as JSON
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            logger.error(f'JSONDecodeError: {e}, Response: {response}')
            raise HTTPException(
                status_code=500, detail=f'Error decoding JSON: {str(e)}. Raw response: {response}'
            )
    except Exception as e:
        logger.error(f'General error processing query: {e}')
        raise HTTPException(status_code=500, detail=f'Error processing query: {str(e)}')


@app.get('/status')
async def get_status():
    global langgraph_client
    if langgraph_client is None:
        return {
            'status': 'not_started',
            'initialised': False,
            'message': 'LangGraph Client has not been created',
        }

    if not langgraph_client.initialised:
        return {
            'status': 'initialising',
            'initialised': False,
            'message': 'LangGraph Client initialisation in progress',
        }

    return {
        'status': 'ready',
        'initialised': True,
        'message': 'LangGraph Client is ready to process queries',
    }


def start_server(server_script: str, host: str = '0.0.0.0', port: int = 8000):
    """Start the FastAPI server"""
    os.environ['MCP_SERVER_SCRIPT'] = server_script
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        logger.error(
            'Usage: python ccp.py <path_to_server_script> optional[host] optional[port]'
        )
        sys.exit(1)

    script_path = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else '0.0.0.0'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    start_server(script_path, host, port)
