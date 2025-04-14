from enum import Enum


class LegalEntityStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    REJECTED = "REJECTED"
    UNSUBMITTED = "UNSUBMITTED"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"

    def __str__(self) -> str:
        return str(self.value)
