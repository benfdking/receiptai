from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReceiptMatchRequest")


@_attrs_define
class ReceiptMatchRequest:
    """The parameter for creating a receipt match.

    Attributes:
        receipt_name (str): The name of the receipt (with the file extension). It will be used in the matching result
            email.
    """

    receipt_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        receipt_name = self.receipt_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "receipt_name": receipt_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        receipt_name = d.pop("receipt_name")

        receipt_match_request = cls(
            receipt_name=receipt_name,
        )

        receipt_match_request.additional_properties = d
        return receipt_match_request

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
