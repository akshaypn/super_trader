#!/bin/bash

# Portfolio Coach Docker Integration Test Script
# This script tests the complete Docker setup including backend, frontend, and database

set -e

echo "🚀 Starting Portfolio Coach Docker Integration Tests..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Test 1: Check if containers are running
echo -e "\n${YELLOW}Test 1: Container Status${NC}"
containers_running=$(docker compose -f docker-compose-simple.yml ps -q | wc -l)
if [ $containers_running -eq 3 ]; then
    print_status 0 "All 3 containers are running"
else
    print_status 1 "Expected 3 containers running, found $containers_running"
fi

# Test 2: Database connectivity
echo -e "\n${YELLOW}Test 2: Database Connectivity${NC}"
db_test=$(docker exec docker-postgres-1 psql -U portfolio_user -d portfolio_coach -c "SELECT COUNT(*) FROM holdings;" 2>/dev/null | grep -E '^[[:space:]]*[0-9]+[[:space:]]*$' | tr -d ' ' || echo "failed")
if [ "$db_test" != "failed" ] && [ "$db_test" -ge 0 ] 2>/dev/null; then
    print_status 0 "Database connection successful (holdings table accessible)"
else
    print_status 1 "Database connection failed"
fi

# Test 3: Backend API health
echo -e "\n${YELLOW}Test 3: Backend API Health${NC}"
health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health)
if [ "$health_response" = "200" ]; then
    print_status 0 "Backend API health check passed"
else
    print_status 1 "Backend API health check failed (HTTP $health_response)"
fi

# Test 4: Frontend health
echo -e "\n${YELLOW}Test 4: Frontend Health${NC}"
frontend_health=$(curl -s http://localhost:3001/health)
if [ "$frontend_health" = "healthy" ]; then
    print_status 0 "Frontend health check passed"
else
    print_status 1 "Frontend health check failed"
fi

# Test 5: Frontend to Backend proxy
echo -e "\n${YELLOW}Test 5: Frontend to Backend Proxy${NC}"
proxy_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/health)
if [ "$proxy_response" = "200" ]; then
    print_status 0 "Frontend to backend proxy working"
else
    print_status 1 "Frontend to backend proxy failed (HTTP $proxy_response)"
fi

# Test 6: Portfolio Summary API
echo -e "\n${YELLOW}Test 6: Portfolio Summary API${NC}"
portfolio_response=$(curl -s http://localhost:5000/api/portfolio-summary | jq -r '.total_value' 2>/dev/null)
if [ "$portfolio_response" != "null" ] && [ "$portfolio_response" != "" ]; then
    print_status 0 "Portfolio summary API working (Total value: $portfolio_response)"
else
    print_status 1 "Portfolio summary API failed"
fi

# Test 7: Holdings API
echo -e "\n${YELLOW}Test 7: Holdings API${NC}"
holdings_count=$(curl -s http://localhost:5000/api/holdings | jq -r '.holdings | length' 2>/dev/null)
if [ "$holdings_count" != "null" ] && [ "$holdings_count" != "" ]; then
    print_status 0 "Holdings API working ($holdings_count holdings found)"
else
    print_status 1 "Holdings API failed"
fi

# Test 8: Settings API
echo -e "\n${YELLOW}Test 8: Settings API${NC}"
settings_response=$(curl -s http://localhost:5000/api/settings | jq -r '.riskProfile' 2>/dev/null)
if [ "$settings_response" != "null" ] && [ "$settings_response" != "" ]; then
    print_status 0 "Settings API working (Risk profile: $settings_response)"
else
    print_status 1 "Settings API failed"
fi

# Test 9: Frontend React App
echo -e "\n${YELLOW}Test 9: Frontend React App${NC}"
frontend_html=$(curl -s http://localhost:3001/ | grep -o "Portfolio Coach" | head -1)
if [ "$frontend_html" = "Portfolio Coach" ]; then
    print_status 0 "Frontend React app serving correctly"
else
    print_status 1 "Frontend React app not serving correctly"
fi

# Test 10: Database Schema
echo -e "\n${YELLOW}Test 10: Database Schema${NC}"
table_count=$(docker exec docker-postgres-1 psql -U portfolio_user -d portfolio_coach -c "\dt" 2>/dev/null | grep -c "table" || echo "0")
if [ "$table_count" -ge 10 ]; then
    print_status 0 "Database schema properly initialized ($table_count tables found)"
else
    print_status 1 "Database schema incomplete ($table_count tables found)"
fi

echo -e "\n${GREEN}🎉 All Integration Tests Completed Successfully!${NC}"
echo -e "\n${YELLOW}Access Points:${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:3001${NC}"
echo -e "  Backend API: ${GREEN}http://localhost:5000${NC}"
echo -e "  Database: ${GREEN}localhost:5434${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. Open http://localhost:3001 in your browser"
echo -e "  2. Configure your Upstox API token in the settings"
echo -e "  3. Set up your OpenAI API key for AI recommendations"
echo -e "  4. Start using the Portfolio Coach system!" 