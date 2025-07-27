"""
Chat service for portfolio analysis with RAG and MCP integration.
Provides AI-powered portfolio insights and recommendations.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import OpenAI
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None

@dataclass
class PortfolioContext:
    """Portfolio context for RAG system."""
    holdings: List[Dict]
    summary: Dict
    market_data: Dict
    risk_metrics: Dict
    historical_data: List[Dict]
    sector_analysis: Dict

class ChatService:
    """Service for AI-powered portfolio chat with RAG and MCP."""
    
    def __init__(self, portfolio_service, market_service, llm_service, risk_service):
        """Initialize chat service."""
        self.portfolio_service = portfolio_service
        self.market_service = market_service
        self.llm_service = llm_service
        self.risk_service = risk_service
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Chat history for context
        self.chat_history: List[ChatMessage] = []
        
        # RAG knowledge base
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> Dict[str, Any]:
        """Build comprehensive knowledge base for RAG."""
        return {
            "portfolio_analysis": {
                "description": "Portfolio analysis and optimization techniques",
                "topics": [
                    "sector allocation", "risk management", "diversification",
                    "rebalancing", "position sizing", "performance analysis"
                ]
            },
            "market_analysis": {
                "description": "Market analysis and timing",
                "topics": [
                    "technical analysis", "fundamental analysis", "market timing",
                    "sector rotation", "global macro", "volatility analysis"
                ]
            },
            "investment_strategies": {
                "description": "Investment strategies and approaches",
                "topics": [
                    "value investing", "growth investing", "momentum trading",
                    "dividend investing", "index investing", "active management"
                ]
            },
            "risk_management": {
                "description": "Risk management and portfolio protection",
                "topics": [
                    "VaR calculation", "drawdown management", "correlation analysis",
                    "liquidity management", "hedging strategies", "stop losses"
                ]
            }
        }
    
    def get_portfolio_context(self) -> PortfolioContext:
        """Get comprehensive portfolio context for RAG."""
        try:
            # Get current portfolio data
            holdings = self.portfolio_service.get_holdings()
            summary = self.portfolio_service.get_portfolio_summary()
            market_data = self.market_service.fetch_market_data()
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(holdings, summary)
            
            # Get historical data (last 30 days)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            historical_data = self._get_historical_data(start_date, end_date)
            
            # Sector analysis
            sector_analysis = self._analyze_sectors(holdings)
            
            return PortfolioContext(
                holdings=holdings,
                summary=summary,
                market_data=market_data,
                risk_metrics=risk_metrics,
                historical_data=historical_data,
                sector_analysis=sector_analysis
            )
            
        except Exception as e:
            logger.error(f"Error getting portfolio context: {e}")
            raise
    
    def _calculate_risk_metrics(self, holdings: List[Dict], summary: Dict) -> Dict:
        """Calculate comprehensive risk metrics."""
        try:
            total_value = summary.get('total_value', 0)
            if total_value == 0:
                return {}
            
            # Calculate position concentration
            position_values = [h['quantity'] * h['last_price'] for h in holdings]
            max_position = max(position_values) if position_values else 0
            concentration_risk = max_position / total_value if total_value > 0 else 0
            
            # Calculate sector concentration
            sector_values = {}
            for holding in holdings:
                sector = self._get_sector(holding['trading_symbol'])
                value = holding['quantity'] * holding['last_price']
                sector_values[sector] = sector_values.get(sector, 0) + value
            
            max_sector_weight = max(sector_values.values()) / total_value if sector_values else 0
            
            # Calculate portfolio beta (simplified)
            portfolio_beta = 0.95  # Default to market beta
            
            return {
                'concentration_risk': concentration_risk,
                'max_sector_weight': max_sector_weight,
                'portfolio_beta': portfolio_beta,
                'total_positions': len(holdings),
                'total_value': total_value,
                'risk_score': self._calculate_risk_score(concentration_risk, max_sector_weight)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def _get_sector(self, symbol: str) -> str:
        """Get sector for a given symbol."""
        sector_map = {
            'RELIANCE': 'Oil & Gas', 'TCS': 'IT', 'HDFCBANK': 'Banking',
            'INFY': 'IT', 'ITC': 'FMCG', 'ICICIBANK': 'Banking',
            'HINDUNILVR': 'FMCG', 'SBIN': 'Banking', 'BHARTIARTL': 'Telecom',
            'KOTAKBANK': 'Banking', 'AXISBANK': 'Banking', 'ASIANPAINT': 'Chemicals',
            'MARUTI': 'Automobile', 'SUNPHARMA': 'Pharmaceuticals',
            'TATAMOTORS': 'Automobile', 'WIPRO': 'IT', 'ULTRACEMCO': 'Cement',
            'TITAN': 'Consumer Goods', 'BAJFINANCE': 'NBFC', 'NESTLEIND': 'FMCG',
            'POWERGRID': 'Power', 'NIFTYBEES': 'ETF', 'GOLDBEES': 'ETF',
            'JUNIORBEES': 'ETF'
        }
        return sector_map.get(symbol, 'Others')
    
    def _calculate_risk_score(self, concentration_risk: float, sector_weight: float) -> float:
        """Calculate overall risk score (0-1, higher = riskier)."""
        # Weighted combination of risk factors
        concentration_score = min(concentration_risk * 2, 1.0)  # Scale up concentration risk
        sector_score = min(sector_weight * 1.5, 1.0)  # Scale up sector concentration
        
        # Overall risk score
        risk_score = (concentration_score * 0.6) + (sector_score * 0.4)
        return min(risk_score, 1.0)
    
    def _get_historical_data(self, start_date, end_date) -> List[Dict]:
        """Get historical portfolio data."""
        try:
            # This would typically come from a tracking service
            # For now, return sample data
            return [
                {
                    'date': start_date + timedelta(days=i),
                    'value': 850000 + (i * 1000),
                    'return': 0.05 + (i * 0.001)
                }
                for i in range((end_date - start_date).days + 1)
            ]
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    def _analyze_sectors(self, holdings: List[Dict]) -> Dict:
        """Analyze sector allocation and performance."""
        try:
            sectors = {}
            total_value = sum(h['quantity'] * h['last_price'] for h in holdings)
            
            for holding in holdings:
                sector = self._get_sector(holding['trading_symbol'])
                value = holding['quantity'] * holding['last_price']
                pnl = holding.get('pnl', 0)
                
                if sector not in sectors:
                    sectors[sector] = {
                        'value': 0,
                        'weight': 0,
                        'pnl': 0,
                        'holdings': [],
                        'count': 0
                    }
                
                sectors[sector]['value'] += value
                sectors[sector]['pnl'] += pnl
                sectors[sector]['holdings'].append(holding['trading_symbol'])
                sectors[sector]['count'] += 1
            
            # Calculate weights
            for sector in sectors:
                sectors[sector]['weight'] = sectors[sector]['value'] / total_value if total_value > 0 else 0
                sectors[sector]['return'] = sectors[sector]['pnl'] / sectors[sector]['value'] if sectors[sector]['value'] > 0 else 0
            
            return sectors
            
        except Exception as e:
            logger.error(f"Error analyzing sectors: {e}")
            return {}
    
    def _retrieve_relevant_context(self, query: str, context: PortfolioContext) -> Dict:
        """Retrieve relevant context for RAG system."""
        try:
            # Simple keyword-based retrieval
            query_lower = query.lower()
            relevant_context = {
                'portfolio_summary': context.summary,
                'market_data': context.market_data,
                'risk_metrics': context.risk_metrics,
                'sector_analysis': context.sector_analysis,
                'top_holdings': sorted(context.holdings, 
                                     key=lambda x: x['quantity'] * x['last_price'], 
                                     reverse=True)[:10],
                'knowledge_base': {}
            }
            
            # Add relevant knowledge base sections
            if any(word in query_lower for word in ['risk', 'volatility', 'drawdown']):
                relevant_context['knowledge_base']['risk_management'] = self.knowledge_base['risk_management']
            
            if any(word in query_lower for word in ['sector', 'allocation', 'diversification']):
                relevant_context['knowledge_base']['portfolio_analysis'] = self.knowledge_base['portfolio_analysis']
            
            if any(word in query_lower for word in ['market', 'timing', 'technical']):
                relevant_context['knowledge_base']['market_analysis'] = self.knowledge_base['market_analysis']
            
            if any(word in query_lower for word in ['strategy', 'investment', 'approach']):
                relevant_context['knowledge_base']['investment_strategies'] = self.knowledge_base['investment_strategies']
            
            return relevant_context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {}
    
    def _build_mcp_prompt(self, query: str, context: Dict, chat_history: List[ChatMessage]) -> str:
        """Build MCP (Model Context Protocol) prompt."""
        try:
            # Portfolio context
            portfolio_summary = context.get('portfolio_summary', {})
            market_data = context.get('market_data', {})
            risk_metrics = context.get('risk_metrics', {})
            sector_analysis = context.get('sector_analysis', {})
            top_holdings = context.get('top_holdings', [])
            
            # Build comprehensive context
            context_str = f"""
PORTFOLIO CONTEXT:
Total Value: ₹{portfolio_summary.get('total_value', 0):,.2f}
Total P&L: ₹{portfolio_summary.get('total_pnl', 0):,.2f} ({portfolio_summary.get('total_pnl', 0)/portfolio_summary.get('total_value', 1)*100:.1f}% return)
Number of Holdings: {portfolio_summary.get('total_stocks', 0)}

MARKET CONTEXT:
Nifty 50: ₹{market_data.get('nifty50', {}).get('price', 0):,.2f} ({market_data.get('nifty50', {}).get('change_percent', 0):+.2f}%)
USD/INR: ₹{market_data.get('usdinr', {}).get('price', 0):.2f}

RISK METRICS:
Concentration Risk: {risk_metrics.get('concentration_risk', 0):.1%}
Max Sector Weight: {risk_metrics.get('max_sector_weight', 0):.1%}
Portfolio Beta: {risk_metrics.get('portfolio_beta', 0):.2f}
Risk Score: {risk_metrics.get('risk_score', 0):.2f}

TOP 10 HOLDINGS:
"""
            
            for i, holding in enumerate(top_holdings, 1):
                value = holding['quantity'] * holding['last_price']
                weight = value / portfolio_summary.get('total_value', 1) * 100
                context_str += f"{i:2d}. {holding['trading_symbol']:12s} - ₹{value:8,.2f} ({weight:4.1f}% weight) | P&L: ₹{holding.get('pnl', 0):8,.2f}\n"
            
            context_str += "\nSECTOR ALLOCATION:\n"
            for sector, data in sector_analysis.items():
                context_str += f"- {sector}: {data['weight']:.1%} weight, {data['return']:.1%} return, {data['count']} holdings\n"
            
            # Add chat history for context
            if chat_history:
                context_str += "\nRECENT CONVERSATION CONTEXT:\n"
                for msg in chat_history[-3:]:  # Last 3 messages
                    context_str += f"{msg.role.upper()}: {msg.content}\n"
            
            # Build final prompt
            prompt = f"""
You are an expert portfolio manager and financial advisor with 20+ years of experience in Indian markets. You have access to real-time portfolio data, market information, and comprehensive analysis tools.

Your role is to provide:
1. **Comprehensive Analysis**: Deep insights into portfolio performance, risk, and opportunities
2. **Actionable Recommendations**: Specific, evidence-backed suggestions for portfolio optimization
3. **Risk Assessment**: Clear evaluation of current risk levels and mitigation strategies
4. **Market Context**: Integration of global and domestic market factors
5. **Educational Insights**: Help the user understand complex financial concepts

{context_str}

USER QUESTION: {query}

Please provide a comprehensive, well-reasoned response that includes:
1. **Direct Answer**: Address the user's specific question
2. **Portfolio Context**: Relate your answer to their current portfolio situation
3. **Market Analysis**: Consider current market conditions and trends
4. **Actionable Points**: Provide specific, actionable recommendations
5. **Risk Considerations**: Highlight any risk factors or concerns
6. **Educational Value**: Explain the reasoning behind your recommendations

Format your response in a clear, professional manner with appropriate sections and bullet points where helpful.
"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building MCP prompt: {e}")
            return f"Please analyze my portfolio and answer: {query}"
    
    def chat(self, user_message: str) -> Dict:
        """Process a chat message and return AI response."""
        try:
            # Add user message to history
            user_msg = ChatMessage(
                role='user',
                content=user_message,
                timestamp=datetime.now()
            )
            self.chat_history.append(user_msg)
            
            # Get portfolio context
            context = self.get_portfolio_context()
            
            # Retrieve relevant context for RAG
            relevant_context = self._retrieve_relevant_context(user_message, context)
            
            # Build MCP prompt
            prompt = self._build_mcp_prompt(user_message, relevant_context, self.chat_history)
            
            # Generate AI response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert portfolio manager and financial advisor. Provide comprehensive, actionable portfolio analysis and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            ai_msg = ChatMessage(
                role='assistant',
                content=ai_response,
                timestamp=datetime.now(),
                metadata={
                    'context_used': list(relevant_context.keys()),
                    'model': 'gpt-4o-mini',
                    'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None
                }
            )
            self.chat_history.append(ai_msg)
            
            # Keep only last 20 messages for context
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]
            
            return {
                'response': ai_response,
                'timestamp': datetime.now().isoformat(),
                'context_used': list(relevant_context.keys()),
                'portfolio_summary': context.summary,
                'risk_metrics': context.risk_metrics
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                'response': f"I apologize, but I encountered an error while analyzing your portfolio: {str(e)}. Please try again or contact support if the issue persists.",
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_chat_history(self) -> List[Dict]:
        """Get chat history for the session."""
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.metadata
            }
            for msg in self.chat_history
        ]
    
    def clear_chat_history(self):
        """Clear chat history."""
        self.chat_history = []
    
    def get_portfolio_insights(self) -> Dict:
        """Get automated portfolio insights."""
        try:
            context = self.get_portfolio_context()
            
            insights = {
                'portfolio_summary': context.summary,
                'risk_metrics': context.risk_metrics,
                'sector_analysis': context.sector_analysis,
                'market_data': context.market_data,
                'recommendations': self._generate_automated_recommendations(context),
                'alerts': self._generate_alerts(context)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting portfolio insights: {e}")
            return {'error': str(e)}
    
    def _generate_automated_recommendations(self, context: PortfolioContext) -> List[Dict]:
        """Generate automated portfolio recommendations."""
        try:
            recommendations = []
            
            # Concentration risk alert
            if context.risk_metrics.get('concentration_risk', 0) > 0.05:
                recommendations.append({
                    'type': 'risk',
                    'priority': 'high',
                    'title': 'High Concentration Risk',
                    'description': f"Your largest position represents {context.risk_metrics['concentration_risk']:.1%} of your portfolio. Consider diversifying to reduce concentration risk.",
                    'action': 'Consider reducing position size or adding diversification'
                })
            
            # Sector concentration alert
            if context.risk_metrics.get('max_sector_weight', 0) > 0.25:
                recommendations.append({
                    'type': 'diversification',
                    'priority': 'medium',
                    'title': 'Sector Concentration',
                    'description': f"Your largest sector represents {context.risk_metrics['max_sector_weight']:.1%} of your portfolio. Consider sector diversification.",
                    'action': 'Review sector allocation and consider rebalancing'
                })
            
            # Performance analysis
            total_return = context.summary.get('total_pnl', 0) / context.summary.get('total_value', 1)
            if total_return < 0:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'title': 'Portfolio Underperformance',
                    'description': f"Your portfolio is showing negative returns ({total_return:.1%}). Review holdings and market conditions.",
                    'action': 'Analyze underperforming positions and market timing'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _generate_alerts(self, context: PortfolioContext) -> List[Dict]:
        """Generate portfolio alerts."""
        try:
            alerts = []
            
            # Market volatility alert
            if context.market_data.get('nifty50', {}).get('change_percent', 0) < -2:
                alerts.append({
                    'type': 'market',
                    'severity': 'warning',
                    'message': 'High market volatility detected. Monitor positions closely.',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Currency risk alert
            usd_inr = context.market_data.get('usdinr', {}).get('price', 0)
            if usd_inr > 87:
                alerts.append({
                    'type': 'currency',
                    'severity': 'info',
                    'message': 'USD/INR at elevated levels. Monitor currency impact on international holdings.',
                    'timestamp': datetime.now().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return [] 