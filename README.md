# Portfolio Coach - AI-Powered Portfolio Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-20.0+-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)

> An intelligent portfolio management system that provides AI-powered analysis, real-time insights, and actionable recommendations for your investment portfolio.

## 🌟 Features

- **🤖 AI Chat Interface** - Interactive portfolio analysis with RAG and MCP integration
- **📊 Real-time Portfolio Tracking** - Live data from Upstox integration
- **📈 Advanced Analytics** - Risk assessment, sector analysis, and performance metrics
- **🎯 Actionable Recommendations** - AI-generated buy/sell/hold suggestions
- **📱 Modern Web Interface** - Responsive React frontend with professional UI
- **🐳 Containerized Deployment** - Docker-based microservices architecture
- **🔒 Secure & Scalable** - Enterprise-grade security and performance

## 🚀 Quick Start

### Prerequisites

- **Docker** (20.0+) and **Docker Compose**
- **Node.js** (18.0+) for local development
- **Python** (3.11+) for backend development
- **PostgreSQL** (13+) for database

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/portfolio-coach.git
   cd portfolio-coach
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Deploy with Docker**
   ```bash
   ./scripts/deploy_complete.sh
   ```

4. **Access the application**
   - **Frontend**: http://localhost:9855
   - **AI Chat**: http://localhost:9855/chat
   - **API**: http://localhost:9854/api/health

## 📖 Documentation

- **[System Architecture](docs/ARCHITECTURE.md)** - Technical architecture overview
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Development Guide](docs/DEVELOPMENT.md)** - Local development setup
- **[Tech Bible](docs/TECH_BIBLE.md)** - Core system design and methodology

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Flask Backend  │    │  PostgreSQL DB  │
│   (Port 9855)   │◄──►│   (Port 9854)   │◄──►│   (Port 9853)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   AI Services   │    │   Data Storage  │
│   (Static Files)│    │  (OpenAI, RAG)  │    │   (Portfolio)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

- **Frontend**: React-based SPA with Tailwind CSS
- **Backend**: Flask REST API with Python services
- **Database**: PostgreSQL for portfolio and user data
- **AI Engine**: OpenAI GPT integration with RAG/MCP
- **Containerization**: Docker Compose for orchestration

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:9853/portfolio_coach

# API Keys
OPENAI_API_KEY=your_openai_api_key
UPSTOX_ACCESS_TOKEN=your_upstox_token

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Port Configuration

- **Frontend**: 9855 (React + Nginx)
- **Backend API**: 9854 (Flask)
- **Database**: 9853 (PostgreSQL)

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd tests
python -m pytest test_*.py

# Frontend tests
cd frontend
npm test

# Integration tests
./tests/test_integration.sh
```

### Test Coverage

- **Unit Tests**: Core business logic and services
- **Integration Tests**: API endpoints and database operations
- **E2E Tests**: Full user workflows
- **Performance Tests**: Load testing and optimization

## 🚀 Deployment

### Production Deployment

1. **Prepare environment**
   ```bash
   ./scripts/deploy_complete.sh
   ```

2. **Monitor services**
   ```bash
   docker compose -f docker/docker-compose-simple.yml logs -f
   ```

3. **Scale if needed**
   ```bash
   docker compose -f docker/docker-compose-simple.yml up -d --scale portfolio_web=3
   ```

### Development Deployment

```bash
# Backend development
source venv/bin/activate
python run.py --mode web

# Frontend development
cd frontend
npm start
```

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Service health check |
| `/api/portfolio-summary` | GET | Portfolio overview |
| `/api/holdings` | GET | Current holdings |
| `/api/market-data` | GET | Live market data |
| `/api/chat` | POST | AI chat interface |
| `/api/chat/insights` | GET | Portfolio insights |

### Example API Usage

```bash
# Get portfolio summary
curl http://localhost:9855/api/portfolio-summary

# Chat with AI
curl -X POST http://localhost:9855/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main risks in my portfolio?"}'
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   ./tests/run_tests.sh
   ```
5. **Submit a pull request**

### Code Style

- **Python**: Follow PEP 8 with Black formatting
- **JavaScript**: ESLint with Prettier formatting
- **Documentation**: Markdown with consistent formatting

## 📈 Performance

### Benchmarks

- **API Response Time**: < 200ms average
- **Database Queries**: < 50ms average
- **AI Response Time**: < 2s average
- **Frontend Load Time**: < 1s average

### Monitoring

- **Health Checks**: Automated service monitoring
- **Logs**: Structured logging with ELK stack
- **Metrics**: Prometheus + Grafana dashboard
- **Alerts**: Automated alerting for issues

## 🔒 Security

### Security Features

- **API Authentication**: JWT-based authentication
- **Data Encryption**: AES-256 encryption at rest
- **HTTPS**: TLS 1.3 encryption in transit
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting and DDoS protection

### Security Best Practices

- Regular security audits
- Dependency vulnerability scanning
- Secure coding guidelines
- Incident response procedures

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT integration
- **Upstox** for market data APIs
- **React** and **Flask** communities
- **Docker** for containerization
- **PostgreSQL** for database

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/portfolio-coach/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/portfolio-coach/discussions)
- **Email**: support@portfolio-coach.com

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Mobile App** - React Native mobile application
- [ ] **Advanced Analytics** - Machine learning predictions
- [ ] **Social Features** - Portfolio sharing and comparison
- [ ] **Multi-Exchange** - Support for multiple exchanges
- [ ] **Automated Trading** - Algorithmic trading integration

### Version History

- **v1.0.0** - Initial release with core features
- **v1.1.0** - AI chat interface and markdown formatting
- **v1.2.0** - Enhanced analytics and reporting
- **v2.0.0** - Mobile app and advanced features (planned)

---

**Made with ❤️ by the Portfolio Coach Team**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/portfolio-coach.svg?style=social&label=Star)](https://github.com/yourusername/portfolio-coach)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/portfolio-coach.svg?style=social&label=Fork)](https://github.com/yourusername/portfolio-coach/fork)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/portfolio-coach.svg)](https://github.com/yourusername/portfolio-coach/issues) 