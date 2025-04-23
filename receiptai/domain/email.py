import datetime
from typing import Union

from anthropic import BaseModel


class Email(BaseModel):
    sender: list[str]
    to: list[str]
    subject: str
    body: str
    date: datetime
    has_attachments: bool


class AttachmentResponse(BaseModel):
    filename: str
    mimeType: str
    data: Union[bytes, str]
