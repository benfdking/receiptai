from enum import Enum


class CardTransactionType(str, Enum):
    BNPL_FEE = "BNPL_FEE"
    CHARGEBACK = "CHARGEBACK"
    COLLECTION = "COLLECTION"
    PURCHASE = "PURCHASE"
    REFUND = "REFUND"
    REWARDS_CREDIT = "REWARDS_CREDIT"

    def __str__(self) -> str:
        return str(self.value)
