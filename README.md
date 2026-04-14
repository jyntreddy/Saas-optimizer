# SaaS Spend Optimizer(Building something huge)

A comprehensive platform for managing and optimizing SaaS subscriptions with AI-powered recommendations.

## 🚀 Features

### Core Features
- **Subscription Management**: Track all your SaaS subscriptions in one place
- **Cost Analytics**: Visualize spending patterns and trends
- **AI Recommendations**: Get intelligent suggestions for cost optimization
- **Automated Alerts**: Receive notifications for upcoming renewals
- **Duplicate Detection**: Identify overlapping services
- **Usage Analytics**: Monitor subscription utilization with real device data
- **SaaS Score**: Optimization score based on actual vs spending
- **Alternative Suggestions**: Find cheaper alternatives to current subscriptions
- **Team Usage Insights**: Track which team members use which tools

### 🖥️ Desktop Device Monitoring
**Complete device access with user permission** to power all features:
- **📱 App Usage Tracking**: Monitors 50+ desktop SaaS applications (Slack, Zoom, Notion, Figma, etc.)
- **🌐 Browser Activity**: Tracks 100+ web-based SaaS services across Chrome, Firefox, Edge, Safari
- **⏱️ Duration Tracking**: Records exact time spent in each application
- **📊 Usage Analytics**: Correlates actual usage with subscription costs
- **💡 Smart Insights**: Identifies unused subscriptions and underutilized tools
- **🎯 Cost Per Usage**: Calculate hourly cost for each service
- **🔄 Automated Sync**: Hourly background sync of usage data to dashboard

### 📧 Email & Receipt Capture
Multiple ways to automatically capture subscription receipts:
- **Chrome Extension**: Gmail API integration for direct receipt scanning ⭐ **[Fully Integrated!](INTEGRATION_COMPLETE.md)**
- **Desktop App**: Native device integration with full email access (macOS, Windows, Linux)
- **Gmail OAuth**: Backend OAuth flow for bulk historical receipt scanning
- **Email Forwarding**: Forward receipts to dedicated email for auto-processing

**Quick Start**: [5-Minute Setup Guide](QUICK_START_EXTENSION.md) | [Full Connection Guide](EXTENSION_DASHBOARD_CONNECTION.md)

## 🏗️ Architecture

### Backend (FastAPI)
- **API Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for session and celery tasks
- **Authentication**: JWT-based authentication
- **Task Queue**: Celery for background jobs
- **Migrations**: Alembic for database migrations

### Frontend (Streamlit)
- **Framework**: Streamlit (Python)
- **Port**: 8501
- **API Client**: Requests with CORS support
- **State Management**: Streamlit session state
- **Charts**: Plotly for interactive visualizations
- **Styling**: Custom CSS with Streamlit theming

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **IaC**: Terraform
- **Database**: AWS RDS PostgreSQL
- **Cache**: AWS ElastiCache Redis
- **Load Balancer**: nginx 

## 🛠️ Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (if running locally)
- Redis (if running locally)

### Development Setup

#### 1. Clone the repository

```bash
git clone <repository-url>
cd saas-optimizer
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API URL (default: http://localhost:8000)

# Start Streamlit server
streamlit run Home.py
```

The frontend will be available at `http://localhost:8501`

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Services:
- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- nginx: `http://localhost`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests

```bash
cd frontend
# Streamlit apps are typically tested through UI automation
# or by testing individual components/utilities
pytest tests/  # If unit tests are added
```

## 🚢 Deployment

### Using Docker Compose (Production)

```bash
docker-compose -f infra/docker-compose.prod.yml up -d
```

### Using Terraform (AWS)

```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan

# Apply infrastructure
terraform apply

# Destroy infrastructure (when needed)
terraform destroy
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{user_id}` - Get user by ID

### Subscriptions
- `GET /api/v1/subscriptions/` - List subscriptions
- `POST /api/v1/subscriptions/` - Create subscription
- `GET /api/v1/subscriptions/{id}` - Get subscription
- `PUT /api/v1/subscriptions/{id}` - Update subscription
- `DELETE /api/v1/subscriptions/{id}` - Delete subscription

### Analytics
- `GET /api/v1/analytics/spending-summary` - Get spending summary
- `GET /api/v1/analytics/spending-by-category` - Spending by category
- `GET /api/v1/analytics/trends` - Spending trends

### Recommendations
- `GET /api/v1/recommendations/cost-savings` - Get cost-saving recommendations
- `GET /api/v1/recommendations/duplicate-services` - Detect duplicates
- `GET /api/v1/recommendations/unused-subscriptions` - Find unused subscriptions

## 🔧 Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/saas_optimizer
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=True
STRIPE_API_KEY=your-stripe-key
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SaaS Optimizer
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI for the excellent backend framework
- Next.js for the powerful frontend framework
- The open-source community
