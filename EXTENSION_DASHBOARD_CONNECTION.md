# Connecting Chrome Extension to Dashboard

This guide shows you how to connect the Gmail Scanner Chrome extension to your SaaS Optimizer dashboard so all scanned receipts appear in real-time.

## Overview

The Chrome extension scans your Gmail for subscription receipts and automatically syncs them to your dashboard. You can then:
- ✅ View all scanned receipts in the **Email Receipts** page
- 📊 See stats on the **Dashboard** (receipts scanned, pending review, matched)
- 💰 Track detected spending from receipts
- 🔗 Match receipts to existing subscriptions or create new ones

## Prerequisites

✅ Backend running on `http://localhost:8000` (or your deployed URL)  
✅ Frontend running on `http://localhost:8501` (or your deployed URL)  
✅ Chrome extension installed (see `CHROME_EXTENSION_SETUP.md`)  
✅ User account created in the app

## Step-by-Step Connection

### 1. Start Your Application

```bash
# From project root
docker-compose up -d

# Verify services are running
curl http://localhost:8000/health  # Backend
curl http://localhost:8501          # Frontend
```

### 2. Create User Account (if needed)

1. Open frontend: http://localhost:8501
2. Click **"Create Account"** in the sidebar
3. Enter:
   - Email: `your@email.com`
   - Password: (secure password)
   - Full Name: `Your Name`
4. Click **Create Account**
5. Login with your credentials

### 3. Configure Chrome Extension

1. **Click extension icon** in Chrome toolbar
2. **Backend Settings** section:
   - Backend URL: `http://localhost:8000` (or your deployed URL)
   - Email: Same email from step 2
   - Password: Same password from step 2
   - Click **"Login to Backend"**
   - ✅ Should show "Backend connected"

3. **Gmail Access** section:
   - Click **"Connect Gmail Account"**
   - Authorize Google OAuth (read-only access)
   - ✅ Should show "Connected as your@gmail.com"

### 4. Scan Gmail for Receipts

1. In the extension popup, click **"🔍 Scan Gmail for Receipts"**
2. Progress bar shows scanning status
3. When complete, you'll see:
   - Number of receipts found
   - "Receipts synced to backend" notification

### 5. View in Dashboard

1. **Open Dashboard**: http://localhost:8501
2. **Login** with your account
3. **Navigate to "📧 Email Receipts"** page (in sidebar)
4. You should see:
   - Stats cards (total receipts, from extension, pending, matched)
   - List of all scanned receipts
   - Details for each receipt (vendor, amount, date, status)

## Data Flow

```
┌─────────────────────┐
│   Gmail API         │
│   (Your emails)     │
└──────────┬──────────┘
           │ OAuth2 + Read
           ▼
┌─────────────────────┐
│ Chrome Extension    │
│ - Searches emails   │
│ - Extracts receipts │
│ - Parses data       │
└──────────┬──────────┘
           │ POST /api/v1/emails/upload
           ▼
┌─────────────────────┐
│ Backend API         │
│ - Stores receipts   │
│ - Tracks stats      │
└──────────┬──────────┘
           │ GET /api/v1/emails/receipts
           ▼
┌─────────────────────┐
│ Dashboard (Streamlit)│
│ - Email Receipts page
│ - Dashboard stats   │
│ - Recommendations   │
└─────────────────────┘
```

## Backend Endpoints Used

The extension communicates with these API endpoints:

### Authentication
- `POST /api/v1/auth/login` - Login to get access token

### Email Receipts
- `POST /api/v1/emails/upload` - Upload scanned receipts (bulk)
- `GET /api/v1/emails/receipts` - Get all receipts for user
- `GET /api/v1/emails/stats` - Get receipt statistics
- `PATCH /api/v1/emails/receipts/{id}/status` - Update receipt status

## Frontend Pages

### 1. Dashboard (📊)
Shows summary stats including:
- **Chrome Extension Activity card**:
  - Scanned Receipts count
  - Pending Review count
  - Matched count
  - Detected Spending total

### 2. Email Receipts (📧)
Full page dedicated to receipts:
- **Stats Cards**: Total, from extension, pending, matched, spending
- **Chrome Extension Setup Guide**: Expandable instructions
- **Receipt List**: All scanned receipts with:
  - Vendor name and email subject
  - Amount and confidence score
  - Date and sender
  - Status (pending, matched, ignored)
  - Actions (Match, Ignore)
  - Detailed view with raw data

## Testing the Connection

### Quick Test

1. **Extension → Click "Scan Gmail"**
2. Wait for scan to complete (progress bar)
3. **Dashboard → Refresh page**
4. Check "Chrome Extension Activity" section
5. **Email Receipts page → Should see scanned items**

### Verify API Integration

```bash
# Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword" \
  | jq -r '.access_token')

# Check receipt stats
curl -s http://localhost:8000/api/v1/emails/stats \
  -H "Authorization: Bearer $TOKEN" | jq

# Get receipts
curl -s http://localhost:8000/api/v1/emails/receipts \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected output:
{
  "total_receipts": 10,
  "pending": 5,
  "matched": 5,
  "from_extension": 10,
  "total_detected_spending": 459.99
}
```

## Features in Action

### Auto-Scan (Hourly)
1. In extension popup, check **"Enable auto-scan (hourly)"**
2. Extension runs in background every hour
3. New receipts automatically appear in dashboard
4. Notification shown when scan completes

### Receipt Management
1. **Pending receipts** appear with yellow status badge
2. Click **"✅ Match"** to link to existing subscription
3. Click **"❌ Ignore"** to mark as not relevant
4. **Matched receipts** show green status
5. View detailed data by expanding receipt card

### Spending Tracking
- Dashboard shows **total detected spending** from all receipts
- Compare to actual subscription costs
- Identify discrepancies or hidden charges
- Track spending trends over time

## Troubleshooting

### Extension says "Backend upload failed"

**Check:**
1. Backend is running: `curl http://localhost:8000/health`
2. Backend URL is correct in extension settings
3. You're logged in to backend (shows "Backend connected")
4. Check browser console (F12) for error details

**Fix:**
```bash
# Restart backend
docker-compose restart backend

# Check logs
docker-compose logs backend

# Verify endpoint
curl http://localhost:8000/api/v1/emails/upload
```

### Dashboard shows 0 receipts

**Check:**
1. Extension successfully scanned Gmail (shows count)
2. You're logged in with the same account as extension
3. Refresh the dashboard page
4. Check Email Receipts page directly

**Debug:**
```bash
# Check if receipts exist in database
docker-compose exec backend python -c "
from app.db.base import SessionLocal
from app.models.email_receipt import EmailReceipt
db = SessionLocal()
count = db.query(EmailReceipt).count()
print(f'Total receipts in DB: {count}')
"
```

### "No receipts found" in extension

**Possible reasons:**
1. Gmail has no subscription emails in last year
2. Email amount not detected (extension filters by amount)
3. SaaS vendor not in SAAS_VENDORS list

**Solutions:**
- Check extension's vendor list in `background.js`
- Try broader date range
- Manually add receipts via dashboard

### Stats not updating

**Try:**
1. Refresh dashboard page (F5)
2. Logout and login again
3. Clear browser cache
4. Check backend logs for errors

## Advanced Configuration

### Custom Backend URL (Production)

If deploying to production:

```javascript
// In extension popup.js, update:
let backendUrl = 'https://your-api-domain.com';

// Or configure in extension settings
```

### Database Direct Access

View all receipts directly:

```sql
-- Connect to PostgreSQL
docker-compose exec db psql -U postgres saas_optimizer

-- Query receipts
SELECT 
  id, 
  vendor, 
  amount, 
  status, 
  gmail_message_id,
  received_date
FROM email_receipts
WHERE gmail_message_id IS NOT NULL
ORDER BY received_date DESC
LIMIT 10;
```

### API Rate Limiting

Extension has built-in rate limiting:
- 100ms delay between Gmail API requests
- Max 50 receipts per scan (configurable)
- Hourly auto-scan to avoid quota issues

## Security Notes

🔒 **Data Privacy:**
- Extension has **read-only** Gmail access
- OAuth tokens stored locally in Chrome (not on server)
- Backend receives only extracted data (vendor, amount, date)
- Raw email bodies truncated to 500 chars before upload
- All communication over HTTPS (in production)

🔐 **Authentication:**
- Backend uses JWT tokens
- Extension stores token in Chrome storage
- Tokens expire after 24 hours (configurable)
- Refresh dashboard login if token expires

## Next Steps

1. ✅ **Review scanned receipts** in Email Receipts page
2. 🔗 **Match receipts** to existing subscriptions
3. ➕ **Create subscriptions** from unmatched receipts
4. 📊 **Track spending** trends in Analytics
5. 💡 **Get recommendations** for cost savings
6. ⚙️ **Enable auto-scan** for continuous monitoring

## Support

For issues:
1. Check backend logs: `docker-compose logs backend | tail -50`
2. Check extension console: Right-click extension → Inspect → Console
3. Review `CHROME_EXTENSION_SETUP.md` for detailed setup
4. See `IMPLEMENTATION_SUMMARY.md` for architecture details

---

**🎉 Your Chrome extension is now fully connected to the dashboard!**  
All Gmail receipts will automatically sync and appear in your SaaS Optimizer dashboard.
