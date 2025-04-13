from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Money")


@_attrs_define
class Money:
    """
    Money fields can be signed or unsigned. Fields are signed (an unsigned value will be interpreted as positive). The
    amount of money will be represented in the smallest denomination
    of the currency indicated. For example, USD 7.00 will be represented in cents with an amount of 700.

        Attributes:
            amount (Union[Unset, int]): The amount of money, in the smallest denomination of the currency indicated by
                currency. For example, when currency is USD, amount is in cents.
            currency (Union[None, Unset, str]): The type of currency, in ISO 4217 format. Default to USD if not specified
    """

    amount: Union[Unset, int] = UNSET
    currency: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        currency: Union[None, Unset, str]
        if isinstance(self.currency, Unset):
            currency = UNSET
        else:
            currency = self.currency

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if amount is not UNSET:
            field_dict["amount"] = amount
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount", UNSET)

        def _parse_currency(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        currency = _parse_currency(d.pop("currency", UNSET))

        money = cls(
            amount=amount,
            currency=currency,
        )

        money.additional_properties = d
        return money

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
