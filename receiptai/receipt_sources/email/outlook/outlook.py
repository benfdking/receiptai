import os
from email.message import Message
from typing import List

from azure.identity import DeviceCodeCredential
from domain.email import AttachmentResponse, Email
from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder


class OutlookService:
    def __init__(self):
        self.outlook_client_id = os.getenv('OUTLOOK_CLIENT_ID')
        if not self.outlook_client_id:
            raise ValueError('OUTLOOK_CLIENT_ID is not set')
        self.credential = DeviceCodeCredential(client_id=self.outlook_client_id, tenant_id='common')
        self.scopes = ['https://graph.microsoft.com/Mail.Read']
        self.graph_client = GraphServiceClient(self.credential, self.scopes)

    async def get_mail(self):
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters()
        request_configuration = (
            MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters=query_params,
            )
        )
        mail = await self.graph_client.me.messages.get(request_configuration=request_configuration)
        mail_list = [self._parse_mail(message) for message in mail]
        return mail_list

    async def search_mail(self, query: str) -> List[Email]:
        """
        Search for emails based on a outlook search query
        """
        query_params = MessagesRequestBuilder.MessagesRequestBuilderSearchQueryParameters(
            query=query,
        )
        request_configuration = (
            MessagesRequestBuilder.MessagesRequestBuilderSearchRequestConfiguration(
                query_parameters=query_params,
            )
        )
        mail = await self.graph_client.me.messages.get(request_configuration=request_configuration)
        mail_list = [self._parse_mail(message) for message in mail]
        return mail_list

    @staticmethod
    def _parse_mail(message: Message) -> Email:
        return Email(
            subject=message.subject,
            body=message.body,
            from_email=message.from_.email_address.name,
            to_email=message.cc_recipients[0].email_address.name if message.cc_recipients else None,
            date=message.received_date_time,
            has_attachments=message.has_attachments,
        )

    async def get_mail_attachments(self, message_id: str) -> List[AttachmentResponse]:
        message = await self.graph_client.me.messages.get(message_id)
        attachments = []
        for attachment in message.attachments:
            attachments.append(
                AttachmentResponse(
                    filename=attachment.name,
                    mimeType=attachment.content_type,
                    data=attachment.content,
                )
            )
        return attachments
