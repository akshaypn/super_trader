-- Portfolio Coach Database Initialization Script
-- This script sets up the database schema for the Portfolio Coach system

-- Create the holdings table to store portfolio positions
CREATE TABLE IF NOT EXISTS holdings (
    isin TEXT PRIMARY KEY,
    cnc_used_quantity INTEGER,
    collateral_type TEXT,
    company_name TEXT,
    haircut NUMERIC,
    product TEXT,
    quantity INTEGER,
    trading_symbol TEXT,
    tradingsymbol TEXT,
    last_price NUMERIC,
    close_price NUMERIC,
    pnl NUMERIC,
    day_change NUMERIC,
    day_change_percentage NUMERIC,
    instrument_token TEXT,
    average_price NUMERIC,
    collateral_quantity INTEGER,
    collateral_update_quantity INTEGER,
    t1_quantity INTEGER,
    exchange TEXT,
    fetched_at TIMESTAMPTZ DEFAULT now(),
    raw_json JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create index on trading symbol for faster lookups
CREATE INDEX IF NOT EXISTS idx_holdings_trading_symbol ON holdings(trading_symbol);
CREATE INDEX IF NOT EXISTS idx_holdings_isin ON holdings(isin);
CREATE INDEX IF NOT EXISTS idx_holdings_fetched_at ON holdings(fetched_at);
CREATE INDEX IF NOT EXISTS idx_holdings_quantity ON holdings(quantity);
CREATE INDEX IF NOT EXISTS idx_holdings_pnl ON holdings(pnl);

-- Create cash_flows table to track cash movements
CREATE TABLE IF NOT EXISTS cash_flows (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'salary', 'dividend', 'transfer', 'withdrawal'
    amount DECIMAL(12,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create market_data table to store daily market indicators
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    nifty_50_close DECIMAL(10,2),
    nifty_50_change DECIMAL(5,2),
    sensex_close DECIMAL(10,2),
    sensex_change DECIMAL(5,2),
    usd_inr_rate DECIMAL(6,2),
    vix DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(date)
);

-- Create trade_recommendations table to track daily recommendations
CREATE TABLE IF NOT EXISTS trade_recommendations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    action VARCHAR(10) NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    symbol VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    limit_price DECIMAL(10,2) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    rationale TEXT NOT NULL,
    instrument_token TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executed', 'cancelled', 'expired'
    execution_price DECIMAL(10,2),
    execution_time TIMESTAMPTZ,
    pnl DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create portfolio_snapshots table to track daily portfolio values
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_value DECIMAL(12,2) NOT NULL,
    total_pnl DECIMAL(12,2) NOT NULL,
    total_stocks INTEGER NOT NULL,
    cash_balance DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(date)
);

-- Create recommendation_executions table to track which recommendations were executed
CREATE TABLE IF NOT EXISTS recommendation_executions (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES trade_recommendations(id),
    execution_date DATE NOT NULL,
    actual_quantity INTEGER,
    actual_price DECIMAL(10,2),
    slippage DECIMAL(5,2),
    execution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create performance_metrics table to track daily performance
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    portfolio_return DECIMAL(5,2),
    benchmark_return DECIMAL(5,2), -- Nifty 50 return
    alpha DECIMAL(5,2),
    beta DECIMAL(5,2),
    sharpe_ratio DECIMAL(5,2),
    max_drawdown DECIMAL(5,2),
    win_rate DECIMAL(5,2),
    total_trades INTEGER,
    profitable_trades INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(date)
);

-- Create sector_allocation table to track sector-wise allocation
CREATE TABLE IF NOT EXISTS sector_allocation (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    sector VARCHAR(50) NOT NULL,
    allocation_percentage DECIMAL(5,2) NOT NULL,
    allocation_value DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(date, sector)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_trade_recommendations_date ON trade_recommendations(date);
CREATE INDEX IF NOT EXISTS idx_trade_recommendations_symbol ON trade_recommendations(symbol);
CREATE INDEX IF NOT EXISTS idx_trade_recommendations_status ON trade_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_date ON portfolio_snapshots(date);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_date ON performance_metrics(date);
CREATE INDEX IF NOT EXISTS idx_sector_allocation_date ON sector_allocation(date);

-- Create views for common queries
CREATE OR REPLACE VIEW daily_portfolio_summary AS
SELECT 
    ps.date,
    ps.total_value,
    ps.total_pnl,
    ps.total_stocks,
    pm.portfolio_return,
    pm.benchmark_return,
    pm.alpha,
    pm.sharpe_ratio,
    COUNT(tr.id) as recommendations_count,
    COUNT(CASE WHEN tr.status = 'executed' THEN 1 END) as executed_count
FROM portfolio_snapshots ps
LEFT JOIN performance_metrics pm ON ps.date = pm.date
LEFT JOIN trade_recommendations tr ON ps.date = tr.date
GROUP BY ps.date, ps.total_value, ps.total_pnl, ps.total_stocks, 
         pm.portfolio_return, pm.benchmark_return, pm.alpha, pm.sharpe_ratio
ORDER BY ps.date DESC;

-- Create view for recommendation performance
CREATE OR REPLACE VIEW recommendation_performance AS
SELECT 
    tr.date,
    tr.symbol,
    tr.action,
    tr.limit_price,
    tr.confidence,
    tr.status,
    re.actual_price,
    re.execution_date,
    CASE 
        WHEN tr.action = 'BUY' AND re.actual_price IS NOT NULL 
        THEN (re.actual_price - tr.limit_price) / tr.limit_price * 100
        WHEN tr.action = 'SELL' AND re.actual_price IS NOT NULL 
        THEN (tr.limit_price - re.actual_price) / tr.limit_price * 100
        ELSE NULL
    END as price_accuracy_percentage,
    tr.pnl
FROM trade_recommendations tr
LEFT JOIN recommendation_executions re ON tr.id = re.recommendation_id
ORDER BY tr.date DESC, tr.confidence DESC;

-- Insert sample data for testing
INSERT INTO market_data (date, nifty_50_close, nifty_50_change, usd_inr_rate) VALUES
(CURRENT_DATE, 24837.00, -0.90, 86.46)
ON CONFLICT (date) DO UPDATE SET
    nifty_50_close = EXCLUDED.nifty_50_close,
    nifty_50_change = EXCLUDED.nifty_50_change,
    usd_inr_rate = EXCLUDED.usd_inr_rate;

-- Note: Sample data removed - will be populated from Upstox API 