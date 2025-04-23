import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.review_approver_type_1 import ReviewApproverType1
    from ..models.review_copilot_approver_type_1 import ReviewCopilotApproverType1
    from ..models.review_reviewers_type_1 import ReviewReviewersType1


T = TypeVar("T", bound="Review")


@_attrs_define
class Review:
    """
    Attributes:
        compliance_status (Union[None, str]): Compliance status of the expense
        reviewers (Union['ReviewReviewersType1', None]):
        approver (Union['ReviewApproverType1', None]):
        copilot_approver (Union['ReviewCopilotApproverType1', None]):
        approved_at (Union[None, datetime.datetime]): Time when the User gave the approval
    """

    compliance_status: Union[None, str]
    reviewers: Union["ReviewReviewersType1", None]
    approver: Union["ReviewApproverType1", None]
    copilot_approver: Union["ReviewCopilotApproverType1", None]
    approved_at: Union[None, datetime.datetime]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.review_approver_type_1 import ReviewApproverType1
        from ..models.review_copilot_approver_type_1 import ReviewCopilotApproverType1
        from ..models.review_reviewers_type_1 import ReviewReviewersType1

        compliance_status: Union[None, str]
        compliance_status = self.compliance_status

        reviewers: Union[None, dict[str, Any]]
        if isinstance(self.reviewers, ReviewReviewersType1):
            reviewers = self.reviewers.to_dict()
        else:
            reviewers = self.reviewers

        approver: Union[None, dict[str, Any]]
        if isinstance(self.approver, ReviewApproverType1):
            approver = self.approver.to_dict()
        else:
            approver = self.approver

        copilot_approver: Union[None, dict[str, Any]]
        if isinstance(self.copilot_approver, ReviewCopilotApproverType1):
            copilot_approver = self.copilot_approver.to_dict()
        else:
            copilot_approver = self.copilot_approver

        approved_at: Union[None, str]
        if isinstance(self.approved_at, datetime.datetime):
            approved_at = self.approved_at.isoformat()
        else:
            approved_at = self.approved_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "compliance_status": compliance_status,
                "reviewers": reviewers,
                "approver": approver,
                "copilot_approver": copilot_approver,
                "approved_at": approved_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_approver_type_1 import ReviewApproverType1
        from ..models.review_copilot_approver_type_1 import ReviewCopilotApproverType1
        from ..models.review_reviewers_type_1 import ReviewReviewersType1

        d = dict(src_dict)

        def _parse_compliance_status(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        compliance_status = _parse_compliance_status(d.pop("compliance_status"))

        def _parse_reviewers(data: object) -> Union["ReviewReviewersType1", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reviewers_type_1 = ReviewReviewersType1.from_dict(data)

                return reviewers_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ReviewReviewersType1", None], data)

        reviewers = _parse_reviewers(d.pop("reviewers"))

        def _parse_approver(data: object) -> Union["ReviewApproverType1", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                approver_type_1 = ReviewApproverType1.from_dict(data)

                return approver_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ReviewApproverType1", None], data)

        approver = _parse_approver(d.pop("approver"))

        def _parse_copilot_approver(data: object) -> Union["ReviewCopilotApproverType1", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                copilot_approver_type_1 = ReviewCopilotApproverType1.from_dict(data)

                return copilot_approver_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ReviewCopilotApproverType1", None], data)

        copilot_approver = _parse_copilot_approver(d.pop("copilot_approver"))

        def _parse_approved_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                approved_at_type_0 = isoparse(data)

                return approved_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        approved_at = _parse_approved_at(d.pop("approved_at"))

        review = cls(
            compliance_status=compliance_status,
            reviewers=reviewers,
            approver=approver,
            copilot_approver=copilot_approver,
            approved_at=approved_at,
        )

        review.additional_properties = d
        return review

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
