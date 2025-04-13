from enum import Enum


class CustomFieldDataType(str, Enum):
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    DECIMAL = "DECIMAL"
    ENUM = "ENUM"
    MONEY = "MONEY"
    OPTION_STRING = "OPTION_STRING"
    STRING = "STRING"
    TIMESTAMP = "TIMESTAMP"

    def __str__(self) -> str:
        return str(self.value)
