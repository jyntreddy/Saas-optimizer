# Chrome Extension Setup Guide

## What Changed

The Gmail email scanning functionality has been **converted from a desktop app to a Chrome extension** using the Gmail API. This provides:

✅ **Easier Distribution**: Install from Chrome Web Store (or load unpacked for development)  
✅ **Better Security**: Google's OAuth2 via Chrome Identity API (no backend token storage)  
✅ **Automatic Updates**: Chrome handles updates automatically  
✅ **Simpler Deployment**: No Electron installer required  
✅ **Direct API Access**: Uses official Gmail API instead of scraping email clients  

## Architecture

### Before (Desktop App)
```
┌──────────────────────┐
│   Desktop App        │
│   (Electron)         │
│                      │
│  - Mail.app          │
│  - Outlook           │
│  - Thunderbird       │
│                      │
│  Scrapes email files │
└──────────┬───────────┘
           │
           ▼
    Backend Storage
```

### After (Chrome Extension)
```
┌──────────────────┐
│   Gmail API      │
└────────┬─────────┘
         │ OAuth2 + REST
         ▼
┌──────────────────┐
│ Chrome Extension │
│  - background.js │  → Gmail API integration
│  - popup.js      │  → User interface
└────────┬─────────┘
         │ REST API
         ▼
  Backend Storage
```

## What Stays (Desktop App)

The **device monitoring features remain in the desktop app**:
- 📱 App usage tracking (50+ desktop apps)
- 🌐 Browser history scanning (Chrome, Firefox, Edge, Safari)
- ⏱️ Usage duration tracking
- 📊 Analytics and SaaS Score calculation
- 📷 Camera-based receipt scanning
- 📅 Calendar integration

**Email scanning is now handled by the Chrome extension.**

## Setup Steps

### 1. Google Cloud Configuration (Required)

You need a Google Cloud project with Gmail API access:

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable Gmail API:
   - Navigation menu > "APIs & Services" > "Library"
   - Search "Gmail API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: **Chrome Extension**
   - You'll need the Extension ID (see step 2 below)
   - Add the Extension ID to allowed applications
   - Click "Create"
   - **Copy the Client ID** (format: `123456789.apps.googleusercontent.com`)

### 2. Extension Configuration

1. **Load the extension** (first time):
   ```bash
   # Open Chrome
   # Go to: chrome://extensions/
   # Enable "Developer mode" (top right toggle)
   # Click "Load unpacked"
   # Select: /path/to/saas-optimizer/browser-extension/
   ```

2. **Copy Extension ID**:
   - The ID appears under the extension name (e.g., `abcdefghijklmnopqrstuvwxyz123456`)
   - Add this to Google Cloud OAuth configuration (see step 1.4 above)

3. **Update manifest.json**:
   ```bash
   cd browser-extension
   # Edit manifest.json
   ```
   
   Replace the `client_id` in the `oauth2` section:
   ```json
   "oauth2": {
     "client_id": "YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com",
     "scopes": [
       "https://www.googleapis.com/auth/gmail.readonly",
       "https://www.googleapis.com/auth/userinfo.email"
     ]
   }
   ```

4. **Reload extension**:
   - Go back to `chrome://extensions/`
   - Click the reload button on the SaaS Optimizer extension

### 3. First Use

1. **Click the extension icon** in your Chrome toolbar
2. **Connect Gmail**:
   - Click "📧 Connect Gmail Account"
   - Google OAuth consent screen appears
   - Select your Google account
   - Review permissions (read-only Gmail access)
   - Click "Allow"
   - Extension now has access to scan Gmail

3. **Scan for receipts**:
   - Click "🔍 Scan Gmail for Receipts"
   - Extension searches last year of emails
   - Progress shown in popup
   - Receipts displayed when complete

4. **(Optional) Connect to Backend**:
   - Enter backend URL: `http://localhost:8000`
   - Enter your account email/password
   - Click "Login to Backend"
   - Found receipts automatically sync to dashboard
   - Enable "Auto-scan" for hourly background scans

## File Changes Summary

### New Files
- ✅ `browser-extension/background.js` - **480 lines** of Gmail API integration
- ✅ `browser-extension/popup.html` - Updated UI with Gmail auth sections
- ✅ `browser-extension/popup.js` - **370 lines** of UI controller logic
- ✅ `browser-extension/manifest.json` - Gmail API permissions & OAuth config
- ✅ `browser-extension/README.md` - Complete setup documentation

### Removed Files
- ❌ `browser-extension/content.js` - No longer needed (was scraping Gmail UI)
- ❌ `browser-extension/content.css` - No longer needed (no content script)

### Backend Changes (To Do)
Files to remove (Gmail OAuth no longer in backend):
- ⏳ `backend/app/api/v1/endpoints/gmail.py`
- ⏳ `backend/app/models/gmail_token.py`
- ⏳ Update `backend/app/api/v1/api.py` (remove gmail router)
- ⏳ Update `backend/app/models/__init__.py` (remove GmailToken import)

**Note**: Backend Gmail endpoints are deprecated but not yet removed. Extension works independently using Chrome Identity API.

## Testing

### Quick Test
```bash
# 1. Ensure extension loaded with valid client_id
# 2. Click extension icon
# 3. Click "Connect Gmail"
# 4. Authorize Google account
# 5. Click "Scan Gmail"
# 6. Check popup shows receipt count
```

### Debug Tips
- **Popup logs**: Right-click extension icon > "Inspect" > Console
- **Background logs**: chrome://extensions/ > Extension details > "Service Worker" link
- **Auth status**: chrome://identity-internals/
- **Gmail API Explorer**: https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list

### Common Issues

**"OAuth2 not granted or revoked"**
- Check `manifest.json` client_id is correct
- Ensure Gmail API enabled in Google Cloud
- Verify Extension ID matches OAuth configuration
- Try: chrome://identity-internals/ > Remove cached token > Retry

**"The OAuth client was not found"**
- Client ID doesn't exist or is wrong
- Re-check you copied full client ID from Google Cloud
- Must end with `.apps.googleusercontent.com`

**"No receipts found"**
- Extension searches last 1 year by default
- Only includes emails with detectable amounts ($XX.XX)
- Check SAAS_VENDORS list in background.js matches your services
- Try searching a shorter time range

## Features

### Gmail API Integration (background.js)
- 📧 OAuth authentication via Chrome Identity API
- 🔍 Smart search for receipt/invoice/billing emails
- 💰 Extracts vendor, amount, date from email body
- 📊 Supports 25+ SaaS vendors (Netflix, Spotify, Adobe, etc.)
- ⚡ Rate-limited API calls (100ms between requests)
- 🔄 Automatic hourly background sync (optional)
- 📝 Progress notifications during scan

### Popup UI (popup.html/popup.js)
- 🎨 Modern gradient design
- 📊 Statistics dashboard (receipt count, last scan time)
- 🔐 Separate Gmail/Backend authentication
- ⚙️ Settings (backend URL, auto-scan toggle)
- 📈 Real-time progress bar during scanning
- ✅ Success/error messages

## Permissions Explained

- `identity`: Chrome Identity API for Google OAuth
- `storage`: Save backend token, settings, pending receipts (local only)
- `notifications`: Show scan completion alerts
- `alarms`: Schedule hourly auto-scans
- `https://www.googleapis.com/*`: Access Gmail API endpoints
- `https://gmail.googleapis.com/*`: Access Gmail API v1

**Privacy**: Extension only accesses Gmail with explicit user permission. OAuth tokens stored locally in Chrome storage (never sent to backend). Extension has **read-only** access.

## Next Steps

1. ✅ Complete Google Cloud setup (get client_id)
2. ✅ Update manifest.json with your client_id
3. ✅ Load extension in Chrome
4. ✅ test Gmail authentication
5. ✅ Scan for receipts
6. ⏳ Remove deprecated backend Gmail endpoints (optional cleanup)
7. ⏳ Publish to Chrome Web Store (for production)

## Production Deployment

To publish the extension:

1. **Prepare for submission**:
   - Finalize client_id from verified Google Cloud project
   - Create promotional images (128x128, 440x280)
   - Write store description and screenshots
   - Privacy policy URL (required for Gmail API access)

2. **Chrome Web Store**:
   - Go to https://chrome.google.com/webstore/devconsole
   - Pay one-time $5 developer fee
   - Upload extension ZIP
   - Fill out store listing
   - Submit for review (typically 1-3 days)

3. **OAuth Verification** (Required for Gmail API):
   - Google requires OAuth consent screen verification
   - Prepare justification for gmail.readonly scope
   - Submit brand verification documents
   - Can take 1-2 weeks

## Support

For issues or questions:
- Check browser-extension/README.md for detailed docs
- Review background.js comments for API usage
- Check Google Cloud logs for API errors
- Review extension Service Worker logs for debugging

---

**Summary**: Chrome extension is fully functional with your Google Cloud OAuth client ID. Desktop app continues to handle device monitoring. Backend Gmail OAuth endpoints can be safely removed.
