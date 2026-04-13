const { exec } = require('child_process');
const util = require('util');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const execPromise = util.promisify(exec);

class SMSReader {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.isMonitoring = false;
    this.platform = process.platform;
  }

  async startMonitoring() {
    if (this.isMonitoring) return;
    this.isMonitoring = true;

    console.log('📱 Starting SMS monitoring...');

    // Initial scan
    await this.scanForTransactions();

    // Monitor for changes every 10 minutes
    this.monitoringInterval = setInterval(async () => {
      await this.scanForTransactions();
    }, 10 * 60 * 1000);
  }

  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
  }

  async scanForTransactions(options = {}) {
    const transactions = [];

    switch (this.platform) {
      case 'darwin':
        // macOS - Access Messages.app database
        transactions.push(...await this.scanMacMessages());
        break;

      case 'win32':
        // Windows - Use Your Phone app or Android emulator
        transactions.push(...await this.scanWindowsPhone());
        break;

      case 'linux':
        // Linux - Use Android Debug Bridge (ADB)
        transactions.push(...await this.scanAndroidADB());
        break;
    }

    console.log(`📱 Found ${transactions.length} new SMS transactions`);
    return transactions;
  }

  async scanMacMessages() {
    const transactions = [];
    
    try {
      // Messages.app stores SMS in ~/Library/Messages/chat.db
      const dbPath = path.join(
        os.homedir(),
        'Library/Messages/chat.db'
      );

      // Use sqlite3 to query the database
      const query = `
        SELECT 
          message.text,
          message.date,
          handle.id as sender
        FROM message
        JOIN handle ON message.handle_id = handle.ROWID
        WHERE message.text LIKE '%debited%' 
           OR message.text LIKE '%credited%'
           OR message.text LIKE '%paid%'
           OR message.text LIKE '%transaction%'
           OR message.text LIKE '%Rs.%'
           OR message.text LIKE '%$%'
        ORDER BY message.date DESC
        LIMIT 100;
      `;

      const { stdout } = await execPromise(
        `sqlite3 "${dbPath}" "${query.replace(/\n/g, ' ')}"`
      );

      const lines = stdout.trim().split('\n');
      
      for (const line of lines) {
        const parts = line.split('|');
        if (parts.length >= 3) {
          const [text, date, sender] = parts;

          try {
            const result = await this.apiClient.uploadSMSTransaction({
              sender: sender.trim(),
              message: text.trim(),
              timestamp: this.convertMacDate(date),
              source: 'desktop-mac-messages'
            });
            transactions.push(result);
            console.log(`✅ Uploaded SMS from ${sender}`);
          } catch (error) {
            console.error(`❌ Failed to upload SMS:`, error.message);
          }
        }
      }
    } catch (error) {
      console.error('Mac Messages scan error:', error.message);
      console.log('💡 Tip: Grant Full Disk Access to the app in System Preferences > Security & Privacy');
    }

return transactions;
  }

  async scanWindowsPhone() {
    const transactions = [];
    
    try {
      // Windows "Your Phone" app stores data in AppData
      const yourPhonePath = path.join(
        os.homedir(),
        'AppData/Local/Packages/Microsoft.YourPhone_8wekyb3d8bbwe/LocalCache'
      );

      // Check if Your Phone is installed
      const exists = await fs.access(yourPhonePath).then(() => true).catch(() => false);
      
      if (!exists) {
        console.log('💡 Tip: Install "Your Phone" app from Microsoft Store to sync Android SMS');
        return transactions;
      }

      // Your Phone stores messages in a SQLite database
      // Implementation would be similar to Mac Messages approach
      console.log('📱 Windows SMS scanning - requires Your Phone app setup');

    } catch (error) {
      console.error('Windows Phone scan error:', error.message);
    }

    return transactions;
  }

  async scanAndroidADB() {
    const transactions = [];
    
    try {
      // Check if ADB is available
      await execPromise('adb version');

      // Get SMS from Android device via ADB
      const { stdout } = await execPromise(
        'adb shell content query --uri content://sms/inbox --projection address,body,date --where "type=1" --sort "date DESC" --limit 100'
      );

      const lines = stdout.trim().split('\n');
      
      for (const line of lines) {
        // Parse ADB output
        const addressMatch = line.match(/address=([^,]+)/);
        const bodyMatch = line.match(/body=([^,]+)/);
        const dateMatch = line.match(/date=([^,]+)/);

        if (addressMatch && bodyMatch && dateMatch) {
          const text = bodyMatch[1];
          
          // Check if it's a transaction SMS
          if (this.isTransactionSMS(text)) {
            try {
              const result = await this.apiClient.uploadSMSTransaction({
                sender: addressMatch[1],
                message: text,
                timestamp: new Date(parseInt(dateMatch[1])),
                source: 'desktop-android-adb'
              });
              transactions.push(result);
              console.log(`✅ Uploaded SMS from ${addressMatch[1]}`);
            } catch (error) {
              console.error(`❌ Failed to upload SMS:`, error.message);
            }
          }
        }
      }
    } catch (error) {
      console.error('Android ADB scan error:', error.message);
      console.log('💡 Tip: Install Android SDK and enable USB debugging on your Android device');
    }

    return transactions;
  }

  isTransactionSMS(text) {
    const keywords = [
      'debited', 'credited', 'paid', 'transaction', 'purchase',
      'payment', 'balance', 'spent', 'charged', 'subscription'
    ];

    const currencyPatterns = [
      /Rs\.?\s*\d+/i,         // Indian Rupees
      /\$\s*\d+/,             // US Dollars
      /€\s*\d+/,              // Euros
      /£\s*\d+/,              // British Pounds
      /INR\s*\d+/i,           // Indian Rupees (INR)
      /USD\s*\d+/i            // US Dollars (USD)
    ];

    const textLower = text.toLowerCase();
    
    const hasKeyword = keywords.some(kw => textLower.includes(kw));
    const hasCurrency = currencyPatterns.some(pattern => pattern.test(text));

    return hasKeyword && hasCurrency;
  }

  convertMacDate(macDate) {
    // macOS Messages uses Core Data timestamp (seconds since Jan 1, 2001)
    const timestamp = parseInt(macDate);
    const unixTimestamp = timestamp + 978307200; // Add seconds from 1970 to 2001
    return new Date(unixTimestamp * 1000);
  }
}

module.exports = SMSReader;
