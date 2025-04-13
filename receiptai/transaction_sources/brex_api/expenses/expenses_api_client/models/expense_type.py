from enum import Enum


class ExpenseType(str, Enum):
    BILLPAY = "BILLPAY"
    CARD = "CARD"
    CLAWBACK = "CLAWBACK"
    REIMBURSEMENT = "REIMBURSEMENT"
    UNSET = "UNSET"

    def __str__(self) -> str:
        return str(self.value)
