from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.statement_end_balance import StatementEndBalance
    from ..models.statement_period import StatementPeriod
    from ..models.statement_start_balance import StatementStartBalance


T = TypeVar("T", bound="Statement")


@_attrs_define
class Statement:
    """
    Attributes:
        id (str):
        period (StatementPeriod):
        start_balance (Union[Unset, StatementStartBalance]):
        end_balance (Union[Unset, StatementEndBalance]):
    """

    id: str
    period: "StatementPeriod"
    start_balance: Union[Unset, "StatementStartBalance"] = UNSET
    end_balance: Union[Unset, "StatementEndBalance"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        period = self.period.to_dict()

        start_balance: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.start_balance, Unset):
            start_balance = self.start_balance.to_dict()

        end_balance: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.end_balance, Unset):
            end_balance = self.end_balance.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "period": period,
            }
        )
        if start_balance is not UNSET:
            field_dict["start_balance"] = start_balance
        if end_balance is not UNSET:
            field_dict["end_balance"] = end_balance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.statement_end_balance import StatementEndBalance
        from ..models.statement_period import StatementPeriod
        from ..models.statement_start_balance import StatementStartBalance

        d = dict(src_dict)
        id = d.pop("id")

        period = StatementPeriod.from_dict(d.pop("period"))

        _start_balance = d.pop("start_balance", UNSET)
        start_balance: Union[Unset, StatementStartBalance]
        if isinstance(_start_balance, Unset):
            start_balance = UNSET
        else:
            start_balance = StatementStartBalance.from_dict(_start_balance)

        _end_balance = d.pop("end_balance", UNSET)
        end_balance: Union[Unset, StatementEndBalance]
        if isinstance(_end_balance, Unset):
            end_balance = UNSET
        else:
            end_balance = StatementEndBalance.from_dict(_end_balance)

        statement = cls(
            id=id,
            period=period,
            start_balance=start_balance,
            end_balance=end_balance,
        )

        statement.additional_properties = d
        return statement

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
