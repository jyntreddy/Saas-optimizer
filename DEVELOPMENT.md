# Development Quick Start

This guide will help you get SaaS Optimizer running on your local machine for development.

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Git

## Option 1: Docker Setup (Recommended)

The easiest way to get started is using Docker:

```bash
# Clone the repository
git clone <repository-url>
cd saas-optimizer

# Run setup script
chmod +x setup.sh
./setup.sh

# Wait for all services to start, then visit:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## Option 2: Manual Setup

### 1. Setup PostgreSQL

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb saas_optimizer
```

### 2. Setup Redis

```bash
# Install Redis (macOS)
brew install redis
brew services start redis
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and configure DATABASE_URL, REDIS_URL, etc.

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Edit .env.local if needed

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Development Workflow

### Making Changes to Backend

1. Create/modify models in `backend/app/models/`
2. Create database migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of changes"
   alembic upgrade head
   ```
3. Update schemas in `backend/app/schemas/`
4. Update routes in `backend/app/api/v1/endpoints/`
5. Write tests in `backend/tests/`
6. Run tests: `pytest`

### Making Changes to Frontend

1. Create/modify components in `frontend/src/components/`
2. Update pages in `frontend/src/app/`
3. Add API hooks in `frontend/src/hooks/`
4. Update types in `frontend/src/types/`
5. Test your changes manually

## Useful Commands

### Backend

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Format code
black app/ tests/

# Type checking
mypy app/

# Create new migration
alembic revision --autogenerate -m "migration message"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type check
npm run type-check
```

### Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Execute command in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Stop all services
docker-compose down

# Remove all data
docker-compose down -v
```

## Project Structure

```
saas-optimizer/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Config & security
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   └── tests/        # Tests
├── frontend/         # Next.js frontend
│   └── src/
│       ├── app/      # Pages
│       ├── components/ # React components
│       ├── hooks/    # Custom hooks
│       └── lib/      # Utilities
└── infra/           # Infrastructure
    ├── docker/      # Dockerfiles
    └── terraform/   # IaC
```

## Common Issues

### Database Connection Error

Make sure PostgreSQL is running:
```bash
brew services list
brew services start postgresql@15
```

Update `DATABASE_URL` in `backend/.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/saas_optimizer
```

### Redis Connection Error

Make sure Redis is running:
```bash
brew services start redis
```

### Port Already in Use

If port 8000 or 3000 is already in use:
```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

### Module Not Found

Make sure you've installed all dependencies:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Next Steps

- Read the [API Documentation](http://localhost:8000/docs)
- Review the codebase
- Create your first subscription via the API or UI
- Explore the recommendation engine
- Add new features!

## Getting Help

- Check the README.md for more information
- Review the API documentation at `/docs`
- Look at existing code for examples
- Ask questions in team chat/issues
