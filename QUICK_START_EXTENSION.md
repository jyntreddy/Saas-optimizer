# 🚀 Quick Start: Chrome Extension → Dashboard

## 5-Minute Setup

### Step 1: Start Services (30 seconds)
```bash
cd saas-optimizer
docker-compose up -d
```

✅ Backend: http://localhost:8000  
✅ Frontend: http://localhost:8501

### Step 2: Create Account (1 minute)
1. Open http://localhost:8501
2. Sidebar → "Create Account"
3. Enter: email, password, name
4. Login

### Step 3: Install Extension (2 minutes)
1. Get Google OAuth Client ID:
   - https://console.cloud.google.com/
   - Create project → Enable Gmail API
   - Credentials → OAuth Client ID → Chrome Extension
   - Copy Client ID

2. Load extension:
   - Chrome → `chrome://extensions/`
   - "Developer mode" ON
   - "Load unpacked" → Select `browser-extension/` folder

3. Configure:
   - Edit `browser-extension/manifest.json`
   - Replace `YOUR_GOOGLE_CLIENT_ID` with your Client ID
   - Reload extension

### Step 4: Connect Extension (1 minute)
1. Click extension icon
2. **Gmail Section**:
   - Click "Connect Gmail Account"
   - Authorize (read-only)
3. **Backend Section**:
   - URL: `http://localhost:8000`
   - Email/Password: (from Step 2)
   - Click "Login to Backend"

### Step 5: Scan & View (30 seconds)
1. Click "🔍 Scan Gmail for Receipts"
2. Wait for scan (shows progress)
3. Dashboard → "📧 Email Receipts" page
4. See all scanned receipts!

## Visual Flow

```
┌─────────────────┐
│  Gmail Account  │  Your subscription emails
└────────┬────────┘
         │ OAuth (read-only)
         ▼
┌─────────────────────┐
│ Chrome Extension    │  Scan button
│ 📧 Gmail Scanner    │  ↓
└────────┬────────────┘  Extracts: vendor, amount, date
         │ POST /api/v1/emails/upload
         ▼
┌─────────────────────┐
│ Backend (Port 8000) │  Stores in PostgreSQL
│ FastAPI + DB        │
└────────┬────────────┘
         │ GET /api/v1/emails/receipts
         ▼
┌─────────────────────┐
│ Frontend (8501)     │  📧 Email Receipts page
│ Streamlit Dashboard │  📊 Dashboard stats
└─────────────────────┘
```

## What You'll See

### In Extension Popup
```
┌─────────────────────────┐
│ 📧 Gmail Scanner        │
├─────────────────────────┤
│ Gmail Access            │
│ ✅ Connected as         │
│    you@gmail.com        │
├─────────────────────────┤
│ Scan Receipts           │
│ [🔍 Scan Gmail...]      │
│                         │
│ Receipts Found: 23      │
│ Last Scan: Just now     │
├─────────────────────────┤
│ Backend Settings        │
│ ✅ Backend connected    │
│ [⚙️ Settings...]        │
└─────────────────────────┘
```

### In Dashboard (http://localhost:8501)

#### Dashboard Page
```
📊 Dashboard
────────────────────────────
📈 Key Metrics
┌──────────┬──────────┬──────────┬──────────┐
│ Monthly  │  Active  │  Annual  │  Yearly  │
│ $450.00  │    12    │ $5400.00 │ $1200    │
└──────────┴──────────┴──────────┴──────────┘

📧 Chrome Extension Activity
┌──────────┬──────────┬──────────┬──────────┐
│ Scanned  │ Pending  │ Matched  │ Detected │
│    23    │    15    │     8    │ $450.00  │
└──────────┴──────────┴──────────┴──────────┘
💡 You have 15 receipts pending review.
```

#### Email Receipts Page
```
📧 Email Receipts
────────────────────────────
📊 Stats
┌──────┬──────┬──────┬──────┬──────────┐
│Total │ Ext  │Pend. │Match │ Detected │
│  23  │  23  │  15  │   8  │ $450.00  │
└──────┴──────┴──────┴──────┴──────────┘

📋 Receipt List
────────────────────────────
Netflix                 $15.99  📅 Apr 1   🟡 Pending
└─ Your subscription...        [✅ Match] [❌ Ignore]

Spotify                 $9.99   📅 Apr 5   🟡 Pending
└─ Spotify Premium...          [✅ Match] [❌ Ignore]

Adobe                   $52.99  📅 Apr 10  🟢 Matched
└─ Creative Cloud...           ✓ Linked to subscription

...
```

## Troubleshooting

### Extension shows "Backend upload failed"
```bash
# Check backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# Restart if needed
docker-compose restart backend
```

### Dashboard shows 0 receipts
1. Verify extension scan completed (shows count)
2. Same email/password in both places?
3. Refresh dashboard (F5)
4. Check backend logs:
   ```bash
   docker-compose logs backend | grep email
   ```

### Can't connect Gmail
1. Check `manifest.json` has valid Client ID
2. Gmail API enabled in Google Cloud?
3. Extension ID matches OAuth config?
4. Try: chrome://identity-internals/ → Remove token

## Success Checklist

✅ Backend running (port 8000)  
✅ Frontend running (port 8501)  
✅ Account created in dashboard  
✅ Extension installed in Chrome  
✅ manifest.json has your Client ID  
✅ Extension connected to Gmail  
✅ Extension connected to backend  
✅ Gmail scanned (shows receipt count)  
✅ Receipts visible in dashboard  
✅ Stats showing on Dashboard page  
✅ Email Receipts page loads  

## Next Steps

1. **Match receipts**: Link to existing subscriptions
2. **Create subscriptions**: Add new ones from receipts
3. **Enable auto-scan**: Hourly background scanning
4. **View analytics**: Track spending trends
5. **Get recommendations**: Cost optimization tips

## Full Docs

- **Setup Guide**: `EXTENSION_DASHBOARD_CONNECTION.md`
- **Extension Details**: `CHROME_EXTENSION_SETUP.md`
- **API Reference**: `EXTENSION_INTEGRATION_SUMMARY.md`

---

**Total Time: ~5 minutes**  
**Result: Gmail receipts automatically tracked in dashboard! 🎉**
