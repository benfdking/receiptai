import base64
import json
import logging
import os
from base64 import urlsafe_b64decode
from email import message_from_bytes
from email.header import decode_header
from typing import Any, Dict, List, Union, cast
from datetime import datetime

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from fs import AttachmentResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email_types import EmailInterface, Attachment
from email_types import Email
from email.utils import parsedate_to_datetime

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


class GmailService(EmailInterface):
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
            date_str = mime_message.get('date')
            if date_str:
                try:
                    # Parse the email date string into a datetime object
                    email_date = parsedate_to_datetime(date_str)
                    email_metadata['date'] = email_date
                except Exception as e:
                    logger.error(f"Error parsing email date '{date_str}': {str(e)}")
                    email_metadata['date'] = None  # Set to None instead of defaulting to now
            else:
                logger.warning(f"No date found in email {email_id}")
                email_metadata['date'] = None

            body_content = None

            # Try to get plain text first
            for part in mime_message.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)
                    if body and isinstance(body, bytes):
                        body_content = body.decode(errors='replace')
                    break

            if body_content is None:
                for part in mime_message.walk():
                    if part.get_content_type() == 'text/html':
                        html_body = part.get_payload(decode=True)
                        if html_body and isinstance(html_body, bytes):
                            soup = BeautifulSoup(html_body.decode(errors='replace'), 'html.parser')

                            # Remove script and style elements
                            for script in soup(['script', 'style']):
                                script.extract()

                            # Handle links - preserve URL information by replacing with "[text](url)"
                            for link_element in soup.find_all('a'):
                                link = cast(Tag, link_element)
                                href = link.get('href')
                                if href:
                                    link_text = link.get_text(strip=True) or href
                                    replacement_string = f'{link_text} {href}'
                                    link.replace_with(NavigableString(replacement_string))

                            # Extract text with better formatting
                            lines = []
                            for element_raw in soup.find_all(
                                ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li']
                            ):
                                element = cast(Tag, element_raw)
                                text = element.get_text(strip=True)
                                if text:
                                    if element.name.startswith('h'):
                                        level = int(element.name[1])
                                        if level == 1:
                                            lines.append(
                                                f'\n{"=" * len(text)}\n{text}\n{"=" * len(text)}'
                                            )
                                        elif level == 2:
                                            lines.append(f'\n{text}\n{"-" * len(text)}')
                                        else:
                                            lines.append(f'\n{text}')
                                    elif element.name == 'li':
                                        lines.append(f'• {text}')
                                    else:
                                        lines.append(text)

                            # If no structured elements found, fall back to regular text extraction
                            if not lines:
                                lines = soup.get_text(separator='\n', strip=True).split('\n')

                            # Filter out empty lines and join with double newlines for paragraph separation
                            body_content = '\n'.join(line for line in lines if line.strip())
                        break

            email_metadata['body'] = body_content or '[No text content found]'

            # Extract metadata
            email_metadata['subject'] = decode_mime_header(
                mime_message.get('subject', 'No Subject')
            )
            email_metadata['sender'] = mime_message.get('from', 'Unknown Sender')
            email_metadata['to'] = mime_message.get('to', 'Unknown Recipient')

            logger.info(f'Retrieved details for email: {email_id}')

            return email_metadata
        except HttpError as error:
            error_msg = f'An HttpError occurred while getting email details: {str(error)}'
            logger.error(error_msg)
            return error_msg

    async def search_emails(self, query: str) -> List[Email]:
        """
        Searches emails based on a query string.

        Args:
            query: The search query string

        Returns:
            A list of email objects that match the search criteria
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

            email_list = []
            for msg in messages:
                email_details = await self.get_email_details(msg['id'])
                if isinstance(email_details, dict):
                    # Convert dictionary to Email object
                    try:
                        email = Email(
                            id=email_details.get('id', ''),
                            subject=email_details.get('subject', ''),
                            body=email_details.get('body', ''),
                            from_email=email_details.get('sender', ''),
                            to_email=email_details.get('to', ''),
                            date= cast(datetime, email_details.get('date', '')),
                        )
                        email_list.append(email)
                    except Exception as e:
                        logger.error(f"Error creating Email object: {str(e)}")
            return email_list

        except HttpError as error:
            logger.error(f'An HttpError occurred: {str(error)}')
            return []

    async def get_email_attachments(self, email_id: str) -> List[Attachment]:
        """
        Retrieves attachment(s) for a specific email.

        Args:
            email_id: The unique identifier for the email

        Returns:
            The attachment data for the specified email
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId='me', id=email_id, format='full')
                .execute()
            )

            payload = message.get('payload', {})
            attachments_data = []
            self._extract_attachments(payload, email_id, attachments_data)

            # Convert to Attachment objects
            attachments = []
            for attachment_data in attachments_data:
                # Decode from base64 to get raw bytes
                content_bytes = base64.b64decode(attachment_data['data'])

                attachment = Attachment(
                    filename=attachment_data['filename'],
                    content_type=attachment_data['mimeType'],
                    content=content_bytes
                )
                attachments.append(attachment)

            return attachments

        except HttpError as error:
            error_msg = f'An error occurred when fetching email attachments: {error}'
            logger.error(error_msg)
            return []

    async def get_email_body_as_attachment(self, email_id: str) -> Union[AttachmentResponse, str]:
        """
        Extracts the email body as an attachment if HTML, or returns plain text.

        Args:
            email_id (str): The ID of the email to extract

        Returns:
            Union[AttachmentResponse, str]: AttachmentResponse with HTML data or plain text string
        """
        try:
            # Get the raw message
            msg = (
                self.service.users()
                .messages()
                .get(userId='me', id=email_id, format='raw')
                .execute()
            )

            raw_data = msg['raw']
            decoded_data = urlsafe_b64decode(raw_data)
            mime_message = message_from_bytes(decoded_data)

            # Extract subject for filename
            subject = decode_mime_header(mime_message.get('subject', 'No Subject'))
            # Use standard library function to sanitize filename
            import re

            safe_subject = re.sub(r'[^\w\s-]', '_', subject)
            safe_subject = re.sub(r'\s+', '_', safe_subject)

            # Check for HTML content first
            for part in mime_message.walk():
                if part.get_content_type() == 'text/html':
                    html_body = part.get_payload(decode=True)
                    if html_body and isinstance(html_body, bytes):
                        html_content = html_body.decode(errors='replace')
                        html_bytes = html_content.encode('utf-8')
                        html_encoded = base64.b64encode(html_bytes).decode('utf-8')

                        # Create an AttachmentResponse instance
                        return cast(
                            AttachmentResponse,
                            {
                                'email': email_id,
                                'filename': f'Email_{safe_subject[:30]}_{email_id[:8]}',
                                'mimeType': 'text/html',
                                'data': html_encoded,
                            },
                        )

            # If no HTML, return plain text as string
            for part in mime_message.walk():
                if part.get_content_type() == 'text/plain':
                    text_body = part.get_payload(decode=True)
                    if text_body and isinstance(text_body, bytes):
                        return text_body.decode(errors='replace')

            return 'No content found in email body'

        except Exception as error:
            error_msg = f'An error occurred extracting email body: {error}'
            logger.error(error_msg)
            return error_msg

    def _extract_attachments(
        self, payload: Dict[str, Any], email_id: str, attachments_list: List[Dict[str, Any]]
    ):
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
                attachment_data = (
                    self.service.users()
                    .messages()
                    .attachments()
                    .get(userId='me', messageId=email_id, id=attachment_id)
                    .execute()
                )

                data = attachment_data.get('data', '')

                if isinstance(data, str):
                    data = data.encode('utf-8')

                file_data = urlsafe_b64decode(data)

                file_data_encoded = base64.b64encode(file_data).decode('utf-8')

                attachments_list.append(
                    {
                        'email': email_id,
                        'filename': filename,
                        'mimeType': mime_type,
                        'data': file_data_encoded,
                    }
                )

            # If there are nested parts, recurse
            if 'parts' in part:
                self._extract_attachments(part, email_id, attachments_list)
