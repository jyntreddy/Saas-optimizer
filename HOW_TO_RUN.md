# 🎯 How to Run the SaaS Optimizer Platform

## ✨ Option 1: One-Command Docker Launch (Recommended)

This runs EVERYTHING - backend, frontend, database, cache - all at once!

### Prerequisites
- Docker Desktop installed and **running** (check menu bar for Docker icon)

### Run
```bash
./run.sh
```

That's it! The script will:
- ✅ Check if Docker is running
- ✅ Build all Docker images
- ✅ Start PostgreSQL database
- ✅ Start Redis cache
- ✅ Run database migrations
- ✅ Start FastAPI backend (port 8000)
- ✅ Start Streamlit frontend (port 8501)

### Access
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000/docs

### Stop
Press `Ctrl+C`, then:
```bash
docker-compose down
```

---

## 🔧 Option 2: Manual Docker Commands

```bash
# Start everything
docker-compose up --build

# Stop everything
docker-compose down

# Clean restart (removes data)
docker-compose down -v && docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 💻 Option 3: Local Development (No Docker)

### Prerequisites
- Python 3.11+
- PostgreSQL running on localhost:5432
- Redis running on localhost:6379

### Terminal 1 - Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run Home.py
```

---

## 🐛 Troubleshooting

### "Docker daemon not running"
→ Start Docker Desktop and wait for it to fully start

### Port already in use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :8501

# Kill the process or use docker-compose down
```

### Database connection error
```bash
# Restart containers
docker-compose restart postgres backend
```

---

## 📚 What's Included

- **Backend (FastAPI)**:
  - User authentication (JWT)
  - Subscription management
  - SMS integration with Twilio
  - Duplicate detection
  - Alternative plan suggestions
  - 11 API endpoints

- **Frontend (Streamlit)**:
  - 📊 Dashboard
  - 📋 Subscriptions
  - 📈 Analytics
  - 💡 Recommendations
  - 💰 Alternatives (cost savings)
  - 📱 SMS Transactions

- **Infrastructure**:
  - PostgreSQL 15
  - Redis 7
  - Docker & Docker Compose
  - Auto-migrations on startup
