import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';

// Get the directory name
const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Gmail receipt searcher class
 */
export class GmailReceiptSearcher {
  constructor(config) {
    this.config = config;
    this.oauth2Client = null;
    this.gmail = null;
  }

  /**
   * Authenticate with Gmail API
   */
  async authenticate() {
    // This is a simplified version - for a real app, you'd want to use OAuth2 with proper token management
    // For simplicity, we're using an application-specific password approach
    this.oauth2Client = new google.auth.JWT(
      this.config.email,
      null,
      this.config.appPassword,
      ['https://www.googleapis.com/auth/gmail.readonly']
    );

    await this.oauth2Client.authorize();
    this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
    
    console.log('Authenticated with Gmail');
  }

  /**
   * Search for receipt emails based on transaction data
   * @param {Object} transaction - Transaction object with date, amount, merchant, etc.
   * @param {Object} options - Search options
   * @returns {Promise<Array>} - Array of email objects containing potential receipts
   */
  async searchReceiptEmails(transaction, options = {}) {
    if (!this.gmail) {
      await this.authenticate();
    }

    const { merchant, date, amount } = transaction;
    
    // Calculate date range (default to +/- 3 days from transaction)
    const searchStartDate = options.searchStartDate || new Date(new Date(date).getTime() - 3 * 24 * 60 * 60 * 1000);
    const searchEndDate = options.searchEndDate || new Date(new Date(date).getTime() + 3 * 24 * 60 * 60 * 1000);
    
    // Format dates for Gmail query
    const afterDate = searchStartDate.toISOString().slice(0, 10);
    const beforeDate = searchEndDate.toISOString().slice(0, 10);
    
    // Build Gmail search query
    let query = `after:${afterDate} before:${beforeDate}`;
    
    // Add search terms based on transaction data
    if (merchant) {
      query += ` from:${merchant} OR subject:${merchant}`;
    }
    
    // Keywords to look for that suggest a receipt
    const receiptKeywords = ['receipt', 'order', 'purchase', 'invoice', 'confirmation'];
    query += ` (${receiptKeywords.join(' OR ')})`;
    
    // If we have an amount, look for it in the email
    if (amount) {
      const amountStr = amount.toFixed(2);
      query += ` "${amountStr}"`;
    }
    
    // Search for emails
    console.log(`Searching Gmail with query: ${query}`);
    const response = await this.gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: options.maxResults || 10,
    });
    
    const messages = response.data.messages || [];
    console.log(`Found ${messages.length} potential receipt emails`);
    
    // Fetch full message details
    const receiptEmails = [];
    for (const message of messages) {
      const emailData = await this.gmail.users.messages.get({
        userId: 'me',
        id: message.id,
        format: 'full',
      });
      
      receiptEmails.push({
        id: emailData.data.id,
        threadId: emailData.data.threadId,
        headers: this.extractHeaders(emailData.data),
        snippet: emailData.data.snippet,
        hasAttachments: this.hasAttachments(emailData.data),
        data: emailData.data,
      });
    }
    
    return receiptEmails;
  }

  /**
   * Extract headers from Gmail message data
   * @param {Object} messageData - Gmail message data
   * @returns {Object} - Headers as an object
   */
  extractHeaders(messageData) {
    const headers = {};
    const headersArray = messageData.payload.headers || [];
    
    for (const header of headersArray) {
      headers[header.name.toLowerCase()] = header.value;
    }
    
    return headers;
  }

  /**
   * Check if a message has attachments
   * @param {Object} messageData - Gmail message data
   * @returns {Boolean} - True if the message has attachments
   */
  hasAttachments(messageData) {
    // Recursive function to check for attachments in the message parts
    const checkParts = (parts) => {
      if (!parts) return false;
      
      for (const part of parts) {
        if (part.filename && part.filename.length > 0) {
          return true;
        }
        
        if (part.parts) {
          const hasAttachmentsInSubparts = checkParts(part.parts);
          if (hasAttachmentsInSubparts) return true;
        }
      }
      
      return false;
    };
    
    return checkParts(messageData.payload.parts);
  }

  /**
   * Download attachments from an email
   * @param {Object} email - Email object with attachment data
   * @param {String} outputDir - Directory to save attachments to
   * @returns {Promise<Array>} - Array of saved attachment file paths
   */
  async downloadAttachments(email, outputDir) {
    if (!this.gmail) {
      await this.authenticate();
    }
    
    // Ensure output directory exists
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const messageData = email.data;
    const savedAttachments = [];
    
    // Recursive function to process message parts and find attachments
    const processParts = async (parts, prefix = '') => {
      if (!parts) return;
      
      for (const part of parts) {
        if (part.filename && part.filename.length > 0) {
          // This part is an attachment
          const attachmentId = part.body.attachmentId;
          const attachmentData = await this.gmail.users.messages.attachments.get({
            userId: 'me',
            messageId: messageData.id,
            id: attachmentId,
          });
          
          // Decode attachment data (base64url encoded)
          const data = attachmentData.data.data.replace(/-/g, '+').replace(/_/g, '/');
          const buffer = Buffer.from(data, 'base64');
          
          // Generate a safe filename
          const filename = `${prefix}${part.filename}`;
          const filePath = path.join(outputDir, filename);
          
          // Save attachment to file
          fs.writeFileSync(filePath, buffer);
          savedAttachments.push(filePath);
          
          console.log(`Saved attachment: ${filePath}`);
        }
        
        if (part.parts) {
          await processParts(part.parts, `${prefix}${part.partId}_`);
        }
      }
    };
    
    await processParts(messageData.payload.parts);
    return savedAttachments;
  }
}

export default GmailReceiptSearcher; 