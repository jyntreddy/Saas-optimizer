# Desktop App - Device Integration Guide

## 🖥️ Overview

The SaaS Optimizer Desktop App provides native device access with user permissions for:
- 📧 **Email Reading** - Scan local mail clients (Mail.app, Outlook, Thunderbird)
- 📱 **SMS Access** - Read transaction SMS from Messages.app or Android devices
- 📸 **Document Scanning** - OCR receipts using camera/screen capture
- 📅 **Calendar Sync** - Track renewal dates from system calendars
- 🔔 **Notifications** - Desktop alerts for renewals and recommendations

## ✨ Features

### Email Reader
- **macOS**: Accesses Mail.app database
- **Windows**: Reads Outlook PST files
- **Linux**: Parses Thunderbird profiles
- **Auto-detection**: Finds receipts from 20+ SaaS vendors
- **Privacy**: All processing happens locally

### SMS Reader
- **macOS**: Reads Messages.app SQLite database
- **Windows**: Syncs via "Your Phone" app
- **Linux**: Uses Android Debug Bridge (ADB)
- **Smart Filtering**: Detects transaction keywords and currency patterns

### Camera Scanner
- **OCR**: Uses Tesseract.js for text extraction
- **Receipt Parsing**: Extracts vendor, amount, date
- **Window Capture**: Scan specific application windows
- **Multi-format**: PNG, JPEG, PDF support

### Calendar Sync
- **Cross-platform**: Works with macOS Calendar, Windows Calendar, Evolution, Thunderbird
- **Renewal Tracking**: Auto-detects subscription renewal events
- **Reminders**: 3-day advance notifications
- **ICS Support**: Reads .ics files from cloud sync folders

## 🚀 Installation

### Prerequisites

```bash
# Node.js 18+ required
node --version

# Optional: Android SDK for SMS via ADB
adb version
```

### Install Desktop App

```bash
cd desktop-app
npm install
```

### Build Application

```bash
# Development mode
npm run dev

# Build for your platform
npm run build        # Auto-detect platform
npm run build:mac    # macOS (DMG + ZIP)
npm run build:win    # Windows (NSIS + Portable)
npm run build:linux  # Linux (AppImage + DEB)
```

## 🔐 Permissions

The app will request permissions on first run:

### macOS
1. **Full Disk Access**: System Preferences > Security & Privacy > Privacy > Full Disk Access
   - Add "SaaS Optimizer.app"
   - Required for Mail.app and Messages.app access

2. **Camera**: Automatically requested for document scanning

3. **Calendar**: Automatically requested for event access

### Windows
1. **Your Phone**: Install from Microsoft Store for SMS sync
2. **Outlook**: Runs with standard user permissions
3. **Camera**: Windows will prompt for permission

### Linux
1. **ADB Setup**: For Android SMS access
   ```bash
   sudo apt install android-tools-adb
   adb devices  # Authorize your device
   ```

2. **Calendar**: Access Evolution or Thunderbird profiles
   ```bash
   chmod +r ~/.local/share/evolution/calendar/*.ics
   ```

## ⚙️ Configuration

### First Run Setup

1. Launch the desktop app
2. Sign in with your SaaS Optimizer account
3. Configure backend URL (default: `http://localhost:8000`)
4. Grant requested permissions
5. Start automatic scanning

### Settings

Access via **Settings** menu:

```javascript
{
  "backendUrl": "http://localhost:8000",
  "frontendUrl": "http://localhost:8501",
  "autoSyncEmails": true,        // Scan emails every 30 min
  "autoSyncSMS": true,            // Scan SMS every 15 min
  "enableReminders": true,        // Calendar notifications
  "ocrLanguage": "eng",           // Tesseract language
  "emailPaths": [],               // Custom email locations
  "smsDatabasePath": null         // Custom SMS database path
}
```

## 📱 Usage

### Scan Emails

```javascript
// From renderer process
const result = await window.electronAPI.scanEmails({
  days: 30,           // Last 30 days
  vendors: ['netflix', 'spotify', 'adobe']
});

console.log(`Found ${result.data.length} receipts`);
```

### Scan SMS

```javascript
const result = await window.electronAPI.scanSMS({
  days: 90,
  keywords: ['debited', 'subscription']
});
```

### Scan Document

```javascript
// Capture and OCR a receipt
const result = await window.electronAPI.scanDocument({
  language: 'eng'
});

console.log(`Vendor: ${result.data.vendor}, Amount: ${result.data.amount}`);
```

### Get Calendar Events

```javascript
const events = await window.electronAPI.getCalendarEvents({
  startDate: new Date(),
  endDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) // 90 days
});

const renewals = events.data.filter(e => 
  e.summary.includes('renewal') || e.summary.includes('subscription')
);
```

### Send Notification

```javascript
await window.electronAPI.sendNotification({
  title: 'Subscription Renewal',
  body: 'Netflix renews in 3 days - $15.99',
  icon: '/path/to/icon.png'
});
```

## 🔄 Automatic Monitoring

The desktop app runs background services:

- **Email Scanner**: Every 30 minutes
- **SMS Scanner**: Every 15 minutes
- **Calendar Sync**: Every hour
- **Renewal Alerts**: 3 days before due date

### Disable Auto-Sync

```javascript
await window.electronAPI.setSetting('autoSyncEmails', false);
await window.electronAPI.setSetting('autoSyncSMS', false);
```

## 🛠️ Development

### Project Structure

```
desktop-app/
├── package.json              # Dependencies & build config
├── src/
│   ├── main.js               # Electron main process
│   ├── preload.js            # Context bridge (IPC)
│   └── services/
│       ├── apiClient.js      # Backend API communication
│       ├── emailReader.js    # Email scanning service
│       ├── smsReader.js      # SMS parsing service
│       ├── cameraScanner.js  # OCR document scanner
│       └── calendarSync.js   # Calendar integration
└── assets/
    ├── icon.png              # App icon (1024x1024)
    ├── icon.icns             # macOS icon
    └── icon.ico              # Windows icon
```

### IPC Communication

```javascript
// In main.js
ipcMain.handle('scan-emails', async (event, options) => {
  const emailReader = new EmailReader(apiClient);
  return await emailReader.scanForReceipts(options);
});

// In preload.js
contextBridge.exposeInMainWorld('electronAPI', {
  scanEmails: (options) => ipcRenderer.invoke('scan-emails', options)
});

// In renderer
const result = await window.electronAPI.scanEmails({ days: 30 });
```

### Add New Service

1. Create service in `src/services/yourService.js`
2. Add IPC handler in `src/main.js`
3. Expose API in `src/preload.js`
4. Use from renderer process

## 🔒 Privacy & Security

### Data Storage
- **Local First**: All scanning happens on your device
- **Encrypted Storage**: Uses electron-store with encryption
- **Secure Auth**: JWT tokens stored in OS keychain
- **No Cloud Sync**: Email/SMS data never leaves your device (except what you upload)

### Permissions
- **Minimal Access**: Only requests necessary permissions
- **User Control**: Can revoke permissions anytime in OS settings
- **Audit Trail**: All API calls logged locally

### Network
- **HTTPS Only**: Backend communication encrypted
- **Token Refresh**: Automatic JWT renewal
- **Offline Mode**: Core features work without internet

## 🐛 Troubleshooting

### macOS: "Cannot access Mail.app"
```bash
# Grant Full Disk Access
System Preferences > Security & Privacy > Privacy > Full Disk Access
# Add "SaaS Optimizer.app"
```

### Windows: "Your Phone not working"
```powershell
# Install from Microsoft Store
# Link your Android phone via Settings > Phone
```

### Linux: "ADB device not found"
```bash
# Enable USB debugging on Android
# Settings > Developer Options > USB Debugging

# Authorize computer
adb devices
# Click "Allow" on your phone
```

### Email/SMS not detected
```javascript
// Check service status
const settings = await window.electronAPI.getSettings();
console.log('Auto-sync enabled:', settings.autoSyncEmails, settings.autoSyncSMS);

// Manual scan
await window.electronAPI.scanEmails({ days: 365 });
```

## 📊 Supported Platforms

| Platform | Email | SMS | Camera | Calendar |
|----------|-------|-----|--------|----------|
| macOS 10.15+ | ✅ Mail.app | ✅ Messages.app | ✅ Screen Capture | ✅ Calendar.app |
| Windows 10+ | ✅ Outlook | ⚠️ Your Phone | ✅ Camera API | ✅ Windows Calendar |
| Linux (Ubuntu 20.04+) | ✅ Thunderbird | ⚠️ ADB | ✅ V4L2 | ✅ Evolution |

✅ Full Support | ⚠️ Requires Setup

## 🚀 Next Steps

1. **Grant Permissions**: Follow prompts for Mail, SMS, Camera, Calendar
2. **Initial Scan**: Run full scan of emails and SMS
3. **Configure Auto-Sync**: Enable background monitoring
4. **Set Reminders**: Connect calendar for renewal alerts
5. **Test Scanning**: Capture a receipt with camera scanner

## 📚 API Reference

See [API.md](./API.md) for complete IPC API documentation.

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.
