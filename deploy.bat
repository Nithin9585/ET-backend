@echo off
REM Production deployment script for Windows

echo 🚀 Starting production deployment...

REM Stop existing containers
echo 📦 Stopping existing containers...
docker-compose down

REM Build new image
echo 🔨 Building new Docker image...
docker-compose build --no-cache

REM Start services
echo ▶️ Starting services...
docker-compose up -d

REM Check health
echo 🏥 Checking service health...
timeout /t 10
curl -f http://localhost:8000/health

if %errorlevel% equ 0 (
    echo ✅ Deployment successful!
    echo 🌐 API is available at: http://localhost:8000
    echo 📖 Documentation at: http://localhost:8000/docs
) else (
    echo ❌ Deployment failed - health check failed
    docker-compose logs
    exit /b 1
)
