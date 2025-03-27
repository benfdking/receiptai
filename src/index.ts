import { Command } from 'commander';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

import { parseTransactionsCsv } from './parsers/csvParser';
import { GmailReceiptSearcher } from './email/gmailSearcher';
import { createScraper } from './web/webScraper';
import ReceiptStorage from './storage/receiptStorage';
import { AppConfig, Transaction, StoredReceipt } from './types';

// Load environment variables
dotenv.config();

// Get the directory name
const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Load configuration from file
 * @returns {AppConfig} Application configuration
 */
const loadConfig = (): AppConfig => {
  const configPath = path.join(__dirname, '../config/local.config.js');
  if (!fs.existsSync(configPath)) {
    throw new Error('Configuration file not found. Please copy config/example.config.js to config/local.config.js and update it with your settings.');
  }
  
  return require(configPath).default;
};

/**
 * Process a single transaction
 * @param {Transaction} transaction - Transaction to process
 * @param {AppConfig} config - Application configuration
 * @param {ReceiptStorage} storage - Receipt storage instance
 * @returns {Promise<StoredReceipt | null>} - Stored receipt if found
 */
const processTransaction = async (
  transaction: Transaction,
  config: AppConfig,
  storage: ReceiptStorage
): Promise<StoredReceipt | null> => {
  console.log(`Processing transaction: ${transaction.date} - ${transaction.merchant} - $${transaction.amount}`);
  
  // First, check if we already have this receipt
  const existingReceipt = storage.findReceiptForTransaction(transaction);
  if (existingReceipt) {
    console.log('Found existing receipt');
    return existingReceipt;
  }
  
  // Try to find receipt in email
  if (config.email.provider === 'gmail') {
    const emailSearcher = new GmailReceiptSearcher(config.email.gmail);
    const emails = await emailSearcher.searchReceiptEmails(transaction);
    
    for (const email of emails) {
      if (email.hasAttachments) {
        const tempDir = path.join(__dirname, '../temp');
        const attachments = await emailSearcher.downloadAttachments(email, tempDir);
        
        if (attachments.length > 0) {
          // Store the first attachment as the receipt
          const storedReceipt = await storage.storeReceipt(transaction, attachments[0]);
          storedReceipt.metadata!.source = 'email';
          
          // Clean up temp files
          for (const attachment of attachments) {
            fs.unlinkSync(attachment);
          }
          
          console.log('Found and stored receipt from email');
          return storedReceipt;
        }
      }
    }
  }
  
  // If no receipt found in email, try merchant website
  if (transaction.merchant) {
    const merchantLower = transaction.merchant.toLowerCase();
    const merchantConfig = config.merchants[merchantLower];
    
    if (merchantConfig?.enabled) {
      const scraper = createScraper(merchantLower, merchantConfig);
      const tempDir = path.join(__dirname, '../temp');
      const receiptPath = await scraper.getReceipt(transaction, tempDir);
      
      if (receiptPath) {
        const storedReceipt = await storage.storeReceipt(transaction, receiptPath);
        storedReceipt.metadata!.source = 'web';
        
        // Clean up temp file
        fs.unlinkSync(receiptPath);
        
        console.log('Found and stored receipt from merchant website');
        return storedReceipt;
      }
    }
  }
  
  console.log('No receipt found');
  return null;
};

const main = async () => {
  const program = new Command();
  
  program
    .name('receiptai')
    .description('Automatically fetch receipts for transactions')
    .version('1.0.0')
    .requiredOption('-t, --transactions <path>', 'Path to transactions CSV file')
    .option('-c, --config <path>', 'Path to configuration file')
    .parse(process.argv);
  
  const options = program.opts();
  
  try {
    // Load configuration
    const config = loadConfig();
    
    // Initialize receipt storage
    const storage = new ReceiptStorage(config.storage);
    
    // Parse transactions
    const transactions = await parseTransactionsCsv(options.transactions);
    console.log(`Found ${transactions.length} transactions to process`);
    
    // Process each transaction
    const results = [];
    for (const transaction of transactions) {
      const result = await processTransaction(transaction, config, storage);
      results.push({
        transaction,
        receipt: result,
      });
    }
    
    // Print summary
    console.log('\nProcessing complete!');
    console.log(`Total transactions: ${results.length}`);
    console.log(`Receipts found: ${results.filter(r => r.receipt).length}`);
    console.log(`Receipts missing: ${results.filter(r => !r.receipt).length}`);
    
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
};

main(); 