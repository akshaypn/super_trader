#!/bin/bash

# Portfolio Coach Complete System Deployment Script
# This script deploys the entire system including frontend, backend, and AI chat interface
# Updated for new port configuration (9853, 9854, 9855) and API key management

set -e

echo "🚀 Starting Portfolio Coach Complete System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Function to prompt for API key
prompt_for_api_key() {
    echo
    print_warning "OpenAI API key not found in .env file"
    echo
    echo "To enable AI chat functionality, you need an OpenAI API key."
    echo "You can get one from: https://platform.openai.com/account/api-keys"
    echo
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    
    if [ -n "$api_key" ]; then
        echo "OPENAI_API_KEY=$api_key" >> .env
        print_success "OpenAI API key added to .env file"
    else
        print_warning "Skipping OpenAI API key setup. AI chat will not be available."
    fi
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_success ".env file created from template"
    else
        print_error ".env file not found and no template available."
        print_status "Please create .env file with the required environment variables:"
        echo "  - UPSTOX_ACCESS_TOKEN"
        echo "  - OPENAI_API_KEY"
        echo "  - SMTP_HOST"
        echo "  - SMTP_PORT"
        echo "  - SMTP_USERNAME"
        echo "  - SMTP_PASSWORD"
        echo "  - AIRFLOW_FERNET_KEY"
        echo "  - AIRFLOW_SECRET_KEY"
        exit 1
    fi
fi

# Check for OpenAI API key
if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=test-key" .env; then
    prompt_for_api_key
else
    print_success "OpenAI API key found in .env file"
fi

print_success ".env file configured"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p dags logs plugins data frontend/build

# Generate Airflow keys if not provided
if [ -z "$AIRFLOW_FERNET_KEY" ]; then
    print_warning "AIRFLOW_FERNET_KEY not set, generating one..."
    export AIRFLOW_FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    echo "AIRFLOW_FERNET_KEY=$AIRFLOW_FERNET_KEY" >> .env
fi

if [ -z "$AIRFLOW_SECRET_KEY" ]; then
    print_warning "AIRFLOW_SECRET_KEY not set, generating one..."
    export AIRFLOW_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    echo "AIRFLOW_SECRET_KEY=$AIRFLOW_SECRET_KEY" >> .env
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker compose -f docker/docker-compose.yml down --remove-orphans || true
docker compose -f docker/docker-compose-simple.yml down --remove-orphans || true

# Build and start services
print_status "Building and starting services..."
docker compose -f docker/docker-compose-simple.yml up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."

# Wait for PostgreSQL
print_status "Waiting for PostgreSQL..."
until docker compose -f docker/docker-compose-simple.yml exec -T postgres pg_isready -U portfolio_user -d portfolio_coach; do
    sleep 5
done
print_success "PostgreSQL is ready"

# Wait for portfolio web service
print_status "Waiting for portfolio web service..."
until curl -f http://localhost:9854/api/health > /dev/null 2>&1; do
    sleep 5
done
print_success "Portfolio web service is ready"

# Wait for frontend
print_status "Waiting for frontend..."
until curl -f http://localhost:9855/health > /dev/null 2>&1; do
    sleep 5
done
print_success "Frontend is ready"

# Test chat functionality
print_status "Testing chat functionality..."
if curl -s http://localhost:9855/api/chat/insights > /dev/null 2>&1; then
    print_success "Chat insights API is working"
else
    print_warning "Chat insights API test failed (this might be normal if no portfolio data)"
fi

# Display service information
echo ""
print_success "🎉 Portfolio Coach Complete System is deployed successfully!"
echo ""
echo "📊 Service URLs:"
echo "  - Frontend Dashboard: http://localhost:9855"
echo "  - Backend API: http://localhost:9854"
echo "  - PostgreSQL: localhost:9853"
echo ""
echo "🤖 AI Chat Interface:"
echo "  - Chat Interface: http://localhost:9855/chat"
echo "  - Portfolio Insights: http://localhost:9855/api/chat/insights"
echo ""
echo "📈 Features Available:"
echo "  - Real-time portfolio tracking from Upstox"
echo "  - AI-powered chat interface with RAG and MCP"
echo "  - Portfolio analysis and risk assessment"
echo "  - Interactive charts and visualizations"
echo "  - Automated recommendations and alerts"
echo ""
echo "🛠️ Management Commands:"
echo "  - View logs: docker compose -f docker/docker-compose-simple.yml logs -f"
echo "  - Stop services: docker compose -f docker/docker-compose-simple.yml down"
echo "  - Restart services: docker compose -f docker/docker-compose-simple.yml restart"
echo "  - Update services: docker compose -f docker/docker-compose-simple.yml up -d --build"
echo ""
echo "🔐 Configuration Status:"
if grep -q "OPENAI_API_KEY=test-key" .env 2>/dev/null || ! grep -q "OPENAI_API_KEY=" .env 2>/dev/null; then
    echo "  ⚠️  OpenAI API key not configured - AI chat will not work"
    echo "  💡 Add your OpenAI API key to .env file for full functionality"
else
    echo "  ✅ OpenAI API key configured - AI chat is available"
fi
echo ""
print_success "Deployment completed successfully! 🚀" 