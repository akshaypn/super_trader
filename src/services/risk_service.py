"""
Risk service for portfolio risk management.
"""

from typing import Dict, List, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class RiskService:
    """Service for risk management operations."""
    
    def __init__(self, max_position_size_pct: float = 0.05, max_drawdown: float = 0.20):
        """Initialize risk service."""
        self.max_position_size_pct = max_position_size_pct
        self.max_drawdown = max_drawdown
    
    def apply_risk_gates(self, trade_ideas: List[Dict], portfolio_data: Dict) -> List[Dict]:
        """Apply risk gates to filter trade ideas."""
        filtered_ideas = []
        total_portfolio_value = portfolio_data.get('total_value', 0)
        
        for idea in trade_ideas:
            if self._passes_risk_gates(idea, total_portfolio_value):
                filtered_ideas.append(idea)
            else:
                logger.info(f"Trade idea {idea['symbol']} rejected by risk gates")
        
        return filtered_ideas
    
    def _passes_risk_gates(self, trade_idea: Dict, total_portfolio_value: float) -> bool:
        """Check if trade idea passes risk gates."""
        if total_portfolio_value <= 0:
            return False
        
        # Position size check
        position_value = trade_idea['quantity'] * trade_idea['limit_price']
        position_size_pct = position_value / total_portfolio_value
        
        if position_size_pct > self.max_position_size_pct:
            logger.warning(f"Position size {position_size_pct:.2%} exceeds maximum {self.max_position_size_pct:.2%}")
            return False
        
        # Confidence score check
        if trade_idea.get('confidence', 0) < 0.5:
            logger.warning(f"Confidence score {trade_idea.get('confidence', 0):.2f} below threshold 0.5")
            return False
        
        return True
    
    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk."""
        if not returns:
            return 0
        
        try:
            returns_array = np.array(returns)
            var_percentile = (1 - confidence_level) * 100
            return np.percentile(returns_array, var_percentile)
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0
    
    def check_drawdown_limit(self, current_pnl: float, total_value: float) -> bool:
        """Check if current drawdown is within limits."""
        if total_value <= 0:
            return True
        
        current_drawdown = abs(current_pnl) / total_value
        return current_drawdown <= self.max_drawdown
    
    def calculate_portfolio_risk_metrics(self, holdings: List[Dict]) -> Dict:
        """Calculate portfolio risk metrics."""
        if not holdings:
            return {
                'total_value': 0,
                'var_95': 0,
                'max_position_size': 0,
                'concentration_risk': 0
            }
        
        total_value = sum(h['quantity'] * h['last_price'] for h in holdings)
        
        # Calculate position sizes
        position_sizes = []
        for holding in holdings:
            position_value = holding['quantity'] * holding['last_price']
            if total_value > 0:
                position_sizes.append(position_value / total_value)
        
        # Calculate concentration risk (Herfindahl index)
        concentration_risk = sum(size ** 2 for size in position_sizes) if position_sizes else 0
        
        return {
            'total_value': total_value,
            'var_95': 0,  # Would need historical data for proper VaR
            'max_position_size': max(position_sizes) if position_sizes else 0,
            'concentration_risk': concentration_risk
        } 