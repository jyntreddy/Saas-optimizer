@echo off
echo Starting SaaS Optimizer setup...

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Copy environment files if they don't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please update .env with your configuration
)

if not exist backend\.env (
    echo Creating backend\.env file...
    copy backend\.env.example backend\.env
    echo Please update backend\.env with your configuration
)

if not exist frontend\.env.local (
    echo Creating frontend\.env.local file...
    copy frontend\.env.local.example frontend\.env.local
    echo Please update frontend\.env.local with your configuration
)

REM Build and start containers
echo Building Docker containers...
cd infra
docker-compose up -d --build

echo.
echo SaaS Optimizer is starting up!
echo.
echo Services:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - nginx: http://localhost
echo.
echo Run 'docker-compose logs -f' to view logs
echo Run 'docker-compose down' to stop all services
