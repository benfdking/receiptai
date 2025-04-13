from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.page_statement import PageStatement
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v2/accounts/cash/{id}/statements",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, PageStatement]]:
    if response.status_code == 200:
        response_200 = PageStatement.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, PageStatement]]:
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
) -> Response[Union[Any, PageStatement]]:
    """
    List cash account statements.


    This endpoint lists all finalized statements for the cash account by ID.

    Args:
        id (str):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PageStatement]]
    """

    kwargs = _get_kwargs(
        id=id,
        cursor=cursor,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[Union[Any, PageStatement]]:
    """
    List cash account statements.


    This endpoint lists all finalized statements for the cash account by ID.

    Args:
        id (str):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PageStatement]
    """

    return sync_detailed(
        id=id,
        client=client,
        cursor=cursor,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[Union[Any, PageStatement]]:
    """
    List cash account statements.


    This endpoint lists all finalized statements for the cash account by ID.

    Args:
        id (str):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PageStatement]]
    """

    kwargs = _get_kwargs(
        id=id,
        cursor=cursor,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[Union[Any, PageStatement]]:
    """
    List cash account statements.


    This endpoint lists all finalized statements for the cash account by ID.

    Args:
        id (str):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PageStatement]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            cursor=cursor,
            limit=limit,
        )
    ).parsed
