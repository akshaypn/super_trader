#!/bin/bash

# Portfolio Coach - Airflow Deployment Script
# This script deploys the complete Airflow-based portfolio coaching system

set -e

echo "🚀 Portfolio Coach - Airflow Deployment"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from env.example"
    echo "cp env.example .env"
    echo "Then edit .env with your credentials:"
    echo "- UPSTOX_ACCESS_TOKEN"
    echo "- OPENAI_API_KEY"
    echo "- SMTP credentials for email delivery"
    exit 1
fi

echo "✅ Environment check passed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p dags logs plugins data

# Build and start services
echo "🐳 Starting Docker services..."
docker-compose -f docker/docker-compose.yml down --remove-orphans
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose -f docker/docker-compose.yml exec -T postgres pg_isready -U portfolio_user -d portfolio_coach > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Airflow webserver
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Airflow webserver is ready"
else
    echo "⚠️  Airflow webserver may still be starting..."
fi

# Check portfolio web interface
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Portfolio web interface is ready"
else
    echo "⚠️  Portfolio web interface may still be starting..."
fi

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📊 Access Points:"
echo "  - Airflow UI: http://localhost:8080 (admin/admin)"
echo "  - Portfolio Web: http://localhost:5000"
echo "  - Database: localhost:5434"
echo ""
echo "📧 Email Configuration:"
echo "  - Reports will be sent to: akshay.nambiar7@gmail.com"
echo "  - Update SMTP credentials in .env if needed"
echo ""
echo "📅 Daily Schedule:"
echo "  - Pipeline runs at 08:45 IST on weekdays"
echo "  - DAG: portfolio_coach_daily"
echo ""
echo "🔍 Monitoring:"
echo "  - View logs: docker-compose -f docker/docker-compose.yml logs -f"
echo "  - Check DAG status: http://localhost:8080"
echo ""
echo "🚀 Your Portfolio Coach is now running with complete Airflow automation!" 