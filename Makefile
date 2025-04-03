dev:
	@python receiptai/client.py receiptai/main.py

lint:
	ruff check .

format:
	ruff format .

