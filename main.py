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

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

class GmailService:
    def __init__(self,
                 creds_file_path: str,
                 token_path: str,
                 scopes: List[str] = ['https://www.googleapis.com/auth/gmail.readonly']):
        """Initialize Gmail service with credentials"""
        self.creds_file_path = creds_file_path
        self.token_path = token_path
        self.scopes = scopes
        self.token = self._get_token()
        self.service = self._get_service()

    def _get_token(self) -> Union[Credentials, Any]:
        """Get or refresh Google API token with robust handling"""
        token = None
        need_new_token = False

        if os.path.exists(self.token_path):
            logger.info('Loading token from file')
            try:
                # Load token data
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)

                if 'refresh_token' not in token_data:
                    logger.warning("Token file exists but missing refresh_token field")
                    need_new_token = True
                else:
                    token = Credentials.from_authorized_user_info(token_data, self.scopes)

                    if token.expired and not token.refresh_token:
                        logger.warning("Token is expired and can't be refreshed")
                        need_new_token = True
            except Exception as e:
                logger.error(f"Error loading token: {e}")
                need_new_token = True
        else:
            logger.info("No token file found")
            need_new_token = True

        if token and token.expired and token.refresh_token:
            logger.info('Token expired, refreshing with refresh token')
            try:
                token.refresh(Request())
                logger.info('Token refreshed successfully')
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                need_new_token = True

        if need_new_token:
            logger.info('Getting new token with refresh capabilities')

            # Create the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.creds_file_path,
                self.scopes
            )

            # Run the authorization flow
            token = flow.run_local_server(
                port=8080,  # Use any available port
                access_type='offline',
                prompt='consent'
            )

            if not token.refresh_token:
                logger.error("Failed to obtain refresh token even with correct parameters")
                raise ValueError("Could not obtain a refresh token. Check your OAuth client configuration.")

        if token:
            with open(self.token_path, 'w') as token_file:
                token_file.write(token.to_json())
                logger.info(f'Token saved to {self.token_path}')

        return token

    def _get_service(self) -> Any:
        """Initialize Gmail API service"""
        try:
            service = build('gmail', 'v1', credentials=self.token)
            return service
        except HttpError as error:
            logger.error(f'An error occurred building Gmail service: {error}')
            raise ValueError(f'An error occurred: {error}')

    async def get_unread_emails(self) -> Union[List[Dict[str, str]], str]:
        """
        Retrieves unread messages from mailbox with details.
        Returns list of email objects with id, subject, sender, and body.
        """
        try:
            user_id = 'me'
            query = 'in:inbox is:unread'  #

            response = self.service.users().messages().list(
                userId=user_id, q=query).execute()

            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            # Handle pagination for large numbers of unread emails
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(
                    userId=user_id, q=query, pageToken=page_token).execute()
                if 'messages' in response:
                    messages.extend(response['messages'])

            logger.info(f"Found {len(messages)} unread emails")

            # Get detailed information for each message
            detailed_messages = []
            for msg in messages:
                email_details = await self.get_email_details(msg['id'])
                if isinstance(email_details, dict):
                    detailed_messages.append(email_details)

            return detailed_messages

        except HttpError as error:
            error_msg = f"An HttpError occurred: {str(error)}"
            logger.error(error_msg)
            return error_msg

    async def get_email_details(self, email_id: str) -> Dict[str, str] | str:
        """
        Retrieves email contents including subject, sender, and body content.
        """
        try:
            msg = self.service.users().messages().get(userId="me", id=email_id, format='raw').execute()
            email_metadata = {}

            email_metadata['id'] = email_id

            raw_data = msg['raw']
            decoded_data = urlsafe_b64decode(raw_data)

            mime_message = message_from_bytes(decoded_data)

            # Extract email body
            body = None
            if mime_message.is_multipart():
                for part in mime_message.walk():
                    # Extract the text/plain part
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)

                        if body and isinstance(body, bytes):
                            body = body.decode(errors='replace')
                        break
            else:
                # For non-multipart messages
                body = mime_message.get_payload(decode=True)
                if body and isinstance(body, bytes):
                    body = body.decode(errors='replace')

            email_metadata['body'] = body or "[No text content found]"

            # Extract metadata
            email_metadata['subject'] = decode_mime_header(mime_message.get('subject', 'No Subject'))
            email_metadata['sender'] = mime_message.get('from', 'Unknown Sender')

            logger.info(f"Retrieved details for email: {email_id}")

            return email_metadata
        except HttpError as error:
            error_msg = f"An HttpError occurred while getting email details: {str(error)}"
            logger.error(error_msg)
            return error_msg

async def main(creds_file_path: str, token_path: str):
    """Initialize and run the Gmail MCP server"""

    gmail_service = GmailService(creds_file_path, token_path)
    server = Server("gmail")

    @server.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        return []  # No prompts, only focusing on the email reading tool

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get-unread-emails",
                description="Retrieve unread emails with detailed content",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name == "get-unread-emails":
            unread_emails = await gmail_service.get_unread_emails()

            # Format as JSON strings with specific fields for each email
            if isinstance(unread_emails, list):
                formatted_emails = []
                for email in unread_emails:
                    body = email.get('body', '')
                    body_preview = body[:200].replace('\n', ' ') + '...' if len(body) > 200 else body

                    formatted_email = {
                        "id": email.get('id', ''),
                        "subject": email.get('subject', ''),
                        "sender": email.get('sender', ''),
                        "body": body_preview
                    }
                    formatted_emails.append(formatted_email)

                return [types.TextContent(
                    type="text",
                    text=json.dumps(formatted_emails, indent=2),
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=str(unread_emails)
                )]
        else:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gmail",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gmail Email Reader MCP Server')
    parser.add_argument(
        '--creds-file-path',
        required=True,
        help='OAuth 2.0 credentials file path'
    )
    parser.add_argument(
        '--token-path',
        required=True,
        help='File location to store and retrieve access and refresh tokens for application'
    )

    args = parser.parse_args()
    asyncio.run(main(args.creds_file_path, args.token_path))
