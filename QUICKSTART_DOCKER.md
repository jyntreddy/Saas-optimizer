# 🚀 Quick Start Guide

## One Command to Run Everything

```bash
docker-compose up --build
```

This will:
- ✅ Build Docker images for backend & frontend
- ✅ Start PostgreSQL database (port 5432)
- ✅ Start Redis cache (port 6379)
- ✅ Run database migrations automatically
- ✅ Start FastAPI backend (port 8000)
- ✅ Start Streamlit frontend (port 8501)

## Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Stop Everything

Press `Ctrl+C` in the terminal, then:

```bash
docker-compose down
```

## Clean Restart (Remove Data)

```bash
docker-compose down -v
docker-compose up --build
```

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Database Access

```bash
docker exec -it saas-optimizer-db psql -U postgres -d saas_optimizer
```

## Manual Installation (Without Docker)

If you prefer to run without Docker:

### Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run Home.py
```

Make sure PostgreSQL and Redis are running locally.
