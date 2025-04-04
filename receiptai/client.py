from typing import Optional
from contextlib import AsyncExitStack, asynccontextmanager
import logging
import json

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv
import os

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
    global mcp_client, server_script_path

    # Get server script path from environment variable or use a default
    server_script_path = os.environ.get('MCP_SERVER_SCRIPT')
    if not server_script_path:
        logger.error("MCP_SERVER_SCRIPT environment variable not set. Server won't start.")
        yield
        return

    logger.info('Initialising MCP client with server script: %s', server_script_path)
    mcp_client = MCPClient()
    try:
        # Initialise the MCP client synchronously to ensure it's ready before serving requests
        await mcp_client.connect_to_server(server_script_path)
        logger.info('MCP client successfully initialised')
    except Exception as e:
        logger.error('Error initialising MCP client: %s', str(e))

    yield  # FastAPI will now process requests

    if mcp_client is not None:
        await mcp_client.cleanup()
        logger.info('MCP client cleaned up')


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.initialised = False

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script
        """
        server_params = StdioServerParameters(command='python', args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # self.session is guaranteed to be non-None at this point
        assert self.session is not None, 'Session should be initialised'
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        logger.info('Connected to server with tools: %s', [tool.name for tool in tools])
        self.initialised = True

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        if not self.initialised:
            raise ValueError('MCP Client is not initialised yet')

        assert self.session is not None, 'Session should be initialised when client is initialised'

        messages = [
            {
                'role': 'user',
                'content': f"""Answer email search and retrieval requests using appropriate email tools.
                You are an llm and have no concept of what time it is. When a date is given, just use it. Your response
                should always be based on the tools results. Never assume a date is in the future. Reason through these
                    1. Determine required function (search, list, get, filter)
                    2. Assess provided parameters (sender, recipient, date range, subject keywords, folder, etc)
                    3. Only decline non-email related queries
                    4. Infer missing parameters from context when reasonable
                    5. If critical parameters cannot be inferred, ask for specific missing information

                    ONLY return email information in this JSON format:
                    {{
                        "count": "Number of emails found",
                        "results": [
                          {{
                            "sender": "Sender email/name",
                            "recipient": "Recipient email/name",
                            "subject": "Email subject",
                            "date": "Send date",
                            "body": "Email content"
                          }}
                        ]
                    }}

                    If no emails found: {{"count": "0", "response": []}}
                    Just return the response and nothing else

                    Here is the user's query: {query}""",
            }
        ]

        response = await self.session.list_tools()
        available_tools = [
            {'name': tool.name, 'description': tool.description, 'input_schema': tool.inputSchema}
            for tool in response.tools
        ]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        # Process response and handle tool calls
        final_text: str = ''

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)

                assistant_message_content.append(content)
                messages.append({'role': 'assistant', 'content': assistant_message_content})
                messages.append(
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'tool_result',
                                'tool_use_id': content.id,
                                'content': result.content,
                            }
                        ],
                    }
                )

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model='claude-3-5-sonnet-20241022',
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools,
                )

                final_text = response.content[0].text

        return final_text

    async def cleanup(self):
        """Clean up resources"""
        if self.initialised:
            await self.exit_stack.aclose()
            self.session = None  # Explicitly set to None after cleanup
            self.initialised = False


app = FastAPI(title='MCP Client API', lifespan=lifespan)

mcp_client: MCPClient | None = None
server_script_path: str | None = None


async def get_mcp_client():
    global mcp_client, server_script_path
    if mcp_client is None:
        raise HTTPException(status_code=503, detail='MCP Client not initialised')
    if not mcp_client.initialised:
        raise HTTPException(status_code=503, detail='MCP Client initialisation in progress')
    return mcp_client


# API endpoints
@app.post('/query', response_model=QueryResponse)
async def handle_query(query: Query, mcp_client: MCPClient = Depends(get_mcp_client)):
    try:
        response = await mcp_client.process_query(query.text)
        # Attempt to parse the response as JSON
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            logger.error(f'JSONDecodeError: {e}, Response: {response}')
            raise HTTPException(
                status_code=500, detail=f'Error decoding JSON: {str(e)}.  Raw response: {response}'
            )
    except Exception as e:
        logger.error(f'General error processing query: {e}')
        raise HTTPException(status_code=500, detail=f'Error processing query: {str(e)}')


@app.get('/status')
async def get_status():
    global mcp_client
    if mcp_client is None:
        return {
            'status': 'not_started',
            'initialised': False,
            'message': 'MCP Client has not been created',
        }

    if not mcp_client.initialised:
        return {
            'status': 'initialising',
            'initialised': False,
            'message': 'MCP Client initialisation in progress',
        }

    return {
        'status': 'ready',
        'initialised': True,
        'message': 'MCP Client is ready to process queries',
    }


def start_server(server_script: str, host: str = '0.0.0.0', port: int = 8000):
    """Start the FastAPI server"""
    os.environ['MCP_SERVER_SCRIPT'] = server_script
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        logger.error(
            'Usage: python client.py <path_to_server_script> optional[host] optional[port]'
        )
        sys.exit(1)

    script_path = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else '0.0.0.0'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    start_server(script_path, host, port)
