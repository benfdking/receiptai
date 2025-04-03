from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateAsyncFileUploadResponse")


@_attrs_define
class CreateAsyncFileUploadResponse:
    """The pre-signed file upload URI and unique identifier of the request.

    Attributes:
        id (str): The unique identifier for the request.
        uri (str): The pre-signed S3 link that should be used to upload the file.
            The maximum size accepted for this document is 50 MB.
    """

    id: str
    uri: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "uri": uri,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        uri = d.pop("uri")

        create_async_file_upload_response = cls(
            id=id,
            uri=uri,
        )

        create_async_file_upload_response.additional_properties = d
        return create_async_file_upload_response

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
