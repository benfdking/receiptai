import os
import json
import asyncio
import logging
import argparse
from typing import Any, List, Dict, Union
from email.header import decode_header
from base64 import urlsafe_b64decode
from email import message_from_bytes

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
        """Get or refresh Google API token"""
        token = None

        if os.path.exists(self.token_path):
            logger.info('Loading token from file')
            token = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not token or not token.valid:
            if token and token.expired and token.refresh_token:
                logger.info('Refreshing token')
                token.refresh(Request())
            else:
                logger.info('Fetching new token')
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file_path, self.scopes)
                token = flow.run_local_server(port=8080)

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
    """Main function to get unread emails"""
    try:
        gmail_service = GmailService(creds_file_path, token_path)

        unread_emails = await gmail_service.get_unread_emails()

        if isinstance(unread_emails, list):
            print(f"Found {len(unread_emails)} unread emails:")
            for i, email in enumerate(unread_emails):
                # Prepare body preview (limit to 100 characters)
                body_preview = email.get('body', '')
                if len(body_preview) > 100:
                    body_preview = body_preview[:100].replace('\n', ' ') + '...'

                # Create output object
                email_output = {
                    "id": email.get('id', ''),
                    "subject": email.get('subject', ''),
                    "sender": email.get('sender', ''),
                    "body": body_preview
                }

                # Print as JSON
                print(json.dumps(email_output))
        else:
            print(f"Error: {unread_emails}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gmail Unread Emails Fetcher')
    parser.add_argument(
        '--creds-file-path',
        required=True,
        help='OAuth 2.0 credentials file path'
    )
    parser.add_argument(
        '--token-path',
        required=True,
        help='File location to store and retrieve access and refresh tokens'
    )

    args = parser.parse_args()
    asyncio.run(main(args.creds_file_path, args.token_path))
