"""
Upstox service for fetching real portfolio data from Upstox API.
"""

import os
import json
import datetime
from typing import Dict, List, Optional
import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Numeric, Text, JSON, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlalchemy import TIMESTAMP
from sqlalchemy.exc import SQLAlchemyError

try:
    import upstox_client
    from upstox_client.rest import ApiException
except ImportError:
    logging.warning("upstox_client not installed. Install with: pip install upstox-python-sdk")

logger = logging.getLogger(__name__)

class UpstoxService:
    """Service for Upstox API operations."""
    
    def __init__(self, database_url: str):
        """Initialize Upstox service."""
        self.database_url = database_url
        self.engine = create_engine(database_url, pool_size=10, max_overflow=20)
        self._setup_database()
    
    def _setup_database(self):
        """Setup database table for Upstox holdings."""
        meta = MetaData(schema=None)
        
        self.holdings_table = Table(
            "holdings", meta,
            Column("isin", Text, primary_key=True),
            Column("cnc_used_quantity", Integer),
            Column("collateral_type", Text),
            Column("company_name", Text),
            Column("haircut", Numeric),
            Column("product", Text),
            Column("quantity", Integer),
            Column("trading_symbol", Text),
            Column("tradingsymbol", Text),
            Column("last_price", Numeric),
            Column("close_price", Numeric),
            Column("pnl", Numeric),
            Column("day_change", Numeric),
            Column("day_change_percentage", Numeric),
            Column("instrument_token", Text),
            Column("average_price", Numeric),
            Column("collateral_quantity", Integer),
            Column("collateral_update_quantity", Integer),
            Column("t1_quantity", Integer),
            Column("exchange", Text),
            Column("fetched_at", TIMESTAMP(timezone=True)),
            Column("raw_json", JSONB),
            Column("created_at", TIMESTAMP(timezone=True)),
            Column("updated_at", TIMESTAMP(timezone=True)),
            extend_existing=True
        )
        
        meta.create_all(self.engine, checkfirst=True)
    
    def get_api_client(self):
        """Get Upstox API client."""
        access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        if not access_token:
            raise RuntimeError("Set UPSTOX_ACCESS_TOKEN in the environment")
        
        cfg = upstox_client.Configuration()
        cfg.access_token = access_token
        return upstox_client.PortfolioApi(upstox_client.ApiClient(cfg))
    
    def fetch_and_store_holdings(self) -> List[Dict]:
        """Fetch holdings from Upstox API and store in database."""
        try:
            api = self.get_api_client()
            logger.info("Fetching holdings from Upstox API...")
            
            # Fetch holdings from Upstox
            response = api.get_holdings("2.0")
            holdings_data = [h.to_dict() for h in response.data]
            
            logger.info(f"Fetched {len(holdings_data)} holdings from Upstox")
            
            # Store in database
            self._upsert_holdings(holdings_data)
            
            return holdings_data
            
        except ApiException as e:
            logger.error(f"Upstox API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching holdings: {e}")
            raise
    
    def _upsert_holdings(self, holdings_data: List[Dict]):
        """Insert or update holdings in database."""
        try:
            # Clear existing data first
            with self.engine.begin() as conn:
                conn.execute(text("DELETE FROM holdings"))
                
                for holding in holdings_data:
                    # Add metadata
                    fetched_at = datetime.datetime.utcnow()
                    
                    # Create a clean copy for JSON storage (remove datetime objects)
                    raw_json = {}
                    for key, value in holding.items():
                        if isinstance(value, datetime.datetime):
                            raw_json[key] = value.isoformat()
                        else:
                            raw_json[key] = value
                    
                    # Simple insert
                    stmt = (
                        insert(self.holdings_table)
                        .values(
                            fetched_at=fetched_at,
                            raw_json=raw_json,
                            **holding
                        )
                    )
                    conn.execute(stmt)
            
            logger.info(f"Successfully stored {len(holdings_data)} holdings in database")
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise
    
    def get_holdings_from_db(self) -> List[Dict]:
        """Get holdings from database."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        isin,
                        trading_symbol,
                        company_name,
                        quantity,
                        average_price,
                        last_price,
                        close_price,
                        pnl,
                        day_change,
                        day_change_percentage,
                        exchange,
                        instrument_token,
                        product,
                        fetched_at
                    FROM holdings 
                    WHERE quantity > 0
                    ORDER BY quantity * last_price DESC
                """))
                
                holdings = []
                for row in result:
                    holding = {
                        'isin': row.isin,
                        'trading_symbol': row.trading_symbol,
                        'company_name': row.company_name,
                        'quantity': row.quantity,
                        'average_price': float(row.average_price) if row.average_price else 0,
                        'last_price': float(row.last_price) if row.last_price else 0,
                        'close_price': float(row.close_price) if row.close_price else 0,
                        'pnl': float(row.pnl) if row.pnl else 0,
                        'day_change': float(row.day_change) if row.day_change else 0,
                        'day_change_percentage': float(row.day_change_percentage) if row.day_change_percentage else 0,
                        'exchange': row.exchange,
                        'instrument_token': row.instrument_token,
                        'product': row.product,
                        'fetched_at': row.fetched_at.isoformat() if row.fetched_at else None
                    }
                    holdings.append(holding)
                
                return holdings
                
        except Exception as e:
            logger.error(f"Error fetching holdings from database: {e}")
            return []
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary from database."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT 
                        COUNT(*) as total_stocks,
                        SUM(quantity * last_price) as total_value,
                        SUM(pnl) as total_pnl,
                        SUM(day_change) as total_day_change
                    FROM holdings 
                    WHERE last_price IS NOT NULL AND quantity > 0
                    """)
                )
                
                row = result.fetchone()
                if row is None:
                    return {
                        'total_stocks': 0,
                        'total_value': 0,
                        'total_pnl': 0,
                        'total_day_change': 0
                    }
                
                return {
                    'total_stocks': row.total_stocks or 0,
                    'total_value': float(row.total_value) if row.total_value else 0,
                    'total_pnl': float(row.total_pnl) if row.total_pnl else 0,
                    'total_day_change': float(row.total_day_change) if row.total_day_change else 0
                }
                
        except Exception as e:
            logger.error(f"Error fetching portfolio summary: {e}")
            return {
                'total_stocks': 0,
                'total_value': 0,
                'total_pnl': 0,
                'total_day_change': 0
            } 