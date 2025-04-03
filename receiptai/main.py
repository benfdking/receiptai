from typing import Any
import json
import argparse
import os
import asyncio
import logging
from email.header import decode_header
from base64 import urlsafe_b64decode
from email import message_from_bytes
from typing import List, Dict, Union

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from receiptai.gmail import GmailService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def decode_mime_header(header: str) -> str:
    """Helper function to decode encoded email headers"""
    decoded_parts = decode_header(header)
    decoded_string = ''
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_string += part.decode(encoding or 'utf-8', errors='replace')
        else:
            decoded_string += part
    return decoded_string


async def main(creds_file_path: str, token_path: str):
    """Initialize and run the Gmail MCP server"""

    gmail_service = GmailService(creds_file_path, token_path)
    server = Server('gmail')

    @server.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        return []  # No prompts, only focusing on the email reading tool

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name='get-unread-emails',
                description='Retrieve unread emails with detailed content',
                inputSchema={'type': 'object', 'properties': {}, 'required': []},
            ),
            types.Tool(
                name='search-emails',
                description="Search emails using Gmail's search syntax and include attachments",
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': "Gmail search query (e.g., 'from:example@gmail.com', 'subject:hello')",
                        }
                    },
                    'required': ['query'],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == 'get-unread-emails':
            unread_emails = await gmail_service.get_unread_emails()

            # Format as JSON strings with specific fields for each email
            if isinstance(unread_emails, list):
                formatted_emails = []
                for email in unread_emails:
                    body = email.get('body', '')
                    body_preview = (
                        body[:200].replace('\n', ' ') + '...' if len(body) > 200 else body
                    )

                    formatted_email = {
                        'id': email.get('id', ''),
                        'subject': email.get('subject', ''),
                        'sender': email.get('sender', ''),
                        'body': body_preview,
                    }
                    formatted_emails.append(formatted_email)

                return [
                    types.TextContent(
                        type='text',
                        text=json.dumps(formatted_emails, indent=2),
                    )
                ]
            else:
                return [types.TextContent(type='text', text=str(unread_emails))]
        elif name == 'search-emails':
            if not arguments or 'query' not in arguments:
                return [
                    types.TextContent(
                        type='text', text='Query parameter is required for search-emails tool.'
                    )
                ]

            query = arguments['query']
            search_results = await gmail_service.search_emails(query)

            # Format as JSON strings with specific fields for each email
            if isinstance(search_results, list):
                formatted_emails = []
                for email in search_results:
                    body = email.get('body', '')
                    attachments = email.get('attachments', [])
                    attachment_filenames = [attachment['filename'] for attachment in attachments]

                    formatted_email = {
                        'id': email.get('id', ''),
                        'subject': email.get('subject', ''),
                        'sender': email.get('sender', ''),
                        'body': body,  # trim?
                        'attachments': attachment_filenames,
                    }
                    formatted_emails.append(formatted_email)

                return [
                    types.TextContent(
                        type='text',
                        text=json.dumps(formatted_emails, indent=2),
                    )
                ]
            else:
                return [types.TextContent(type='text', text=str(search_results))]
        else:
            logger.error(f'Unknown tool: {name}')
            raise ValueError(f'Unknown tool: {name}')

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name='gmail',
                server_version='0.1.0',
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gmail Email Reader MCP Server')
    parser.add_argument('--creds-file-path', required=True, help='OAuth 2.0 credentials file path')
    parser.add_argument(
        '--token-path',
        required=True,
        help='File location to store and retrieve access and refresh tokens for application',
    )

    args = parser.parse_args()
    asyncio.run(main(args.creds_file_path, args.token_path))
