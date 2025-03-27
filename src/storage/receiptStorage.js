import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name
const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Class for managing receipt storage and organization
 */
export class ReceiptStorage {
  constructor(config) {
    this.config = config;
    this.storagePath = config.path || path.join(__dirname, '../../data/receipts');
    this.ensureStorageDirectory();
  }

  /**
   * Ensure the receipt storage directory exists
   */
  ensureStorageDirectory() {
    if (!fs.existsSync(this.storagePath)) {
      fs.mkdirSync(this.storagePath, { recursive: true });
      console.log(`Created receipt storage directory: ${this.storagePath}`);
    }
  }

  /**
   * Generate a filename for a receipt based on transaction data
   * @param {Object} transaction - Transaction data
   * @param {String} extension - File extension (defaults to .pdf)
   * @returns {String} - Filename for the receipt
   */
  generateFilename(transaction, extension = '.pdf') {
    const { date, merchant, amount } = transaction;
    
    // Format date as YYYY-MM-DD
    const dateStr = new Date(date).toISOString().slice(0, 10);
    
    // Sanitize merchant name for use in filename
    const merchantStr = merchant
      ? merchant.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 30)
      : 'unknown';
    
    // Format amount with 2 decimal places
    const amountStr = amount 
      ? Math.abs(amount).toFixed(2).replace('.', '_')
      : 'unknown';
    
    return `${dateStr}_${merchantStr}_${amountStr}${extension}`;
  }

  /**
   * Store a receipt file for a transaction
   * @param {Object} transaction - Transaction data
   * @param {String} receiptPath - Path to the receipt file
   * @returns {Promise<String>} - Path to the stored receipt
   */
  async storeReceipt(transaction, receiptPath) {
    if (!fs.existsSync(receiptPath)) {
      throw new Error(`Receipt file not found: ${receiptPath}`);
    }
    
    // Generate destination filename
    const extension = path.extname(receiptPath);
    const filename = this.generateFilename(transaction, extension);
    const destinationPath = path.join(this.storagePath, filename);
    
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
    
    // Update the transaction record with the receipt path
    return destinationPath;
  }

  /**
   * Find an existing receipt for a transaction
   * @param {Object} transaction - Transaction to find receipt for
   * @returns {String|null} - Path to receipt if found, null otherwise
   */
  findReceiptForTransaction(transaction) {
    // Generate possible filenames for the receipt
    const possibleNames = [];
    
    // Standard filename
    possibleNames.push(this.generateFilename(transaction, '.pdf'));
    possibleNames.push(this.generateFilename(transaction, '.jpg'));
    possibleNames.push(this.generateFilename(transaction, '.png'));
    
    // Check if any of the possible filenames exist
    for (const filename of possibleNames) {
      const fullPath = path.join(this.storagePath, filename);
      if (fs.existsSync(fullPath)) {
        console.log(`Found existing receipt: ${fullPath}`);
        return fullPath;
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
          return merchantPath;
        }
      }
    }
    
    return null;
  }

  /**
   * List all stored receipts
   * @returns {Array<String>} - Array of paths to all stored receipts
   */
  listAllReceipts() {
    const results = [];
    
    // Function to recursively scan directories
    const scanDir = (dirPath) => {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        
        if (entry.isDirectory()) {
          scanDir(fullPath);
        } else if (entry.isFile()) {
          // Check for common receipt file extensions
          const ext = path.extname(entry.name).toLowerCase();
          if (['.pdf', '.jpg', '.jpeg', '.png'].includes(ext)) {
            results.push(fullPath);
          }
        }
      }
    };
    
    scanDir(this.storagePath);
    return results;
  }

  /**
   * Delete a receipt
   * @param {String} receiptPath - Path to the receipt to delete
   * @returns {Boolean} - True if deletion was successful
   */
  deleteReceipt(receiptPath) {
    try {
      fs.unlinkSync(receiptPath);
      console.log(`Deleted receipt: ${receiptPath}`);
      return true;
    } catch (error) {
      console.error(`Error deleting receipt: ${error.message}`);
      return false;
    }
  }
}

export default ReceiptStorage; 