#!/bin/bash

# WaferMaps Startup Script
# This script builds and starts the entire application stack

echo "🚀 Starting WaferMaps - Semiconductor Fab Defect Data Exploration Platform"
echo "=================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "📦 Building and starting services..."
echo ""

# Build and start all services
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ WaferMaps is starting up!"
echo ""
echo "📱 Access the application at:"
echo "   Frontend: http://localhost:13001"
echo "   Backend API: http://localhost:18080"
echo "   API Documentation: http://localhost:18080/docs"
echo "   MinIO Console: http://localhost:9003"
echo ""
echo "🔑 Default login credentials:"
echo "   Username: admin"
echo "   Password: password123"
echo ""
echo "📊 To generate synthetic data, run:"
echo "   docker-compose exec backend python scripts/generate_synthetic_data.py"
echo ""
echo "🛑 To stop the application, run:"
echo "   docker-compose down"
echo ""
echo "📋 To view logs, run:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "�� Happy exploring!"
