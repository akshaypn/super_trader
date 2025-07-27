from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime, timedelta
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.portfolio_service import PortfolioService
from services.market_service import MarketService
from services.tracking_service import TrackingService
from services.chat_service import ChatService
from services.llm_service import LLMService
from services.risk_service import RiskService
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize services
portfolio_service = PortfolioService(Config.DATABASE_URL)
market_service = MarketService()
tracking_service = TrackingService(Config.DATABASE_URL)
llm_service = LLMService()
risk_service = RiskService()
chat_service = ChatService(portfolio_service, market_service, llm_service, risk_service)

@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/portfolio-summary')
def portfolio_summary():
    """Get portfolio summary data."""
    try:
        summary = portfolio_service.get_portfolio_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/holdings')
def holdings():
    """Get current holdings data."""
    try:
        holdings_data = portfolio_service.get_holdings()
        return jsonify({'holdings': holdings_data})
    except Exception as e:
        logger.error(f"Error getting holdings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-data')
def market_data():
    """Get current market data."""
    try:
        market_data = market_service.fetch_market_data()
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports')
def reports():
    """Get daily reports from tracking service."""
    try:
        # Get reports from the last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Get daily portfolio summaries
        daily_summaries = tracking_service.get_daily_summary(start_date, end_date)
        
        # Format reports for frontend
        reports = []
        for summary in daily_summaries:
            report = {
                'date': summary['date'].isoformat() if hasattr(summary['date'], 'isoformat') else str(summary['date']),
                'total_value': float(summary['total_value']) if summary['total_value'] else 0,
                'total_pnl': float(summary['total_pnl']) if summary['total_pnl'] else 0,
                'total_stocks': int(summary['total_stocks']) if summary['total_stocks'] else 0,
                'portfolio_return': float(summary['portfolio_return']) if summary['portfolio_return'] else 0,
                'benchmark_return': float(summary['benchmark_return']) if summary['benchmark_return'] else 0,
                'alpha': float(summary['alpha']) if summary['alpha'] else 0,
                'sharpe_ratio': float(summary['sharpe_ratio']) if summary['sharpe_ratio'] else 0,
                'recommendations_count': int(summary['recommendations_count']) if summary['recommendations_count'] else 0,
                'executed_count': int(summary['executed_count']) if summary['executed_count'] else 0
            }
            reports.append(report)
        
        # Sort by date descending
        reports.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(reports)
    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<date>')
def report_detail(date):
    """Get detailed report for a specific date."""
    try:
        # Parse date
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get portfolio snapshot
        snapshot = tracking_service.get_portfolio_snapshot(report_date)
        
        # Get trade recommendations for the date
        recommendations = tracking_service.get_trade_recommendations(report_date)
        
        # Get market data for the date
        market_data = tracking_service.get_market_data(report_date)
        
        # Get performance metrics
        performance = tracking_service.get_performance_metrics(report_date)
        
        report = {
            'date': date,
            'total_value': float(snapshot['total_value']) if snapshot and snapshot['total_value'] else 0,
            'total_pnl': float(snapshot['total_pnl']) if snapshot and snapshot['total_pnl'] else 0,
            'total_stocks': int(snapshot['total_stocks']) if snapshot and snapshot['total_stocks'] else 0,
            'recommendations': recommendations,
            'market_context': market_data,
            'portfolio_return': float(performance['portfolio_return']) if performance and performance['portfolio_return'] else 0,
            'benchmark_return': float(performance['benchmark_return']) if performance and performance['benchmark_return'] else 0,
            'alpha': float(performance['alpha']) if performance and performance['alpha'] else 0,
            'beta': float(performance['beta']) if performance and performance['beta'] else 1.0,
            'sharpe_ratio': float(performance['sharpe_ratio']) if performance and performance['sharpe_ratio'] else 0,
            'win_rate': float(performance['win_rate']) if performance and performance['win_rate'] else 0
        }
        
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error getting report detail: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get user settings."""
    try:
        # For now, return default settings
        # In a real implementation, this would be stored in a database
        settings = {
            'salary': 70000,
            'monthlyBudget': 100000,
            'monthlyTarget': 10000,
            'riskProfile': 'moderate',
            'targetEqWeight': 0.75,
            'maxDrawdown': 0.20,
            'rebalThreshold': 5,
            'capitalGainsBudget': 0.03,
            'liquidityBufferMonths': 6,
            'email': 'akshay.nambiar7@gmail.com'
        }
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save user settings."""
    try:
        settings = request.json
        
        # Validate required fields
        required_fields = ['salary', 'monthlyBudget', 'monthlyTarget', 'riskProfile']
        for field in required_fields:
            if field not in settings:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # In a real implementation, this would be saved to a database
        # For now, just log the settings
        logger.info(f"Settings saved: {settings}")
        
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh-portfolio')
def refresh_portfolio():
    """Manually refresh portfolio data from Upstox."""
    try:
        # Fetch fresh data from Upstox
        portfolio_service.get_holdings()  # This will fetch and store fresh data
        
        # Get updated summary
        summary = portfolio_service.get_portfolio_summary()
        
        return jsonify({
            'message': 'Portfolio refreshed successfully',
            'summary': summary
        })
    except Exception as e:
        logger.error(f"Error refreshing portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-pipeline')
def run_pipeline():
    """Manually trigger the portfolio analysis pipeline."""
    try:
        # Import the runner
        from scripts.portfolio_coach_runner import PortfolioCoachRunner
        
        # Run the pipeline
        runner = PortfolioCoachRunner()
        result = runner.run_full_pipeline()
        
        return jsonify({
            'message': 'Pipeline executed successfully',
            'result': result
        })
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message and return AI response."""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        response = chat_service.chat(user_message)
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history."""
    try:
        history = chat_service.get_chat_history()
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """Clear chat history."""
    try:
        chat_service.clear_chat_history()
        return jsonify({'message': 'Chat history cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/insights', methods=['GET'])
def get_portfolio_insights():
    """Get automated portfolio insights."""
    try:
        insights = chat_service.get_portfolio_insights()
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Error getting portfolio insights: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
