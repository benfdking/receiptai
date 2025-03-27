import { Command } from 'commander';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

interface CommandOptions {
  input?: string;
  output?: string;
  format?: string;
}

async function main() {
  const program = new Command();

  program
    .name('receiptai')
    .description('CLI tool for processing receipts')

  program
    .command('get-receipt')
    .description('Get a receipt from an email or website')
    .option('-t, --timestamp <timestamp>', 'Timestamp of the transaction')
    .option('-m, --merchant <merchant>', 'Merchant of the transaction')
    .option('-a, --amount <amount>', 'Amount of the transaction')
    .option('-c, --currency <currency>', 'Currency of the transaction')
    .action(async (options: CommandOptions) => {
      try {
        // TODO: Implement receipt processing logic
        console.log('Getting receipt...');
        console.log('Options:', options);
      } catch (error) {
        console.error('Error processing receipt:', error);
        process.exit(1);
      }
    });

  program.parse();
}

// ES module equivalent of if (require.main === module)
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
