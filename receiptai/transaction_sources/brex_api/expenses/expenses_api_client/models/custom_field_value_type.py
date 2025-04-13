from enum import Enum


class CustomFieldValueType(str, Enum):
    LIST = "LIST"
    SINGLE_VALUE = "SINGLE_VALUE"

    def __str__(self) -> str:
        return str(self.value)
