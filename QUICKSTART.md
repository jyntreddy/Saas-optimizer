# Quick Start Guide

## Running the Application

### Method 1: Using Docker Compose (Recommended)

```bash
# Start all services
cd infra
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Method 2: Local Development

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
alembic upgrade head
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
pip install -r requirements.txt
cp .env.example .env
# Edit .env (default API_URL=http://localhost:8000 is fine)
streamlit run Home.py
```

**Terminal 3 - Celery (Optional):**
```bash
cd backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=info
```

## Demo Credentials

```
Email: demo@example.com
Password: demo123
```

## Key Features

1. **Dashboard** (http://localhost:8501) - View spending overview
2. **Subscriptions** - Add, edit, delete subscriptions
3. **Analytics** - Detailed cost analysis with charts
4. **Recommendations** - AI-powered cost optimization tips

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## CORS Configuration

The FastAPI backend is configured to allow requests from Streamlit (port 8501):

```python
# backend/app/core/config.py
BACKEND_CORS_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
```

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify .env database credentials
- Run migrations: `alembic upgrade head`

### Frontend can't connect to API
- Ensure backend is running on port 8000
- Check frontend .env has correct API_URL
- Verify CORS settings in backend config

### Docker issues
- Clear containers: `docker-compose down -v`
- Rebuild images: `docker-compose build --no-cache`
- Check logs: `docker-compose logs backend frontend`

## Next Steps

1. Login with demo credentials
2. Add your first subscription
3. View analytics dashboard
4. Check AI recommendations
5. Explore API documentation
