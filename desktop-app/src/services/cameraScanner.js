const { desktopCapturer } = require('electron');
const Tesseract = require('tesseract.js');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

class CameraScanner {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }

  async captureAndExtract(options = {}) {
    try {
      console.log('📸 Starting document capture...');

      // Get camera sources
      const sources = await desktopCapturer.getSources({ 
        types: ['window', 'screen'],
        thumbnailSize: { width: 1920, height: 1080 }
      });

      // Use the first camera/screen source
      const source = sources[0];
      if (!source) {
        throw new Error('No camera source available');
      }

      // Get the image from the thumbnail
      const image = source.thumbnail.toPNG();

      // Save temporarily
      const tempPath = path.join(os.tmpdir(), `scan-${Date.now()}.png`);
      await fs.writeFile(tempPath, image);

      console.log('🔍 Extracting text from image...');

      // Perform OCR on the image
      const { data: { text } } = await Tesseract.recognize(
        tempPath,
        'eng',
        {
          logger: (m) => {
            if (m.status === 'recognizing text') {
              console.log(`OCR Progress: ${Math.round(m.progress * 100)}%`);
            }
          }
        }
      );

      // Clean up temp file
      await fs.unlink(tempPath).catch(() => {});

      console.log('✅ Text extracted:', text.substring(0, 100) + '...');

      // Parse the extracted text for receipt information
      const receiptData = this.parseReceiptText(text);

      // Upload to backend
      if (receiptData) {
        const result = await this.apiClient.uploadScannedDocument({
          ...receiptData,
          raw_text: text,
          source: 'desktop-camera-scanner'
        });

        console.log(`✅ Uploaded scanned receipt: ${receiptData.vendor || 'Unknown'}`);
        return result;
      }

      return { text, message: 'No receipt information found' };

    } catch (error) {
      console.error('Camera scanner error:', error);
      throw error;
    }
  }

  parseReceiptText(text) {
    const vendors = [
      'netflix', 'spotify', 'adobe', 'microsoft', 'google', 'amazon',
      'dropbox', 'slack', 'zoom', 'github', 'aws', 'azure', 'heroku',
      'digitalocean', 'linode', 'cloudflare', 'twilio', 'sendgrid'
    ];

    // Detect vendor
    const textLower = text.toLowerCase();
    let vendor = null;
    
    for (const v of vendors) {
      if (textLower.includes(v)) {
        vendor = v;
        break;
      }
    }

    // Extract amount using various currency patterns
    const amountPatterns = [
      /\$\s*(\d+(?:\.\d{2})?)/,           // $XX.XX
      /USD\s*(\d+(?:\.\d{2})?)/i,         // USD XX.XX
      /Total[:\s]+\$?\s*(\d+\.\d{2})/i,   // Total: $XX.XX
      /Amount[:\s]+\$?\s*(\d+\.\d{2})/i,  // Amount: $XX.XX
      /Rs\.?\s*(\d+(?:\.\d{2})?)/i,       // Rs. XX.XX
      /INR\s*(\d+(?:\.\d{2})?)/i          // INR XX.XX
    ];

    let amount = null;
    for (const pattern of amountPatterns) {
      const match = text.match(pattern);
      if (match) {
        amount = parseFloat(match[1]);
        break;
      }
    }

    // Extract date
    const datePatterns = [
      /(\d{1,2}\/\d{1,2}\/\d{2,4})/,                    // MM/DD/YYYY
      /(\d{4}-\d{2}-\d{2})/,                            // YYYY-MM-DD
      /(\w+ \d{1,2},? \d{4})/,                          // Month DD, YYYY
      /Date[:\s]+(\d{1,2}\/\d{1,2}\/\d{2,4})/i          // Date: MM/DD/YYYY
    ];

    let date = null;
    for (const pattern of datePatterns) {
      const match = text.match(pattern);
      if (match) {
        date = match[1];
        break;
      }
    }

    if (!vendor && !amount) {
      return null;
    }

    return {
      vendor,
      amount,
      date,
      category: this.inferCategory(vendor)
    };
  }

  inferCategory(vendor) {
    const categories = {
      'netflix': 'Entertainment',
      'spotify': 'Entertainment',
      'adobe': 'Software',
      'microsoft': 'Software',
      'google': 'Cloud Services',
      'amazon': 'Cloud Services',
      'aws': 'Cloud Services',
      'azure': 'Cloud Services',
      'heroku': 'Cloud Services',
      'digitalocean': 'Cloud Services',
      'dropbox': 'Cloud Storage',
      'slack': 'Communication',
      'zoom': 'Communication',
      'github': 'Development',
      'twilio': 'Communication',
      'sendgrid': 'Communication'
    };

    return categories[vendor?.toLowerCase()] || 'Other';
  }

  // Capture specific window for receipt scanning
  async captureWindow(windowTitle) {
    const sources = await desktopCapturer.getSources({ 
      types: ['window'],
      thumbnailSize: { width: 1920, height: 1080 }
    });

    const source = sources.find(s => 
      s.name.toLowerCase().includes(windowTitle.toLowerCase())
    );

    if (!source) {
      throw new Error(`Window "${windowTitle}" not found`);
    }

    return source.thumbnail.toPNG();
  }
}

module.exports = CameraScanner;
