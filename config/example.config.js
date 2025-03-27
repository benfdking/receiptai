// Example configuration file
// Copy this to local.config.js and fill in your details

export default {
  // Email providers
  email: {
    provider: 'gmail', // Options: 'gmail', 'imap'
    gmail: {
      email: process.env.GMAIL_EMAIL,
      appPassword: process.env.GMAIL_APP_PASSWORD, 
    },
    imap: {
      host: process.env.IMAP_HOST,
      port: process.env.IMAP_PORT,
      user: process.env.IMAP_USER,
      password: process.env.IMAP_PASSWORD,
      tls: true,
    },
    // How far back to search for receipts (in days)
    searchPeriod: 30, 
  },
  
  // Merchant websites credentials and settings
  merchants: {
    amazon: {
      enabled: true,
      email: process.env.AMAZON_EMAIL,
      password: process.env.AMAZON_PASSWORD,
      orderHistoryUrl: 'https://www.amazon.com/gp/css/order-history',
    },
    // Add more merchants as needed
  },
  
  // Receipt storage settings
  storage: {
    path: process.env.RECEIPT_STORAGE_PATH || './data/receipts',
    nameFormat: '{date}_{merchant}_{amount}.pdf', // Format for saved receipts
    createMissingDirectories: true,
  },
  
  // OCR settings for image-based receipts
  ocr: {
    enabled: true,
    tesseractPath: process.env.TESSERACT_PATH,
  },
  
  // Transaction matching settings
  matching: {
    // How close the transaction amount needs to be to the receipt amount (percentage)
    amountTolerance: 0.01, // 1%
    // Maximum number of days between transaction date and receipt date
    dateTolerance: 3, 
  },
}; 