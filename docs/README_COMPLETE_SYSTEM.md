# Super Trader Portfolio Coach

A sophisticated portfolio management system that provides actionable buy/sell/hold guidance based on your long-term wealth plan. The system analyzes your live holdings and generates evidence-backed recommendations for portfolio optimization.

## Features

- **Daily Portfolio Analysis**: Automated analysis of your holdings every trading day
- **LLM-Powered Recommendations**: AI-generated trade ideas using GPT-4
- **Risk Management**: Comprehensive risk gates and position sizing
- **Multi-Critic System**: Multiple AI critics validate recommendations
- **Web Dashboard**: Real-time portfolio visualization
- **Slack/Email Integration**: Automated report delivery

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 15+
- Redis (optional, for caching)
- Docker & Docker Compose (for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd super-trader-clean
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys and configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   # Using Docker Compose (recommended)
   docker-compose -f docker/docker-compose.yml up -d postgres
   
   # Or manually create database and run deployment/init.sql
   ```

### Running the Application

#### Web Interface
```bash
python run.py --mode web
```
Access the dashboard at http://localhost:5000

#### Portfolio Coach Runner
```bash
# Test configuration
python run.py --mode test-config

# Run full pipeline
python run.py --mode runner

# Dry run mode
python run.py --mode runner --dry-run
```

#### Docker Deployment
```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

## Configuration

The system uses a configuration file (`~/.coach/config.yml`) with the following structure:

```yaml
investor_id: "akshay"
salary_day: 25
monthly_inflow: 70_000
risk_profile: "moderate"
target_eq_weight: 0.75
max_drawdown: 0.20
strategic_beta: 0.95
rebal_threshold: 5
capital_gains_budget: 0.03
liquidity_buffer_months: 6
slack_channel: "#portfolio-coach"
email_to: "akshay@example.com"
```

## Architecture

The system follows the architecture outlined in the tech bible:

1. **Data Layer**: PostgreSQL for holdings, market data, and signals
2. **Signal Engine**: Valuation, momentum, and drift analysis
3. **LLM Layer**: GPT-4 for idea generation, GPT-3.5 for criticism
4. **Risk Engine**: VaR, position sizing, and liquidity checks
5. **Reporting**: Markdown reports with Slack/email delivery

## API Endpoints

- `GET /` - Portfolio dashboard
- `GET /health` - Health check
- `GET /api/holdings` - Portfolio holdings data
- `GET /api/portfolio-summary` - Portfolio summary statistics

## Development

### Project Structure
```
super-trader-clean/
├── src/                    # Source code
│   ├── config.py          # Configuration management
│   ├── web/               # Web interface
│   ├── services/          # Business logic services
│   ├── database/          # Database models and utilities
│   └── utils/             # Utility functions
├── scripts/               # Runner scripts
├── deployment/            # Database initialization
├── docker/                # Docker configuration
├── tests/                 # Test files
└── logs/                  # Application logs
```

### Testing
```bash
# Run tests
pytest

# Test configuration
python run.py --mode test-config
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.
