# Desktop App - Quick Reference

## Installation

```bash
cd desktop-app
./install.sh
```

## Development

```bash
npm run dev          # Start in development mode
npm run build        # Build for current platform
npm run build:mac    # Build for macOS
npm run build:win    # Build for Windows
npm run build:linux  # Build for Linux
```

## Permissions

### macOS
```
System Preferences → Security & Privacy → Privacy → Full Disk Access
→ Add "SaaS Optimizer.app"
```

### Windows
```
Install "Your Phone" from Microsoft Store
Link Android phone
```

### Linux
```bash
sudo apt install android-tools-adb
sudo usermod -a -G video $USER
```

## API Usage

```javascript
// Scan emails
await window.electronAPI.scanEmails({ days: 30 })

// Scan SMS
await window.electronAPI.scanSMS({ days: 90 })

// Scan document
await window.electronAPI.scanDocument()

// Get calendar events
await window.electronAPI.getCalendarEvents({ 
  startDate: new Date() 
})

// Send notification
await window.electronAPI.sendNotification({
  title: 'Renewal Alert',
  body: 'Netflix renews in 3 days'
})

// Settings
await window.electronAPI.setSetting('autoSyncEmails', true)
const settings = await window.electronAPI.getSettings()
```

## Configuration Files

```
macOS:    ~/Library/Application Support/saas-optimizer/
Windows:  %APPDATA%/saas-optimizer/
Linux:    ~/.config/saas-optimizer/
```

## Logs

```
macOS:    ~/Library/Logs/SaaS Optimizer/
Windows:  %APPDATA%/SaaS Optimizer/logs/
Linux:    ~/.config/saas-optimizer/logs/
```

## Troubleshooting

### Email not scanning
```bash
# macOS
sqlite3 ~/Library/Mail/V10/MailData/Envelope\ Index \
  "SELECT COUNT(*) FROM messages;"

# Linux
ls ~/.thunderbird/*/ImapMail/*/*
```

### SMS not working
```bash
# macOS
sqlite3 ~/Library/Messages/chat.db \
  "SELECT COUNT(*) FROM message;"

# Linux (Android ADB)
adb devices
adb shell content query --uri content://sms/inbox --limit 5
```

### Camera not accessible
```bash
# Linux - Add user to video group
sudo usermod -a -G video $USER
# Then log out and back in
```

## Backend Endpoints

```bash
# Upload SMS
POST /api/v1/sms/upload
{
  "sender": "NETFLIX",
  "message": "Your subscription...",
  "timestamp": "2024-04-13T10:00:00Z",
  "source": "desktop-app"
}

# Scan email
POST /api/v1/emails/scan
{
  "subject": "Your Netflix receipt",
  "body": "...",
  "from": "billing@netflix.com"
}
```

## File Structure

```
desktop-app/
├── src/
│   ├── main.js                # Electron main
│   ├── preload.js             # IPC bridge
│   └── services/
│       ├── emailReader.js     # Email scanning
│       ├── smsReader.js       # SMS parsing
│       ├── cameraScanner.js   # OCR/camera
│       ├── calendarSync.js    # Calendar sync
│       └── apiClient.js       # Backend API
├── package.json               # Dependencies
└── assets/                    # Icons
```

## Build Outputs

```
dist/
├── SaaS Optimizer-1.0.0.dmg          # macOS installer
├── SaaS Optimizer-1.0.0-mac.zip      # macOS portable
├── SaaS Optimizer Setup 1.0.0.exe    # Windows installer
├── SaaS Optimizer 1.0.0.exe          # Windows portable
├── SaaS-Optimizer-1.0.0.AppImage     # Linux AppImage
└── saas-optimizer_1.0.0_amd64.deb    # Debian package
```

## Documentation

- [DESKTOP_APP_SETUP.md](../DESKTOP_APP_SETUP.md) - Full setup guide
- [README.md](README.md) - Desktop app documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

**Quick Links:**
- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs
