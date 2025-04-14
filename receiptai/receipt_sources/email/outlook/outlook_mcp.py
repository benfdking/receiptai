from domain.email import AttachmentResponse
from fastmcp import FastMCP
from pydantic import BaseModel
from receipt_sources.email.outlook.outlook import OutlookService

fastmcp = FastMCP()
service = OutlookService()


class Mail(BaseModel):
    subject: str
    body: str
    from_email: str
    to_email: str
    date: str
    has_attachments: bool


@fastmcp.tool(name='get-mail')
async def get_mail() -> list[Mail]:
    mail = await service.get_mail()
    return mail


@fastmcp.tool(name='search-mail')
async def search_mail(query: str) -> list[Mail]:
    mail = await service.search_mail(query)
    return mail


@fastmcp.tool(name='save-email-attachment')
async def save_email_attachment(message_id: str, attachment_id: str) -> str:
    attachment = await service.get_mail_attachment(message_id, attachment_id)
    return attachment


@fastmcp.tool(name='get-mail-attachments')
async def get_mail_attachments(message_id: str) -> list[AttachmentResponse]:
    attachments = await service.get_mail_attachments(message_id)
    return attachments


if __name__ == '__main__':
    fastmcp.run()
