import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.expense_payment_status import ExpensePaymentStatus
from ...models.expense_status import ExpenseStatus
from ...models.expense_type import ExpenseType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    expand: Union[None, Unset, list[str]] = UNSET,
    user_id: Union[None, Unset, list[str]] = UNSET,
    parent_expense_id: Union[None, Unset, list[str]] = UNSET,
    budget_id: Union[None, Unset, list[str]] = UNSET,
    spending_entity_id: Union[None, Unset, list[str]] = UNSET,
    expense_type: Union[None, Unset, list[ExpenseType]] = UNSET,
    status: Union[None, Unset, list[ExpenseStatus]] = UNSET,
    payment_status: Union[None, Unset, list[ExpensePaymentStatus]] = UNSET,
    purchased_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    purchased_at_end: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_end: Union[None, Unset, datetime.datetime] = UNSET,
    load_custom_fields: Union[None, Unset, bool] = UNSET,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
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

    json_user_id: Union[None, Unset, list[str]]
    if isinstance(user_id, Unset):
        json_user_id = UNSET
    elif isinstance(user_id, list):
        json_user_id = user_id

    else:
        json_user_id = user_id
    params["user_id[]"] = json_user_id

    json_parent_expense_id: Union[None, Unset, list[str]]
    if isinstance(parent_expense_id, Unset):
        json_parent_expense_id = UNSET
    elif isinstance(parent_expense_id, list):
        json_parent_expense_id = parent_expense_id

    else:
        json_parent_expense_id = parent_expense_id
    params["parent_expense_id[]"] = json_parent_expense_id

    json_budget_id: Union[None, Unset, list[str]]
    if isinstance(budget_id, Unset):
        json_budget_id = UNSET
    elif isinstance(budget_id, list):
        json_budget_id = budget_id

    else:
        json_budget_id = budget_id
    params["budget_id[]"] = json_budget_id

    json_spending_entity_id: Union[None, Unset, list[str]]
    if isinstance(spending_entity_id, Unset):
        json_spending_entity_id = UNSET
    elif isinstance(spending_entity_id, list):
        json_spending_entity_id = spending_entity_id

    else:
        json_spending_entity_id = spending_entity_id
    params["spending_entity_id[]"] = json_spending_entity_id

    json_expense_type: Union[None, Unset, list[str]]
    if isinstance(expense_type, Unset):
        json_expense_type = UNSET
    elif isinstance(expense_type, list):
        json_expense_type = []
        for expense_type_type_0_item_data in expense_type:
            expense_type_type_0_item = expense_type_type_0_item_data.value
            json_expense_type.append(expense_type_type_0_item)

    else:
        json_expense_type = expense_type
    params["expense_type[]"] = json_expense_type

    json_status: Union[None, Unset, list[str]]
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, list):
        json_status = []
        for status_type_0_item_data in status:
            status_type_0_item = status_type_0_item_data.value
            json_status.append(status_type_0_item)

    else:
        json_status = status
    params["status[]"] = json_status

    json_payment_status: Union[None, Unset, list[str]]
    if isinstance(payment_status, Unset):
        json_payment_status = UNSET
    elif isinstance(payment_status, list):
        json_payment_status = []
        for payment_status_type_0_item_data in payment_status:
            payment_status_type_0_item = payment_status_type_0_item_data.value
            json_payment_status.append(payment_status_type_0_item)

    else:
        json_payment_status = payment_status
    params["payment_status[]"] = json_payment_status

    json_purchased_at_start: Union[None, Unset, str]
    if isinstance(purchased_at_start, Unset):
        json_purchased_at_start = UNSET
    elif isinstance(purchased_at_start, datetime.datetime):
        json_purchased_at_start = purchased_at_start.isoformat()
    else:
        json_purchased_at_start = purchased_at_start
    params["purchased_at_start"] = json_purchased_at_start

    json_purchased_at_end: Union[None, Unset, str]
    if isinstance(purchased_at_end, Unset):
        json_purchased_at_end = UNSET
    elif isinstance(purchased_at_end, datetime.datetime):
        json_purchased_at_end = purchased_at_end.isoformat()
    else:
        json_purchased_at_end = purchased_at_end
    params["purchased_at_end"] = json_purchased_at_end

    json_updated_at_start: Union[None, Unset, str]
    if isinstance(updated_at_start, Unset):
        json_updated_at_start = UNSET
    elif isinstance(updated_at_start, datetime.datetime):
        json_updated_at_start = updated_at_start.isoformat()
    else:
        json_updated_at_start = updated_at_start
    params["updated_at_start"] = json_updated_at_start

    json_updated_at_end: Union[None, Unset, str]
    if isinstance(updated_at_end, Unset):
        json_updated_at_end = UNSET
    elif isinstance(updated_at_end, datetime.datetime):
        json_updated_at_end = updated_at_end.isoformat()
    else:
        json_updated_at_end = updated_at_end
    params["updated_at_end"] = json_updated_at_end

    json_load_custom_fields: Union[None, Unset, bool]
    if isinstance(load_custom_fields, Unset):
        json_load_custom_fields = UNSET
    else:
        json_load_custom_fields = load_custom_fields
    params["load_custom_fields"] = json_load_custom_fields

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
        "url": "/v1/expenses",
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
    expand: Union[None, Unset, list[str]] = UNSET,
    user_id: Union[None, Unset, list[str]] = UNSET,
    parent_expense_id: Union[None, Unset, list[str]] = UNSET,
    budget_id: Union[None, Unset, list[str]] = UNSET,
    spending_entity_id: Union[None, Unset, list[str]] = UNSET,
    expense_type: Union[None, Unset, list[ExpenseType]] = UNSET,
    status: Union[None, Unset, list[ExpenseStatus]] = UNSET,
    payment_status: Union[None, Unset, list[ExpensePaymentStatus]] = UNSET,
    purchased_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    purchased_at_end: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_end: Union[None, Unset, datetime.datetime] = UNSET,
    load_custom_fields: Union[None, Unset, bool] = UNSET,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[Any]:
    """List expenses

     List expenses under the same account. Admin and bookkeeper have access to any expense, and regular
    users can only access their own.

    Args:
        expand (Union[None, Unset, list[str]]):
        user_id (Union[None, Unset, list[str]]):
        parent_expense_id (Union[None, Unset, list[str]]):
        budget_id (Union[None, Unset, list[str]]):
        spending_entity_id (Union[None, Unset, list[str]]):
        expense_type (Union[None, Unset, list[ExpenseType]]):
        status (Union[None, Unset, list[ExpenseStatus]]):
        payment_status (Union[None, Unset, list[ExpensePaymentStatus]]):
        purchased_at_start (Union[None, Unset, datetime.datetime]):
        purchased_at_end (Union[None, Unset, datetime.datetime]):
        updated_at_start (Union[None, Unset, datetime.datetime]):
        updated_at_end (Union[None, Unset, datetime.datetime]):
        load_custom_fields (Union[None, Unset, bool]):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        expand=expand,
        user_id=user_id,
        parent_expense_id=parent_expense_id,
        budget_id=budget_id,
        spending_entity_id=spending_entity_id,
        expense_type=expense_type,
        status=status,
        payment_status=payment_status,
        purchased_at_start=purchased_at_start,
        purchased_at_end=purchased_at_end,
        updated_at_start=updated_at_start,
        updated_at_end=updated_at_end,
        load_custom_fields=load_custom_fields,
        cursor=cursor,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    expand: Union[None, Unset, list[str]] = UNSET,
    user_id: Union[None, Unset, list[str]] = UNSET,
    parent_expense_id: Union[None, Unset, list[str]] = UNSET,
    budget_id: Union[None, Unset, list[str]] = UNSET,
    spending_entity_id: Union[None, Unset, list[str]] = UNSET,
    expense_type: Union[None, Unset, list[ExpenseType]] = UNSET,
    status: Union[None, Unset, list[ExpenseStatus]] = UNSET,
    payment_status: Union[None, Unset, list[ExpensePaymentStatus]] = UNSET,
    purchased_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    purchased_at_end: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_start: Union[None, Unset, datetime.datetime] = UNSET,
    updated_at_end: Union[None, Unset, datetime.datetime] = UNSET,
    load_custom_fields: Union[None, Unset, bool] = UNSET,
    cursor: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[Any]:
    """List expenses

     List expenses under the same account. Admin and bookkeeper have access to any expense, and regular
    users can only access their own.

    Args:
        expand (Union[None, Unset, list[str]]):
        user_id (Union[None, Unset, list[str]]):
        parent_expense_id (Union[None, Unset, list[str]]):
        budget_id (Union[None, Unset, list[str]]):
        spending_entity_id (Union[None, Unset, list[str]]):
        expense_type (Union[None, Unset, list[ExpenseType]]):
        status (Union[None, Unset, list[ExpenseStatus]]):
        payment_status (Union[None, Unset, list[ExpensePaymentStatus]]):
        purchased_at_start (Union[None, Unset, datetime.datetime]):
        purchased_at_end (Union[None, Unset, datetime.datetime]):
        updated_at_start (Union[None, Unset, datetime.datetime]):
        updated_at_end (Union[None, Unset, datetime.datetime]):
        load_custom_fields (Union[None, Unset, bool]):
        cursor (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        expand=expand,
        user_id=user_id,
        parent_expense_id=parent_expense_id,
        budget_id=budget_id,
        spending_entity_id=spending_entity_id,
        expense_type=expense_type,
        status=status,
        payment_status=payment_status,
        purchased_at_start=purchased_at_start,
        purchased_at_end=purchased_at_end,
        updated_at_start=updated_at_start,
        updated_at_end=updated_at_end,
        load_custom_fields=load_custom_fields,
        cursor=cursor,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
