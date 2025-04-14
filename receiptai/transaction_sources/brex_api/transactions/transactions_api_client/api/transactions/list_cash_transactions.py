import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
    posted_at_start: Union[None, Unset, datetime.datetime] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_cursor: Union[None, Unset, str]
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

    json_limit: Union[None, Unset, int]
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    json_posted_at_start: Union[None, Unset, str]
    if isinstance(posted_at_start, Unset):
        json_posted_at_start = UNSET
    elif isinstance(posted_at_start, datetime.datetime):
        json_posted_at_start = posted_at_start.isoformat()
    else:
        json_posted_at_start = posted_at_start
    params["posted_at_start"] = json_posted_at_start

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v2/transactions/cash/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == 400:
        return None
    if response.status_code == 401:
        return None
    if response.status_code == 403:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
    posted_at_start: Union[None, Unset, datetime.datetime] = UNSET,
) -> Response[Any]:
    """
    List transactions for the selected cash account.


    This endpoint lists all transactions for the cash account with the selected ID.

    Args:
        id (str):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):
        posted_at_start (Union[None, Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        cursor=cursor,
        limit=limit,
        posted_at_start=posted_at_start,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
    posted_at_start: Union[None, Unset, datetime.datetime] = UNSET,
) -> Response[Any]:
    """
    List transactions for the selected cash account.


    This endpoint lists all transactions for the cash account with the selected ID.

    Args:
        id (str):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):
        posted_at_start (Union[None, Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        cursor=cursor,
        limit=limit,
        posted_at_start=posted_at_start,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
