# Portfolio Coach - API Documentation

## Overview

The Portfolio Coach API provides comprehensive endpoints for portfolio management, market data, AI-powered analysis, and user interactions. All endpoints follow RESTful conventions and return JSON responses.

## Base URL

```
Development: http://localhost:9854
Production: https://api.portfolio-coach.com
```

## Authentication

Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

## Common Response Format

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-07-27T13:47:52.718709"
}
```

## Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {}
  },
  "timestamp": "2025-07-27T13:47:52.718709"
}
```

## Health & Status Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-07-27T13:47:52.718709",
  "services": {
    "database": "healthy",
    "ai_service": "healthy",
    "market_data": "healthy"
  }
}
```

## Portfolio Management

### Get Portfolio Summary

```http
GET /api/portfolio-summary
```

**Response:**
```json
{
  "total_value": 860906.04,
  "total_pnl": 50036.27,
  "total_stocks": 133,
  "total_day_change": 0,
  "currency": "INR",
  "last_updated": "2025-07-27T13:47:52.718709"
}
```

### Get Holdings

```http
GET /api/holdings
```

**Query Parameters:**
- `sector` (optional): Filter by sector
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "holdings": [
    {
      "symbol": "RELIANCE",
      "quantity": 100,
      "avg_price": 285.17,
      "current_price": 306.17,
      "market_value": 30617.4,
      "pnl": 2030.55,
      "pnl_percentage": 6.63,
      "sector": "Oil & Gas",
      "weight": 0.0356
    }
  ],
  "total_count": 133,
  "pagination": {
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### Get Sector Analysis

```http
GET /api/sector-analysis
```

**Response:**
```json
{
  "sectors": [
    {
      "name": "Banking",
      "count": 5,
      "value": 35671.75,
      "weight": 0.0414,
      "pnl": 5590.95,
      "return": 0.1567,
      "holdings": ["ICICIBANK", "KOTAKBANK", "HDFCBANK", "SBIN", "AXISBANK"]
    }
  ],
  "total_sectors": 11
}
```

## Market Data

### Get Market Overview

```http
GET /api/market-data
```

**Response:**
```json
{
  "nifty_50": {
    "close": 24837.0,
    "change": -0.898,
    "change_percentage": -0.36,
    "volume": 0
  },
  "sensex": {
    "close": 81463.09,
    "change": -0.877,
    "change_percentage": -0.35,
    "volume": 0
  },
  "usd_inr": {
    "rate": 86.457,
    "change": 0.097,
    "change_percentage": 0.11
  },
  "timestamp": "2025-07-27T13:47:52.718709"
}
```

### Get Stock Quote

```http
GET /api/market-data/quote/{symbol}
```

**Response:**
```json
{
  "symbol": "RELIANCE",
  "name": "Reliance Industries Limited",
  "current_price": 306.17,
  "change": 2.15,
  "change_percentage": 0.71,
  "volume": 1234567,
  "market_cap": 2073456789012,
  "pe_ratio": 18.5,
  "dividend_yield": 0.45,
  "timestamp": "2025-07-27T13:47:52.718709"
}
```

## AI Chat Interface

### Send Chat Message

```http
POST /api/chat
```

**Request Body:**
```json
{
  "message": "What are the main risks in my portfolio?",
  "context": "portfolio_analysis"
}
```

**Response:**
```json
{
  "response": "Based on your portfolio analysis, here are the main risks...",
  "timestamp": "2025-07-27T13:47:52.718709",
  "context_used": ["portfolio_data", "risk_metrics", "market_data"],
  "confidence_score": 0.85,
  "suggestions": [
    "Consider diversifying your sector allocation",
    "Review your concentration risk"
  ]
}
```

### Get Portfolio Insights

```http
GET /api/chat/insights
```

**Response:**
```json
{
  "portfolio_summary": {
    "total_value": 860906.04,
    "total_pnl": 50036.27,
    "total_stocks": 133
  },
  "risk_metrics": {
    "concentration_risk": 0.051,
    "max_sector_weight": 0.732,
    "portfolio_beta": 0.95,
    "risk_score": 0.461
  },
  "recommendations": [
    {
      "title": "High Concentration Risk",
      "description": "Your largest position represents 5.1% of your portfolio.",
      "action": "Consider reducing position size or adding diversification",
      "priority": "high",
      "type": "risk"
    }
  ],
  "sector_analysis": {
    "Automobile": {
      "count": 1,
      "value": 2749.6,
      "weight": 0.003,
      "pnl": -1293.8,
      "return": -0.471
    }
  }
}
```

### Get Chat History

```http
GET /api/chat/history
```

**Query Parameters:**
- `limit` (optional): Number of messages (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "history": [
    {
      "id": "msg_123",
      "role": "user",
      "content": "What are the main risks in my portfolio?",
      "timestamp": "2025-07-27T13:45:00.000000"
    },
    {
      "id": "msg_124",
      "role": "assistant",
      "content": "Based on your portfolio analysis...",
      "timestamp": "2025-07-27T13:45:05.000000",
      "metadata": {
        "context_used": ["portfolio_data", "risk_metrics"],
        "confidence_score": 0.85
      }
    }
  ],
  "total_count": 25
}
```

### Clear Chat History

```http
POST /api/chat/clear
```

**Response:**
```json
{
  "message": "Chat history cleared successfully",
  "timestamp": "2025-07-27T13:47:52.718709"
}
```

## Reports & Analytics

### Get Performance Report

```http
GET /api/reports/performance
```

**Query Parameters:**
- `period` (optional): Time period (1d, 1w, 1m, 3m, 6m, 1y, all)
- `format` (optional): Response format (json, pdf, csv)

**Response:**
```json
{
  "period": "1m",
  "total_return": 5.82,
  "benchmark_return": 4.15,
  "alpha": 1.67,
  "beta": 0.95,
  "sharpe_ratio": 1.23,
  "max_drawdown": -2.15,
  "volatility": 12.5,
  "holdings_performance": [
    {
      "symbol": "RELIANCE",
      "return": 6.63,
      "contribution": 0.15,
      "weight": 0.0356
    }
  ],
  "sector_performance": [
    {
      "sector": "Banking",
      "return": 15.67,
      "weight": 0.0414
    }
  ]
}
```

### Get Risk Report

```http
GET /api/reports/risk
```

**Response:**
```json
{
  "risk_metrics": {
    "var_95": 2.15,
    "var_99": 3.45,
    "expected_shortfall": 2.85,
    "beta": 0.95,
    "correlation": 0.78
  },
  "concentration_analysis": {
    "top_holdings": [
      {
        "symbol": "RELIANCE",
        "weight": 0.0356,
        "risk_contribution": 0.045
      }
    ],
    "sector_concentration": {
      "highest": "Others",
      "weight": 0.732,
      "risk_level": "high"
    }
  },
  "stress_tests": {
    "market_crash_20": -8.5,
    "interest_rate_hike": -2.3,
    "currency_devaluation": -1.8
  }
}
```

## User Management

### User Profile

```http
GET /api/user/profile
```

**Response:**
```json
{
  "user_id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "preferences": {
    "currency": "INR",
    "timezone": "Asia/Kolkata",
    "notifications": {
      "email": true,
      "push": false,
      "sms": false
    }
  },
  "subscription": {
    "plan": "premium",
    "status": "active",
    "expires_at": "2025-12-31T23:59:59.000000"
  }
}
```

### Update User Profile

```http
PUT /api/user/profile
```

**Request Body:**
```json
{
  "name": "John Doe",
  "preferences": {
    "currency": "INR",
    "notifications": {
      "email": true,
      "push": true
    }
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_ERROR` | Invalid or missing authentication token |
| `AUTHORIZATION_ERROR` | Insufficient permissions for the operation |
| `VALIDATION_ERROR` | Invalid input parameters |
| `NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests in a given time |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | External service temporarily unavailable |

## Rate Limiting

- **Standard endpoints**: 1000 requests per hour
- **AI chat endpoints**: 100 requests per hour
- **Market data endpoints**: 5000 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

Endpoints that return lists support pagination with the following parameters:

- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

Response includes pagination metadata:

```json
{
  "data": [],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total_count": 133,
    "has_more": true,
    "next_offset": 50
  }
}
```

## Webhooks

### Configure Webhook

```http
POST /api/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["portfolio_update", "risk_alert"],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

| Event | Description | Payload |
|-------|-------------|---------|
| `portfolio_update` | Portfolio value or holdings changed | Portfolio summary data |
| `risk_alert` | Risk threshold exceeded | Risk metrics and alerts |
| `market_alert` | Significant market movement | Market data and analysis |

## SDKs & Libraries

### Python SDK

```python
from portfolio_coach import PortfolioCoach

client = PortfolioCoach(api_key="your-api-key")
portfolio = client.get_portfolio_summary()
```

### JavaScript SDK

```javascript
import { PortfolioCoach } from '@portfolio-coach/sdk';

const client = new PortfolioCoach({ apiKey: 'your-api-key' });
const portfolio = await client.getPortfolioSummary();
```

## Support

For API support and questions:

- **Documentation**: [docs.portfolio-coach.com](https://docs.portfolio-coach.com)
- **Status Page**: [status.portfolio-coach.com](https://status.portfolio-coach.com)
- **Support Email**: api-support@portfolio-coach.com
- **Developer Forum**: [community.portfolio-coach.com](https://community.portfolio-coach.com) 