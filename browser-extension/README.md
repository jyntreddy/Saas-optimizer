# SaaS Optimizer Browser Extension

Chrome/Edge extension for automatically detecting and capturing subscription receipts from Gmail.

## Features

- 🔍 **One-Click Scanning**: Scan currently open email for receipt data
- ⚡ **Auto-Detection**: Automatically highlights receipt emails in Gmail inbox  
- 💰 **Smart Recognition**: Detects 20+ SaaS vendors and extracts pricing
- 🔒 **Secure**: Uses your existing SaaS Optimizer account

## Installation

### For Chrome/Edge (Development Mode)

1. Open Chrome/Edge and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `browser-extension` folder
5. The extension icon should appear in your toolbar

### For Firefox

1. Go to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select the `manifest.json` file in the `browser-extension` folder

## Setup

1. Click the extension icon in your toolbar
2. Enter your SaaS Optimizer API URL (default: `http://localhost:8000`)
3. Login with your account credentials
4. You're ready to scan!

## Usage

### Scan Single Email

1. Open any email in Gmail
2. Click the extension icon
3. Click "🔍 Scan Current Email"
4. Receipt data is automatically sent to your SaaS Optimizer account

### Auto-Scan Inbox

1. Go to Gmail inbox
2. Click the extension icon  
3. Click "⚡ Auto-Scan Receipts"
4. Extension will scan visible emails with receipt keywords

### Visual Indicators

- Receipt emails in your inbox are highlighted with a green border
- 💰 badge appears next to potential receipts

## How It Works

1. **Detection**: Content script identifies emails with keywords like "receipt", "invoice", "subscription"
2. **Extraction**: Parses email subject, sender, body, and date
3. **Analysis**: Backend AI extracts vendor, amount, currency
4. **Storage**: Receipt is saved to your SaaS Optimizer account

## Privacy

- Extension only accesses Gmail when you explicitly click scan
- No emails are stored in the extension
- All data sent directly to your SaaS Optimizer API
- Login credentials stored locally in browser

## Permissions

- `activeTab`: Access current Gmail tab when scanning
- `storage`: Save API URL and login token
- `mail.google.com`: Inject content script to detect receipts

## Development

### File Structure

```
browser-extension/
├── manifest.json       # Extension config
├── popup.html          # Extension popup UI
├── popup.js            # Popup logic
├── content.js          # Gmail page script
├── content.css         # Styling for Gmail
├── background.js       # Background tasks
└── icons/              # Extension icons
```

### Testing

1. Make changes to files
2. Go to `chrome://extensions/`
3. Click reload icon on the extension
4. Test in Gmail

## Troubleshooting

**"Could not extract email data"**
- Make sure you have an email open (not inbox view)
- Gmail's HTML structure may have changed

**"Login failed"**
- Check API URL is correct
- Ensure backend is running
- Verify credentials

**Nothing happens when clicking scan**
- Check browser console for errors (F12)
- Ensure you're on mail.google.com
- Try refreshing Gmail

## Future Enhancements

- [ ] Support for Outlook web
- [ ] Attachment parsing (PDF receipts)
- [ ] Bulk scanning with progress indicator
- [ ] Offline queue for scans
- [ ] Settings page with customization
