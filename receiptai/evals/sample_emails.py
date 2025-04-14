from datetime import datetime

from transaction import Transaction

sample_transactions = [
    Transaction(
        id='1',
        amount=8.40,
        currency='GBP',
        merchant='slack',
        date=datetime(2025, 4, 14),
    ),
    Transaction(
        id='2',
        amount=89.00,
        currency='USD',
        merchant='Stable',
        date=datetime(2025, 2, 17),
    ),
    Transaction(
        id='3',
        amount=60.00,
        currency='GBP',
        merchant='ICE',
        date=datetime(2025, 1, 25),
    ),
    Transaction(
        id='4',
        amount=21.72,
        currency='GBP',
        merchant='Microsoft',
        date=datetime(2025, 1, 11),
    ),
    Transaction(
        id='5',
        amount=18.00,
        currency='GBP',
        merchant='Anthropic',
        date=datetime(2025, 1, 5),
    ),
]
