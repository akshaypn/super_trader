#!/usr/bin/env python3
"""
Portfolio Coach Runner
======================

Main runner class for the Portfolio Coach system that orchestrates
the daily portfolio analysis and recommendation pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add src directory to Python path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from config import Config, PortfolioCoachConfig
from services.portfolio_service import PortfolioService
from services.market_service import MarketService
from services.llm_service import LLMService
from services.risk_service import RiskService
from services.report_service import ReportService

logger = logging.getLogger(__name__)

class PortfolioCoachRunner:
    """Main runner class for Portfolio Coach system."""
    
    def __init__(self, config: Optional[PortfolioCoachConfig] = None):
        """Initialize the runner with configuration."""
        self.config = config or PortfolioCoachConfig()
        self.setup_logging()
        
        # Initialize services
        self.portfolio_service = PortfolioService(Config.DATABASE_URL)
        self.market_service = MarketService()
        self.llm_service = LLMService()
        self.risk_service = RiskService()
        self.report_service = ReportService()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/portfolio_coach.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def test_configuration(self):
        """Test the configuration and connectivity."""
        logger.info("Testing Portfolio Coach configuration...")
        
        try:
            # Validate basic config
            Config.validate()
            logger.info("✓ Basic configuration validated")
            
            # Validate OpenAI config
            Config.validate_openai()
            logger.info("✓ OpenAI configuration validated")
            
            # Test database connection
            self._test_database_connection()
            logger.info("✓ Database connection successful")
            
            # Test portfolio data availability
            self._test_portfolio_data()
            logger.info("✓ Portfolio data accessible")
            
            logger.info("Configuration test completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Configuration test failed: {e}")
            return False
    
    def _test_database_connection(self):
        """Test database connectivity."""
        from sqlalchemy import create_engine, text
        
        engine = create_engine(Config.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    
    def _test_portfolio_data(self):
        """Test portfolio data availability."""
        from sqlalchemy import create_engine, text
        
        engine = create_engine(Config.DATABASE_URL)
        with engine.connect() as conn:
            # Check if holdings table exists and has data
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = 'holdings'
            """))
            if result.fetchone().count == 0:
                raise RuntimeError("Holdings table does not exist")
            
            # Check if there's any data
            result = conn.execute(text("SELECT COUNT(*) as count FROM holdings"))
            count = result.fetchone().count
            logger.info(f"Found {count} holdings in database")
    
    def run_full_pipeline(self):
        """Run the complete Portfolio Coach pipeline."""
        logger.info("Starting Portfolio Coach pipeline...")
        
        try:
            # Step 1: Pre-flight checks
            self._pre_flight_checks()
            
            # Step 2: Fetch market data
            market_data = self._fetch_market_data()
            
            # Step 3: Get portfolio snapshot
            portfolio_data = self._get_portfolio_snapshot()
            
            # Step 4: Generate signals
            signals = self._generate_signals(portfolio_data, market_data)
            
            # Step 5: Generate trade ideas
            trade_ideas = self._generate_trade_ideas(signals)
            
            # Step 6: Apply risk gates
            filtered_ideas = self._apply_risk_gates(trade_ideas)
            
            # Step 7: Get critic votes
            approved_ideas = self._get_critic_votes(filtered_ideas)
            
            # Step 8: Generate report
            self._generate_report(approved_ideas, signals)
            
            logger.info("Portfolio Coach pipeline completed successfully!")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def _pre_flight_checks(self):
        """Perform pre-flight checks."""
        logger.info("Running pre-flight checks...")
        
        # Test configuration
        self.test_configuration()
        
        # Check if it's a trading day (Monday-Friday)
        today = datetime.now()
        if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
            logger.info("Weekend detected - but continuing for testing purposes")
            # return  # Commented out for testing
        
        logger.info("Pre-flight checks completed")
    
    def _fetch_market_data(self) -> Dict:
        """Fetch market data from various sources."""
        logger.info("Fetching market data...")
        
        market_data = self.market_service.fetch_market_data()
        logger.info("Market data fetched successfully")
        return market_data
    
    def _get_portfolio_snapshot(self) -> Dict:
        """Get current portfolio snapshot from database."""
        logger.info("Getting portfolio snapshot...")
        
        holdings = self.portfolio_service.get_holdings()
        portfolio_summary = self.portfolio_service.get_portfolio_summary()
        
        portfolio_data = {
            "holdings": holdings,
            "total_value": portfolio_summary["total_value"],
            "total_pnl": portfolio_summary["total_pnl"],
            "total_stocks": portfolio_summary["total_stocks"],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Portfolio snapshot: {len(holdings)} holdings, ₹{portfolio_data['total_value']:,.0f} value")
        return portfolio_data
    
    def _generate_signals(self, portfolio_data: Dict, market_data: Dict) -> Dict:
        """Generate trading signals based on portfolio and market data."""
        logger.info("Generating trading signals...")
        
        signals = {
            "valuation_signals": [],
            "momentum_signals": [],
            "drift_signals": [],
            "risk_signals": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Placeholder for signal generation logic
        # This would implement the decision stack from the tech bible
        
        logger.info("Trading signals generated")
        return signals
    
    def _generate_trade_ideas(self, signals: Dict) -> List[Dict]:
        """Generate trade ideas using LLM."""
        logger.info("Generating trade ideas...")
        
        # Get portfolio and market data for context
        portfolio_data = self._get_portfolio_snapshot()
        market_data = self._fetch_market_data()
        
        trade_ideas = self.llm_service.generate_trade_ideas(portfolio_data, market_data, signals)
        
        logger.info(f"Generated {len(trade_ideas)} trade ideas")
        return trade_ideas
    
    def _apply_risk_gates(self, trade_ideas: List[Dict]) -> List[Dict]:
        """Apply risk gates to filter trade ideas."""
        logger.info("Applying risk gates...")
        
        portfolio_data = self._get_portfolio_snapshot()
        filtered_ideas = self.risk_service.apply_risk_gates(trade_ideas, portfolio_data)
        
        logger.info(f"Risk gates applied: {len(filtered_ideas)} ideas passed")
        return filtered_ideas
    
    def _get_critic_votes(self, trade_ideas: List[Dict]) -> List[Dict]:
        """Get critic votes on trade ideas."""
        logger.info("Getting critic votes...")
        
        portfolio_data = self._get_portfolio_snapshot()
        approved_ideas = self.llm_service.critique_trade_ideas(trade_ideas, portfolio_data)
        
        logger.info(f"Critic votes: {len(approved_ideas)} ideas approved")
        return approved_ideas
    
    def _generate_report(self, trade_ideas: List[Dict], signals: Dict):
        """Generate and send the final report."""
        logger.info("Generating report...")
        
        portfolio_data = self._get_portfolio_snapshot()
        market_data = self._fetch_market_data()
        
        report = self.report_service.generate_report(trade_ideas, portfolio_data, market_data)
        
        logger.info("Report generated successfully")
        logger.info(report)
        
        # Send email
        try:
            self.report_service.send_email(report)
            logger.info("Email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
        
        # Send to Slack (placeholder)
        try:
            self.report_service.send_slack_message(report)
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
        
        return report 