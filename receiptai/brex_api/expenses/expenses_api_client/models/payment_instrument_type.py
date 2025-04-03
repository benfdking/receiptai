from enum import Enum


class PaymentInstrumentType(str, Enum):
    CARD = "CARD"

    def __str__(self) -> str:
        return str(self.value)
