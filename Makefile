dev:
	@python receiptai/client.py receiptai/gmail_mcp.py

lint:
	ruff check .

format:
	ruff format .

generate-api-client:
	openapi-python-client generate --path ./receiptai/brex_api/brex-expenses.json --output-path ./receiptai/brex_api/expenses --overwrite
	openapi-python-client generate --path ./receiptai/brex_api/brex-transactions.json --output-path ./receiptai/brex_api/transactions --overwrite
