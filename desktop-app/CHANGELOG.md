# CHANGELOG

All notable changes to the SaaS Optimizer Desktop App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-04-13

### Added
- 📧 **Email Reader Service**
  - Native Mail.app support (macOS)
  - Microsoft Outlook support (Windows)
  - Thunderbird support (Linux)
  - Automatic receipt detection from 20+ SaaS vendors
  - Background monitoring every 30 minutes

- 📱 **SMS Reader Service**
  - Messages.app integration (macOS)
  - Your Phone app integration (Windows)
  - Android Debug Bridge (ADB) support (Linux)
  - Transaction keyword detection
  - Background monitoring every 15 minutes

- 📸 **Camera Scanner Service**
  - Tesseract.js OCR integration
  - Receipt text extraction (vendor, amount, date)
  - Window capture for specific applications
  - Multi-format support (PNG, JPEG, PDF)

- 📅 **Calendar Sync Service**
  - macOS Calendar.app integration
  - Windows Calendar integration
  - Evolution/Thunderbird support (Linux)
  - ICS file parsing
  - Renewal event detection
  - 3-day advance reminders

- 🔔 **Native Notifications**
  - Desktop alerts for renewals
  - Recommendation notifications
  - Multi-platform support (macOS, Windows, Linux)

- ⚙️ **Settings Management**
  - Encrypted local storage (electron-store)
  - Backend URL configuration
  - Auto-sync toggles
  - Custom email/SMS paths

- 🔐 **Security Features**
  - JWT token authentication
  - OS-level permission requests
  - Local-first data processing
  - HTTPS-only backend communication

- 📦 **Build System**
  - electron-builder configuration
  - macOS DMG and ZIP packages
  - Windows NSIS installer and portable EXE
  - Linux AppImage and DEB packages
  - Code signing support (macOS and Windows)

### Changed
- **Backend Integration**
  - Removed Twilio dependency from requirements.txt
  - Updated SMS endpoint from `/webhook` to `/upload`
  - Changed from Twilio form-encoded to JSON API
  - Added SMSTransactionUpload schema

- **Architecture**
  - Migrated from cloud SMS service to native device access
  - Implemented IPC bridge for renderer-main communication
  - Added background service orchestration

### Deprecated
- Twilio SMS webhook endpoint (replaced with direct upload)
- TwilioWebhook schema (replaced with SMSTransactionUpload)

### Removed
- `twilio==8.10.3` from requirements.txt
- `/api/v1/sms/webhook` endpoint
- Twilio-specific form-encoded data handling

### Security
- All data processing happens locally on user's device
- No SMS/email data sent to third-party services
- Encrypted storage for sensitive settings
- Token refresh mechanism
- Audit trail for API calls

## [Unreleased]

### Planned Features
- Auto-updater using electron-updater
- Crash reporting with Sentry
- App store distribution (Mac App Store, Microsoft Store)
- Multi-language OCR support
- Browser history scanning for SaaS logins
- Chrome/Firefox bookmark sync

---

For full documentation, see:
- [README.md](README.md) - Desktop app overview
- [../DESKTOP_APP_SETUP.md](../DESKTOP_APP_SETUP.md) - Setup guide
- [../EMAIL_AUTOMATION_GUIDE.md](../EMAIL_AUTOMATION_GUIDE.md) - Email features
