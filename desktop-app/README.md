# Desktop App - Device Integration Guide

## 🖥️ Overview

The SaaS Optimizer Desktop App provides comprehensive device monitoring with user permissions for:
- 📧 **Email Reading** - Scan local mail clients (Mail.app, Outlook, Thunderbird)
- 📱 **App Usage Tracking** - Monitor which SaaS applications you actually use
- 🌐 **Browser Activity** - Track web-based SaaS usage from browser history
- 📊 **Usage Analytics** - Comprehensive dashboard with cost optimization insights
- 📸 **Document Scanning** - OCR receipts using camera/screen capture
- 📅 **Calendar Sync** - Track renewal dates from system calendars
- 🔔 **Notifications** - Desktop alerts for renewals and recommendations
- 💡 **Smart Recommendations** - AI-powered cost savings based on actual usage

## ✨ Features

### App Usage Monitor
- **Real-time Tracking**: Monitors which SaaS applications are running
- **50+ Applications**: Tracks Slack, Zoom, Notion, Figma, VS Code, and more
- **Duration Tracking**: Records how long each app is used
- **Category Analysis**: Groups by Communication, Productivity, Development, Design, etc.
- **Privacy-first**: All monitoring happens locally on your device
- **Usage Insights**: Identifies unused or underused subscriptions

### Browser Activity Monitor
- **Multi-browser Support**: Chrome, Firefox, Edge, Safari
- **Web SaaS Detection**: Tracks usage of 100+ web-based services
- **Visit Analysis**: Counts visits and active days for each service
- **Smart Correlation**: Matches browser activity with subscription costs
- **Privacy**: One-time history scan, data stays local until you sync

### Usage Analytics Dashboard
Powered by comprehensive device monitoring, the dashboard provides:
- **📊 Dashboard**: Real-time overview of subscriptions, spending, and SaaS Score
- **💰 Cost Analysis**: Monthly/annual spending breakdown by category and vendor
- **📈 Usage Trends**: See which tools you actually use vs what you pay for
- **💡 Recommendations**: AI-generated cost-saving suggestions based on real usage
- **🔄 Alternatives**: Find cheaper alternatives to your current subscriptions
- **🏆 SaaS Score**: 0-100 score measuring subscription optimization
- **⚠️ Unused Alerts**: Identify subscriptions you haven't used in 30+ days
- **👥 Team Insights**: Understand team usage patterns (multi-user)

### Email Reader
- **macOS**: Accesses Mail.app database
- **Windows**: Reads Outlook PST files
- **Linux**: Parses Thunderbird profiles
- **Auto-detection**: Finds receipts from 20+ SaaS vendors
- **Privacy**: All processing happens locally

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
1. **Outlook**: Runs with standard user permissions
2. **Camera**: Windows will prompt for permission

### Linux
1. **Calendar**: Access Evolution or Thunderbird profiles
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
  "autoSyncEmails": true,           // Scan emails every 30 min
  "enableAppMonitoring": true,      // Track application usage
  "enableBrowserMonitoring": true,  // Scan browser history
  "autoSyncUsage": true,            // Upload usage data hourly
  "enableReminders": true,          // Calendar notifications
  "ocrLanguage": "eng",             // Tesseract language
  "emailPaths": []                  // Custom email locations
}
```

## 📱 Usage

### Get Dashboard Analytics

```javascript
// Get comprehensive dashboard with all metrics
const dashboard = await window.electronAPI.getDashboardAnalytics();

console.log('SaaS Score:', dashboard.data.overview.saasScore);
console.log('Monthly Spend:', dashboard.data.overview.monthlySpend);
console.log('Potential Savings:', dashboard.data.overview.potentialSavings);
console.log('Unused Subscriptions:', dashboard.data.overview.unusedSubscriptions);
```

### Get App Usage

```javascript
// Get application usage tracking data
const appUsage = await window.electronAPI.getAppUsage();

console.log('Currently Running Apps:', appUsage.data.currentlyRunning);
console.log('Usage by Category:', appUsage.data.byCategory);
console.log('Usage by Vendor:', appUsage.data.byVendor);
```

### Get Browser Usage

```javascript
// Get web-based SaaS usage from browser history
const browserUsage = await window.electronAPI.getBrowserUsage(168); // Last 7 days

console.log('Web Services Used:', browserUsage.data.summary);
console.log('By Category:', browserUsage.data.byCategory);
```

### Get Alternatives

```javascript
// Get cheaper alternatives for subscriptions
const alternatives = await window.electronAPI.getAlternatives([
  { vendor: 'Slack', cost: 8 },
  { vendor: 'Zoom', cost: 15 }
]);

console.log('Alternatives:', alternatives.data);
```

### Toggle App Monitoring

```javascript
// Enable or disable app monitoring
await window.electronAPI.toggleAppMonitoring(true);  // Enable
await window.electronAPI.toggleAppMonitoring(false); // Disable
```

### Scan Emails

```javascript
// From renderer process
const result = await window.electronAPI.scanEmails({
  days: 30,           // Last 30 days
  vendors: ['netflix', 'spotify', 'adobe']
});

console.log(`Found ${result.data.length} receipts`);
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

- **App Usage Monitor**: Every 5 seconds (tracks running apps)
- **Browser History Scan**: On-demand and during sync
- **Email Scanner**: Every 30 minutes
- **Calendar Sync**: Every hour
- **Usage Data Sync**: Every 30 minutes (uploads to backend)
- **Renewal Alerts**: 3 days before due date

### Disable Auto-Sync

```javascript
await window.electronAPI.setSetting('autoSyncEmails', false);
await window.electronAPI.setSetting('autoSyncUsage', false);
await window.electronAPI.toggleAppMonitoring(false); // Stop app tracking
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
- **No Cloud Sync**: Email data never leaves your device (except what you upload)

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

### Email not detected
```javascript
// Check service status
const settings = await window.electronAPI.getSettings();
console.log('Auto-sync enabled:', settings.autoSyncEmails);

// Manual scan
await window.electronAPI.scanEmails({ days: 365 });
```

## 📊 Supported Platforms

| Platform | Email | Camera | Calendar |
|----------|-------|--------|----------|
| macOS 10.15+ | ✅ Mail.app | ✅ Screen Capture | ✅ Calendar.app |
| Windows 10+ | ✅ Outlook | ✅ Camera API | ✅ Windows Calendar |
| Linux (Ubuntu 20.04+) | ✅ Thunderbird | ✅ V4L2 | ✅ Evolution |

✅ Full Support | ⚠️ Requires Setup

## 🚀 Next Steps

1. **Grant Permissions**: Follow prompts for Mail, Camera, Calendar
2. **Initial Scan**: Run full scan of emails
3. **Configure Auto-Sync**: Enable background monitoring
4. **Set Reminders**: Connect calendar for renewal alerts
5. **Test Scanning**: Capture a receipt with camera scanner

## 📚 API Reference

See [API.md](./API.md) for complete IPC API documentation.

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.
