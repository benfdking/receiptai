import playwright, { Browser, BrowserContext, Page } from 'playwright';
import fs from 'fs';
import path from 'path';
import { ScraperConfig, Transaction } from '../types';

/**
 * Base WebScraper class for retrieving receipts from merchant websites
 */
export abstract class WebScraper {
  protected config: ScraperConfig;
  protected browser: Browser | null;
  protected context: BrowserContext | null;

  constructor(config: ScraperConfig) {
    this.config = config;
    this.browser = null;
    this.context = null;
  }

  /**
   * Initialize the browser instance
   */
  protected async initialize(): Promise<Page> {
    this.browser = await playwright.chromium.launch({
      headless: true, // Set to false for debugging
    });
    this.context = await this.browser.newContext();
    
    // Add event listeners for console messages during debugging
    const page = await this.context.newPage();
    page.on('console', msg => console.log(`[Browser Console] ${msg.text()}`));
    
    return page;
  }

  /**
   * Close the browser instance
   */
  protected async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.context = null;
    }
  }

  /**
   * Abstract method to be implemented by specific merchant scrapers
   */
  abstract getReceipt(transaction: Transaction, outputDir: string): Promise<string | null>;
}

/**
 * Amazon-specific receipt scraper
 */
export class AmazonReceiptScraper extends WebScraper {
  constructor(config: ScraperConfig) {
    super(config);
  }

  /**
   * Log in to Amazon
   * @param {Page} page - Playwright page object
   */
  private async login(page: Page): Promise<void> {
    console.log('Logging into Amazon...');
    
    await page.goto('https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0');
    
    // Fill in email and continue
    await page.fill('#ap_email', this.config.email);
    await page.click('#continue');
    
    // Fill in password and sign in
    await page.fill('#ap_password', this.config.password);
    await page.click('#signInSubmit');
    
    // Wait for navigation and check for success
    await page.waitForNavigation();
    
    // Check if we're logged in by looking for account elements
    const isLoggedIn = await page.isVisible('css=a[href*="nav_youraccount_btn"]');
    if (!isLoggedIn) {
      throw new Error('Failed to log in to Amazon. Check credentials or possible CAPTCHA.');
    }
    
    console.log('Successfully logged into Amazon');
  }

  /**
   * Navigate to order history and find the order matching the transaction
   * @param {Page} page - Playwright page object
   * @param {Transaction} transaction - Transaction to find receipt for
   * @returns {Promise<string | null>} - Order ID if found, null otherwise
   */
  private async findOrder(page: Page, transaction: Transaction): Promise<string | null> {
    console.log('Searching for order matching transaction...');
    
    // Navigate to order history
    await page.goto('https://www.amazon.com/gp/css/order-history');
    
    // Calculate date range for search (default to +/- 3 days from transaction)
    const txnDate = new Date(transaction.date);
    const startDate = new Date(txnDate);
    startDate.setDate(startDate.getDate() - 3);
    const endDate = new Date(txnDate);
    endDate.setDate(endDate.getDate() + 3);
    
    // Format dates for Amazon's filter (MM/DD/YYYY)
    const startDateStr = `${startDate.getMonth() + 1}/${startDate.getDate()}/${startDate.getFullYear()}`;
    const endDateStr = `${endDate.getMonth() + 1}/${endDate.getDate()}/${endDate.getFullYear()}`;
    
    // Apply time filter
    await page.click('#time-filter');
    await page.click('text=Custom');
    
    // Enter start and end dates
    await page.fill('#start-date', startDateStr);
    await page.fill('#end-date', endDateStr);
    await page.click('button:has-text("Apply")');
    
    // Wait for results to load
    await page.waitForSelector('.order-card');
    
    // Extract all order IDs and totals from the page
    const orders = await page.$$eval('.order-card', (cards) => {
      return cards.map(card => {
        const orderIdElem = card.querySelector('.order-info a');
        const orderId = orderIdElem ? orderIdElem.textContent?.trim().replace('Order # ', '') : null;
        
        const totalElem = card.querySelector('.a-color-price');
        // Extract just the numeric value from the price (remove currency symbol)
        const total = totalElem ? parseFloat(totalElem.textContent!.trim().replace(/[^0-9.]/g, '')) : null;
        
        return { orderId, total };
      });
    });
    
    // Find the order with a matching total (within a small tolerance)
    const txnAmount = Math.abs(transaction.amount);
    const tolerance = txnAmount * 0.01; // 1% tolerance
    
    for (const order of orders) {
      if (order.orderId && order.total && Math.abs(order.total - txnAmount) <= tolerance) {
        console.log(`Found matching order: ${order.orderId}`);
        return order.orderId;
      }
    }
    
    console.log('No matching order found');
    return null;
  }

  /**
   * Download the receipt for an order
   * @param {Page} page - Playwright page object
   * @param {string} orderId - Amazon order ID
   * @param {string} outputPath - Path to save the receipt to
   * @returns {Promise<string | null>} - Path to the saved receipt file, or null if failed
   */
  private async downloadReceipt(page: Page, orderId: string, outputPath: string): Promise<string | null> {
    console.log(`Downloading receipt for order ${orderId}...`);
    
    // Navigate to the order details page
    await page.goto(`https://www.amazon.com/gp/css/summary/print.html/ref=ppx_yo_dt_b_invoice_o00?ie=UTF8&orderID=${orderId}`);
    
    // Wait for the receipt page to load
    await page.waitForSelector('.a-container');
    
    // Create the output directory if it doesn't exist
    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // PDF is the most reliable format for saving receipts
    await page.pdf({ path: outputPath });
    
    console.log(`Receipt saved to ${outputPath}`);
    return outputPath;
  }

  /**
   * Find and download a receipt for a transaction
   * @param {Transaction} transaction - Transaction to find receipt for
   * @param {string} outputDir - Directory to save receipts to
   * @returns {Promise<string | null>} - Path to the receipt file, or null if not found
   */
  async getReceipt(transaction: Transaction, outputDir: string): Promise<string | null> {
    let page: Page | null = null;
    try {
      page = await this.initialize();
      await this.login(page);
      
      const orderId = await this.findOrder(page, transaction);
      if (!orderId) {
        return null;
      }
      
      const outputPath = path.join(outputDir, `amazon_${orderId}_${transaction.date}.pdf`);
      return await this.downloadReceipt(page, orderId, outputPath);
    } catch (error) {
      console.error('Error retrieving Amazon receipt:', error);
      return null;
    } finally {
      await this.close();
    }
  }
}

// Factory function to create a scraper for a specific merchant
export const createScraper = (merchant: string, config: ScraperConfig): WebScraper => {
  const scrapers: { [key: string]: new (config: ScraperConfig) => WebScraper } = {
    amazon: AmazonReceiptScraper,
    // Add more merchants as needed
  };
  
  const ScraperClass = scrapers[merchant.toLowerCase()];
  if (!ScraperClass) {
    throw new Error(`Unsupported merchant: ${merchant}`);
  }
  
  return new ScraperClass(config);
};

export default { WebScraper, AmazonReceiptScraper, createScraper }; 