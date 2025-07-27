# Portfolio Coach Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2.0+
- At least 4GB RAM available
- Ports 3001, 5000, and 5434 available

### 1. Clone and Setup
```bash
git clone <repository-url>
cd super-trader-clean
```

### 2. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:
```bash
UPSTOX_ACCESS_TOKEN=your_real_upstox_token
OPENAI_API_KEY=your_real_openai_key
```

### 3. Build and Deploy
```bash
cd docker
docker compose -f docker-compose-simple.yml build
docker compose -f docker-compose-simple.yml up -d
```

### 4. Verify Deployment
```bash
# Run integration tests
./test_integration.sh

# Or manually check
curl http://localhost:5000/api/health
curl http://localhost:3001/health
```

### 5. Access the Application
- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:5000
- **Database:** localhost:5434

## Production Deployment

### 1. Use Full Stack (with Airflow)
```bash
# Build with Airflow support
docker compose build
docker compose up -d
```

### 2. Configure SSL (Recommended)
```bash
# Add SSL certificates
mkdir -p ssl
# Place your certificates in ssl/ directory
```

### 3. Set Up Monitoring
```bash
# Add monitoring containers
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

## Management Commands

### Start Services
```bash
docker compose -f docker-compose-simple.yml up -d
```

### Stop Services
```bash
docker compose -f docker-compose-simple.yml down
```

### View Logs
```bash
# All services
docker compose -f docker-compose-simple.yml logs

# Specific service
docker compose -f docker-compose-simple.yml logs portfolio_web
```

### Restart Services
```bash
docker compose -f docker-compose-simple.yml restart
```

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose -f docker-compose-simple.yml down
docker compose -f docker-compose-simple.yml build --no-cache
docker compose -f docker-compose-simple.yml up -d
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3001
lsof -i :5000
lsof -i :5434

# Kill the process or change ports in docker-compose-simple.yml
```

#### 2. Database Connection Issues
```bash
# Check database container
docker compose -f docker-compose-simple.yml logs postgres

# Test database connection
docker exec docker-postgres-1 psql -U portfolio_user -d portfolio_coach -c "SELECT 1;"
```

#### 3. API Token Issues
```bash
# Check backend logs for API errors
docker compose -f docker-compose-simple.yml logs portfolio_web

# Verify environment variables
docker exec docker-portfolio_web-1 env | grep -E "(UPSTOX|OPENAI)"
```

#### 4. Frontend Not Loading
```bash
# Check frontend logs
docker compose -f docker-compose-simple.yml logs portfolio_frontend

# Test nginx configuration
docker exec docker-portfolio_frontend-1 nginx -t
```

### Reset Everything
```bash
# Stop and remove all containers
docker compose -f docker-compose-simple.yml down -v

# Remove all images
docker rmi docker-portfolio_web docker-portfolio_frontend

# Start fresh
docker compose -f docker-compose-simple.yml up -d
```

## Performance Tuning

### Memory Limits
```yaml
# Add to docker-compose-simple.yml
services:
  portfolio_web:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Database Optimization
```sql
-- Run in database container
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
```

## Security Considerations

### 1. Use Secrets for Sensitive Data
```bash
# Create Docker secrets
echo "your_upstox_token" | docker secret create upstox_token -
echo "your_openai_key" | docker secret create openai_key -
```

### 2. Network Security
```yaml
# Use internal networks
networks:
  portfolio_internal:
    internal: true
```

### 3. Regular Updates
```bash
# Update base images
docker compose -f docker-compose-simple.yml pull
docker compose -f docker-compose-simple.yml up -d
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker exec docker-postgres-1 pg_dump -U portfolio_user portfolio_coach > backup.sql

# Restore backup
docker exec -i docker-postgres-1 psql -U portfolio_user portfolio_coach < backup.sql
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v docker_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v docker_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## Support

For issues and questions:
1. Check the logs: `docker compose -f docker-compose-simple.yml logs`
2. Run the test script: `./test_integration.sh`
3. Review the test results: `cat DOCKER_TEST_RESULTS.md`
4. Check the main documentation in the project root 