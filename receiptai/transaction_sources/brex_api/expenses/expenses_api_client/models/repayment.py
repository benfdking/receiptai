import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="Repayment")


@_attrs_define
class Repayment:
    """
    Attributes:
        repayment_initiated_by (Union['User', None, Unset]):
        repayment_initiation_date (Union[None, Unset, datetime.datetime]):
    """

    repayment_initiated_by: Union["User", None, Unset] = UNSET
    repayment_initiation_date: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User

        repayment_initiated_by: Union[None, Unset, dict[str, Any]]
        if isinstance(self.repayment_initiated_by, Unset):
            repayment_initiated_by = UNSET
        elif isinstance(self.repayment_initiated_by, User):
            repayment_initiated_by = self.repayment_initiated_by.to_dict()
        else:
            repayment_initiated_by = self.repayment_initiated_by

        repayment_initiation_date: Union[None, Unset, str]
        if isinstance(self.repayment_initiation_date, Unset):
            repayment_initiation_date = UNSET
        elif isinstance(self.repayment_initiation_date, datetime.datetime):
            repayment_initiation_date = self.repayment_initiation_date.isoformat()
        else:
            repayment_initiation_date = self.repayment_initiation_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repayment_initiated_by is not UNSET:
            field_dict["repayment_initiated_by"] = repayment_initiated_by
        if repayment_initiation_date is not UNSET:
            field_dict["repayment_initiation_date"] = repayment_initiation_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)

        def _parse_repayment_initiated_by(data: object) -> Union["User", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                repayment_initiated_by_type_1 = User.from_dict(data)

                return repayment_initiated_by_type_1
            except:  # noqa: E722
                pass
            return cast(Union["User", None, Unset], data)

        repayment_initiated_by = _parse_repayment_initiated_by(d.pop("repayment_initiated_by", UNSET))

        def _parse_repayment_initiation_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                repayment_initiation_date_type_0 = isoparse(data)

                return repayment_initiation_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        repayment_initiation_date = _parse_repayment_initiation_date(d.pop("repayment_initiation_date", UNSET))

        repayment = cls(
            repayment_initiated_by=repayment_initiated_by,
            repayment_initiation_date=repayment_initiation_date,
        )

        repayment.additional_properties = d
        return repayment

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
