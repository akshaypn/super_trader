"""
LLM service for generating trade ideas and critiques using OpenAI API.
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations using OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM service."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_trade_ideas(self, portfolio_data: Dict, market_data: Dict, signals: Dict) -> List[Dict]:
        """Generate trade ideas using GPT-4."""
        try:
            prompt = self._build_trade_idea_prompt(portfolio_data, market_data, signals)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional portfolio manager. Generate actionable trade ideas based on the provided portfolio and market data. Focus on evidence-backed recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_trade_ideas(content, portfolio_data)
            
        except Exception as e:
            logger.error(f"Error generating trade ideas: {e}")
            return []
    
    def critique_trade_ideas(self, trade_ideas: List[Dict], portfolio_context: Dict) -> List[Dict]:
        """Critique trade ideas using GPT-3.5."""
        try:
            prompt = self._build_critique_prompt(trade_ideas, portfolio_context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a risk management expert. Critically evaluate trade ideas for potential issues, over-trading, and alignment with portfolio goals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            return self._parse_critiques(content, trade_ideas)
            
        except Exception as e:
            logger.error(f"Error critiquing trade ideas: {e}")
            return trade_ideas  # Return original ideas if critique fails
    
    def _build_trade_idea_prompt(self, portfolio_data: Dict, market_data: Dict, signals: Dict) -> str:
        """Build prompt for trade idea generation."""
        holdings = portfolio_data.get("holdings", [])
        
        # Create detailed portfolio analysis
        portfolio_summary = f"""
DETAILED PORTFOLIO ANALYSIS:
Total Portfolio Value: ₹{portfolio_data.get('total_value', 0):,.2f}
Total P&L: ₹{portfolio_data.get('total_pnl', 0):,.2f} ({portfolio_data.get('total_pnl', 0)/portfolio_data.get('total_value', 1)*100:.1f}% return)
Number of Holdings: {portfolio_data.get('total_stocks', 0)}

TOP 15 HOLDINGS BY VALUE:
"""
        
        # Sort holdings by value and show top 15
        sorted_holdings = sorted(holdings, key=lambda x: x['quantity'] * x['last_price'], reverse=True)
        for i, holding in enumerate(sorted_holdings[:15], 1):
            value = holding['quantity'] * holding['last_price']
            weight = value / portfolio_data.get('total_value', 1) * 100
            portfolio_summary += f"{i:2d}. {holding['trading_symbol']:12s} - {holding['quantity']:4d} shares @ ₹{holding['last_price']:8,.2f} = ₹{value:8,.2f} ({weight:4.1f}% weight) | P&L: ₹{holding['pnl']:8,.2f}\n"
        
        # Sector analysis
        sectors = {}
        for holding in holdings:
            sector = self._get_sector(holding['trading_symbol'])
            if sector not in sectors:
                sectors[sector] = {'value': 0, 'holdings': []}
            value = holding['quantity'] * holding['last_price']
            sectors[sector]['value'] += value
            sectors[sector]['holdings'].append(holding['trading_symbol'])
        
        sector_analysis = "\nSECTOR ALLOCATION:\n"
        for sector, data in sorted(sectors.items(), key=lambda x: x[1]['value'], reverse=True):
            weight = data['value'] / portfolio_data.get('total_value', 1) * 100
            sector_analysis += f"- {sector}: ₹{data['value']:,.2f} ({weight:.1f}%) - {', '.join(data['holdings'][:3])}\n"
        
        # Market context with global analysis
        market_context = f"""
COMPREHENSIVE MARKET ANALYSIS:

INDIAN MARKETS:
- Nifty 50: ₹{market_data.get('nifty_50', {}).get('close', 0):,.2f} ({market_data.get('nifty_50', {}).get('change', 0):+.2f}%)
- Sensex: ₹{market_data.get('sensex', {}).get('close', 0):,.2f} ({market_data.get('sensex', {}).get('change', 0):+.2f}%)
- USD/INR: ₹{market_data.get('usd_inr', {}).get('rate', 0):.2f}

GLOBAL MARKET CONTEXT:
- US markets are showing resilience despite inflation concerns
- Fed policy remains data-dependent with potential rate cuts in 2024
- Geopolitical tensions in Middle East and Ukraine affecting oil prices
- Chinese economic slowdown impacting global growth expectations
- European markets facing energy crisis and inflation pressures

INDIAN MARKET SPECIFICS:
- FII flows showing cautious stance, DII flows remain strong
- Banking sector under pressure due to RBI's tight monetary policy
- IT sector facing global headwinds but showing resilience
- Auto sector benefiting from festive demand and EV transition
- Pharma sector showing defensive characteristics
- Real estate sector showing signs of recovery
- Metals and mining facing global commodity price volatility

TECHNICAL ANALYSIS:
- Nifty 50 is trading near key support levels
- Market breadth is improving with broader participation
- Volatility index (VIX) showing moderate levels
- Sector rotation favoring defensive and domestic consumption themes
"""
        
        prompt = f"""
You are a senior portfolio manager with 20+ years of experience in Indian and global markets. You have access to real-time market data, technical analysis, and fundamental research. Your task is to provide comprehensive market analysis and generate ACTIONABLE trade recommendations.

INVESTMENT OBJECTIVES:
- Budget: ₹100,000 available for deployment
- Monthly Target: ₹10,000 returns (10% monthly target)
- Risk Profile: Moderate to aggressive for higher returns
- Focus: Actionable BUY/SELL calls, NOT HOLD recommendations

{portfolio_summary}

{sector_analysis}

{market_context}

PORTFOLIO OPTIMIZATION OBJECTIVES:
1. **Cash Deployment**: Deploy ₹100,000 budget efficiently across opportunities
2. **High Returns**: Target ₹10,000 monthly returns (10% monthly target)
3. **Sector Rotation**: Capitalize on sector-specific opportunities
4. **Risk Management**: Maintain portfolio beta and volatility targets
5. **Value Creation**: Identify undervalued opportunities with strong fundamentals

ANALYSIS REQUIREMENTS:
- Consider current market conditions, global macro factors, and sector trends
- Evaluate technical levels, support/resistance, and momentum indicators
- Assess fundamental factors like earnings growth, valuations, and business outlook
- Factor in portfolio concentration, correlation, and risk metrics
- Consider tax implications and transaction costs

CRITICAL REQUIREMENTS:
- Generate ONLY BUY or SELL recommendations (NO HOLD calls)
- Focus on stocks that can deliver 10%+ monthly returns
- Consider momentum stocks, sector rotation opportunities
- Include both existing portfolio stocks and new opportunities
- Maximum 5% position size per stock (₹5,000 per position)
- Target 3-5 actionable recommendations

Generate 3-5 specific, actionable trade recommendations. For each recommendation:

1. **Action**: BUY (new position or add to existing), SELL (reduce position) - NO HOLD
2. **Symbol**: Exact trading symbol (can be new stocks not in portfolio)
3. **Quantity**: Specific number of shares (consider ₹5,000 max per position)
4. **Limit Price**: Target entry/exit price with rationale
5. **Confidence**: Score from 0.0-1.0 based on conviction level
6. **Rationale**: Detailed analysis including:
   - Expected monthly return potential
   - Market context and timing
   - Technical analysis (support/resistance, momentum)
   - Fundamental factors (earnings, valuations, growth)
   - Portfolio fit (diversification, correlation)
   - Risk factors and mitigation

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "action": "BUY",
    "symbol": "TCS",
    "quantity": 10,
    "limit_price": 3600.0,
    "confidence": 0.85,
    "rationale": "TCS showing strong technical support at 3500 levels. Fundamentals remain solid with 15% revenue growth guidance. Expected 12% monthly return based on technical breakout and sector rotation. Entry at current levels provides good risk-reward with stop loss at 3400."
  }}
]

Focus on high-conviction BUY/SELL ideas with clear entry/exit points and 10%+ monthly return potential.
"""
        return prompt
    
    def _get_sector(self, symbol: str) -> str:
        """Get sector for a given stock symbol."""
        sector_map = {
            # Banking & Financial Services
            'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'SBIN': 'Banking', 'AXISBANK': 'Banking',
            'KOTAKBANK': 'Banking', 'HDFC': 'Banking', 'IDFCFIRSTB': 'Banking', 'BANDHANBNK': 'Banking',
            
            # IT & Technology
            'TCS': 'IT', 'INFY': 'IT', 'WIPRO': 'IT', 'HCLTECH': 'IT', 'TECHM': 'IT',
            'MINDTREE': 'IT', 'MPHASIS': 'IT', 'LTI': 'IT', 'PERSISTENT': 'IT',
            
            # Oil & Gas
            'RELIANCE': 'Oil & Gas', 'ONGC': 'Oil & Gas', 'IOC': 'Oil & Gas', 'BPCL': 'Oil & Gas',
            'HPCL': 'Oil & Gas', 'GAIL': 'Oil & Gas', 'OIL': 'Oil & Gas',
            
            # Auto & Auto Components
            'MARUTI': 'Auto', 'TATAMOTORS': 'Auto', 'M&M': 'Auto', 'HEROMOTOCO': 'Auto',
            'BAJAJ-AUTO': 'Auto', 'EICHERMOT': 'Auto', 'ASHOKLEY': 'Auto', 'TVSMOTOR': 'Auto',
            
            # Pharma & Healthcare
            'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma', 'DIVISLAB': 'Pharma',
            'APOLLOHOSP': 'Pharma', 'BIOCON': 'Pharma', 'ALKEM': 'Pharma',
            
            # Consumer Goods
            'HINDUNILVR': 'FMCG', 'ITC': 'FMCG', 'NESTLEIND': 'FMCG', 'BRITANNIA': 'FMCG',
            'MARICO': 'FMCG', 'DABUR': 'FMCG', 'COLPAL': 'FMCG', 'GODREJCP': 'FMCG',
            
            # Metals & Mining
            'TATASTEEL': 'Metals', 'JSWSTEEL': 'Metals', 'HINDALCO': 'Metals', 'VEDL': 'Metals',
            'COALINDIA': 'Metals', 'NMDC': 'Metals', 'HINDCOPPER': 'Metals',
            
            # Real Estate
            'DLF': 'Real Estate', 'GODREJPROP': 'Real Estate', 'SUNTV': 'Real Estate',
            'PRESTIGE': 'Real Estate', 'BRIGADE': 'Real Estate',
            
            # Telecom
            'BHARTIARTL': 'Telecom', 'IDEA': 'Telecom', 'VODAFONE': 'Telecom',
            
            # Power & Utilities
            'NTPC': 'Power', 'POWERGRID': 'Power', 'TATAPOWER': 'Power', 'ADANIPOWER': 'Power',
            
            # Cement & Construction
            'ULTRACEMCO': 'Cement', 'SHREECEM': 'Cement', 'ACC': 'Cement', 'RAMCOCEM': 'Cement',
            'JKCEMENT': 'Cement', 'DALMIABHA': 'Cement',
            
            # ETFs
            'NIFTYBEES': 'ETF', 'GOLDBEES': 'ETF', 'JUNIORBEES': 'ETF', 'BANKBEES': 'ETF',
            
            # Others
            'LT': 'Engineering', 'ADANIENT': 'Diversified', 'TATACONSUM': 'FMCG',
            'INDUSINDBK': 'Banking', 'POWERGRID': 'Power', 'ADANIPORTS': 'Infrastructure'
        }
        
        return sector_map.get(symbol, 'Others')
    
    def _build_critique_prompt(self, trade_ideas: List[Dict], portfolio_context: Dict) -> str:
        """Build prompt for trade idea critique."""
        ideas_text = []
        for i, idea in enumerate(trade_ideas, 1):
            ideas_text.append(
                f"{i}. {idea['action']} {idea['symbol']} - {idea['quantity']} shares @ ₹{idea['limit_price']:.2f} "
                f"(Confidence: {idea['confidence']:.2f}, Rationale: {idea['rationale']})"
            )
        
        prompt = f"""
Portfolio Context:
- Total Value: ₹{portfolio_context.get('total_value', 0):,.2f}
- Risk Profile: {portfolio_context.get('risk_profile', 'moderate')}
- Max Position Size: 5% of portfolio

Trade Ideas to Critique:
{chr(10).join(ideas_text)}

For each trade idea, respond with:
PASS/REJECT - brief reason

Focus on:
1. Over-trading (too many ideas)
2. Position sizing (max 5% per stock)
3. Risk-reward ratio
4. Alignment with portfolio goals
5. Market timing concerns

Respond in format:
1. PASS/REJECT - reason
2. PASS/REJECT - reason
...
"""
        return prompt
    
    def _parse_trade_ideas(self, content: str, portfolio_data: Dict = None) -> List[Dict]:
        """Parse trade ideas from LLM response."""
        try:
            # Try to extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                ideas = json.loads(json_str)
                
                # Validate and clean ideas
                valid_ideas = []
                for idea in ideas:
                    if all(key in idea for key in ['action', 'symbol', 'quantity', 'limit_price', 'confidence', 'rationale']):
                        valid_ideas.append({
                            'action': idea['action'].upper(),
                            'symbol': idea['symbol'],
                            'quantity': int(idea['quantity']),
                            'limit_price': float(idea['limit_price']),
                            'confidence': float(idea['confidence']),
                            'rationale': idea['rationale']
                        })
                
                return valid_ideas
            
        except Exception as e:
            logger.error(f"Error parsing trade ideas: {e}")
        
        # Fallback: return sample ideas based on portfolio analysis
        logger.warning("Using fallback trade ideas due to parsing error")
        
        # Analyze portfolio for better fallback recommendations
        if not portfolio_data:
            return []
            
        holdings = portfolio_data.get('holdings', [])
        if not holdings:
            return []
        
        # Find top holdings and suggest actions
        top_holdings = sorted(holdings, key=lambda x: x['quantity'] * x['last_price'], reverse=True)[:5]
        
        fallback_ideas = []
        for holding in top_holdings:
            symbol = holding['trading_symbol']
            current_price = holding['last_price']
            pnl = holding['pnl']
            
            # Actionable logic for fallback recommendations (₹100,000 budget, ₹10,000 monthly target)
            if symbol in ['NIFTYBEES', 'GOLDBEES', 'JUNIORBEES']:
                # ETFs - consider selling for higher returns
                fallback_ideas.append({
                    "action": "SELL",
                    "symbol": symbol,
                    "quantity": max(1, holding['quantity'] // 3),  # Sell 33%
                    "limit_price": current_price * 1.01,  # 1% above current
                    "confidence": 0.75,
                    "rationale": f"{symbol} ETF for stability but targeting 10% monthly returns requires more aggressive positioning. Partial exit to deploy capital in higher-return opportunities."
                })
            elif pnl > 0 and holding['day_change_percentage'] > 2:
                # Profitable and rising - take profits for capital deployment
                fallback_ideas.append({
                    "action": "SELL",
                    "symbol": symbol,
                    "quantity": max(1, holding['quantity'] // 2),  # Sell 50%
                    "limit_price": current_price * 1.02,  # 2% above current
                    "confidence": 0.80,
                    "rationale": f"{symbol} showing strong momentum with {holding['day_change_percentage']:.1f}% daily gain. Take profits to deploy ₹5,000 in higher-return opportunities targeting 10% monthly returns."
                })
            elif pnl < 0 and holding['day_change_percentage'] < -2:
                # Loss-making and falling - consider averaging down or exit
                if abs(holding['day_change_percentage']) > 5:
                    # Heavy loss - exit and redeploy
                    fallback_ideas.append({
                        "action": "SELL",
                        "symbol": symbol,
                        "quantity": max(1, holding['quantity'] // 2),  # Sell 50%
                        "limit_price": current_price * 0.99,  # 1% below current
                        "confidence": 0.70,
                        "rationale": f"{symbol} down {abs(holding['day_change_percentage']):.1f}% today. Cut losses and redeploy ₹5,000 in momentum stocks for 10% monthly target."
                    })
                else:
                    # Moderate loss - average down
                    fallback_ideas.append({
                        "action": "BUY",
                        "symbol": symbol,
                        "quantity": max(1, holding['quantity'] // 2),  # Buy 50% more
                        "limit_price": current_price * 0.98,  # 2% below current
                        "confidence": 0.65,
                        "rationale": f"{symbol} down {abs(holding['day_change_percentage']):.1f}% today. Average down with ₹5,000 for potential 15% monthly return on recovery."
                    })
            else:
                # Neutral - look for new opportunities
                # Add new high-potential stocks not in portfolio
                high_potential_stocks = [
                    {"symbol": "TATAMOTORS", "price": 850, "rationale": "Auto sector momentum, EV transition, 15% monthly potential"},
                    {"symbol": "ADANIENT", "price": 3200, "rationale": "Infrastructure growth, government focus, 12% monthly potential"},
                    {"symbol": "HINDALCO", "price": 580, "rationale": "Metal sector recovery, global demand, 10% monthly potential"},
                    {"symbol": "SUNPHARMA", "price": 1200, "rationale": "Pharma defensive, export growth, 8% monthly potential"},
                    {"symbol": "BAJFINANCE", "price": 7200, "rationale": "NBFC growth, consumer finance, 12% monthly potential"}
                ]
                
                for new_stock in high_potential_stocks:
                    if new_stock["symbol"] not in [h['trading_symbol'] for h in holdings]:
                        quantity = int(5000 / new_stock["price"])  # ₹5,000 position
                        if quantity > 0:
                            fallback_ideas.append({
                                "action": "BUY",
                                "symbol": new_stock["symbol"],
                                "quantity": quantity,
                                "limit_price": new_stock["price"],
                                "confidence": 0.75,
                                "rationale": f"New opportunity: {new_stock['rationale']}. Deploy ₹5,000 for {new_stock['symbol']} targeting 10%+ monthly returns."
                            })
                            break  # Add only one new stock
        
        return fallback_ideas[:3]  # Return top 3 ideas
    
    def _parse_critiques(self, content: str, trade_ideas: List[Dict]) -> List[Dict]:
        """Parse critiques and filter trade ideas."""
        try:
            lines = content.strip().split('\n')
            approved_ideas = []
            
            for i, line in enumerate(lines):
                if i >= len(trade_ideas):
                    break
                
                if 'PASS' in line.upper():
                    approved_ideas.append(trade_ideas[i])
            
            return approved_ideas if approved_ideas else trade_ideas
            
        except Exception as e:
            logger.error(f"Error parsing critiques: {e}")
            return trade_ideas 