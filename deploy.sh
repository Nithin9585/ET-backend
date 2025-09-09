#!/bin/bash
# Production deployment script

echo "🚀 Starting production deployment..."

# Stop existing containers
echo "📦 Stopping existing containers..."
docker-compose down

# Build new image
echo "🔨 Building new Docker image..."
docker-compose build --no-cache

# Start services
echo "▶️ Starting services..."
docker-compose up -d

# Check health
echo "🏥 Checking service health..."
sleep 10
curl -f http://localhost:8000/health

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 API is available at: http://localhost:8000"
    echo "📖 Documentation at: http://localhost:8000/docs"
else
    echo "❌ Deployment failed - health check failed"
    docker-compose logs
    exit 1
fi
