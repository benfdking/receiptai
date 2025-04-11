from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

class Transaction(BaseModel):
    id: str
    amount: float
    currency: str
    date: datetime
    description: str

class TransactionWithDocument(BaseModel):
    transaction: Transaction
    document: Path



