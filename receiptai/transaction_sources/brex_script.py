#! /usr/bin/env python3

import asyncio
import os

from brex_api.expenses.expenses_api_client.api.expenses.list_expenses import asyncio_detailed
from brex_api.expenses.expenses_api_client.client import AuthenticatedClient
from brex_script_pydantic_models import Model
from dotenv import load_dotenv
from transaction import Transaction

load_dotenv()

brex_token = os.getenv('BREX_API_KEY')


async def main():
    client = AuthenticatedClient(
        base_url='https://platform.brexapis.com',
        token=brex_token,
    )
    response = await asyncio_detailed(
        client=client,
        expand=[
            'merchant',
            'location',
            'receipts',
        ],
    )
    # Read the response content as a string
    response = Model.model_validate_json(response.content)

    transactions = [
        Transaction(
            id=expense.id,
            amount=expense.original_amount.amount,
            currency=expense.original_amount.currency,
            date=expense.purchased_at,
            merchant=expense.merchant.raw_descriptor,
        )
        for expense in response.items
        if expense.receipts is None
    ]
    print(transactions)


if __name__ == '__main__':
    asyncio.run(main())
