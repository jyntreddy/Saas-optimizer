# SaaS Optimizer - Gmail Scanner Extension

Chrome extension for automatically scanning Gmail for subscription receipts using the Gmail API.

## Features

- 📧 **Gmail API Integration**: Direct access to Gmail using official API
- 🔍 **Smart Scanning**: Searches for receipts from 25+ SaaS vendors
- 💰 **Auto-Extraction**: Detects vendor names, amounts, and dates
- 🔒 **Secure OAuth**: Uses Chrome Identity API for Google authentication
- ⚡ **Background Sync**: Optional hourly auto-scan for new receipts
- 📊 **Backend Integration**: Syncs receipts to SaaS Optimizer dashboard

## Requirements

1. **Google Cloud Project** with Gmail API enabled
2. **OAuth 2.0 Client ID** configured for Chrome extension
3. **SaaS Optimizer Backend** running (optional, for data storage)

## Setup

### 1. Google Cloud Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"

   - Search for "Gmail API" and enable it

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Chrome Extension" as application type
   - Get your Chrome extension ID:
     - Go to `chrome://extensions/` with Developer mode enabled
     - Load the extension (unpacked)
     - Copy the Extension ID shown
   - Paste the Extension ID in the OAuth configuration
   - Click "Create"

5. Copy the Client ID (you'll need this for manifest.json)

### 2. Extension Configuration

1. Open `manifest.json` in the `browser-extension` folder
2. Update the `oauth2.client_id` field with your Client ID:
   ```json
   "oauth2": {
     "client_id": "YOUR_CLIENT_ID_HERE.apps.googleusercontent.com",
     "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
   }
   ```

### 3. Install Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `browser-extension` folder
5. The extension icon should appear in your toolbar

### 4. First-Time Setup

1. Click the extension icon
2. Click "📧 Connect Gmail Account"
3. Authorize the extension to read your Gmail (read-only access)
4. (Optional) Login to backend to sync receipts:
   - Enter backend URL (default: `http://localhost:8000`)
   - Enter your account credentials
   - Click "Login to Backend"
5. Enable auto-scan if desired (scans hourly for new receipts)

## Usage

### Manual Scan

1. Click the extension icon
2. Click "🔍 Scan Gmail for Receipts"
3. Extension will search last year of emails for receipts
4. Progress shown in popup
5. Found receipts automatically synced to backend (if connected)

### Auto-Scan

1. In the extension popup, check "Enable auto-scan (hourly)"
2. Extension will automatically scan Gmail every hour
3. New receipts synced to backend automatically
4. Notification shown when scan completes

### View Results

- Check the extension popup for receipt count
- View detailed data in your SaaS Optimizer dashboard
- Last scan time shown in popup

## How It Works

1. **Authentication**: Chrome Identity API provides OAuth token for Gmail
2. **Search**: Gmail API searches for emails matching receipt keywords
3. **Extraction**: Parses email headers and body to find vendor/amount
4. **Sync**: Sends receipt data to backend via REST API
5. **Storage**: Backend stores receipts in PostgreSQL database

## Privacy & Security

- **Read-only access**: Extension only reads Gmail, never modifies or deletes
- **Secure OAuth**: Google handles authentication via Chrome Identity API
- **No server-side tokens**: OAuth tokens stored only in Chrome storage
- **Minimal scope**: Only `gmail.readonly` permission requested
- **No external sharing**: Receipt data only sent to your configured backend
- **Local processing**: Email parsing happens in browser, not on server

## Permissions

- `identity`: Chrome Identity API for Google OAuth
- `storage`: Save backend token and settings locally
- `notifications`: Show scan completion messages
- `alarms`: Schedule hourly auto-scans
- `googleapis.com`: Access Gmail API endpoints

## Development

### File Structure

```
browser-extension/
├── manifest.json       # Extension config with Gmail API permissions
├── popup.html          # Extension popup UI
├── popup.js            # Popup logic and UI controller
├── background.js       # Service worker with Gmail API integration
├── icons/              # Extension icons
└── README.md           # This file
```

### API Functions (background.js)

- `getAuthToken()`: Get OAuth2 token using Chrome Identity API
- `searchGmailReceipts()`: Search Gmail for subscription emails
- `getMessageDetails()`: Fetch full email content
- `parseReceiptData()`: Extract vendor/amount from email
- `sendReceiptsToBackend()`: Sync receipts to backend
- `scanGmailForReceipts()`: Main scan orchestration function

### Testing Locally

1. Make changes to extension files
2. Go to `chrome://extensions/`
3. Click reload button on the SaaS Optimizer extension
4. Test in the popup or check background script logs

### Debug Tips

- Open extension popup, right-click > "Inspect" for popup console
- Go to `chrome://extensions/` > "Service Worker" link for background logs
- Check `chrome://identity-internals/` for auth token status
- Use Gmail API Explorer to test queries: https://developers.google.com/gmail/api/v1/reference

## Troubleshooting

**"OAuth2 not granted or revoked"**
- Check `manifest.json` has correct client_id
- Ensure Gmail API is enabled in Google Cloud Console
- Verify extension ID matches OAuth configuration
- Try removing and re-adding the extension

**"Failed to connect: message: The OAuth client was not found"**
- Client ID in manifest.json doesn't exist
- Double-check you copied the full client ID
- Ensure it ends with `.apps.googleusercontent.com`

**"Backend upload failed"**
- Check backend is running at configured URL
- Verify you're logged in to backend
- Check backend logs for errors
- Network issues may prevent sync (receipts saved locally until sync works)

**"No receipts found"**
- Try different time ranges (extension searches last year by default)
- Receipts must have amount in body to be included
- Check SaaS vendor names match those in SAAS_VENDORS array
- Manual search query can be customized in background.js

## Architecture

```
┌─────────────┐
│   Gmail     │
│     API     │
└──────┬──────┘
       │ OAuth + REST
┌──────▼──────────────────┐
│  Chrome Extension       │
│  ┌──────────────────┐   │
│  │  background.js   │   │  Gmail API Integration
│  │  - Auth          │   │
│  │  - Search        │   │
│  │  - Parse         │   │
│  └────────┬─────────┘   │
│           │              │
│  ┌────────▼─────────┐   │
│  │    popup.js      │   │  User Interface
│  │    popup.html    │   │
│  └──────────────────┘   │
└────────┬────────────────┘
         │ REST API
┌────────▼────────────────┐
│  SaaS Optimizer Backend │  FastAPI + PostgreSQL
│  - Email storage        │
│  - Analytics            │
│  - Recommendations      │
└─────────────────────────┘
```

## Future Enhancements  

- [ ] Filter by date range in UI
- [ ] Custom search queries
- [ ] PDF attachment parsing
- [ ] Multi-account support
- [ ] Export receipts to CSV
- [ ] Advanced filtering in popup
- [ ] Receipt categorization
- [ ] Duplicate detection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See main repository LICENSE file.
