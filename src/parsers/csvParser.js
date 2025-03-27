import fs from 'fs';
import csvParser from 'csv-parser';

/**
 * Parses transaction data from a CSV file
 * @param {string} filePath - Path to the CSV file
 * @param {Object} options - Parser options
 * @returns {Promise<Array>} - Array of transaction objects
 */
export const parseTransactionsCsv = (filePath, options = {}) => {
  const results = [];
  
  // Default column mappings (can be overridden through options)
  const columnMappings = {
    date: options.dateColumn || 'date',
    description: options.descriptionColumn || 'description',
    amount: options.amountColumn || 'amount',
    merchant: options.merchantColumn || 'merchant',
  };
  
  return new Promise((resolve, reject) => {
    fs.createReadStream(filePath)
      .on('error', (error) => reject(error))
      .pipe(csvParser())
      .on('data', (data) => {
        // Map CSV columns to our standard transaction format
        const transaction = {
          date: data[columnMappings.date],
          description: data[columnMappings.description],
          amount: parseFloat(data[columnMappings.amount]),
          merchant: data[columnMappings.merchant] || extractMerchant(data[columnMappings.description]),
          rawData: data, // Keep original data for reference
        };
        
        results.push(transaction);
      })
      .on('end', () => {
        resolve(results);
      });
  });
};

/**
 * Attempts to extract merchant name from transaction description
 * @param {string} description - Transaction description
 * @returns {string} - Extracted merchant name or null if not found
 */
export const extractMerchant = (description) => {
  if (!description) return null;
  
  // Common patterns in transaction descriptions
  // This is a simplified version and can be expanded for better matching
  
  // Remove card numbers, dates, reference numbers
  const cleanDesc = description
    .replace(/\d{4}X{4}\d{4}/g, '') // Card numbers
    .replace(/\d{2}\/\d{2}\/\d{2,4}/g, '') // Dates
    .replace(/REF\s*#?\s*\d+/gi, '') // Reference numbers
    .trim();
  
  // Look for merchant names in all caps (common in many bank statements)
  const capsMatch = cleanDesc.match(/([A-Z][A-Z\s&]+[A-Z])/);
  if (capsMatch) return capsMatch[0].trim();
  
  // If no clear pattern, return the first few words
  const words = cleanDesc.split(/\s+/);
  return words.slice(0, 3).join(' ');
};

export default parseTransactionsCsv; 