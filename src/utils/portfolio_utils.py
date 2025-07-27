"""
Portfolio utility functions.
"""

from typing import Dict, List, Optional
from decimal import Decimal


def calculate_portfolio_value(holdings: List[Dict]) -> float:
    """Calculate total portfolio value from holdings."""
    return sum(
        holding.get('quantity', 0) * holding.get('last_price', 0)
        for holding in holdings
    )


def calculate_drift_percentage(current_weight: float, target_weight: float) -> float:
    """Calculate drift percentage from target weight."""
    if target_weight == 0:
        return 0
    return ((current_weight - target_weight) / target_weight) * 100


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format currency amount with proper formatting."""
    if currency == "INR":
        return f"₹{amount:,.2f}"
    return f"{amount:,.2f}"


def calculate_position_weight(position_value: float, total_portfolio_value: float) -> float:
    """Calculate position weight as percentage of portfolio."""
    if total_portfolio_value == 0:
        return 0
    return (position_value / total_portfolio_value) * 100 