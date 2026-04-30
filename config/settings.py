"""
Configuration module for AI Investment System
Loads and manages configuration settings
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Configuration settings"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    FRED_API_KEY = os.getenv("FRED_API_KEY", "")
    
    # Asset Tickers
    GOLD_TICKER = os.getenv("GOLD_TICKER", "GC=F")
    SP500_TICKER = os.getenv("SP500_TICKER", "^GSPC")
    BITCOIN_TICKER = os.getenv("BITCOIN_TICKER", "BTC-USD")
    VIX_TICKER = os.getenv("VIX_TICKER", "^VIX")
    DXY_TICKER = os.getenv("DXY_TICKER", "DXY=F")
    
    # Data Configuration
    LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "365"))
    DEFAULT_FORECAST_DAYS = int(os.getenv("FORECAST_DAYS", "30"))
    
    # Model Configuration
    ARIMA_ORDER = tuple(map(int, os.getenv("ARIMA_ORDER", "5,1,2").split(",")))
    LSTM_EPOCHS = int(os.getenv("LSTM_EPOCHS", "50"))
    LSTM_BATCH_SIZE = int(os.getenv("LSTM_BATCH_SIZE", "32"))
    
    # Risk Configuration
    RISK_FREE_RATE = float(os.getenv("RISK_FREE_RATE", "0.05"))
    CONFIDENCE_LEVEL = float(os.getenv("CONFIDENCE_LEVEL", "0.95"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        
        warnings = []
        
        if not cls.OPENAI_API_KEY:
            warnings.append("⚠️ OpenAI API key not set. AI reports will use fallback templates.")
        
        if cls.LOOKBACK_DAYS < 100:
            warnings.append("⚠️ Lookback days too small. Recommend at least 100 days.")
        
        if cls.RISK_FREE_RATE < 0 or cls.RISK_FREE_RATE > 1:
            warnings.append("⚠️ Risk-free rate out of range (0-1).")
        
        for warning in warnings:
            logger.warning(warning)
        
        return len(warnings) == 0
    
    @classmethod
    def to_dict(cls):
        """Convert config to dictionary"""
        return {
            'openai_api_key': '***' if cls.OPENAI_API_KEY else 'Not set',
            'gold_ticker': cls.GOLD_TICKER,
            'sp500_ticker': cls.SP500_TICKER,
            'bitcoin_ticker': cls.BITCOIN_TICKER,
            'lookback_days': cls.LOOKBACK_DAYS,
            'forecast_days': cls.DEFAULT_FORECAST_DAYS,
            'arima_order': cls.ARIMA_ORDER,
            'risk_free_rate': cls.RISK_FREE_RATE,
            'confidence_level': cls.CONFIDENCE_LEVEL
        }


# Validate on import
Config.validate()
