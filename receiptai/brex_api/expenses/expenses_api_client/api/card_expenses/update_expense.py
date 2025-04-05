from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.expense import Expense
from ...models.update_expense_request import UpdateExpenseRequest
from ...types import Response


def _get_kwargs(
    expense_id: str,
    *,
    body: UpdateExpenseRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/v1/expenses/card/{expense_id}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Expense]]:
    if response.status_code == 200:
        response_200 = Expense.from_dict(response.json())

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
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, Expense]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    expense_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExpenseRequest,
) -> Response[Union[Any, Expense]]:
    """Update an expense

     Update an expense. Admin and bookkeeper have access to any expense, and regular users can only
    access their own.

    Args:
        expense_id (str):
        body (UpdateExpenseRequest): The parameter for updating an expense.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Expense]]
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
    client: AuthenticatedClient,
    body: UpdateExpenseRequest,
) -> Optional[Union[Any, Expense]]:
    """Update an expense

     Update an expense. Admin and bookkeeper have access to any expense, and regular users can only
    access their own.

    Args:
        expense_id (str):
        body (UpdateExpenseRequest): The parameter for updating an expense.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Expense]
    """

    return sync_detailed(
        expense_id=expense_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    expense_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExpenseRequest,
) -> Response[Union[Any, Expense]]:
    """Update an expense

     Update an expense. Admin and bookkeeper have access to any expense, and regular users can only
    access their own.

    Args:
        expense_id (str):
        body (UpdateExpenseRequest): The parameter for updating an expense.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Expense]]
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
    client: AuthenticatedClient,
    body: UpdateExpenseRequest,
) -> Optional[Union[Any, Expense]]:
    """Update an expense

     Update an expense. Admin and bookkeeper have access to any expense, and regular users can only
    access their own.

    Args:
        expense_id (str):
        body (UpdateExpenseRequest): The parameter for updating an expense.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Expense]
    """

    return (
        await asyncio_detailed(
            expense_id=expense_id,
            client=client,
            body=body,
        )
    ).parsed
