from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Receipt")


@_attrs_define
class Receipt:
    """The receipt associated with the expense.

    Attributes:
        id (str): The unique identifier for the receipt.
        download_uris (Union[None, Unset, list[str]]): [Presigned S3
            link](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)(s) to download file(s) of
            the receipt. Link(s) expire in 15 minutes.
    """

    id: str
    download_uris: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        download_uris: Union[None, Unset, list[str]]
        if isinstance(self.download_uris, Unset):
            download_uris = UNSET
        elif isinstance(self.download_uris, list):
            download_uris = self.download_uris

        else:
            download_uris = self.download_uris

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if download_uris is not UNSET:
            field_dict["download_uris"] = download_uris

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_download_uris(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                download_uris_type_0 = cast(list[str], data)

                return download_uris_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        download_uris = _parse_download_uris(d.pop("download_uris", UNSET))

        receipt = cls(
            id=id,
            download_uris=download_uris,
        )

        receipt.additional_properties = d
        return receipt

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
