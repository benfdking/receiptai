from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_async_file_upload_response import CreateAsyncFileUploadResponse
from ...models.receipt_upload_request import ReceiptUploadRequest
from ...types import Response


def _get_kwargs(
    expense_id: str,
    *,
    body: ReceiptUploadRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/expenses/card/{expense_id}/receipt_upload",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, CreateAsyncFileUploadResponse]]:
    if response.status_code == 201:
        response_201 = CreateAsyncFileUploadResponse.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, CreateAsyncFileUploadResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    expense_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReceiptUploadRequest,
) -> Response[Union[Any, CreateAsyncFileUploadResponse]]:
    """Create a new receipt upload


    The `uri` will be a pre-signed S3 URL allowing you to upload the receipt securely. This URL can only
    be used for a `PUT` operation and expires 30 minutes after its creation. Once your upload is
    complete, we will try to match the receipt with existing expenses.

    Refer to these [docs](https://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html)
    on how to upload to this pre-signed S3 URL. We highly recommend using one of AWS SDKs if they're
    available for your language to upload these files.

    Args:
        expense_id (str):
        body (ReceiptUploadRequest): The parameter for creating a receipt upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CreateAsyncFileUploadResponse]]
    """

    kwargs = _get_kwargs(
        expense_id=expense_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    expense_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReceiptUploadRequest,
) -> Optional[Union[Any, CreateAsyncFileUploadResponse]]:
    """Create a new receipt upload


    The `uri` will be a pre-signed S3 URL allowing you to upload the receipt securely. This URL can only
    be used for a `PUT` operation and expires 30 minutes after its creation. Once your upload is
    complete, we will try to match the receipt with existing expenses.

    Refer to these [docs](https://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html)
    on how to upload to this pre-signed S3 URL. We highly recommend using one of AWS SDKs if they're
    available for your language to upload these files.

    Args:
        expense_id (str):
        body (ReceiptUploadRequest): The parameter for creating a receipt upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CreateAsyncFileUploadResponse]
    """

    return sync_detailed(
        expense_id=expense_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    expense_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReceiptUploadRequest,
) -> Response[Union[Any, CreateAsyncFileUploadResponse]]:
    """Create a new receipt upload


    The `uri` will be a pre-signed S3 URL allowing you to upload the receipt securely. This URL can only
    be used for a `PUT` operation and expires 30 minutes after its creation. Once your upload is
    complete, we will try to match the receipt with existing expenses.

    Refer to these [docs](https://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html)
    on how to upload to this pre-signed S3 URL. We highly recommend using one of AWS SDKs if they're
    available for your language to upload these files.

    Args:
        expense_id (str):
        body (ReceiptUploadRequest): The parameter for creating a receipt upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CreateAsyncFileUploadResponse]]
    """

    kwargs = _get_kwargs(
        expense_id=expense_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    expense_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ReceiptUploadRequest,
) -> Optional[Union[Any, CreateAsyncFileUploadResponse]]:
    """Create a new receipt upload


    The `uri` will be a pre-signed S3 URL allowing you to upload the receipt securely. This URL can only
    be used for a `PUT` operation and expires 30 minutes after its creation. Once your upload is
    complete, we will try to match the receipt with existing expenses.

    Refer to these [docs](https://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html)
    on how to upload to this pre-signed S3 URL. We highly recommend using one of AWS SDKs if they're
    available for your language to upload these files.

    Args:
        expense_id (str):
        body (ReceiptUploadRequest): The parameter for creating a receipt upload.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CreateAsyncFileUploadResponse]
    """

    return (
        await asyncio_detailed(
            expense_id=expense_id,
            client=client,
            body=body,
        )
    ).parsed
