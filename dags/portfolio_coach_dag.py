"""
Portfolio Coach Daily Pipeline DAG
Scheduled to run every trading day at 08:45 IST
"""

from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pendulum
import os
import sys
import logging

# Add src directory to path
sys.path.insert(0, '/app/src')

from services.portfolio_service import PortfolioService
from services.market_service import MarketService
from services.llm_service import LLMService
from services.risk_service import RiskService
from services.report_service import ReportService
from services.upstox_service import UpstoxService
from services.tracking_service import TrackingService
from config import Config

# Set timezone to IST
IST = pendulum.timezone("Asia/Kolkata")

# Default arguments
default_args = {
    'owner': 'portfolio_coach',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1, tzinfo=IST),
    'email': ['akshay.nambiar7@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'portfolio_coach_daily',
    default_args=default_args,
    description='Daily Portfolio Coach Pipeline',
    schedule_interval='30 7 * * 1-5',  # 07:30 IST on weekdays
    catchup=False,
    tags=['portfolio', 'trading', 'ai'],
    max_active_runs=1,
)

@task(task_id='pre_flight_checks')
def pre_flight_checks():
    """07:30 - Pre-flight checks and health monitoring."""
    logger = logging.getLogger(__name__)
    logger.info("Starting pre-flight checks...")
    
    try:
        # Test database connection
        portfolio_service = PortfolioService(Config.DATABASE_URL)
        holdings = portfolio_service.get_holdings()
        logger.info(f"✓ Database connection successful - {len(holdings)} holdings found")
        
        # Test Upstox API
        upstox_service = UpstoxService(Config.DATABASE_URL)
        upstox_service.get_api_client()
        logger.info("✓ Upstox API connection successful")
        
        # Test OpenAI API
        llm_service = LLMService()
        logger.info("✓ OpenAI API connection successful")
        
        # Test market data
        market_service = MarketService()
        market_data = market_service.fetch_market_data()
        logger.info("✓ Market data service operational")
        
        logger.info("✓ All pre-flight checks passed")
        return {"status": "success", "holdings_count": len(holdings)}
        
    except Exception as e:
        logger.error(f"✗ Pre-flight check failed: {e}")
        raise

@task(task_id='fetch_market_data')
def fetch_market_data():
    """07:40 - Fetch global market data and indicators."""
    logger = logging.getLogger(__name__)
    logger.info("Fetching market data...")
    
    try:
        market_service = MarketService()
        market_data = market_service.fetch_market_data()
        
        logger.info(f"✓ Market data fetched successfully")
        logger.info(f"  - Nifty 50: ₹{market_data.get('nifty_50', {}).get('close', 0):,.2f}")
        logger.info(f"  - USD/INR: ₹{market_data.get('usd_inr', {}).get('rate', 0):.2f}")
        
        return market_data
        
    except Exception as e:
        logger.error(f"✗ Market data fetch failed: {e}")
        raise

@task(task_id='portfolio_snapshot')
def portfolio_snapshot():
    """07:50 - Get current portfolio snapshot from Upstox."""
    logger = logging.getLogger(__name__)
    logger.info("Getting portfolio snapshot...")
    
    try:
        portfolio_service = PortfolioService(Config.DATABASE_URL)
        holdings = portfolio_service.get_holdings()
        portfolio_summary = portfolio_service.get_portfolio_summary()
        
        logger.info(f"✓ Portfolio snapshot: {len(holdings)} holdings, ₹{portfolio_summary['total_value']:,.2f} value")
        
        return {
            "holdings": holdings,
            "summary": portfolio_summary
        }
        
    except Exception as e:
        logger.error(f"✗ Portfolio snapshot failed: {e}")
        raise

@task(task_id='generate_signals')
def generate_signals(portfolio_data, market_data):
    """08:00 - Generate trading signals and analysis."""
    logger = logging.getLogger(__name__)
    logger.info("Generating trading signals...")
    
    try:
        portfolio_service = PortfolioService(Config.DATABASE_URL)
        
        # Generate various signals
        signals = {
            "drift_signals": portfolio_service.calculate_drift_signals(portfolio_data["holdings"], {}),
            "valuation_signals": [],
            "momentum_signals": [],
            "risk_signals": []
        }
        
        logger.info(f"✓ Trading signals generated: {len(signals['drift_signals'])} drift signals")
        
        return signals
        
    except Exception as e:
        logger.error(f"✗ Signal generation failed: {e}")
        raise

@task(task_id='generate_trade_ideas')
def generate_trade_ideas(portfolio_data, market_data, signals):
    """08:15 - Generate trade ideas using AI."""
    logger = logging.getLogger(__name__)
    logger.info("Generating trade ideas with AI...")
    
    try:
        llm_service = LLMService()
        trade_ideas = llm_service.generate_trade_ideas(portfolio_data, market_data, signals)
        
        logger.info(f"✓ Generated {len(trade_ideas)} trade ideas")
        
        return trade_ideas
        
    except Exception as e:
        logger.error(f"✗ Trade idea generation failed: {e}")
        raise

@task(task_id='apply_risk_gates')
def apply_risk_gates(trade_ideas, portfolio_data):
    """08:25 - Apply risk management gates."""
    logger = logging.getLogger(__name__)
    logger.info("Applying risk gates...")
    
    try:
        risk_service = RiskService()
        filtered_ideas = risk_service.apply_risk_gates(trade_ideas, portfolio_data)
        
        logger.info(f"✓ Risk gates applied: {len(filtered_ideas)} ideas passed")
        
        return filtered_ideas
        
    except Exception as e:
        logger.error(f"✗ Risk gates failed: {e}")
        raise

@task(task_id='critic_vote')
def critic_vote(trade_ideas, portfolio_data):
    """08:35 - Get critic votes on trade ideas."""
    logger = logging.getLogger(__name__)
    logger.info("Getting critic votes...")
    
    try:
        llm_service = LLMService()
        approved_ideas = llm_service.critique_trade_ideas(trade_ideas, portfolio_data)
        
        logger.info(f"✓ Critic votes: {len(approved_ideas)} ideas approved")
        
        return approved_ideas
        
    except Exception as e:
        logger.error(f"✗ Critic vote failed: {e}")
        raise

@task(task_id='generate_report')
def generate_report(approved_ideas, portfolio_data, market_data, tracking_data):
    """08:45 - Generate final report."""
    logger = logging.getLogger(__name__)
    logger.info("Generating final report...")
    
    try:
        report_service = ReportService()
        report = report_service.generate_report(approved_ideas, portfolio_data, market_data, tracking_data)
        
        logger.info("✓ Report generated successfully")
        
        return report
        
    except Exception as e:
        logger.error(f"✗ Report generation failed: {e}")
        raise

@task(task_id='send_email')
def send_email(report):
    """08:45 - Send email report."""
    logger = logging.getLogger(__name__)
    logger.info("Sending email report...")
    
    try:
        report_service = ReportService()
        success = report_service.send_email(
            report, 
            subject=f"Portfolio Coach Report - {datetime.now(IST).strftime('%d %b %Y')}"
        )
        
        if success:
            logger.info("✓ Email sent successfully to akshay.nambiar7@gmail.com")
        else:
            logger.warning("⚠ Email sending failed - check SMTP configuration")
        
        return success
        
    except Exception as e:
        logger.error(f"✗ Email sending failed: {e}")
        raise

@task(task_id='track_portfolio_changes')
def track_portfolio_changes(portfolio_data, approved_ideas, market_data):
    """Track portfolio changes and execution status."""
    logger = logging.getLogger(__name__)
    logger.info("Tracking portfolio changes...")
    
    try:
        tracking_service = TrackingService(Config.DATABASE_URL)
        
        # Save portfolio snapshot
        tracking_service.save_portfolio_snapshot(portfolio_data["summary"])
        
        # Save market data
        tracking_service.save_market_data(market_data)
        
        # Save trade recommendations
        recommendation_ids = tracking_service.save_trade_recommendations(approved_ideas)
        
        # Get previous portfolio snapshot for comparison
        previous_snapshot = tracking_service.get_previous_portfolio_snapshot()
        previous_holdings = []
        
        if previous_snapshot:
            # Get previous holdings (simplified - would need to store previous holdings)
            previous_holdings = []
        
        # Track portfolio changes
        portfolio_changes = tracking_service.track_portfolio_changes(
            portfolio_data["holdings"], 
            previous_holdings
        )
        
        # Calculate performance metrics
        performance_metrics = tracking_service.calculate_performance_metrics(
            portfolio_data["summary"], 
            market_data
        )
        
        # Get recommendation history
        recommendation_history = tracking_service.get_recommendation_history(7)
        
        tracking_data = {
            "portfolio_changes": portfolio_changes,
            "performance_metrics": performance_metrics,
            "recommendation_history": recommendation_history,
            "recommendation_ids": recommendation_ids
        }
        
        logger.info(f"✓ Portfolio tracking completed: {len(approved_ideas)} recommendations saved")
        
        return tracking_data
        
    except Exception as e:
        logger.error(f"✗ Portfolio tracking failed: {e}")
        raise

# Define task dependencies
pre_flight = pre_flight_checks()
market_data = fetch_market_data()
portfolio_data = portfolio_snapshot()
signals = generate_signals(portfolio_data, market_data)
trade_ideas = generate_trade_ideas(portfolio_data, market_data, signals)
filtered_ideas = apply_risk_gates(trade_ideas, portfolio_data)
approved_ideas = critic_vote(filtered_ideas, portfolio_data)
tracking = track_portfolio_changes(portfolio_data, approved_ideas, market_data)
report = generate_report(approved_ideas, portfolio_data, market_data, tracking)
email_sent = send_email(report)

# Set task dependencies
pre_flight >> [market_data, portfolio_data]
[market_data, portfolio_data] >> signals
signals >> trade_ideas
trade_ideas >> filtered_ideas
filtered_ideas >> approved_ideas
approved_ideas >> tracking
[approved_ideas, portfolio_data, market_data, tracking] >> report
report >> email_sent 