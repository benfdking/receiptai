from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OptionString")


@_attrs_define
class OptionString:
    """Option string fields have a label and a identifier.

    Attributes:
        option_id (str): The identifier when custom field data is of type option string.
        option_label (str): The label when custom field data is of type option string.
    """

    option_id: str
    option_label: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        option_id = self.option_id

        option_label = self.option_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "option_id": option_id,
                "option_label": option_label,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        option_id = d.pop("option_id")

        option_label = d.pop("option_label")

        option_string = cls(
            option_id=option_id,
            option_label=option_label,
        )

        option_string.additional_properties = d
        return option_string

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
