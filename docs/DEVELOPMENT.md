# Portfolio Coach - Development Guide

## Overview

This guide provides comprehensive instructions for setting up and contributing to the Portfolio Coach development environment.

## Prerequisites

### Required Software

- **Python 3.11+**
- **Node.js 18.0+**
- **Docker & Docker Compose**
- **PostgreSQL 13+**
- **Git**

### Recommended Tools

- **VS Code** with extensions:
  - Python
  - JavaScript/TypeScript
  - Docker
  - GitLens
  - Prettier
  - ESLint

## Development Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/portfolio-coach.git
cd portfolio-coach
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Database Setup

```bash
# Using Docker
docker run --name portfolio-postgres \
  -e POSTGRES_DB=portfolio_coach \
  -e POSTGRES_USER=portfolio_user \
  -e POSTGRES_PASSWORD=portfolio_password \
  -p 9853:5432 \
  -d postgres:13

# Or using local PostgreSQL
createdb portfolio_coach
```

## Running the Application

### Development Mode

#### Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask development server
python run.py --mode web
```

#### Frontend

```bash
cd frontend
npm start
```

#### Docker Development

```bash
# Start all services
docker compose -f docker/docker-compose-simple.yml up -d

# View logs
docker compose -f docker/docker-compose-simple.yml logs -f
```

### Production Mode

```bash
# Deploy with production configuration
./scripts/deploy_complete.sh
```

## Project Structure

```
portfolio-coach/
├── src/                    # Backend source code
│   ├── api/               # API endpoints
│   ├── services/          # Business logic services
│   ├── database/          # Database models and migrations
│   ├── utils/             # Utility functions
│   └── web/               # Flask application
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context
│   │   └── utils/         # Frontend utilities
│   └── public/            # Static assets
├── docker/                # Docker configuration
├── docs/                  # Documentation
├── scripts/               # Deployment and utility scripts
├── tests/                 # Test files
└── requirements.txt       # Python dependencies
```

## Code Style & Standards

### Python (Backend)

#### Code Style

- **Formatter**: Black
- **Linter**: Flake8
- **Type Checking**: mypy
- **Import Sorting**: isort

#### Configuration

```ini
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3
```

#### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### JavaScript (Frontend)

#### Code Style

- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Checking**: TypeScript (optional)

#### Configuration

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

## Testing

### Backend Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_portfolio_service.py

# Run with verbose output
python -m pytest tests/ -v
```

### Frontend Testing

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- --testNamePattern="Portfolio"
```

### Integration Testing

```bash
# Run integration tests
./tests/test_integration.sh

# Test API endpoints
curl -X GET http://localhost:9854/api/health
curl -X GET http://localhost:9855/api/portfolio-summary
```

## Database Management

### Migrations

```bash
# Create new migration
flask db migrate -m "Add user preferences table"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Seed Data

```bash
# Load sample data
python scripts/seed_data.py

# Reset database
python scripts/reset_db.py
```

## API Development

### Adding New Endpoints

1. **Create endpoint in `src/web/app.py`**

```python
@app.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    try:
        # Business logic
        result = some_service.process()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

2. **Add service in `src/services/`**

```python
class NewService:
    def __init__(self):
        self.db = Database()
    
    def process(self):
        # Implementation
        pass
```

3. **Add tests in `tests/`**

```python
def test_new_endpoint():
    response = client.get('/api/new-endpoint')
    assert response.status_code == 200
    assert 'data' in response.json
```

### API Documentation

Update API documentation in `docs/API.md` when adding new endpoints.

## Frontend Development

### Adding New Components

1. **Create component in `frontend/src/components/`**

```jsx
import React from 'react';

const NewComponent = ({ data }) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold">{data.title}</h2>
      <p className="text-gray-600">{data.description}</p>
    </div>
  );
};

export default NewComponent;
```

2. **Add to page in `frontend/src/pages/`**

```jsx
import NewComponent from '../components/NewComponent';

const NewPage = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Fetch data
    fetchData().then(setData);
  }, []);

  return (
    <div className="container mx-auto px-4">
      <NewComponent data={data} />
    </div>
  );
};
```

### State Management

Use React Context for global state:

```jsx
// frontend/src/context/AppContext.js
import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
```

## Debugging

### Backend Debugging

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Flask debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### Frontend Debugging

```javascript
// Browser console
console.log('Debug info:', data);

// React DevTools
// Install React Developer Tools browser extension

// Debug with VS Code
// Add breakpoints in VS Code debugger
```

### Docker Debugging

```bash
# View container logs
docker logs <container_name>

# Execute commands in container
docker exec -it <container_name> /bin/bash

# View container resources
docker stats
```

## Performance Optimization

### Backend Optimization

1. **Database Queries**
   - Use indexes
   - Optimize queries
   - Use connection pooling

2. **Caching**
   - Redis for session data
   - In-memory caching
   - CDN for static assets

3. **Async Processing**
   - Background tasks
   - Message queues
   - Parallel processing

### Frontend Optimization

1. **Code Splitting**
   - Lazy loading
   - Dynamic imports
   - Route-based splitting

2. **Bundle Optimization**
   - Tree shaking
   - Minification
   - Compression

3. **Performance Monitoring**
   - Lighthouse audits
   - Core Web Vitals
   - Bundle analysis

## Security

### Backend Security

1. **Input Validation**
   - Sanitize all inputs
   - Use validation libraries
   - Prevent SQL injection

2. **Authentication**
   - JWT tokens
   - Password hashing
   - Rate limiting

3. **Data Protection**
   - Encryption at rest
   - HTTPS only
   - Secure headers

### Frontend Security

1. **XSS Prevention**
   - Sanitize user inputs
   - Use Content Security Policy
   - Escape HTML content

2. **CSRF Protection**
   - CSRF tokens
   - SameSite cookies
   - Secure headers

## Deployment

### Local Deployment

```bash
# Build and run with Docker
docker compose -f docker/docker-compose-simple.yml up --build

# Or run services individually
python run.py --mode web &
cd frontend && npm start
```

### Production Deployment

```bash
# Deploy to production
./scripts/deploy_complete.sh

# Monitor deployment
docker compose -f docker/docker-compose-simple.yml logs -f
```

## Contributing

### Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make changes**
   - Follow coding standards
   - Add tests
   - Update documentation

3. **Run tests**
   ```bash
   # Backend tests
   python -m pytest tests/
   
   # Frontend tests
   cd frontend && npm test
   ```

4. **Submit pull request**
   - Clear description
   - Link to issues
   - Include screenshots if UI changes

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Error handling implemented

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check port usage
   lsof -i :9855
   
   # Kill process using port
   kill -9 <PID>
   ```

2. **Database connection issues**
   ```bash
   # Check database status
   docker logs portfolio-postgres
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Frontend build issues**
   ```bash
   # Clear cache
   rm -rf frontend/node_modules
   npm install
   
   # Rebuild
   npm run build
   ```

### Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions
- **Support**: Contact development team

## Resources

### Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tools

- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - Database management
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code](https://code.visualstudio.com/) - Code editor

### Learning Resources

- [Python Best Practices](https://realpython.com/python-best-practices/)
- [React Best Practices](https://reactjs.org/docs/hooks-rules.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [API Design Best Practices](https://restfulapi.net/) 