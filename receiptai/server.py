from contextlib import asynccontextmanager
import json
import logging
from client import LangGraphClient, Query, QueryResponse, get_langchain_client
from fastapi import FastAPI, Depends, HTTPException
import os
import uvicorn
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()
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

app = FastAPI(title='LangGraph MCP Client API', lifespan=lifespan)

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
