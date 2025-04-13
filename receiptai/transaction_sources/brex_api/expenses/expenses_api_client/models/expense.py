import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.category import Category
from ..models.expense_payment_status import ExpensePaymentStatus
from ..models.expense_status import ExpenseStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.expense_billing_amount_type_1 import ExpenseBillingAmountType1
    from ..models.expense_original_amount_type_1 import ExpenseOriginalAmountType1


T = TypeVar("T", bound="Expense")


@_attrs_define
class Expense:
    """
    Attributes:
        id (str): Unique ID associated with the expense.
        updated_at (datetime.datetime): The last time the expense was updated.
        memo (Union[None, Unset, str]): The memo of the expense.
        location_id (Union[None, Unset, str]):
        department_id (Union[None, Unset, str]):
        category (Union[Category, None, Unset]):
        merchant_id (Union[None, Unset, str]):
        budget_id (Union[None, Unset, str]):
        original_amount (Union['ExpenseOriginalAmountType1', None, Unset]):
        billing_amount (Union['ExpenseBillingAmountType1', None, Unset]):
        purchased_at (Union[None, Unset, datetime.datetime]): The time the purchase was made.
        status (Union[ExpenseStatus, None, Unset]):
        payment_status (Union[ExpensePaymentStatus, None, Unset]):
    """

    id: str
    updated_at: datetime.datetime
    memo: Union[None, Unset, str] = UNSET
    location_id: Union[None, Unset, str] = UNSET
    department_id: Union[None, Unset, str] = UNSET
    category: Union[Category, None, Unset] = UNSET
    merchant_id: Union[None, Unset, str] = UNSET
    budget_id: Union[None, Unset, str] = UNSET
    original_amount: Union["ExpenseOriginalAmountType1", None, Unset] = UNSET
    billing_amount: Union["ExpenseBillingAmountType1", None, Unset] = UNSET
    purchased_at: Union[None, Unset, datetime.datetime] = UNSET
    status: Union[ExpenseStatus, None, Unset] = UNSET
    payment_status: Union[ExpensePaymentStatus, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.expense_billing_amount_type_1 import ExpenseBillingAmountType1
        from ..models.expense_original_amount_type_1 import ExpenseOriginalAmountType1

        id = self.id

        updated_at = self.updated_at.isoformat()

        memo: Union[None, Unset, str]
        if isinstance(self.memo, Unset):
            memo = UNSET
        else:
            memo = self.memo

        location_id: Union[None, Unset, str]
        if isinstance(self.location_id, Unset):
            location_id = UNSET
        else:
            location_id = self.location_id

        department_id: Union[None, Unset, str]
        if isinstance(self.department_id, Unset):
            department_id = UNSET
        else:
            department_id = self.department_id

        category: Union[None, Unset, str]
        if isinstance(self.category, Unset):
            category = UNSET
        elif isinstance(self.category, Category):
            category = self.category.value
        else:
            category = self.category

        merchant_id: Union[None, Unset, str]
        if isinstance(self.merchant_id, Unset):
            merchant_id = UNSET
        else:
            merchant_id = self.merchant_id

        budget_id: Union[None, Unset, str]
        if isinstance(self.budget_id, Unset):
            budget_id = UNSET
        else:
            budget_id = self.budget_id

        original_amount: Union[None, Unset, dict[str, Any]]
        if isinstance(self.original_amount, Unset):
            original_amount = UNSET
        elif isinstance(self.original_amount, ExpenseOriginalAmountType1):
            original_amount = self.original_amount.to_dict()
        else:
            original_amount = self.original_amount

        billing_amount: Union[None, Unset, dict[str, Any]]
        if isinstance(self.billing_amount, Unset):
            billing_amount = UNSET
        elif isinstance(self.billing_amount, ExpenseBillingAmountType1):
            billing_amount = self.billing_amount.to_dict()
        else:
            billing_amount = self.billing_amount

        purchased_at: Union[None, Unset, str]
        if isinstance(self.purchased_at, Unset):
            purchased_at = UNSET
        elif isinstance(self.purchased_at, datetime.datetime):
            purchased_at = self.purchased_at.isoformat()
        else:
            purchased_at = self.purchased_at

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, ExpenseStatus):
            status = self.status.value
        else:
            status = self.status

        payment_status: Union[None, Unset, str]
        if isinstance(self.payment_status, Unset):
            payment_status = UNSET
        elif isinstance(self.payment_status, ExpensePaymentStatus):
            payment_status = self.payment_status.value
        else:
            payment_status = self.payment_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "updated_at": updated_at,
            }
        )
        if memo is not UNSET:
            field_dict["memo"] = memo
        if location_id is not UNSET:
            field_dict["location_id"] = location_id
        if department_id is not UNSET:
            field_dict["department_id"] = department_id
        if category is not UNSET:
            field_dict["category"] = category
        if merchant_id is not UNSET:
            field_dict["merchant_id"] = merchant_id
        if budget_id is not UNSET:
            field_dict["budget_id"] = budget_id
        if original_amount is not UNSET:
            field_dict["original_amount"] = original_amount
        if billing_amount is not UNSET:
            field_dict["billing_amount"] = billing_amount
        if purchased_at is not UNSET:
            field_dict["purchased_at"] = purchased_at
        if status is not UNSET:
            field_dict["status"] = status
        if payment_status is not UNSET:
            field_dict["payment_status"] = payment_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.expense_billing_amount_type_1 import ExpenseBillingAmountType1
        from ..models.expense_original_amount_type_1 import ExpenseOriginalAmountType1

        d = dict(src_dict)
        id = d.pop("id")

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_memo(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        memo = _parse_memo(d.pop("memo", UNSET))

        def _parse_location_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        location_id = _parse_location_id(d.pop("location_id", UNSET))

        def _parse_department_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        department_id = _parse_department_id(d.pop("department_id", UNSET))

        def _parse_category(data: object) -> Union[Category, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                category_type_1 = Category(data)

                return category_type_1
            except:  # noqa: E722
                pass
            return cast(Union[Category, None, Unset], data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_merchant_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        merchant_id = _parse_merchant_id(d.pop("merchant_id", UNSET))

        def _parse_budget_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        budget_id = _parse_budget_id(d.pop("budget_id", UNSET))

        def _parse_original_amount(data: object) -> Union["ExpenseOriginalAmountType1", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                original_amount_type_1 = ExpenseOriginalAmountType1.from_dict(data)

                return original_amount_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ExpenseOriginalAmountType1", None, Unset], data)

        original_amount = _parse_original_amount(d.pop("original_amount", UNSET))

        def _parse_billing_amount(data: object) -> Union["ExpenseBillingAmountType1", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                billing_amount_type_1 = ExpenseBillingAmountType1.from_dict(data)

                return billing_amount_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ExpenseBillingAmountType1", None, Unset], data)

        billing_amount = _parse_billing_amount(d.pop("billing_amount", UNSET))

        def _parse_purchased_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                purchased_at_type_0 = isoparse(data)

                return purchased_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        purchased_at = _parse_purchased_at(d.pop("purchased_at", UNSET))

        def _parse_status(data: object) -> Union[ExpenseStatus, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_1 = ExpenseStatus(data)

                return status_type_1
            except:  # noqa: E722
                pass
            return cast(Union[ExpenseStatus, None, Unset], data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_payment_status(data: object) -> Union[ExpensePaymentStatus, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                payment_status_type_1 = ExpensePaymentStatus(data)

                return payment_status_type_1
            except:  # noqa: E722
                pass
            return cast(Union[ExpensePaymentStatus, None, Unset], data)

        payment_status = _parse_payment_status(d.pop("payment_status", UNSET))

        expense = cls(
            id=id,
            updated_at=updated_at,
            memo=memo,
            location_id=location_id,
            department_id=department_id,
            category=category,
            merchant_id=merchant_id,
            budget_id=budget_id,
            original_amount=original_amount,
            billing_amount=billing_amount,
            purchased_at=purchased_at,
            status=status,
            payment_status=payment_status,
        )

        expense.additional_properties = d
        return expense

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
