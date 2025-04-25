from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel
from datetime import datetime

class Email(BaseModel):
    id: str
    subject: str
    body: str
    from_email: str
    to_email: str
    date: datetime

class Attachment(BaseModel):
    filename: str
    content_type: str
    content: bytes

class EmailInterface(ABC):
    """Email interface that defines the required methods for email operations."""

    @abstractmethod
    async def get_email_attachments(self, email_id: str) -> List[Attachment]:
        """
        Retrieves attachment(s) for a specific email.

        Args:
            email_id: The unique identifier for the email

        Returns:
            The attachment data for the specified email
        """
        pass

    @abstractmethod
    async def search_emails(self, query: str) -> List[Email]:
        """
        Searches emails based on a query string.

        Args:
            query: The search query string

        Returns:
            A list of email objects that match the search criteria
        """
        pass
