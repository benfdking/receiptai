from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    expand: Union[None, Unset, list[str]] = UNSET,
    load_custom_fields: Union[None, Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_expand: Union[None, Unset, list[str]]
    if isinstance(expand, Unset):
        json_expand = UNSET
    elif isinstance(expand, list):
        json_expand = expand

    else:
        json_expand = expand
    params["expand[]"] = json_expand

    json_load_custom_fields: Union[None, Unset, bool]
    if isinstance(load_custom_fields, Unset):
        json_load_custom_fields = UNSET
    else:
        json_load_custom_fields = load_custom_fields
    params["load_custom_fields"] = json_load_custom_fields

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/expenses/{id}",
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
    if response.status_code == 404:
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
    expand: Union[None, Unset, list[str]] = UNSET,
    load_custom_fields: Union[None, Unset, bool] = UNSET,
) -> Response[Any]:
    """Get an expense

     Get an expense by its ID.

    Args:
        id (str):
        expand (Union[None, Unset, list[str]]):
        load_custom_fields (Union[None, Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        expand=expand,
        load_custom_fields=load_custom_fields,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    expand: Union[None, Unset, list[str]] = UNSET,
    load_custom_fields: Union[None, Unset, bool] = UNSET,
) -> Response[Any]:
    """Get an expense

     Get an expense by its ID.

    Args:
        id (str):
        expand (Union[None, Unset, list[str]]):
        load_custom_fields (Union[None, Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id=id,
        expand=expand,
        load_custom_fields=load_custom_fields,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
