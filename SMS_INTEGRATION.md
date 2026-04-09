# SMS Integration Guide

## Overview

The SaaS Optimizer now supports automatic subscription detection from SMS messages through Twilio webhooks. When you receive subscription charge notifications via SMS, the system automatically:

1. Parses the message to extract vendor, amount, and transaction details
2. Matches it with existing subscriptions or creates new ones
3. Provides recommendations for duplicate or unused subscriptions
4. Suggests cheaper alternatives

## Features Implemented

### Backend Endpoints

#### 1. `/api/v1/sms/webhook` (POST)
**Purpose**: Receive SMS webhooks from Twilio

**Request** (Form data from Twilio):
```
MessageSid: SM1234567890abcdef
From: +1234567890
To: +0987654321
Body: "Your Netflix subscription of $15.99 has been charged"
```

**Response**:
```json
{
  "status": "success",
  "message": "SMS processed",
  "transaction_id": "123",
  "parsed_vendor": "Netflix",
  "parsed_amount": "15.99"
}
```

#### 2. `/api/v1/sms/transactions` (GET)
**Purpose**: Get all SMS transactions for the user

**Query Parameters**:
- `status` (optional): Filter by status (pending/confirmed/ignored/matched)
- `skip`: Pagination offset
- `limit`: Number of results

**Response**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "vendor": "Netflix",
    "amount": 15.99,
    "currency": "USD",
    "status": "pending",
    "confidence_score": 0.85,
    "raw_message": "Your Netflix subscription...",
    "created_at": "2026-04-09T10:00:00Z"
  }
]
```

#### 3. `/api/v1/sms/transactions/{id}/status` (PATCH)
**Purpose**: Update transaction status (confirm/ignore)

**Parameters**:
- `status`: "confirmed" or "ignored"

#### 4. `/api/v1/subscriptions/summary` (GET)
**Purpose**: Get comprehensive subscription analysis

**Response**:
```json
{
  "total_subscriptions": 5,
  "total_monthly_spend": 89.95,
  "total_annual_spend": 1079.40,
  "spending_by_provider": {
    "Netflix": 15.99,
    "Spotify": 9.99
  },
  "duplicates": [
    {
      "subscription_id": 3,
      "service_name": "Netflix",
      "type": "exact_duplicate",
      "potential_savings": 15.99
    }
  ],
  "low_usage_subscriptions": [
    {
      "subscription_id": 5,
      "service_name": "Gym Membership",
      "monthly_cost": 50.00,
      "recommendation": "No usage in last 60 days"
    }
  ],
  "potential_savings": 65.99
}
```

#### 5. `/api/v1/subscriptions/alternatives` (GET)
**Purpose**: Get alternative subscription suggestions

**Response**:
```json
[
  {
    "subscription_id": 1,
    "subscription_name": "Netflix Premium",
    "current_cost": 19.99,
    "alternatives": [
      {
        "alternative_name": "Netflix Basic",
        "alternative_cost": 6.99,
        "monthly_savings": 13.00,
        "annual_savings": 156.00,
        "savings_percentage": 65.03
      }
    ],
    "total_potential_savings": 13.00
  }
]
```

## Frontend Pages

### 1. 💰 Alternatives (pages/5_💰_Alternatives.py)
- Displays cheaper alternative plans
- Shows potential monthly/annual savings
- Compares features between plans
- Visualizes savings with charts

**Key Features**:
- Total savings banner
- Alternative suggestions for each subscription
- Best alternative highlighting
- Savings breakdown charts

### 2. 📱 SMS Transactions (pages/6_📱_SMS_Transactions.py)
- Lists all detected SMS transactions
- Filter by status (pending/confirmed/ignored)
- Confirm or ignore transactions
- Create subscriptions from SMS

**Key Features**:
- Status indicators (pending/confirmed/ignored/matched)
- Confidence scores with color coding
- Action buttons (Confirm, Ignore, Create Subscription)
- Restore ignored transactions

### 3. Enhanced Dashboard
- Shows alerts for duplicates and low-usage
- Quick links to view details
- Integrated with summary endpoint

## SMS Parsing Service

**Location**: `backend/app/services/sms_parser.py`

### Capabilities

The SMS parser can extract:
- **Vendor names**: Netflix, Spotify, Amazon, etc. (25+ services)
- **Amounts**: $99.99, USD 50, etc.
- **Currency**: USD, EUR, GBP, INR, etc.
- **Transaction dates**: Parsed timestamps

### Patterns Recognized

**Amount Patterns**:
- `$99.99`
- `USD 50.00`
- `amount: $25`
- `charged $15.99`

**Vendor Detection**:
- Keyword matching (netflix, spotify, etc.)
- Pattern matching (`charged by Netflix`)
- Context-aware extraction

**Confidence Scoring**:
- 0.0 - 1.0 scale
- Based on vendor detection, amount extraction, and keyword presence
- 🟢 High (≥0.7), 🟡 Medium (0.4-0.7), 🔴 Low (<0.4)

## Setting Up Twilio Integration

### Step 1: Create Twilio Account
1. Sign up at [twilio.com](https://www.twilio.com)
2. Get a phone number
3. Note your Account SID and Auth Token

### Step 2: Configure Webhook
1. In Twilio Console, go to Phone Numbers
2. Select your number
3. Under "Messaging", set webhook URL:
   ```
   https://your-domain.com/api/v1/sms/webhook
   ```
4. Method: POST
5. Save configuration

### Step 3: Test Integration
```bash
# Send test SMS to your Twilio number
curl -X POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json \
  --data-urlencode "From=+1234567890" \
  --data-urlencode "To={YourTwilioNumber}" \
  --data-urlencode "Body=Your Netflix subscription of $15.99 has been charged" \
  -u {AccountSid}:{AuthToken}
```

### Step 4: Forward Bank SMS
Set up SMS forwarding rules on your phone to forward subscription notifications to your Twilio number.

## Database Models

### SMSTransaction
```python
- id: int
- user_id: int
- from_number: str
- to_number: str
- message_sid: str (unique)
- raw_message: text
- vendor: str
- amount: float
- currency: str
- transaction_date: datetime
- subscription_id: int (nullable)
- matched: bool
- confidence_score: float
- status: str (pending/confirmed/ignored/matched)
- created_at: datetime
- updated_at: datetime
```

### SubscriptionAlternative
```python
- id: int
- subscription_id: int
- alternative_name: str
- alternative_provider: str
- alternative_cost: float
- billing_cycle: str
- monthly_savings: float
- annual_savings: float
- savings_percentage: float
- reason: text
- features_comparison: text
- recommendation_score: float
- created_at: datetime
- updated_at: datetime
```

## Usage Flow

### 1. SMS Received
```
User receives SMS → Twilio → Webhook → SMS Parser → Database
```

### 2. User Reviews Transaction
```
SMS Transactions page → View pending → Confirm/Ignore → Update status
```

### 3. Create Subscription
```
SMS Transaction → "Create Subscription" → New subscription added → Linked to SMS
```

### 4. View Alternatives
```
Alternatives page → See cheaper options → Compare features → Potential savings
```

### 5. Analyze Summary
```
Summary endpoint → Detect duplicates → Find low-usage → Show savings
```

## Running Migrations

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "add sms and alternatives tables"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Testing

### Test SMS Parsing
```python
# In Python console
from app.services.sms_parser import SMSParser

message = "Your Netflix subscription of $15.99 has been charged"
parsed = SMSParser.parse(message)
print(parsed)
# Output: ParsedSMS(vendor='Netflix', amount=15.99, currency='USD', confidence=0.9)
```

### Test API Endpoints
```bash
# Get transactions
curl -X GET http://localhost:8000/api/v1/sms/transactions \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get summary
curl -X GET http://localhost:8000/api/v1/subscriptions/summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get alternatives
curl -X GET http://localhost:8000/api/v1/subscriptions/alternatives \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Alternative Plans Database

Currently hardcoded in `backend/app/api/v1/endpoints/alternatives.py`:

```python
ALTERNATIVE_PLANS = {
    "netflix": [
        {"name": "Netflix Basic", "cost": 6.99},
        {"name": "Hulu", "cost": 7.99},
        {"name": "Disney+", "cost": 7.99}
    ],
    "spotify": [...],
    "dropbox": [...],
    # Add more
}
```

**Future Enhancement**: Move to database table for dynamic updates.

## Security Considerations

1. **Webhook Validation**: Add Twilio signature validation
2. **Rate Limiting**: Already implemented in middleware
3. **Authentication**: All endpoints require JWT token
4. **Input Sanitization**: SMS content is sanitized before parsing
5. **Data Privacy**: SMS messages contain sensitive financial data

## Troubleshooting

### SMS Not Detected
- Check Twilio webhook configuration
- Verify webhook URL is accessible
- Check backend logs for parsing errors

### Low Confidence Scores
- Message format may not match patterns
- Add custom patterns in `sms_parser.py`
- Manually review and confirm transactions

### No Alternatives Found
- Add service to `ALTERNATIVE_PLANS` dictionary
- Check service name matching logic
- Generic alternatives are shown as fallback

## Next Steps

1. **Enhance Parsing**: Add more vendor patterns
2. **Machine Learning**: Train model on actual SMS data
3. **Alternative API**: Integrate with pricing APIs
4. **SMS Insights**: Add usage analytics from SMS frequency
5. **Notifications**: Alert users of suspicious charges
6. **Bulk Actions**: Confirm/ignore multiple transactions

## Support

For questions or issues:
- Check logs: `backend/logs/`
- Review API docs: `http://localhost:8000/docs`
- Frontend console: Browser DevTools
