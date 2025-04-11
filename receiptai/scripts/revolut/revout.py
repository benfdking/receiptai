#! /usr/bin/env python3

import asyncio
import csv
from datetime import datetime
from pathlib import Path
from typing import List
from transaction import Transaction

async def read_revolut_transactions(csv_path: Path) -> List[Transaction]:
    transactions = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Type'] == 'CARD_PAYMENT':
                # Convert amount to float, removing any commas
                amount = float(row['Amount'].replace(',', ''))
                # Parse the date
                date = datetime.strptime(row['Started Date'], '%Y-%m-%d %H:%M:%S')
                # Create transaction ID from date and amount
                transaction_id = f"{date.strftime('%Y%m%d%H%M%S')}_{abs(amount)}"
                
                transaction = Transaction(
                    id=transaction_id,
                    amount=amount,
                    currency=row['Currency'],
                    date=date,
                    merchant=row['Description']
                )
                transactions.append(transaction)
    return transactions

async def main():
    csv_path = Path('receiptai/scripts/revolut/account-statement_2024-10-30_2025-04-11_en-gb_2bedb4.csv')
    transactions = await read_revolut_transactions(csv_path)
    
    # Print the transactions
    for transaction in transactions:
        print(f"Transaction: {transaction.merchant} - {transaction.amount} {transaction.currency} on {transaction.date}")

if __name__ == "__main__":
    asyncio.run(main())
