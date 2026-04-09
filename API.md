# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.saas-optimizer.com`

All API endpoints are prefixed with `/api/v1`.

## Authentication

Most endpoints require authentication using JWT tokens.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### Users

#### Create User

```http
POST /api/v1/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response: 201 Created**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Current User

```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

### Subscriptions

#### List Subscriptions

```http
GET /api/v1/subscriptions/?skip=0&limit=100
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "service_name": "Netflix",
    "provider": "Netflix Inc",
    "cost": 15.99,
    "billing_cycle": "monthly",
    "status": "active",
    "start_date": "2024-01-01T00:00:00Z",
    "renewal_date": "2024-02-01T00:00:00Z",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

#### Create Subscription

```http
POST /api/v1/subscriptions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "service_name": "Spotify",
  "provider": "Spotify AB",
  "cost": 9.99,
  "billing_cycle": "monthly",
  "status": "active",
  "start_date": "2024-01-15T00:00:00Z",
  "renewal_date": "2024-02-15T00:00:00Z"
}
```

**Response: 201 Created**
```json
{
  "id": 2,
  "user_id": 1,
  "service_name": "Spotify",
  "provider": "Spotify AB",
  "cost": 9.99,
  "billing_cycle": "monthly",
  "status": "active",
  "start_date": "2024-01-15T00:00:00Z",
  "renewal_date": "2024-02-15T00:00:00Z",
  "created_at": "2024-01-15T12:00:00Z"
}
```

#### Get Subscription

```http
GET /api/v1/subscriptions/{subscription_id}
Authorization: Bearer <token>
```

#### Update Subscription

```http
PUT /api/v1/subscriptions/{subscription_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "cost": 12.99,
  "status": "active"
}
```

#### Delete Subscription

```http
DELETE /api/v1/subscriptions/{subscription_id}
Authorization: Bearer <token>
```

**Response: 204 No Content**

### Analytics

#### Get Spending Summary

```http
GET /api/v1/analytics/spending-summary
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
{
  "total_monthly_spend": 125.50,
  "total_yearly_spend": 299.00,
  "total_subscriptions": 8,
  "estimated_annual_cost": 1805.00
}
```

#### Get Spending by Category

```http
GET /api/v1/analytics/spending-by-category
Authorization: Bearer <token>
```

#### Get Spending Trends

```http
GET /api/v1/analytics/trends
Authorization: Bearer <token>
```

### Recommendations

#### Get Cost Saving Recommendations

```http
GET /api/v1/recommendations/cost-savings
Authorization: Bearer <token>
```

**Response: 200 OK**
```json
[
  {
    "type": "high_cost",
    "subscription_id": 5,
    "service_name": "Adobe Creative Cloud",
    "message": "Consider reviewing Adobe Creative Cloud - high monthly cost of $54.99",
    "potential_savings": 10.99
  }
]
```

#### Detect Duplicate Services

```http
GET /api/v1/recommendations/duplicate-services
Authorization: Bearer <token>
```

#### Detect Unused Subscriptions

```http
GET /api/v1/recommendations/unused-subscriptions
Authorization: Bearer <token>
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "User with this email already exists"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Subscription not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API requests are rate limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated requests

## Pagination

List endpoints support pagination using `skip` and `limit` query parameters:

```http
GET /api/v1/subscriptions/?skip=20&limit=10
```

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)

## Interactive Documentation

Visit these URLs for interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
