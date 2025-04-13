import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
    user_ids: Union[None, Unset, list[str]] = UNSET,
    posted_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    expand: Union[None, Unset, list[str]] = UNSET,
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

    json_user_ids: Union[None, Unset, list[str]]
    if isinstance(user_ids, Unset):
        json_user_ids = UNSET
    elif isinstance(user_ids, list):
        json_user_ids = user_ids

    else:
        json_user_ids = user_ids
    params["user_ids"] = json_user_ids

    json_posted_at_start: Union[None, Unset, str]
    if isinstance(posted_at_start, Unset):
        json_posted_at_start = UNSET
    elif isinstance(posted_at_start, datetime.datetime):
        json_posted_at_start = posted_at_start.isoformat()
    else:
        json_posted_at_start = posted_at_start
    params["posted_at_start"] = json_posted_at_start

    json_expand: Union[None, Unset, list[str]]
    if isinstance(expand, Unset):
        json_expand = UNSET
    elif isinstance(expand, list):
        json_expand = expand

    else:
        json_expand = expand
    params["expand[]"] = json_expand

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/transactions/card/primary",
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
    *,
    client: AuthenticatedClient,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
    user_ids: Union[None, Unset, list[str]] = UNSET,
    posted_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    expand: Union[None, Unset, list[str]] = UNSET,
) -> Response[Any]:
    r"""
    List transactions for all card accounts.


    This endpoint lists all settled transactions for all card accounts.
    Regular users may only fetch their own \"PURCHASE\",\"REFUND\" and \"CHARGEBACK\" settled
    transactions.

    Args:
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):
        user_ids (Union[None, Unset, list[str]]):
        posted_at_start (Union[None, Unset, datetime.datetime]):
        expand (Union[None, Unset, list[str]]): `expense_id` can be passed to `expand[]` query
            parameter to get expanded, e.g., `?expand[]=expense_id`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        cursor=cursor,
        limit=limit,
        user_ids=user_ids,
        posted_at_start=posted_at_start,
        expand=expand,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
    user_ids: Union[None, Unset, list[str]] = UNSET,
    posted_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    expand: Union[None, Unset, list[str]] = UNSET,
) -> Response[Any]:
    r"""
    List transactions for all card accounts.


    This endpoint lists all settled transactions for all card accounts.
    Regular users may only fetch their own \"PURCHASE\",\"REFUND\" and \"CHARGEBACK\" settled
    transactions.

    Args:
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):
        user_ids (Union[None, Unset, list[str]]):
        posted_at_start (Union[None, Unset, datetime.datetime]):
        expand (Union[None, Unset, list[str]]): `expense_id` can be passed to `expand[]` query
            parameter to get expanded, e.g., `?expand[]=expense_id`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        cursor=cursor,
        limit=limit,
        user_ids=user_ids,
        posted_at_start=posted_at_start,
        expand=expand,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
