import asyncio
import json
import logging
import os
from datetime import datetime
from typing import cast

import mcp.server.stdio
import mcp.types as types
from dotenv import load_dotenv
from fs import LocalFileSystem
from gmail_service import GmailService
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_system = LocalFileSystem(base_directory='creds/file_storage')


async def gmail_mcp():
    """Initialize and run the Gmail MCP server using environment variables"""
    # Load environment variables from .env file
    load_dotenv()

    # TODO(jimmy): move to config obj
    creds_file_path = os.environ.get('CREDS_FILE_PATH')
    token_path = os.environ.get('TOKEN_JSON_PATH')

    # Validate environment variables
    if not creds_file_path:
        logger.error('CREDS_FILE_PATH environment variable is not set')
        raise ValueError('CREDS_FILE_PATH environment variable is required')

    if not token_path:
        logger.error('TOKEN_JSON_PATH environment variable is not set')
        raise ValueError('TOKEN_JSON_PATH environment variable is required')

    logger.info(f'Using credentials file: {creds_file_path}')
    logger.info(f'Using token path: {token_path}')

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
            types.Tool(
                name='get-email-attachments',
                description='Retrieve attachments from a specific email by its ID',
                inputSchema={
                    'type': 'object',
                    'properties': {'email_id': {'type': 'string'}},
                    'required': ['email_id'],
                },
            ),
            types.Tool(
                name='get-email-body-as-attachment',
                description='Retrieve the body of an email as an attachment',
                inputSchema={
                    'type': 'object',
                    'properties': {'email_id': {'type': 'string'}},
                    'required': ['email_id'],
                },
            ),
            types.Tool(
                name='save-email-attachments',
                description='Retrieve and saves all from a specific email by its ID to a file system',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'email_id': {'type': 'string'},
                    },
                    'required': ['email_id'],
                },
            ),
            types.Tool(
                name='save-email-content-as-attachment',
                description='Save email content as an attachment to a file system',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'email_id': {'type': 'string'},
                    },
                    'required': ['email_id'],
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
                    body_preview = body.replace('\n', ' ')

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

                    formatted_email = {
                        'id': email.get('id', ''),
                        'subject': email.get('subject', ''),
                        'sender': email.get('sender', ''),
                        'body': body,  # trim?
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

        elif name == 'get-email-attachments':
            if not arguments or 'email_id' not in arguments:
                return [
                    types.TextContent(
                        type='text', text='Query parameter is required for search-emails tool.'
                    )
                ]

            email_id = cast(str, arguments.get('email_id'))
            attachments = await gmail_service.get_email_attachments(email_id)
            return [types.TextContent(type='text', text=json.dumps(attachments, indent=2))]

        elif name == 'save-email-attachments':
            if not arguments or 'email_id' not in arguments:
                return [
                    types.TextContent(
                        type='text',
                        text=json.dumps(
                            {
                                'status': 'error',
                                'message': 'Email ID parameter is required for save-email-attachments tool.',
                            },
                            indent=2,
                        ),
                    )
                ]

            # TODO: add directory to args
            email_id = cast(str, arguments.get('email_id'))

            attachments = await gmail_service.get_email_attachments(email_id)

            response = {
                'email_id': email_id,
                'attachments': [],
                'summary': {'total': 0, 'successful': 0, 'failed': 0},
            }

            # Handle error response
            if not isinstance(attachments, list):
                response['status'] = 'error'
                response['message'] = str(attachments)
                return [types.TextContent(type='text', text=json.dumps(response, indent=2))]

            # Handle no attachments case
            if len(attachments) == 0:
                response['status'] = 'success'
                response['message'] = 'No attachments found in this email'
                return [types.TextContent(type='text', text=json.dumps(response, indent=2))]

            # Update total count
            response['summary']['total'] = len(attachments)
            response['status'] = 'success'

            # Process each attachment
            for attachment in attachments:
                attachment = cast(dict, attachment)
                attachment_result = {
                    'filename': attachment.get('filename', 'unknown'),
                    'mimeType': attachment.get('mimeType', 'application/octet-stream'),
                }

                try:
                    filename = attachment.get('filename')
                    mime_type = attachment.get('mimeType', 'application/octet-stream')
                    content = attachment.get('data')

                    # Skip invalid attachments but report them
                    if not filename or not content:
                        attachment_result['status'] = 'skipped'
                        attachment_result['reason'] = 'Missing filename or content'
                        response['summary']['failed'] += 1
                        response['attachments'].append(attachment_result)
                        continue

                    safe_filename = os.path.basename(filename)  # Ensure no path traversal

                    # Handle potential duplicate filenames
                    if os.path.exists(os.path.join(file_system.base_directory, safe_filename)):
                        now = datetime.now()
                        current_time = now.strftime('%H:%M:%S')
                        current_date = now.strftime('%Y-%m-%d')
                        base, ext = os.path.splitext(safe_filename)
                        safe_filename = f'{base}_{email_id[:8]}{ext}_{current_date}T{current_time}'
                        attachment_result['renamed'] = True
                        attachment_result['original_filename'] = filename

                    # Save file
                    full_path = file_system.save_file(safe_filename, mime_type, content)

                    # Record success
                    attachment_result['status'] = 'success'
                    attachment_result['saved_path'] = full_path
                    response['summary']['successful'] += 1

                except Exception as e:
                    attachment_result['status'] = 'error'
                    attachment_result['error'] = str(e)
                    response['summary']['failed'] += 1

                response['attachments'].append(attachment_result)

            # Add overall status message
            if response['summary']['failed'] == 0:
                response['message'] = (
                    f'All {response["summary"]["total"]} {"attachments" if len(attachments) > 1 else "attachment"} saved successfully'
                )
            else:
                response['message'] = (
                    f'{response["summary"]["successful"]} of {response["summary"]["total"]} attachments saved successfully'
                )

            return [types.TextContent(type='text', text=json.dumps(response, indent=2))]

        elif name == 'get-email-body-as-attachment':
            if not arguments or 'email_id' not in arguments:
                return [types.TextContent(type='text', text='Missing email_id argument')]
            email_id = arguments['email_id']
            try:
                email = await gmail_service.get_email_body_as_attachment(email_id)
                return [types.TextContent(type='text', text=json.dumps(email, indent=2))]
            except Exception as e:
                return [types.TextContent(type='text', text=f'Error fetching email: {str(e)}')]

        elif name == 'save-email-content-as-attachment':
            if not arguments or 'email_id' not in arguments:
                return [types.TextContent(type='text', text='Missing email_id argument')]
            email_id = arguments['email_id']
            try:
                attachment_response = await gmail_service.get_email_body_as_attachment(email_id)

                attachment_response = cast(dict[str, str], attachment_response)
                # Get email details from the response
                filename = attachment_response.get('filename', f'email_{email_id}')
                mime_type = attachment_response.get('mimeType', 'text/html')
                content = attachment_response.get('data')

                if not content:
                    return [
                        types.TextContent(
                            type='text',
                            text=json.dumps(
                                {
                                    'status': 'error',
                                    'message': 'No content to save in the email body',
                                },
                                indent=2,
                            ),
                        )
                    ]

                # Save the content to the file system
                safe_filename = os.path.basename(filename)

                # Handle potential duplicate filenames
                if os.path.exists(os.path.join(file_system.base_directory, safe_filename)):
                    now = datetime.now()
                    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
                    base, ext = os.path.splitext(safe_filename)
                    safe_filename = f'{base}_{timestamp}{ext}'

                # Save file
                saved_path = file_system.save_file(safe_filename, mime_type, content, True)

                return [
                    types.TextContent(
                        type='text',
                        text=json.dumps(
                            {
                                'status': 'success',
                                'message': 'Email content saved successfully',
                                'email_id': email_id,
                                'saved_path': saved_path,
                                'filename': safe_filename,
                                'mimeType': mime_type,
                            },
                            indent=2,
                        ),
                    )
                ]
            except Exception as e:
                return [
                    types.TextContent(
                        type='text',
                        text=json.dumps(
                            {
                                'status': 'error',
                                'message': f'Error saving email content: {str(e)}',
                                'email_id': email_id,
                            },
                            indent=2,
                        ),
                    )
                ]

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
    asyncio.run(gmail_mcp())
