from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Address")


@_attrs_define
class Address:
    """Company business address (must be in the US; no PO box or virtual/forwarding addresses allowed).

    Attributes:
        line1 (Union[None, Unset, str]): Address line 1, no PO Box.
        line2 (Union[None, Unset, str]): Address line 2 (e.g., apartment, suite, unit, or building).
        city (Union[None, Unset, str]): City, district, suburb, town, or village.
        state (Union[None, Unset, str]): For US-addressed the 2-letter State abbreviation. For international-addresses
            the county, providence, or region.
        country (Union[None, Unset, str]): Two-letter country code (ISO 3166-1 alpha-2).
        postal_code (Union[None, Unset, str]): ZIP or postal code.
        phone_number (Union[None, Unset, str]): Phone number.
    """

    line1: Union[None, Unset, str] = UNSET
    line2: Union[None, Unset, str] = UNSET
    city: Union[None, Unset, str] = UNSET
    state: Union[None, Unset, str] = UNSET
    country: Union[None, Unset, str] = UNSET
    postal_code: Union[None, Unset, str] = UNSET
    phone_number: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        line1: Union[None, Unset, str]
        if isinstance(self.line1, Unset):
            line1 = UNSET
        else:
            line1 = self.line1

        line2: Union[None, Unset, str]
        if isinstance(self.line2, Unset):
            line2 = UNSET
        else:
            line2 = self.line2

        city: Union[None, Unset, str]
        if isinstance(self.city, Unset):
            city = UNSET
        else:
            city = self.city

        state: Union[None, Unset, str]
        if isinstance(self.state, Unset):
            state = UNSET
        else:
            state = self.state

        country: Union[None, Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        else:
            country = self.country

        postal_code: Union[None, Unset, str]
        if isinstance(self.postal_code, Unset):
            postal_code = UNSET
        else:
            postal_code = self.postal_code

        phone_number: Union[None, Unset, str]
        if isinstance(self.phone_number, Unset):
            phone_number = UNSET
        else:
            phone_number = self.phone_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if line1 is not UNSET:
            field_dict["line1"] = line1
        if line2 is not UNSET:
            field_dict["line2"] = line2
        if city is not UNSET:
            field_dict["city"] = city
        if state is not UNSET:
            field_dict["state"] = state
        if country is not UNSET:
            field_dict["country"] = country
        if postal_code is not UNSET:
            field_dict["postal_code"] = postal_code
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_line1(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        line1 = _parse_line1(d.pop("line1", UNSET))

        def _parse_line2(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        line2 = _parse_line2(d.pop("line2", UNSET))

        def _parse_city(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        city = _parse_city(d.pop("city", UNSET))

        def _parse_state(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        state = _parse_state(d.pop("state", UNSET))

        def _parse_country(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        country = _parse_country(d.pop("country", UNSET))

        def _parse_postal_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        postal_code = _parse_postal_code(d.pop("postal_code", UNSET))

        def _parse_phone_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        phone_number = _parse_phone_number(d.pop("phone_number", UNSET))

        address = cls(
            line1=line1,
            line2=line2,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            phone_number=phone_number,
        )

        address.additional_properties = d
        return address

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
