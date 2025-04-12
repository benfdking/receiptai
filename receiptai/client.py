from typing import Optional
from contextlib import AsyncExitStack
import logging
import os

from dotenv.main import load_dotenv
from fastapi import HTTPException, Request
from pydantic import BaseModel

from langchain_mcp_adapters.client import MultiServerMCPClient, StdioConnection
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from templates import EMAIL_SEARCH_TEMPLATE
from enum import Enum



logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

load_dotenv()

ENVCONFIG_MODEL=os.environ.get("ENVCONFIG_MODEL", "llama3.1:8b")
ENVCONFIG_MODEL=os.environ.get("MODEL_CHOICE", "local")




class ModelChoice(Enum):
    LOCAL = "local"
    REMOTE = "remote"


class LangGraphClient:
    def __init__(self):
        self.session: Optional[MultiServerMCPClient] = None
        self.exit_stack = AsyncExitStack()
        self.mcpClient = None
        self.agent = None
        self.initialised = False

        if ENVCONFIG_MODEL == ModelChoice.LOCAL:
            self.model = ChatOllama(
                model=ENVCONFIG_MODEL,
                temperature=0,
                num_predict=256,
            )
        else:
            self.model = ChatAnthropic(
                        model_name="claude-3-5-sonnet-20240620",
                        temperature=0,
                        timeout=None,
                        max_retries=2,
                        stop=["end_turn"]
                    )

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




def get_langchain_client(request: Request) -> LangGraphClient:
    """Get the LangGraph client from the app state."""
    if not hasattr(request.app, "langgraph_client"):
        raise HTTPException(status_code=503, detail='LangGraph Client not initialized')

    client = request.app.langgraph_client
    if client is None:
        raise HTTPException(status_code=503, detail='LangGraph Client not initialized')
    if not client.initialised:
        raise HTTPException(status_code=503, detail='LangGraph Client initialization in progress')
    return client
