const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const { simpleParser } = require('mailparser');

class EmailReader {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.emailPaths = this.getEmailPaths();
    this.isMonitoring = false;
  }

  getEmailPaths() {
    const platform = process.platform;
    const homedir = os.homedir();
    const paths = [];

    // macOS Mail.app
    if (platform === 'darwin') {
      paths.push(path.join(homedir, 'Library/Mail/V10'));
      paths.push(path.join(homedir, 'Library/Mail/V9'));
      paths.push(path.join(homedir, 'Library/Mail/V8'));
    }

    // Windows Outlook
    if (platform === 'win32') {
      paths.push(path.join(homedir, 'AppData/Local/Microsoft/Outlook'));
      paths.push(path.join(homedir, 'Documents/Outlook Files'));
    }

    // Thunderbird (cross-platform)
    if (platform === 'darwin') {
      paths.push(path.join(homedir, 'Library/Thunderbird/Profiles'));
    } else if (platform === 'win32') {
      paths.push(path.join(homedir, 'AppData/Roaming/Thunderbird/Profiles'));
    } else {
      paths.push(path.join(homedir, '.thunderbird'));
    }

    return paths;
  }

  async startMonitoring() {
    if (this.isMonitoring) return;
    this.isMonitoring = true;

    console.log('📧 Starting email monitoring...');

    // Initial scan
    await this.scanForReceipts();

    // Monitor for changes every 5 minutes
    this.monitoringInterval = setInterval(async () => {
      await this.scanForReceipts();
    }, 5 * 60 * 1000);
  }

  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
  }

  async scanForReceipts(options = {}) {
    const receipts = [];
    const keywords = [
      'receipt', 'invoice', 'payment', 'subscription', 'renewal',
      'billing', 'charged', 'purchase', 'order confirmation'
    ];

    const vendors = [
      'netflix', 'spotify', 'adobe', 'microsoft', 'google', 'amazon',
      'dropbox', 'slack', 'zoom', 'github', 'aws', 'azure', 'heroku'
    ];

    for (const emailPath of this.emailPaths) {
      try {
        const exists = await fs.access(emailPath).then(() => true).catch(() => false);
        if (!exists) continue;

        const files = await this.findEmailFiles(emailPath);
        
        for (const file of files) {
          try {
            const content = await fs.readFile(file, 'utf-8');
            const parsed = await simpleParser(content);

            // Check if email is a receipt
            const subject = (parsed.subject || '').toLowerCase();
            const body = (parsed.text || '').toLowerCase();
            const from = (parsed.from?.text || '').toLowerCase();

            const isReceipt = keywords.some(kw => 
              subject.includes(kw) || body.includes(kw)
            );

            const isFromVendor = vendors.some(vendor => 
              from.includes(vendor) || subject.includes(vendor)
            );

            if (isReceipt || isFromVendor) {
              const receiptData = {
                subject: parsed.subject,
                from: parsed.from?.text,
                to: parsed.to?.text,
                date: parsed.date,
                body: parsed.text,
                html: parsed.html,
                source: 'desktop-email-reader'
              };

              // Upload to backend
              try {
                const result = await this.apiClient.uploadEmailReceipt(receiptData);
                receipts.push(result);
                console.log(`✅ Uploaded receipt: ${parsed.subject}`);
              } catch (error) {
                console.error(`❌ Failed to upload: ${parsed.subject}`, error.message);
              }
            }
          } catch (error) {
            // Skip corrupted email files
            continue;
          }
        }
      } catch (error) {
        console.error(`Error scanning ${emailPath}:`, error.message);
      }
    }

    console.log(`📧 Found ${receipts.length} new receipts`);
    return receipts;
  }

  async findEmailFiles(basePath, extensions = ['.eml', '.emlx', '.msg']) {
    const files = [];

    async function walk(dir, depth = 0) {
      if (depth > 5) return; // Limit recursion depth

      try {
        const items = await fs.readdir(dir, { withFileTypes: true });

        for (const item of items) {
          const fullPath = path.join(dir, item.name);

          if (item.isDirectory()) {
            await walk(fullPath, depth + 1);
          } else if (item.isFile()) {
            const ext = path.extname(item.name).toLowerCase();
            if (extensions.includes(ext)) {
              files.push(fullPath);
            }
          }
        }
      } catch (error) {
        // Skip inaccessible directories
      }
    }

    await walk(basePath);
    return files;
  }
}

module.exports = EmailReader;
