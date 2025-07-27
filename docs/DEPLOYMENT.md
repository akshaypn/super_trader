# Portfolio Coach - Deployment Guide

## Overview

This guide covers deploying Portfolio Coach in various environments, from local development to production.

## Prerequisites

- **Docker** (20.0+) and **Docker Compose**
- **Git** for version control
- **SSH access** to deployment servers
- **Domain name** (for production)

## Local Development Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/portfolio-coach.git
cd portfolio-coach

# Deploy with automated script
./scripts/deploy_complete.sh
```

### Manual Deployment

```bash
# 1. Set up environment
cp env.example .env
# Edit .env with your configuration

# 2. Start services
docker compose -f docker/docker-compose-simple.yml up -d

# 3. Verify deployment
curl http://localhost:9855/health
curl http://localhost:9854/api/health
```

## Staging Deployment

### Environment Setup

```bash
# Create staging environment
mkdir -p staging
cd staging

# Clone repository
git clone https://github.com/yourusername/portfolio-coach.git
cd portfolio-coach

# Create staging configuration
cp env.example .env.staging
```

### Staging Configuration

```bash
# .env.staging
DATABASE_URL=postgresql://user:pass@staging-db:5432/portfolio_coach
OPENAI_API_KEY=your_openai_api_key
UPSTOX_ACCESS_TOKEN=your_upstox_token
ENVIRONMENT=staging
DEBUG=false
```

### Deploy to Staging

```bash
# Deploy staging environment
ENVIRONMENT=staging ./scripts/deploy_complete.sh

# Monitor deployment
docker compose -f docker/docker-compose-simple.yml logs -f
```

## Production Deployment

### Server Requirements

- **CPU**: 4+ cores
- **RAM**: 8GB+ 
- **Storage**: 100GB+ SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Network**: Stable internet connection

### Production Setup

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deployment user
sudo useradd -m -s /bin/bash portfolio
sudo usermod -aG docker portfolio
```

#### 2. Application Deployment

```bash
# Switch to deployment user
sudo su - portfolio

# Clone repository
git clone https://github.com/yourusername/portfolio-coach.git
cd portfolio-coach

# Create production configuration
cp env.example .env.production
```

#### 3. Production Configuration

```bash
# .env.production
DATABASE_URL=postgresql://portfolio_user:secure_password@localhost:9853/portfolio_coach
OPENAI_API_KEY=your_production_openai_key
UPSTOX_ACCESS_TOKEN=your_production_upstox_token
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_secure_secret_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

#### 4. Deploy Production

```bash
# Deploy with production configuration
ENVIRONMENT=production ./scripts/deploy_complete.sh

# Set up monitoring
docker compose -f docker/docker-compose-simple.yml up -d
```

### SSL/HTTPS Setup

#### Using Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Using Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/portfolio-coach
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:9855;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:9854;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Docker Deployment

### Docker Compose Configuration

```yaml
# docker/docker-compose-production.yml
version: '3.8'

services:
  frontend:
    image: portfolio-frontend:latest
    ports:
      - "9855:80"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    depends_on:
      - backend

  backend:
    image: portfolio-backend:latest
    ports:
      - "9854:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@database:5432/portfolio_coach
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - UPSTOX_ACCESS_TOKEN=${UPSTOX_ACCESS_TOKEN}
    restart: unless-stopped
    depends_on:
      - database

  database:
    image: postgres:13
    ports:
      - "9853:5432"
    environment:
      - POSTGRES_DB=portfolio_coach
      - POSTGRES_USER=portfolio_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deployment/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Build and Deploy

```bash
# Build production images
docker build -t portfolio-backend:latest .
docker build -t portfolio-frontend:latest frontend/

# Deploy with production compose
docker compose -f docker/docker-compose-production.yml up -d

# Monitor deployment
docker compose -f docker/docker-compose-production.yml logs -f
```

## Kubernetes Deployment

### Namespace Setup

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: portfolio-coach
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: portfolio-config
  namespace: portfolio-coach
data:
  DATABASE_URL: "postgresql://user:pass@postgres-service:5432/portfolio_coach"
  ENVIRONMENT: "production"
```

### Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: portfolio-secrets
  namespace: portfolio-coach
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded-key>
  UPSTOX_ACCESS_TOKEN: <base64-encoded-token>
  DB_PASSWORD: <base64-encoded-password>
```

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: portfolio-backend
  namespace: portfolio-coach
spec:
  replicas: 3
  selector:
    matchLabels:
      app: portfolio-backend
  template:
    metadata:
      labels:
        app: portfolio-backend
    spec:
      containers:
      - name: backend
        image: portfolio-backend:latest
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: portfolio-config
        - secretRef:
            name: portfolio-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: portfolio-backend-service
  namespace: portfolio-coach
spec:
  selector:
    app: portfolio-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: portfolio-ingress
  namespace: portfolio-coach
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: portfolio-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: portfolio-frontend-service
            port:
              number: 80
      - path: /api/
        pathType: Prefix
        backend:
          service:
            name: portfolio-backend-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Monitor deployment
kubectl get pods -n portfolio-coach
kubectl logs -f deployment/portfolio-backend -n portfolio-coach
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Portfolio Coach

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm install
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t portfolio-backend:${{ github.sha }} .
        docker build -t portfolio-frontend:${{ github.sha }} frontend/
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag portfolio-backend:${{ github.sha }} your-registry/portfolio-backend:latest
        docker tag portfolio-frontend:${{ github.sha }} your-registry/portfolio-frontend:latest
        docker push your-registry/portfolio-backend:latest
        docker push your-registry/portfolio-frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        ssh ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }} << 'EOF'
          cd /opt/portfolio-coach
          git pull origin main
          docker pull your-registry/portfolio-backend:latest
          docker pull your-registry/portfolio-frontend:latest
          docker compose -f docker/docker-compose-production.yml up -d
        EOF
```

## Monitoring and Logging

### Health Checks

```bash
# Application health
curl http://localhost:9855/health
curl http://localhost:9854/api/health

# Database health
docker exec portfolio-postgres pg_isready -U portfolio_user

# Service status
docker compose -f docker/docker-compose-simple.yml ps
```

### Logging

```bash
# View application logs
docker compose -f docker/docker-compose-simple.yml logs -f

# View specific service logs
docker compose -f docker/docker-compose-simple.yml logs -f backend

# Export logs
docker compose -f docker/docker-compose-simple.yml logs > logs.txt
```

### Monitoring Setup

```yaml
# docker/monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana_data:
```

## Backup and Recovery

### Database Backup

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec portfolio-postgres pg_dump -U portfolio_user portfolio_coach > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/portfolio-coach/backup.sh
```

### Recovery

```bash
# Restore from backup
gunzip -c backup_20250101_020000.sql.gz | docker exec -i portfolio-postgres psql -U portfolio_user -d portfolio_coach
```

## Security Considerations

### Environment Variables

- Store sensitive data in environment variables
- Use secrets management in production
- Rotate API keys regularly
- Use strong passwords for databases

### Network Security

- Use HTTPS in production
- Configure firewall rules
- Implement rate limiting
- Use VPN for server access

### Application Security

- Keep dependencies updated
- Scan for vulnerabilities
- Implement proper authentication
- Use secure headers

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check port usage
   sudo netstat -tulpn | grep :9855
   
   # Kill conflicting process
   sudo kill -9 <PID>
   ```

2. **Database connection issues**
   ```bash
   # Check database status
   docker logs portfolio-postgres
   
   # Reset database
   docker compose -f docker/docker-compose-simple.yml down -v
   docker compose -f docker/docker-compose-simple.yml up -d
   ```

3. **Memory issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Increase memory limits
   # Edit docker-compose.yml
   ```

### Performance Optimization

1. **Database optimization**
   - Add indexes
   - Optimize queries
   - Use connection pooling

2. **Application optimization**
   - Enable caching
   - Use CDN for static assets
   - Implement load balancing

3. **Infrastructure optimization**
   - Use SSD storage
   - Optimize network settings
   - Monitor resource usage

## Support

For deployment issues:

- **Documentation**: Check this guide and other docs
- **Logs**: Review application and system logs
- **Community**: Use GitHub Discussions
- **Support**: Contact the development team 