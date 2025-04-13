from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="ReviewerDetails")


@_attrs_define
class ReviewerDetails:
    """
    Attributes:
        reviewer (Union[None, Unset, list['User']]):
        status (Union[None, Unset, str]):
    """

    reviewer: Union[None, Unset, list["User"]] = UNSET
    status: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reviewer: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.reviewer, Unset):
            reviewer = UNSET
        elif isinstance(self.reviewer, list):
            reviewer = []
            for reviewer_type_0_item_data in self.reviewer:
                reviewer_type_0_item = reviewer_type_0_item_data.to_dict()
                reviewer.append(reviewer_type_0_item)

        else:
            reviewer = self.reviewer

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reviewer is not UNSET:
            field_dict["reviewer"] = reviewer
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)

        def _parse_reviewer(data: object) -> Union[None, Unset, list["User"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                reviewer_type_0 = []
                _reviewer_type_0 = data
                for reviewer_type_0_item_data in _reviewer_type_0:
                    reviewer_type_0_item = User.from_dict(reviewer_type_0_item_data)

                    reviewer_type_0.append(reviewer_type_0_item)

                return reviewer_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["User"]], data)

        reviewer = _parse_reviewer(d.pop("reviewer", UNSET))

        def _parse_status(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        status = _parse_status(d.pop("status", UNSET))

        reviewer_details = cls(
            reviewer=reviewer,
            status=status,
        )

        reviewer_details.additional_properties = d
        return reviewer_details

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
