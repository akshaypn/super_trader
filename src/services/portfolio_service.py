"""
Portfolio service for managing portfolio data and operations.
"""

from typing import Dict, List, Optional
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
from .upstox_service import UpstoxService

logger = logging.getLogger(__name__)

class PortfolioService:
    """Service for portfolio operations."""
    
    def __init__(self, database_url: str):
        """Initialize portfolio service."""
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.upstox_service = UpstoxService(database_url)
    
    def get_holdings(self) -> List[Dict]:
        """Get current portfolio holdings from Upstox."""
        try:
            # First, fetch fresh data from Upstox API
            self.upstox_service.fetch_and_store_holdings()
            
            # Then get from database
            return self.upstox_service.get_holdings_from_db()
                
        except Exception as e:
            logger.error(f"Error fetching holdings: {e}")
            # Fallback to database if API fails
            return self.upstox_service.get_holdings_from_db()
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary statistics."""
        try:
            return self.upstox_service.get_portfolio_summary()
        except Exception as e:
            logger.error(f"Error fetching portfolio summary: {e}")
            return {
                'total_stocks': 0,
                'total_value': 0,
                'total_pnl': 0,
                'total_day_change': 0
            }
    
    def calculate_drift_signals(self, holdings: List[Dict], target_weights: Dict[str, float]) -> List[Dict]:
        """Calculate drift signals for portfolio rebalancing."""
        total_value = sum(h['quantity'] * h['last_price'] for h in holdings)
        if total_value == 0:
            return []
        
        drift_signals = []
        for holding in holdings:
            symbol = holding['trading_symbol']
            current_value = holding['quantity'] * holding['last_price']
            current_weight = (current_value / total_value) * 100
            target_weight = target_weights.get(symbol, 0)
            
            drift_percentage = ((current_weight - target_weight) / target_weight * 100) if target_weight > 0 else 0
            
            if abs(drift_percentage) >= 5:  # 5% drift threshold
                drift_signals.append({
                    'symbol': symbol,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'drift_percentage': drift_percentage,
                    'action': 'TRIM' if drift_percentage > 0 else 'BUY',
                    'confidence': min(abs(drift_percentage) / 10, 0.9)  # Higher drift = higher confidence
                })
        
        return drift_signals 