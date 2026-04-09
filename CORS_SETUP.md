# CORS and API Communication Setup

## Overview

This document explains how the FastAPI backend (port 8000) and Streamlit frontend (port 8501) communicate with CORS properly configured.

## Architecture

```
┌─────────────────────┐         CORS Enabled         ┌──────────────────────┐
│                     │         HTTP Requests        │                      │
│  Streamlit Frontend │ ────────────────────────────>│  FastAPI Backend     │
│  localhost:8501     │ <────────────────────────────│  localhost:8000      │
│                     │         JSON Responses       │                      │
└─────────────────────┘                              └──────────────────────┘
```

## CORS Configuration

### Backend (FastAPI)

**Location**: `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
```

**Middleware Setup**: `backend/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### Frontend (Streamlit)

**Location**: `frontend/utils/api.py`

```python
import requests

API_URL = "http://localhost:8000"
BASE_URL = f"{API_URL}/api/v1"

def get_subscriptions(token: str):
    response = requests.get(
        f"{BASE_URL}/subscriptions/",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

**Configuration**: `frontend/.streamlit/config.toml`

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false
```

## API Client Implementation

### Authentication Flow

1. **Login Request**:
```python
def login(email: str, password: str):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()  # Returns: {"access_token": "...", "token_type": "bearer"}
```

2. **Authenticated Requests**:
```python
def get_subscriptions(token: str):
    response = requests.get(
        f"{BASE_URL}/subscriptions/",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### API Endpoints Used

| Endpoint | Method | Purpose | Authentication |
|----------|--------|---------|----------------|
| `/api/v1/auth/login` | POST | User login | No |
| `/api/v1/users/` | POST | Create user | No |
| `/api/v1/users/me` | GET | Get current user | Yes |
| `/api/v1/subscriptions/` | GET | List subscriptions | Yes |
| `/api/v1/subscriptions/` | POST | Create subscription | Yes |
| `/api/v1/subscriptions/{id}` | PUT | Update subscription | Yes |
| `/api/v1/subscriptions/{id}` | DELETE | Delete subscription | Yes |
| `/api/v1/analytics/spending-summary` | GET | Get analytics | Yes |
| `/api/v1/recommendations/cost-savings` | GET | Get recommendations | Yes |

## Session Management

**Location**: `frontend/utils/session.py`

```python
import streamlit as st

def login_user(token: str, user: dict):
    st.session_state.logged_in = True
    st.session_state.token = token
    st.session_state.user = user

def get_token() -> str:
    return st.session_state.get("token", None)
```

Session state variables:
- `logged_in`: Boolean flag
- `token`: JWT access token
- `user`: User information dict

## Testing CORS

### Manual Test

```bash
# Terminal 1 - Start backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Start frontend
cd frontend
streamlit run Home.py

# Terminal 3 - Test API directly
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demo123"
```

### Using Browser DevTools

1. Open http://localhost:8501
2. Open Browser DevTools (F12)
3. Go to Network tab
4. Login and interact with the app
5. Check requests to http://localhost:8000
6. Verify response headers include:
   - `access-control-allow-origin: http://localhost:8501`
   - `access-control-allow-credentials: true`

## Environment Variables

### Backend `.env`

```env
# API Configuration
PROJECT_NAME=SaaS Optimizer
API_V1_PREFIX=/api/v1

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:8501","http://127.0.0.1:8501","http://localhost:8000","http://127.0.0.1:8000"]

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/saas_optimizer

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend `.env`

```env
API_URL=http://localhost:8000
API_V1_PREFIX=/api/v1
```

## Docker Configuration

**docker-compose.yml**:

```yaml
services:
  backend:
    build: ../backend
    ports:
      - "8000:8000"
    environment:
      - BACKEND_CORS_ORIGINS=["http://frontend:8501","http://localhost:8501"]
  
  frontend:
    build: ../frontend
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
```

## Troubleshooting

### CORS Errors

**Symptom**: "Access to fetch at 'http://localhost:8000' from origin 'http://localhost:8501' has been blocked by CORS policy"

**Solution**:
1. Check `BACKEND_CORS_ORIGINS` includes `http://localhost:8501`
2. Restart backend server
3. Clear browser cache

### Connection Refused

**Symptom**: "Connection refused" when Streamlit tries to reach FastAPI

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check frontend .env has correct API_URL
3. Ensure no firewall blocking ports

### Authentication Issues

**Symptom**: 401 Unauthorized errors

**Solution**:
1. Verify token is being sent: Check Network tab
2. Check token hasn't expired (30 min default)
3. Verify `Authorization: Bearer <token>` header format

## Production Considerations

### CORS Origins

Update `BACKEND_CORS_ORIGINS` for production:

```python
BACKEND_CORS_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com"
]
```

### Security

1. **HTTPS**: Use HTTPS in production
2. **Environment Variables**: Never commit real credentials
3. **Token Storage**: Consider secure token storage
4. **Rate Limiting**: Already implemented in middleware
5. **CSRF Protection**: Streamlit handles this

### Performance

1. **Connection Pooling**: Configure in requests
2. **Caching**: Use Redis for API responses
3. **Compression**: Enable gzip compression
4. **CDN**: Serve static assets via CDN
