"""
Tracking service for portfolio changes and historical performance.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, date
from sqlalchemy import create_engine, text, insert, update
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class TrackingService:
    """Service for tracking portfolio changes and performance."""
    
    def __init__(self, database_url: str):
        """Initialize tracking service."""
        self.database_url = database_url
        self.engine = create_engine(database_url)
    
    def save_portfolio_snapshot(self, portfolio_data: Dict) -> bool:
        """Save daily portfolio snapshot."""
        try:
            with self.engine.begin() as conn:
                stmt = insert(text("portfolio_snapshots")).values(
                    date=date.today(),
                    total_value=portfolio_data.get('total_value', 0),
                    total_pnl=portfolio_data.get('total_pnl', 0),
                    total_stocks=portfolio_data.get('total_stocks', 0),
                    cash_balance=portfolio_data.get('cash_balance', 0)
                )
                conn.execute(stmt)
            
            logger.info(f"Portfolio snapshot saved for {date.today()}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving portfolio snapshot: {e}")
            return False
    
    def save_market_data(self, market_data: Dict) -> bool:
        """Save daily market data."""
        try:
            with self.engine.begin() as conn:
                stmt = insert(text("market_data")).values(
                    date=date.today(),
                    nifty_50_close=market_data.get('nifty_50', {}).get('close', 0),
                    nifty_50_change=market_data.get('nifty_50', {}).get('change', 0),
                    sensex_close=market_data.get('sensex', {}).get('close', 0),
                    sensex_change=market_data.get('sensex', {}).get('change', 0),
                    usd_inr_rate=market_data.get('usd_inr', {}).get('rate', 0),
                    vix=market_data.get('vix', 0)
                )
                conn.execute(stmt)
            
            logger.info(f"Market data saved for {date.today()}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving market data: {e}")
            return False
    
    def save_trade_recommendations(self, recommendations: List[Dict]) -> List[int]:
        """Save trade recommendations and return their IDs."""
        recommendation_ids = []
        
        try:
            with self.engine.begin() as conn:
                for rec in recommendations:
                    stmt = insert(text("trade_recommendations")).values(
                        date=date.today(),
                        action=rec['action'],
                        symbol=rec['symbol'],
                        quantity=rec['quantity'],
                        limit_price=rec['limit_price'],
                        confidence=rec['confidence'],
                        rationale=rec['rationale'],
                        instrument_token=rec.get('instrument_token', f"NSE_EQ|{rec['symbol']}")
                    )
                    result = conn.execute(stmt)
                    recommendation_ids.append(result.inserted_primary_key[0])
            
            logger.info(f"Saved {len(recommendations)} trade recommendations")
            return recommendation_ids
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving trade recommendations: {e}")
            return []
    
    def track_portfolio_changes(self, current_holdings: List[Dict], previous_holdings: List[Dict]) -> Dict:
        """Track changes in portfolio holdings."""
        changes = {
            'new_positions': [],
            'exited_positions': [],
            'quantity_changes': [],
            'value_changes': []
        }
        
        # Create dictionaries for easy lookup
        current_dict = {h['trading_symbol']: h for h in current_holdings}
        previous_dict = {h['trading_symbol']: h for h in previous_holdings}
        
        # Find new positions
        for symbol, holding in current_dict.items():
            if symbol not in previous_dict:
                changes['new_positions'].append({
                    'symbol': symbol,
                    'quantity': holding['quantity'],
                    'value': holding['quantity'] * holding['last_price']
                })
        
        # Find exited positions
        for symbol, holding in previous_dict.items():
            if symbol not in current_dict:
                changes['exited_positions'].append({
                    'symbol': symbol,
                    'quantity': holding['quantity'],
                    'value': holding['quantity'] * holding['last_price']
                })
        
        # Find quantity changes
        for symbol, current in current_dict.items():
            if symbol in previous_dict:
                previous = previous_dict[symbol]
                if current['quantity'] != previous['quantity']:
                    changes['quantity_changes'].append({
                        'symbol': symbol,
                        'previous_quantity': previous['quantity'],
                        'current_quantity': current['quantity'],
                        'change': current['quantity'] - previous['quantity']
                    })
        
        logger.info(f"Portfolio changes tracked: {len(changes['new_positions'])} new, {len(changes['exited_positions'])} exited")
        return changes
    
    def get_previous_portfolio_snapshot(self) -> Optional[Dict]:
        """Get the most recent portfolio snapshot."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT total_value, total_pnl, total_stocks, cash_balance, date
                    FROM portfolio_snapshots 
                    WHERE date < CURRENT_DATE
                    ORDER BY date DESC 
                    LIMIT 1
                """))
                row = result.fetchone()
                
                if row:
                    return {
                        'total_value': float(row.total_value),
                        'total_pnl': float(row.total_pnl),
                        'total_stocks': row.total_stocks,
                        'cash_balance': float(row.cash_balance) if row.cash_balance else 0,
                        'date': row.date
                    }
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting previous portfolio snapshot: {e}")
            return None
    
    def get_recommendation_history(self, days: int = 30) -> List[Dict]:
        """Get recommendation history for the last N days."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        date, action, symbol, quantity, limit_price, 
                        confidence, status, pnl, rationale
                    FROM trade_recommendations 
                    WHERE date >= CURRENT_DATE - INTERVAL ':days days'
                    ORDER BY date DESC, confidence DESC
                """), {'days': days})
                
                recommendations = []
                for row in result:
                    recommendations.append({
                        'date': row.date,
                        'action': row.action,
                        'symbol': row.symbol,
                        'quantity': row.quantity,
                        'limit_price': float(row.limit_price),
                        'confidence': float(row.confidence),
                        'status': row.status,
                        'pnl': float(row.pnl) if row.pnl else None,
                        'rationale': row.rationale
                    })
                
                return recommendations
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting recommendation history: {e}")
            return []
    
    def update_recommendation_status(self, recommendation_id: int, status: str, execution_price: float = None) -> bool:
        """Update recommendation execution status."""
        try:
            with self.engine.begin() as conn:
                stmt = update(text("trade_recommendations")).where(
                    text("id = :id")
                ).values(
                    status=status,
                    execution_price=execution_price,
                    execution_time=datetime.now() if status == 'executed' else None
                )
                conn.execute(stmt, {'id': recommendation_id})
            
            logger.info(f"Updated recommendation {recommendation_id} status to {status}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating recommendation status: {e}")
            return False
    
    def calculate_performance_metrics(self, portfolio_data: Dict, market_data: Dict) -> Dict:
        """Calculate daily performance metrics."""
        try:
            # Get previous day's data
            previous_snapshot = self.get_previous_portfolio_snapshot()
            
            if not previous_snapshot:
                return {
                    'portfolio_return': 0.0,
                    'benchmark_return': market_data.get('nifty_50', {}).get('change', 0),
                    'alpha': 0.0,
                    'beta': 1.0,
                    'sharpe_ratio': 0.0,
                    'max_drawdown': 0.0,
                    'win_rate': 0.0,
                    'total_trades': 0,
                    'profitable_trades': 0
                }
            
            # Calculate portfolio return
            current_value = portfolio_data.get('total_value', 0)
            previous_value = previous_snapshot['total_value']
            
            if previous_value > 0:
                portfolio_return = (current_value - previous_value) / previous_value * 100
            else:
                portfolio_return = 0.0
            
            # Get benchmark return
            benchmark_return = market_data.get('nifty_50', {}).get('change', 0)
            
            # Calculate alpha (excess return)
            alpha = portfolio_return - benchmark_return
            
            # Get recent recommendations for win rate calculation
            recent_recommendations = self.get_recommendation_history(7)
            executed_recommendations = [r for r in recent_recommendations if r['status'] == 'executed']
            
            total_trades = len(executed_recommendations)
            profitable_trades = len([r for r in executed_recommendations if r['pnl'] and r['pnl'] > 0])
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0.0
            
            metrics = {
                'portfolio_return': portfolio_return,
                'benchmark_return': benchmark_return,
                'alpha': alpha,
                'beta': 1.0,  # Simplified - would need historical data for proper calculation
                'sharpe_ratio': 0.0,  # Would need risk-free rate and volatility
                'max_drawdown': 0.0,  # Would need historical data
                'win_rate': win_rate,
                'total_trades': total_trades,
                'profitable_trades': profitable_trades
            }
            
            # Save metrics
            self.save_performance_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def save_performance_metrics(self, metrics: Dict) -> bool:
        """Save performance metrics to database."""
        try:
            with self.engine.begin() as conn:
                stmt = insert(text("performance_metrics")).values(
                    date=date.today(),
                    portfolio_return=metrics.get('portfolio_return', 0),
                    benchmark_return=metrics.get('benchmark_return', 0),
                    alpha=metrics.get('alpha', 0),
                    beta=metrics.get('beta', 1.0),
                    sharpe_ratio=metrics.get('sharpe_ratio', 0),
                    max_drawdown=metrics.get('max_drawdown', 0),
                    win_rate=metrics.get('win_rate', 0),
                    total_trades=metrics.get('total_trades', 0),
                    profitable_trades=metrics.get('profitable_trades', 0)
                )
                conn.execute(stmt)
            
            logger.info(f"Performance metrics saved for {date.today()}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving performance metrics: {e}")
            return False
    
    def get_daily_summary(self, start_date=None, end_date=None) -> List[Dict]:
        """Get daily portfolio summary for a date range."""
        try:
            query = """
                SELECT 
                    ps.date,
                    ps.total_value,
                    ps.total_pnl,
                    ps.total_stocks,
                    pm.portfolio_return,
                    pm.benchmark_return,
                    pm.alpha,
                    pm.sharpe_ratio,
                    COUNT(tr.id) as recommendations_count,
                    COUNT(CASE WHEN tr.status = 'executed' THEN 1 END) as executed_count
                FROM portfolio_snapshots ps
                LEFT JOIN performance_metrics pm ON ps.date = pm.date
                LEFT JOIN trade_recommendations tr ON ps.date = tr.date
            """
            
            params = {}
            if start_date and end_date:
                query += " WHERE ps.date BETWEEN :start_date AND :end_date"
                params = {'start_date': start_date, 'end_date': end_date}
            
            query += " GROUP BY ps.date, ps.total_value, ps.total_pnl, ps.total_stocks, pm.portfolio_return, pm.benchmark_return, pm.alpha, pm.sharpe_ratio ORDER BY ps.date DESC"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                return [dict(row) for row in result]
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting daily summary: {e}")
            return []

    def get_portfolio_snapshot(self, date) -> Optional[Dict]:
        """Get portfolio snapshot for a specific date."""
        try:
            query = "SELECT * FROM portfolio_snapshots WHERE date = :date"
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'date': date})
                row = result.fetchone()
                return dict(row) if row else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting portfolio snapshot: {e}")
            return None

    def get_trade_recommendations(self, date) -> List[Dict]:
        """Get trade recommendations for a specific date."""
        try:
            query = "SELECT * FROM trade_recommendations WHERE date = :date ORDER BY confidence DESC"
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'date': date})
                return [dict(row) for row in result]
        except SQLAlchemyError as e:
            logger.error(f"Error getting trade recommendations: {e}")
            return []

    def get_market_data(self, date) -> Optional[Dict]:
        """Get market data for a specific date."""
        try:
            query = "SELECT * FROM market_data WHERE date = :date"
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'date': date})
                row = result.fetchone()
                return dict(row) if row else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting market data: {e}")
            return None

    def get_performance_metrics(self, date) -> Optional[Dict]:
        """Get performance metrics for a specific date."""
        try:
            query = "SELECT * FROM performance_metrics WHERE date = :date"
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'date': date})
                row = result.fetchone()
                return dict(row) if row else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting performance metrics: {e}")
            return None 