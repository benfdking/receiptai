from enum import Enum


class ExpensePaymentStatus(str, Enum):
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    CANCELED = "CANCELED"
    CASH_ADVANCE = "CASH_ADVANCE"
    CLEARED = "CLEARED"
    CREDITED = "CREDITED"
    DECLINED = "DECLINED"
    NOT_STARTED = "NOT_STARTED"
    PROCESSING = "PROCESSING"
    REFUNDED = "REFUNDED"
    REFUNDING = "REFUNDING"
    SCHEDULED = "SCHEDULED"

    def __str__(self) -> str:
        return str(self.value)
