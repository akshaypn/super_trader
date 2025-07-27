import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

@dataclass
class PortfolioCoachConfig:
    """Portfolio coach specific configuration."""
    investor_id: str = "akshay"
    salary_day: int = 25  # day of month
    monthly_inflow: int = 70_000  # INR
    risk_profile: str = "moderate"  # conservative | moderate | aggressive
    target_eq_weight: float = 0.75  # % of financial net-worth
    max_drawdown: float = 0.20  # portfolio peak-to-trough tolerance
    strategic_beta: float = 0.95  # vs NIFTY-50
    rebal_threshold: int = 5  # % drift that triggers action
    capital_gains_budget: float = 0.03  # % of NAV taxable churn p.a.
    liquidity_buffer_months: int = 6
    slack_channel: str = "#portfolio-coach"
    email_to: str = "akshay@example.com"
    
    # LLM Configuration
    idea_gen_model: str = "gpt-4"  # For idea generation
    critic_model: str = "gpt-3.5-turbo"  # For criticism
    critic_count: int = 3  # Number of critics
    critic_pass_threshold: int = 2  # Minimum critics that must pass
    
    # Risk Configuration
    max_position_size_pct: float = 0.05  # 5% max per stock
    var_confidence: float = 0.95  # VaR confidence level
    max_daily_trades: int = 5  # Maximum trades per day
    min_liquidity_adv_multiple: int = 20  # Minimum 20x ADV for liquidity

class Config:
    """Configuration class for the application."""
    
    # Upstox API Configuration
    UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/fin")
    
    # Database Pool Configuration
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        if not cls.UPSTOX_ACCESS_TOKEN:
            raise RuntimeError("Set UPSTOX_ACCESS_TOKEN in the environment")
        
        if not cls.DATABASE_URL:
            raise RuntimeError("Set DATABASE_URL in the environment")
    
    @classmethod
    def validate_openai(cls):
        """Validate OpenAI configuration."""
        if not cls.OPENAI_API_KEY:
            raise RuntimeError("Set OPENAI_API_KEY in the environment")
