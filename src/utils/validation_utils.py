"""
Validation utility functions.
"""

from typing import Dict, List, Optional
from decimal import Decimal


def validate_trade_idea(trade_idea: Dict) -> tuple[bool, str]:
    """Validate a trade idea."""
    required_fields = ['action', 'symbol', 'quantity', 'limit_price']
    
    # Check required fields
    for field in required_fields:
        if field not in trade_idea:
            return False, f"Missing required field: {field}"
    
    # Validate action
    if trade_idea['action'] not in ['BUY', 'SELL', 'HOLD']:
        return False, "Invalid action. Must be BUY, SELL, or HOLD"
    
    # Validate quantity
    if trade_idea['action'] != 'HOLD' and trade_idea['quantity'] <= 0:
        return False, "Quantity must be positive for BUY/SELL actions"
    
    # Validate price
    if trade_idea['limit_price'] <= 0:
        return False, "Limit price must be positive"
    
    # Validate confidence score
    confidence = trade_idea.get('confidence_score', 0)
    if not (0 <= confidence <= 1):
        return False, "Confidence score must be between 0 and 1"
    
    return True, "Trade idea is valid"


def validate_portfolio_config(config: Dict) -> tuple[bool, str]:
    """Validate portfolio configuration."""
    required_fields = [
        'investor_id', 'monthly_inflow', 'risk_profile', 
        'target_eq_weight', 'max_drawdown'
    ]
    
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    # Validate risk profile
    if config['risk_profile'] not in ['conservative', 'moderate', 'aggressive']:
        return False, "Invalid risk profile"
    
    # Validate weights
    if not (0 <= config['target_eq_weight'] <= 1):
        return False, "Target equity weight must be between 0 and 1"
    
    if not (0 <= config['max_drawdown'] <= 1):
        return False, "Max drawdown must be between 0 and 1"
    
    return True, "Configuration is valid"


def validate_holdings_data(holdings: List[Dict]) -> tuple[bool, str]:
    """Validate holdings data structure."""
    if not isinstance(holdings, list):
        return False, "Holdings must be a list"
    
    required_fields = ['isin', 'trading_symbol', 'quantity', 'last_price']
    
    for i, holding in enumerate(holdings):
        for field in required_fields:
            if field not in holding:
                return False, f"Holding {i} missing required field: {field}"
        
        # Validate quantity
        if holding['quantity'] < 0:
            return False, f"Holding {i} has negative quantity"
        
        # Validate price
        if holding['last_price'] < 0:
            return False, f"Holding {i} has negative price"
    
    return True, "Holdings data is valid" 