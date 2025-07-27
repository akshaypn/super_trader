# Contributing to Portfolio Coach

Thank you for your interest in contributing to Portfolio Coach! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18.0+**
- **Docker & Docker Compose**
- **Git**

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/portfolio-coach.git
   cd portfolio-coach
   ```

2. **Set up the development environment**
   ```bash
   # Backend setup
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend setup
   cd frontend
   npm install
   cd ..
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start the application**
   ```bash
   # Start all services
   docker compose -f docker/docker-compose-simple.yml up -d
   
   # Or run individually
   python run.py --mode web &
   cd frontend && npm start
   ```

## Development Workflow

### Branch Naming Convention

Use descriptive branch names with prefixes:

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

Examples:
- `feature/ai-chat-interface`
- `bugfix/portfolio-calculation-error`
- `docs/api-documentation-update`

### Commit Message Format

Follow the conventional commits format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(chat): add markdown formatting support

fix(api): resolve portfolio calculation error

docs: update API documentation

test: add integration tests for chat service
```

## Code Style

### Python (Backend)

#### Code Formatting

We use **Black** for code formatting and **isort** for import sorting.

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Format code manually
black src/
isort src/
```

#### Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

Example:
```python
from typing import Dict, List, Optional
from datetime import datetime

def calculate_portfolio_risk(
    holdings: List[Dict[str, float]], 
    market_data: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate portfolio risk metrics.
    
    Args:
        holdings: List of portfolio holdings
        market_data: Current market data
        
    Returns:
        Dictionary containing risk metrics
    """
    # Implementation
    pass
```

### JavaScript (Frontend)

#### Code Formatting

We use **Prettier** for code formatting and **ESLint** for linting.

```bash
# Format code
cd frontend
npm run format

# Lint code
npm run lint
```

#### Code Style Guidelines

- Use functional components with hooks
- Follow React best practices
- Use TypeScript for type safety (optional)
- Write meaningful component and variable names
- Use proper error handling

Example:
```jsx
import React, { useState, useEffect } from 'react';

interface PortfolioProps {
  data: PortfolioData;
  onUpdate: (data: PortfolioData) => void;
}

const Portfolio: React.FC<PortfolioProps> = ({ data, onUpdate }) => {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Component logic
  }, [data]);

  return (
    <div className="portfolio-container">
      {/* Component JSX */}
    </div>
  );
};

export default Portfolio;
```

## Testing

### Backend Testing

#### Running Tests

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

#### Writing Tests

Follow these guidelines:

- Write tests for all new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Use fixtures for common test data

Example:
```python
import pytest
from unittest.mock import Mock, patch
from src.services.portfolio_service import PortfolioService

class TestPortfolioService:
    @pytest.fixture
    def portfolio_service(self):
        return PortfolioService()
    
    def test_calculate_portfolio_value_success(self, portfolio_service):
        """Test successful portfolio value calculation."""
        holdings = [{"symbol": "AAPL", "quantity": 10, "price": 150.0}]
        expected_value = 1500.0
        
        result = portfolio_service.calculate_value(holdings)
        
        assert result == expected_value
    
    def test_calculate_portfolio_value_empty_holdings(self, portfolio_service):
        """Test portfolio value calculation with empty holdings."""
        holdings = []
        expected_value = 0.0
        
        result = portfolio_service.calculate_value(holdings)
        
        assert result == expected_value
```

### Frontend Testing

#### Running Tests

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- --testNamePattern="Portfolio"
```

#### Writing Tests

Use React Testing Library for component testing:

```jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Portfolio from '../components/Portfolio';

describe('Portfolio Component', () => {
  const mockData = {
    totalValue: 100000,
    holdings: []
  };

  test('renders portfolio value correctly', () => {
    render(<Portfolio data={mockData} />);
    
    expect(screen.getByText('₹100,000')).toBeInTheDocument();
  });

  test('handles update button click', () => {
    const mockOnUpdate = jest.fn();
    render(<Portfolio data={mockData} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByText('Update'));
    
    expect(mockOnUpdate).toHaveBeenCalled();
  });
});
```

### Integration Testing

```bash
# Run integration tests
./tests/test_integration.sh

# Test API endpoints
curl -X GET http://localhost:9854/api/health
curl -X GET http://localhost:9855/api/portfolio-summary
```

## Documentation

### Code Documentation

- Write clear docstrings for all functions and classes
- Include type hints for better code understanding
- Add comments for complex logic
- Update README.md for new features

### API Documentation

- Update `docs/API.md` when adding new endpoints
- Include request/response examples
- Document error codes and messages
- Add authentication requirements

### User Documentation

- Update user guides for new features
- Include screenshots for UI changes
- Write clear installation instructions
- Provide troubleshooting guides

## Pull Request Process

### Before Submitting

1. **Ensure your code follows style guidelines**
   ```bash
   # Backend
   black src/
   isort src/
   flake8 src/
   
   # Frontend
   cd frontend
   npm run format
   npm run lint
   ```

2. **Run all tests**
   ```bash
   # Backend tests
   python -m pytest tests/
   
   # Frontend tests
   cd frontend && npm test
   
   # Integration tests
   ./tests/test_integration.sh
   ```

3. **Update documentation**
   - Update relevant documentation files
   - Add comments for complex code
   - Update API documentation if needed

### Creating a Pull Request

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information or context.
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code coverage is checked
   - Style guidelines are verified

2. **Code Review**
   - At least one maintainer reviews the PR
   - Address any feedback or requested changes
   - Ensure all tests pass

3. **Merge**
   - PR is merged after approval
   - Feature branch is deleted
   - Changes are deployed to staging

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, browser, versions)
- **Screenshots** if applicable
- **Error messages** or logs

### Issue Template

```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 90]
- Version: [e.g. 1.0.0]

## Additional Information
Any other context about the problem.
```

## Feature Requests

### Suggesting Features

When suggesting new features:

- **Describe the problem** you're trying to solve
- **Explain the proposed solution**
- **Provide use cases** and examples
- **Consider implementation complexity**
- **Check if similar features exist**

### Feature Request Template

```markdown
## Problem Statement
Describe the problem you're trying to solve.

## Proposed Solution
Describe your proposed solution.

## Use Cases
Provide specific use cases and examples.

## Alternatives Considered
Describe any alternatives you've considered.

## Additional Context
Any other context or screenshots.
```

## Getting Help

### Resources

- **Documentation**: Check the `docs/` directory
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions
- **Code**: Review existing code for examples

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions
- **Email**: For sensitive or private matters

## Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Project documentation**

## License

By contributing to Portfolio Coach, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have any questions about contributing, please:

1. Check the documentation in the `docs/` directory
2. Search existing issues and discussions
3. Create a new discussion for general questions
4. Contact the maintainers for specific concerns

Thank you for contributing to Portfolio Coach! 🚀 