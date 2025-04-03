from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Merchant")


@_attrs_define
class Merchant:
    """
    Attributes:
        raw_descriptor (str): Merchant descriptor, it can be the merchant name.
        mcc (str): A four-digit number listed in ISO 18245 for retail financial services, e.g. 4121 for Taxicabs and
            Rideshares. Please refer to https://en.wikipedia.org/wiki/Merchant_category_code for more details.
        country (str): Merchant's country, in ISO 3166-1 alpha-3 format.
    """

    raw_descriptor: str
    mcc: str
    country: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        raw_descriptor = self.raw_descriptor

        mcc = self.mcc

        country = self.country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "raw_descriptor": raw_descriptor,
                "mcc": mcc,
                "country": country,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        raw_descriptor = d.pop("raw_descriptor")

        mcc = d.pop("mcc")

        country = d.pop("country")

        merchant = cls(
            raw_descriptor=raw_descriptor,
            mcc=mcc,
            country=country,
        )

        merchant.additional_properties = d
        return merchant

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
