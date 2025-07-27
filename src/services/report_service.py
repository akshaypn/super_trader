"""
Report service for generating and sending portfolio reports.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ReportService:
    """Service for generating and sending portfolio reports."""
    
    def __init__(self):
        """Initialize report service."""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO', 'akshay@example.com')
    
    def generate_report(self, trade_ideas: List[Dict], portfolio_data: Dict, market_data: Dict, tracking_data: Dict = None) -> str:
        """Generate markdown report."""
        current_date = datetime.now().strftime('%d %b %Y')
        
        # Portfolio summary
        portfolio_summary = f"""
### {current_date} – Portfolio Coach (08:45 IST)

**Portfolio Summary:**
- Total Value: ₹{portfolio_data.get('total_value', 0):,.2f}
- Total P&L: ₹{portfolio_data.get('total_pnl', 0):,.2f}
- Number of Holdings: {portfolio_data.get('total_stocks', 0)}

**Market Context:**
- Nifty 50: ₹{market_data.get('nifty_50', {}).get('close', 0):,.2f} ({market_data.get('nifty_50', {}).get('change', 0):+.2f}%)
- USD/INR: ₹{market_data.get('usd_inr', {}).get('rate', 0):.2f}

**Trade Recommendations:**
"""
        
        # Trade ideas table
        if trade_ideas:
            report = portfolio_summary + """
| # | Action | Symbol | Qty | Limit | Confidence | Rationale |
|---|--------|--------|----:|------:|-----------:|-----------|
"""
            
            for i, idea in enumerate(trade_ideas, 1):
                confidence_emoji = "🟢" if idea["confidence"] >= 0.75 else "🟠" if idea["confidence"] >= 0.6 else "🔴"
                report += f"| {i} | **{idea['action']}** | {idea['symbol']} | {idea['quantity']} | ₹{idea['limit_price']:,} | {confidence_emoji} {idea['confidence']:.2f} | {idea['rationale']} |\n"
            
            # GTT JSON block
            report += "\n*Copy-paste-ready GTT JSON block below:*\n\n"
            report += "```json\n"
            gtt_orders = []
            for idea in trade_ideas:
                if idea['action'] != 'HOLD':
                    # Get instrument token from portfolio data if available
                    instrument_token = f"NSE_EQ|{idea['symbol']}"
                    
                    # Try to find the actual instrument token from holdings
                    for holding in portfolio_data.get('holdings', []):
                        if holding['trading_symbol'] == idea['symbol']:
                            instrument_token = holding.get('instrument_token', f"NSE_EQ|{idea['symbol']}")
                            break
                    
                    gtt_orders.append({
                        "transaction_type": idea['action'],
                        "instrument_token": instrument_token,
                        "quantity": idea['quantity'],
                        "product": "I",
                        "price": idea['limit_price']
                    })
            report += json.dumps(gtt_orders, indent=2)
            report += "\n```\n"
            
        else:
            report = portfolio_summary + "\n**No trade recommendations for today.**\n\n"
            report += "Portfolio is well-balanced and no significant opportunities identified.\n"
        
        # Historical Performance Section
        if tracking_data:
            report += "\n\n**📊 Historical Performance:**\n"
            if tracking_data.get('portfolio_changes'):
                changes = tracking_data['portfolio_changes']
                if changes['new_positions']:
                    report += f"- **New Positions:** {len(changes['new_positions'])} stocks added\n"
                if changes['exited_positions']:
                    report += f"- **Exited Positions:** {len(changes['exited_positions'])} stocks sold\n"
                if changes['quantity_changes']:
                    report += f"- **Quantity Changes:** {len(changes['quantity_changes'])} positions modified\n"
            
            if tracking_data.get('performance_metrics'):
                metrics = tracking_data['performance_metrics']
                report += f"- **Portfolio Return:** {metrics.get('portfolio_return', 0):.2f}% (vs Nifty: {metrics.get('benchmark_return', 0):.2f}%)\n"
                report += f"- **Alpha:** {metrics.get('alpha', 0):.2f}%\n"
                report += f"- **Win Rate:** {metrics.get('win_rate', 0):.1f}% ({metrics.get('profitable_trades', 0)}/{metrics.get('total_trades', 0)} trades)\n"
        
        # Risk banner
        total_value = portfolio_data.get('total_value', 0)
        if total_value > 0:
            max_drawdown = 0.20  # 20% max drawdown
            current_drawdown = abs(portfolio_data.get('total_pnl', 0)) / total_value
            
            if current_drawdown > max_drawdown * 0.8:
                report += f"\n⚠️ **Risk Alert:** Current drawdown ({current_drawdown:.1%}) approaching maximum threshold ({max_drawdown:.1%})\n"
        
        # Sources and Methodology
        report += "\n\n**📚 Sources & Methodology:**\n"
        report += "- **Portfolio Data:** Upstox API (real-time holdings)\n"
        report += "- **Market Data:** Yahoo Finance API (Nifty 50, Sensex, USD/INR)\n"
        report += "- **AI Analysis:** OpenAI GPT-4o-mini (trade ideas) + GPT-3.5-turbo (critique)\n"
        report += "- **Risk Management:** Position sizing (5% max), confidence scoring (≥0.6)\n"
        report += "- **Technical Analysis:** Support/resistance, momentum indicators, sector rotation\n"
        report += "- **Fundamental Analysis:** P/E ratios, earnings growth, sector trends\n"
        report += "- **Global Context:** Fed policy, geopolitical factors, commodity prices\n"
        
        report += f"\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST*"
        
        return report
    
    def send_email(self, report: str, subject: str = None) -> bool:
        """Send report via email."""
        if not all([self.smtp_username, self.smtp_password]):
            logger.warning("SMTP credentials not configured, skipping email send")
            return False
        
        try:
            if subject is None:
                subject = f"Portfolio Coach Report - {datetime.now().strftime('%d %b %Y')}"
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            # Convert markdown to HTML (basic conversion)
            html_content = self._markdown_to_html(report)
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {self.email_to}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_slack_message(self, report: str) -> bool:
        """Send report to Slack (placeholder for future implementation)."""
        # TODO: Implement Slack integration
        logger.info("Slack integration not yet implemented")
        return False
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to basic HTML."""
        html = markdown
        
        # Headers
        html = html.replace('### ', '<h3>').replace('\n\n', '</h3>\n\n')
        
        # Bold
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        
        # Tables
        if '|' in html:
            lines = html.split('\n')
            in_table = False
            table_html = []
            
            for line in lines:
                if '|' in line and '---' not in line:
                    if not in_table:
                        table_html.append('<table border="1" style="border-collapse: collapse; width: 100%;">')
                        in_table = True
                    
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    row_html = '<tr>' + ''.join([f'<td style="padding: 8px;">{cell}</td>' for cell in cells]) + '</tr>'
                    table_html.append(row_html)
                elif in_table:
                    table_html.append('</table>')
                    in_table = False
            
            if in_table:
                table_html.append('</table>')
            
            # Replace table in original text
            table_start = html.find('|')
            table_end = html.rfind('|')
            if table_start != -1 and table_end != -1:
                html = html[:table_start] + '\n'.join(table_html) + html[table_end+1:]
        
        # Code blocks
        html = html.replace('```json', '<pre><code>').replace('```', '</code></pre>')
        
        # Line breaks
        html = html.replace('\n', '<br>\n')
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """ 