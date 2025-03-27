# ReceiptAI

A tool to automatically fetch receipts for your transactions by:
1. Scanning your emails for receipt attachments or embedded receipts
2. If not found in emails, attempting to retrieve receipts from merchant websites

## Features

- Parse transaction data from various formats (CSV, PDF, etc.)
- Search through emails for receipts matching transaction data
- Authenticate with and navigate merchant websites to retrieve receipts
- Store and organize receipts for easy access
- OCR capabilities for extracting information from image-based receipts

## Project Structure

```
receiptai/
├── src/                        # Source code
│   ├── parsers/                # Transaction data parsers
│   ├── email/                  # Email processing modules
│   ├── web/                    # Web scraping for merchant sites
│   ├── storage/                # Receipt storage and organization
│   └── ocr/                    # OCR for image processing
├── config/                     # Configuration files
├── data/                       # Sample data and cached information
└── tests/                      # Test suite
```

## Setup and Installation

```bash
# Install dependencies
npm install

# Set up configuration
cp config/example.config.js config/local.config.js
# Edit local.config.js with your credentials
```

## Usage

```bash
# Process transactions from a CSV file
node src/index.js --transactions=data/transactions.csv
```

## Security Note

This application requires access to your email and potentially merchant account credentials. All credentials are stored locally and are never transmitted to third-party servers. Use at your own risk and consider using app-specific passwords when possible. 