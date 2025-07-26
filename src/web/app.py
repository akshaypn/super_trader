from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import threading
import time
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    """Create database connection."""
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/fin")
    return create_engine(database_url)

@app.route('/')
def index():
    """Main page showing portfolio holdings."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Docker container monitoring."""
    try:
        # Test database connection
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': time.time()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@app.route('/api/holdings')
def get_holdings():
    """API endpoint to get holdings data."""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    h.isin,
                    h.company_name,
                    h.trading_symbol,
                    h.quantity,
                    h.average_price,
                    h.last_price,
                    h.close_price,
                    h.pnl,
                    h.day_change,
                    h.day_change_percentage,
                    h.exchange,
                    h.fetched_at
                FROM holdings h
                ORDER BY h.company_name
            """))
            
            holdings = []
            for row in result:
                holdings.append({
                    'isin': row.isin,
                    'company_name': row.company_name,
                    'trading_symbol': row.trading_symbol,
                    'quantity': row.quantity,
                    'average_price': float(row.average_price) if row.average_price else 0,
                    'last_price': float(row.last_price) if row.last_price else 0,
                    'close_price': float(row.close_price) if row.close_price else 0,
                    'pnl': float(row.pnl) if row.pnl else 0,
                    'day_change': float(row.day_change) if row.day_change else 0,
                    'day_change_percentage': float(row.day_change_percentage) if row.day_change_percentage else 0,
                    'exchange': row.exchange,
                    'fetched_at': row.fetched_at.isoformat() if row.fetched_at else None
                })
            
            return jsonify({
                'success': True,
                'data': holdings,
                'count': len(holdings)
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/portfolio-summary')
def get_portfolio_summary():
    """API endpoint to get portfolio summary."""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_stocks,
                    SUM(quantity * last_price) as total_value,
                    SUM(pnl) as total_pnl,
                    SUM(day_change) as total_day_change
                FROM holdings 
                WHERE last_price IS NOT NULL
            """))
            
            row = result.fetchone()
            return jsonify({
                'success': True,
                'data': {
                    'total_stocks': row.total_stocks,
                    'total_value': float(row.total_value) if row.total_value else 0,
                    'total_pnl': float(row.total_pnl) if row.total_pnl else 0,
                    'total_day_change': float(row.total_day_change) if row.total_day_change else 0
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
