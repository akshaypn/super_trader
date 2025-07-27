"""
Market utility functions.
"""

import yfinance as yf
from typing import Dict, Optional
from datetime import datetime, timedelta


def get_stock_price(symbol: str, exchange: str = "NSE") -> Optional[float]:
    """Get current stock price using yfinance."""
    try:
        # Add exchange suffix for Indian stocks
        if exchange == "NSE":
            ticker = f"{symbol}.NS"
        else:
            ticker = symbol
            
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('regularMarketPrice')
    except Exception:
        return None


def calculate_var(returns: list, confidence_level: float = 0.95) -> float:
    """Calculate Value at Risk."""
    if not returns:
        return 0
    
    import numpy as np
    returns_array = np.array(returns)
    var_percentile = (1 - confidence_level) * 100
    return np.percentile(returns_array, var_percentile)


def get_market_data(symbols: list, period: str = "1d") -> Dict:
    """Get market data for multiple symbols."""
    market_data = {}
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(period=period)
            
            if not hist.empty:
                market_data[symbol] = {
                    'close': hist['Close'].iloc[-1],
                    'volume': hist['Volume'].iloc[-1],
                    'change': hist['Close'].iloc[-1] - hist['Open'].iloc[0],
                    'change_percent': ((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
                }
        except Exception:
            continue
    
    return market_data 