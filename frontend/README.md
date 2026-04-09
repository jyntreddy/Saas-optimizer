# SaaS Optimizer - Streamlit Frontend

Modern Streamlit-based frontend for the SaaS Optimizer platform.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run Streamlit
streamlit run Home.py
```

The app will be available at `http://localhost:8501`

### With Docker

```bash
cd infra
docker-compose up frontend
```

## 📁 Project Structure

```
frontend/
├── Home.py                 # Main entry point
├── pages/                  # Application pages
│   ├── 1_📊_Dashboard.py
│   ├── 2_📋_Subscriptions.py
│   ├── 3_📈_Analytics.py
│   └── 4_💡_Recommendations.py
├── components/             # Reusable components
│   └── sidebar.py
├── utils/                  # Utility functions
│   ├── api.py             # API client
│   ├── session.py         # Session management
│   └── formatting.py      # Formatting helpers
├── .streamlit/            # Streamlit config
│   └── config.toml
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
API_URL=http://localhost:8000
API_V1_PREFIX=/api/v1
```

### Streamlit Config

Configuration is in `.streamlit/config.toml`:

- **Server Port**: 8501
- **Theme**: Primary color #0ea5e9
- **CORS**: Disabled for local development

## 📡 API Communication

The frontend communicates with the FastAPI backend via HTTP requests:

- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api/v1`
- **Authentication**: JWT Bearer tokens

### API Client Usage

```python
from utils.api import login, get_subscriptions

# Login
result = login("user@example.com", "password")
token = result["access_token"]

# Get subscriptions
subscriptions = get_subscriptions(token)
```

## 🎨 Pages

### 🏠 Home
- Welcome page
- Feature overview
- Quick navigation

### 📊 Dashboard
- Key metrics
- Spending charts
- Recent subscriptions

### 📋 Subscriptions
- List all subscriptions
- Add new subscription
- Edit/Delete subscriptions
- Filter by status/billing cycle

### 📈 Analytics
- Detailed spending analysis
- Trends and charts
- Export data

### 💡 Recommendations
- AI-powered cost optimization
- Potential savings calculator
- Actionable suggestions

## 🔐 Authentication

Authentication is handled via the sidebar:

1. **Login Tab**: Existing users
2. **Register Tab**: New users

Session is maintained using `st.session_state`:
- `logged_in`: Boolean
- `token`: JWT access token
- `user`: User information

## 🎨 Styling

Custom CSS is applied for:
- Consistent color scheme
- Responsive layout
- Card-based UI elements
- Custom buttons

Primary color: `#0ea5e9` (blue)

## 📊 Data Visualization

Using Plotly for interactive charts:
- Pie charts (spending distribution)
- Bar charts (billing cycles)
- Line charts (trends)
- Tables (detailed data)

## 🧪 Testing

```bash
# Run the app in development mode
streamlit run Home.py --server.runOnSave=true
```

## 🚢 Deployment

### Docker

```bash
docker build -t saas-optimizer-frontend -f infra/docker/frontend/Dockerfile .
docker run -p 8501:8501 saas-optimizer-frontend
```

### Production

For production deployment:
1. Update `.env` with production API URL
2. Configure CORS in backend
3. Use proper authentication
4. Enable HTTPS

## 📝 Demo Credentials

```
Email: demo@example.com
Password: demo123
```

## 🤝 Contributing

1. Add new pages in `pages/` directory
2. Use naming convention: `N_Icon_Name.py`
3. Follow existing component patterns
4. Update this README

## 📚 Dependencies

- `streamlit` - Web framework
- `requests` - HTTP client
- `pandas` - Data manipulation
- `plotly` - Interactive charts
- `python-dotenv` - Environment variables

## 🔗 Links

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501
