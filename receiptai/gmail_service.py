
from typing import Any
import json
import os
import logging
import base64

from email.header import decode_header
from base64 import urlsafe_b64decode
from email import message_from_bytes
from typing import List, Dict, Union
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from fs import AttachmentResponse
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
    def __init__(
        self,
        creds_file_path: str,
        token_path: str,
        scopes: List[str] = ['https://www.googleapis.com/auth/gmail.readonly'],
    ):
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
                    logger.warning('Token file exists but missing refresh_token field')
                    need_new_token = True
                else:
                    token = Credentials.from_authorized_user_info(token_data, self.scopes)

                    if token.expired and not token.refresh_token:
                        logger.warning("Token is expired and can't be refreshed")
                        need_new_token = True
            except Exception as e:
                logger.error(f'Error loading token: {e}')
                need_new_token = True
        else:
            logger.info('No token file found')
            need_new_token = True

        if token and token.expired and token.refresh_token:
            logger.info('Token expired, refreshing with refresh token')
            try:
                token.refresh(Request())
                logger.info('Token refreshed successfully')
            except Exception as e:
                logger.error(f'Error refreshing token: {e}')
                need_new_token = True

        if need_new_token:
            logger.info('Getting new token with refresh capabilities')

            # Create the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(self.creds_file_path, self.scopes)

            # Run the authorization flow
            token = flow.run_local_server(
                port=8080,  # Use any available port
                access_type='offline',
                prompt='consent',
            )

            if not token.refresh_token:
                logger.error('Failed to obtain refresh token even with correct parameters')
                raise ValueError(
                    'Could not obtain a refresh token. Check your OAuth client configuration.'
                )

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

            response = self.service.users().messages().list(userId=user_id, q=query).execute()

            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            # Handle pagination for large numbers of unread emails
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = (
                    self.service.users()
                    .messages()
                    .list(userId=user_id, q=query, pageToken=page_token)
                    .execute()
                )
                if 'messages' in response:
                    messages.extend(response['messages'])

            logger.info(f'Found {len(messages)} unread emails')

            # Get detailed information for each message
            detailed_messages = []
            for msg in messages:
                email_details = await self.get_email_details(msg['id'])
                if isinstance(email_details, dict):
                    detailed_messages.append(email_details)

            return detailed_messages

        except HttpError as error:
            error_msg = f'An HttpError occurred: {str(error)}'
            logger.error(error_msg)
            return error_msg

    async def get_email_details(self, email_id: str) -> Dict[str, str] | str:
        """
        Retrieves email contents including subject, sender, body content, and attachments.
        """
        try:
            msg = (
                self.service.users()
                .messages()
                .get(userId='me', id=email_id, format='raw')
                .execute()
            )
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
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True)

                    if body and isinstance(body, bytes):
                        body = body.decode(errors='replace')
                    break
            else:
                # For non-multipart messages
                body = mime_message.get_payload(decode=True)
                if body and isinstance(body, bytes):
                    body = body.decode(errors='replace')

            email_metadata['body'] = body or '[No text content found]'

            # Extract metadata
            email_metadata['subject'] = decode_mime_header(
                mime_message.get('subject', 'No Subject')
            )
            email_metadata['sender'] = mime_message.get('from', 'Unknown Sender')

            # Extract attachments
            attachments = []
            for part in mime_message.walk():
                if (
                    part.get_content_maintype() == 'multipart'
                    or part.get('Content-Disposition') is None
                ):
                    continue
                filename = part.get_filename()
                if filename:
                    attachment = {
                        'filename': filename,
                        'content': part.get_payload(decode=True).decode(errors='ignore')
                        if part.get_payload(decode=True)
                        else '',
                    }
                    attachments.append(attachment)
            email_metadata['attachments'] = attachments

            logger.info(f'Retrieved details for email: {email_id}')

            return email_metadata
        except HttpError as error:
            error_msg = f'An HttpError occurred while getting email details: {str(error)}'
            logger.error(error_msg)
            return error_msg

    async def search_emails(self, query: str) -> Union[List[Dict[str, str]], str]:
        """
        Searches emails using Gmail's search syntax.
        ref -> https://developers.google.com/workspace/gmail/api/guides/filtering

        Returns list of email objects with id, subject, sender, and body.

        Args:
            query (str): Gmail search query (e.g., 'from:example@gmail.com', 'subject:hello',
                        'after:2023/04/14 before:2023/04/16 (subject:"Amazon" OR "Amazon") £42.99'
        """
        try:
            user_id = 'me'

            response = self.service.users().messages().list(userId=user_id, q=query).execute()

            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            # Handle pagination for large numbers of search results
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = (
                    self.service.users()
                    .messages()
                    .list(userId=user_id, q=query, pageToken=page_token)
                    .execute()
                )
                if 'messages' in response:
                    messages.extend(response['messages'])

            logger.info(f'Found {len(messages)} emails matching query: {query}')

            detailed_messages = []
            for msg in messages:
                email_details = await self.get_email_details(msg['id'])
                if isinstance(email_details, dict):
                    detailed_messages.append(email_details)

            return detailed_messages

        except HttpError as error:
            error_msg = f'An HttpError occurred: {str(error)}'
            logger.error(error_msg)
            return error_msg

    async def get_email_attachments(self, email_id: str) -> Union[List[AttachmentResponse], str]:
            """
            Retrieve all attachments from a specific email by its ID.
            Returns a list of dictionaries, each containing:
                - filename
                - mimeType
                - data (raw byte content or base64-encoded string)
            If no attachments found or an error occurs, returns an empty list or error string.
            """
            try:
                message = self.service.users().messages().get(
                    userId='me', id=email_id, format='full'
                ).execute()

                payload = message.get('payload', {})
                attachments = []
                self._extract_attachments(payload, email_id, attachments)
                return attachments

            except HttpError as error:
                error_msg = f"An error occurred when fetching email attachments: {error}"
                logger.error(error_msg)
                return error_msg

    def _extract_attachments(self, payload: Dict[str, Any], email_id: str, attachments_list: List[Dict[str, Any]]):
        """
        Recursively traverses the parts of an email payload to find attachments.

        If an attachment is found (identified by filename and attachmentId), it downloads the attachment data,
        decodes it from its URL-safe Base64 encoding, and then re-encodes it to a standard Base64 string
        for inclusion in the attachments list.

        Args:
            payload (Dict[str, Any]): The payload of the email message, which may contain nested parts.
            email_id (str): The ID of the email message.
            attachments_list (List[Dict[str, Any]]): A list to which the extracted attachment information will be appended.
        """
        parts = payload.get('parts', [])
        for part in parts:
            filename = part.get('filename')
            body = part.get('body', {})
            mime_type = part.get('mimeType')
            attachment_id = body.get('attachmentId')

            # If the part has a filename and an attachmentId, it's likely an attachment
            if filename and attachment_id:
                attachment_data = self.service.users().messages().attachments().get(
                    userId='me',
                    messageId=email_id,
                    id=attachment_id
                ).execute()

                data = attachment_data.get('data', '')

                if isinstance(data, str):
                    data = data.encode('utf-8')

                file_data = urlsafe_b64decode(data)

                file_data_encoded = base64.b64encode(file_data).decode('utf-8')

                attachments_list.append({
                    'filename': filename,
                    'mimeType': mime_type,
                    'data': file_data_encoded
                })

            # If there are nested parts, recurse
            if 'parts' in part:
                self._extract_attachments(part, email_id, attachments_list)
