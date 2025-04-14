.PHONY: dev inspect test lint format generate-api-client

ci: lint test

dev:
	@python receiptai/server.py receiptai/receipt_sources/email/gmail/gmail_mcp.py receiptai/receipt_sources/email/outlook/outlook_mcp.py

inspect-gmail:
	@mcp dev receiptai/receipt_sources/email/gmail/gmail_mcp.py

inspect-outlook:
	@mcp dev receiptai/receipt_sources/email/outlook/outlook_mcp.py

test:
	@pytest -v

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

install-dev:
	uv venv
	source .venv/bin/activate
	uv pip install -e .

brex-script:
	./receiptai/brex_script.py

generate-api-client:
	openapi-python-client generate --path ./receiptai/brex_api/brex-expenses.json --output-path ./receiptai/brex_api/expenses --overwrite
	openapi-python-client generate --path ./receiptai/brex_api/brex-transactions.json --output-path ./receiptai/brex_api/transactions --overwrite
