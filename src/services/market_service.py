"""
Market service for fetching and processing market data.
"""

import yfinance as yf
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketService:
    """Service for market data operations."""
    
    def __init__(self):
        """Initialize market service."""
        pass
    
    def fetch_market_data(self) -> Dict:
        """Fetch current market data."""
        try:
            market_data = {
                "nifty_50": self._get_index_data("^NSEI"),
                "sensex": self._get_index_data("^BSESN"),
                "usd_inr": self._get_forex_data("USDINR=X"),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Market data fetched successfully")
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            # Return fallback data
            return {
                "nifty_50": {"close": 22000, "change": 0.5},
                "sensex": {"close": 73000, "change": 0.3},
                "usd_inr": {"rate": 83.5, "change": -0.1},
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_index_data(self, symbol: str) -> Dict:
        """Get index data for a given symbol."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close > 0 else 0
            
            return {
                "close": current_price,
                "change": change_percent,
                "volume": info.get('volume', 0)
            }
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return {"close": 0, "change": 0, "volume": 0}
    
    def _get_forex_data(self, symbol: str) -> Dict:
        """Get forex data for a given symbol."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_rate = info.get('regularMarketPrice', 0)
            previous_rate = info.get('previousClose', current_rate)
            change = current_rate - previous_rate
            change_percent = (change / previous_rate * 100) if previous_rate > 0 else 0
            
            return {
                "rate": current_rate,
                "change": change_percent
            }
            
        except Exception as e:
            logger.error(f"Error fetching forex data for {symbol}: {e}")
            return {"rate": 83.5, "change": 0}
    
    def get_stock_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current stock prices for multiple symbols."""
        prices = {}
        
        for symbol in symbols:
            try:
                # Add .NS suffix for Indian stocks
                ticker_symbol = f"{symbol}.NS"
                ticker = yf.Ticker(ticker_symbol)
                price = ticker.info.get('regularMarketPrice')
                
                if price:
                    prices[symbol] = price
                    
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")
                continue
        
        return prices 