.PHONY: dev inspect lint format generate-api-client

dev:
	@python receiptai/server.py receiptai/gmail_mcp.py

inspect:
	@mcp dev receiptai/gmail_mcp.py

lint:
	ruff check .

format:
	ruff format .

install-dev:
	uv venv
	source .venv/bin/activate
	uv pip install -e .

generate-api-client:
	openapi-python-client generate --path ./receiptai/brex_api/brex-expenses.json --output-path ./receiptai/brex_api/expenses --overwrite
	openapi-python-client generate --path ./receiptai/brex_api/brex-transactions.json --output-path ./receiptai/brex_api/transactions --overwrite
