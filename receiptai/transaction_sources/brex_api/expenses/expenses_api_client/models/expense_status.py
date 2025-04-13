from enum import Enum


class ExpenseStatus(str, Enum):
    APPROVED = "APPROVED"
    CANCELED = "CANCELED"
    DRAFT = "DRAFT"
    OUT_OF_POLICY = "OUT_OF_POLICY"
    SETTLED = "SETTLED"
    SPLIT = "SPLIT"
    SUBMITTED = "SUBMITTED"
    VOID = "VOID"

    def __str__(self) -> str:
        return str(self.value)
