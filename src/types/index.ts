// Configuration Types
export interface EmailConfig {
  provider: 'gmail' | 'imap';
  gmail?: {
    email: string;
    appPassword: string;
  };
  imap?: {
    host: string;
    port: number;
    user: string;
    password: string;
    tls: boolean;
  };
  searchPeriod: number;
}

export interface MerchantConfig {
  enabled: boolean;
  email: string;
  password: string;
  orderHistoryUrl: string;
}

export interface StorageConfig {
  path: string;
  nameFormat: string;
  createMissingDirectories: boolean;
  organizeByMerchant?: boolean;
}

export interface OcrConfig {
  enabled: boolean;
  tesseractPath: string;
}

export interface MatchingConfig {
  amountTolerance: number;
  dateTolerance: number;
}

export interface AppConfig {
  email: EmailConfig;
  merchants: {
    [key: string]: MerchantConfig;
  };
  storage: StorageConfig;
  ocr: OcrConfig;
  matching: MatchingConfig;
}

// Transaction Types
export interface Transaction {
  date: string;
  description: string;
  amount: number;
  merchant: string | null;
  rawData?: Record<string, any>;
}

// Email Types
export interface EmailHeaders {
  [key: string]: string;
}

export interface EmailMessage {
  id: string;
  threadId: string;
  headers: EmailHeaders;
  snippet: string;
  hasAttachments: boolean;
  data: any; // Gmail API message data type
}

// Parser Types
export interface ParserOptions {
  dateColumn?: string;
  descriptionColumn?: string;
  amountColumn?: string;
  merchantColumn?: string;
}

// Web Scraper Types
export interface ScraperConfig {
  email: string;
  password: string;
  [key: string]: any;
}

// Receipt Storage Types
export interface StoredReceipt {
  path: string;
  transaction: Transaction;
  metadata?: {
    source: 'email' | 'web' | 'manual';
    timestamp: string;
    [key: string]: any;
  };
} 