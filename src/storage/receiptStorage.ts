import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { StorageConfig, Transaction, StoredReceipt } from '../types';

// Get the directory name
const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Class for managing receipt storage and organization
 */
export class ReceiptStorage {
  private config: StorageConfig;
  private storagePath: string;

  constructor(config: StorageConfig) {
    this.config = config;
    this.storagePath = config.path || path.join(__dirname, '../../data/receipts');
    this.ensureStorageDirectory();
  }

  /**
   * Ensure the receipt storage directory exists
   */
  private ensureStorageDirectory(): void {
    if (!fs.existsSync(this.storagePath)) {
      fs.mkdirSync(this.storagePath, { recursive: true });
      console.log(`Created receipt storage directory: ${this.storagePath}`);
    }
  }

  /**
   * Generate a filename for a receipt based on transaction data
   * @param {Transaction} transaction - Transaction data
   * @param {string} extension - File extension (defaults to .pdf)
   * @returns {string} - Filename for the receipt
   */
  private generateFilename(transaction: Transaction, extension = '.pdf'): string {
    const { date, merchant, amount } = transaction;
    
    // Format date as YYYY-MM-DD
    const dateStr = new Date(date).toISOString().slice(0, 10);
    
    // Sanitize merchant name for use in filename
    const merchantStr = merchant
      ? merchant.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 30)
      : 'unknown';
    
    // Format amount with 2 decimal places
    const amountStr = amount !== undefined
      ? Math.abs(amount).toFixed(2).replace('.', '_')
      : 'unknown';
    
    return `${dateStr}_${merchantStr}_${amountStr}${extension}`;
  }

  /**
   * Store a receipt file for a transaction
   * @param {Transaction} transaction - Transaction data
   * @param {string} receiptPath - Path to the receipt file
   * @returns {Promise<StoredReceipt>} - Stored receipt information
   */
  async storeReceipt(transaction: Transaction, receiptPath: string): Promise<StoredReceipt> {
    if (!fs.existsSync(receiptPath)) {
      throw new Error(`Receipt file not found: ${receiptPath}`);
    }
    
    // Generate destination filename
    const extension = path.extname(receiptPath);
    const filename = this.generateFilename(transaction, extension);
    let destinationPath = path.join(this.storagePath, filename);
    
    // If we want to organize by merchant, create subdirectories
    if (this.config.organizeByMerchant && transaction.merchant) {
      const merchantDir = path.join(
        this.storagePath, 
        transaction.merchant.toLowerCase().replace(/[^a-z0-9]/g, '_')
      );
      
      if (!fs.existsSync(merchantDir)) {
        fs.mkdirSync(merchantDir, { recursive: true });
      }
      
      destinationPath = path.join(merchantDir, filename);
    }
    
    // Copy the file to the storage location
    fs.copyFileSync(receiptPath, destinationPath);
    console.log(`Stored receipt for transaction at: ${destinationPath}`);
    
    // Create and return the stored receipt information
    const storedReceipt: StoredReceipt = {
      path: destinationPath,
      transaction,
      metadata: {
        source: 'manual', // This can be updated by the caller
        timestamp: new Date().toISOString(),
      },
    };
    
    return storedReceipt;
  }

  /**
   * Find an existing receipt for a transaction
   * @param {Transaction} transaction - Transaction to find receipt for
   * @returns {StoredReceipt | null} - Stored receipt if found, null otherwise
   */
  findReceiptForTransaction(transaction: Transaction): StoredReceipt | null {
    // Generate possible filenames for the receipt
    const possibleNames = [
      this.generateFilename(transaction, '.pdf'),
      this.generateFilename(transaction, '.jpg'),
      this.generateFilename(transaction, '.png'),
    ];
    
    // Check if any of the possible filenames exist
    for (const filename of possibleNames) {
      const fullPath = path.join(this.storagePath, filename);
      if (fs.existsSync(fullPath)) {
        console.log(`Found existing receipt: ${fullPath}`);
        return {
          path: fullPath,
          transaction,
          metadata: {
            source: 'manual',
            timestamp: fs.statSync(fullPath).mtime.toISOString(),
          },
        };
      }
      
      // If organizing by merchant, check in merchant directory too
      if (this.config.organizeByMerchant && transaction.merchant) {
        const merchantDir = path.join(
          this.storagePath, 
          transaction.merchant.toLowerCase().replace(/[^a-z0-9]/g, '_')
        );
        
        const merchantPath = path.join(merchantDir, filename);
        if (fs.existsSync(merchantPath)) {
          console.log(`Found existing receipt in merchant directory: ${merchantPath}`);
          return {
            path: merchantPath,
            transaction,
            metadata: {
              source: 'manual',
              timestamp: fs.statSync(merchantPath).mtime.toISOString(),
            },
          };
        }
      }
    }
    
    return null;
  }

  /**
   * List all stored receipts
   * @returns {StoredReceipt[]} - Array of stored receipt information
   */
  listAllReceipts(): StoredReceipt[] {
    const results: StoredReceipt[] = [];
    
    // Function to recursively scan directories
    const scanDir = (dirPath: string): void => {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        
        if (entry.isDirectory()) {
          scanDir(fullPath);
        } else if (entry.isFile()) {
          // Check for common receipt file extensions
          const ext = path.extname(entry.name).toLowerCase();
          if (['.pdf', '.jpg', '.jpeg', '.png'].includes(ext)) {
            // Try to parse transaction info from filename
            const filename = path.basename(entry.name, ext);
            const [dateStr, merchantStr, amountStr] = filename.split('_');
            
            const transaction: Transaction = {
              date: dateStr,
              merchant: merchantStr || null,
              amount: amountStr ? parseFloat(amountStr.replace('_', '.')) : 0,
              description: '',
            };
            
            results.push({
              path: fullPath,
              transaction,
              metadata: {
                source: 'manual',
                timestamp: fs.statSync(fullPath).mtime.toISOString(),
              },
            });
          }
        }
      }
    };
    
    scanDir(this.storagePath);
    return results;
  }

  /**
   * Delete a receipt
   * @param {string} receiptPath - Path to the receipt to delete
   * @returns {boolean} - True if deletion was successful
   */
  deleteReceipt(receiptPath: string): boolean {
    try {
      fs.unlinkSync(receiptPath);
      console.log(`Deleted receipt: ${receiptPath}`);
      return true;
    } catch (error) {
      console.error(`Error deleting receipt: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return false;
    }
  }
}

export default ReceiptStorage; 