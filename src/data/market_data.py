"""
Market Data Collection Module
Fetches data for gold, stocks, crypto, and macroeconomic indicators
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataCollector:
    """Collects market data from various sources"""
    
    # Asset tickers
    GOLD_TICKER = "GC=F"  # Gold Futures
    SP500_TICKER = "^GSPC"  # S&P 500
    BITCOIN_TICKER = "BTC-USD"  # Bitcoin
    VIX_TICKER = "^VIX"  # Volatility Index
    DXY_TICKER = "DXY=F"  # US Dollar Index
    
    def __init__(self, lookback_days: int = 730):
        """
        Initialize MarketDataCollector
        
        Args:
            lookback_days: Number of days to fetch historical data
        """
        self.lookback_days = lookback_days
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=lookback_days)
    
    def fetch_price_data(self, ticker: str, interval: str = "1d") -> pd.DataFrame:
        """
        Fetch price data for a given ticker
        
        Args:
            ticker: Stock/commodity ticker symbol
            interval: Data interval (1d, 1h, 1m, etc.)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching {ticker} data from {self.start_date.date()} to {self.end_date.date()}")
            
            data = yf.download(
                ticker,
                start=self.start_date,
                end=self.end_date,
                interval=interval,
                progress=False
            )
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()

            # Handle MultiIndex columns from newer yfinance versions
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data.columns = [str(col).lower() for col in data.columns]
            data = data.sort_index()
            
            logger.info(f"Successfully fetched {len(data)} records for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_multiple_assets(self, tickers: list) -> dict:
        """
        Fetch data for multiple assets at once
        
        Args:
            tickers: List of ticker symbols
        
        Returns:
            Dictionary with ticker as key and DataFrame as value
        """
        data = {}
        for ticker in tickers:
            data[ticker] = self.fetch_price_data(ticker)
        
        return data
    
    def get_gold_data(self) -> pd.DataFrame:
        """Fetch gold price data"""
        return self.fetch_price_data(self.GOLD_TICKER)
    
    def get_sp500_data(self) -> pd.DataFrame:
        """Fetch S&P 500 data"""
        return self.fetch_price_data(self.SP500_TICKER)
    
    def get_bitcoin_data(self) -> pd.DataFrame:
        """Fetch Bitcoin data"""
        return self.fetch_price_data(self.BITCOIN_TICKER)
    
    def get_vix_data(self) -> pd.DataFrame:
        """Fetch VIX (Volatility Index) data"""
        return self.fetch_price_data(self.VIX_TICKER)
    
    def get_dxy_data(self) -> pd.DataFrame:
        """Fetch US Dollar Index data"""
        return self.fetch_price_data(self.DXY_TICKER)
    
    def calculate_returns(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate daily returns from price data
        
        Args:
            data: DataFrame with 'close' or 'adj close' column
        
        Returns:
            Series with daily returns
        """
        close_col = 'adj close' if 'adj close' in data.columns else 'close'
        returns = data[close_col].pct_change() * 100
        return returns
    
    def calculate_moving_average(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate moving average"""
        close_col = 'adj close' if 'adj close' in data.columns else 'close'
        return data[close_col].rolling(window=window).mean()
    
    def calculate_volatility(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate rolling volatility (standard deviation of returns)"""
        returns = self.calculate_returns(data)
        return returns.rolling(window=window).std()
    
    def get_current_price(self, ticker: str) -> float:
        """Get the most recent price for a ticker"""
        try:
            data = yf.Ticker(ticker)
            price = data.history(period='1d')['Close'].iloc[-1]
            return float(price)
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {str(e)}")
            return None

    # ── Technical Indicators ──────────────────────────────────────────

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index — overbought >70, oversold <30."""
        delta = prices.diff()
        gain  = delta.clip(lower=0).rolling(period).mean()
        loss  = (-delta.clip(upper=0)).rolling(period).mean()
        rs    = gain / loss.replace(0, np.nan)
        return 100 - 100 / (1 + rs)

    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0):
        """Return (upper, middle, lower) Bollinger Bands."""
        middle = prices.rolling(period).mean()
        std    = prices.rolling(period).std()
        return middle + std_dev * std, middle, middle - std_dev * std

    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Return (macd_line, signal_line, histogram)."""
        ema_fast   = prices.ewm(span=fast, adjust=False).mean()
        ema_slow   = prices.ewm(span=slow, adjust=False).mean()
        macd_line  = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram  = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range — volatility-based stop-loss distance."""
        cl = 'adj close' if 'adj close' in data.columns else 'close'
        hi = 'high'  if 'high'  in data.columns else None
        lo = 'low'   if 'low'   in data.columns else None
        close = data[cl]
        if hi and lo:
            tr = pd.concat([
                data[hi] - data[lo],
                (data[hi] - close.shift()).abs(),
                (data[lo] - close.shift()).abs(),
            ], axis=1).max(axis=1)
        else:
            tr = close.diff().abs()
        return tr.rolling(period).mean()

    def get_technical_indicators(self, data: pd.DataFrame) -> dict:
        """
        Return a dict of all technical indicators for a price DataFrame.
        All series are aligned to data.index.
        """
        cl = 'adj close' if 'adj close' in data.columns else 'close'
        prices = data[cl].dropna()

        rsi               = self.calculate_rsi(prices)
        bb_upper, bb_mid, bb_lower = self.calculate_bollinger_bands(prices)
        macd, sig, hist   = self.calculate_macd(prices)
        atr               = self.calculate_atr(data)

        # Current ATR value (most recent)
        atr_value = float(atr.dropna().iloc[-1]) if not atr.dropna().empty else float(prices.std() * 0.02)

        # RSI signal
        rsi_now = float(rsi.dropna().iloc[-1]) if not rsi.dropna().empty else 50.0
        if rsi_now < 30:
            rsi_signal = "Oversold"
        elif rsi_now > 70:
            rsi_signal = "Overbought"
        else:
            rsi_signal = "Neutral"

        # MACD signal
        macd_now = float(macd.dropna().iloc[-1])  if not macd.dropna().empty  else 0.0
        sig_now  = float(sig.dropna().iloc[-1])   if not sig.dropna().empty   else 0.0
        hist_now = float(hist.dropna().iloc[-1])  if not hist.dropna().empty  else 0.0
        macd_signal = "Bullish" if hist_now > 0 else "Bearish"

        # Bollinger Band position
        upper_now = float(bb_upper.dropna().iloc[-1]) if not bb_upper.dropna().empty else float(prices.iloc[-1]) * 1.04
        lower_now = float(bb_lower.dropna().iloc[-1]) if not bb_lower.dropna().empty else float(prices.iloc[-1]) * 0.96
        price_now = float(prices.iloc[-1])
        bb_pct    = (price_now - lower_now) / (upper_now - lower_now) * 100 if (upper_now != lower_now) else 50.0
        if bb_pct > 80:
            bb_signal = "Near upper band — potential resistance"
        elif bb_pct < 20:
            bb_signal = "Near lower band — potential support"
        else:
            bb_signal = "Mid-range — no immediate signal"

        def _series_to_list(s: pd.Series, idx) -> list:
            aligned = s.reindex(idx)
            return [None if (v != v) else float(v) for v in aligned]

        idx = prices.index
        return {
            "rsi":         _series_to_list(rsi, idx),
            "rsi_now":     rsi_now,
            "rsi_signal":  rsi_signal,
            "bb_upper":    _series_to_list(bb_upper, idx),
            "bb_middle":   _series_to_list(bb_mid, idx),
            "bb_lower":    _series_to_list(bb_lower, idx),
            "bb_pct":      round(bb_pct, 1),
            "bb_signal":   bb_signal,
            "macd":        _series_to_list(macd, idx),
            "macd_signal": _series_to_list(sig, idx),
            "macd_hist":   _series_to_list(hist, idx),
            "macd_now":    macd_now,
            "macd_signal_now": macd_signal,
            "atr":         atr_value,
            "atr_pct":     round(atr_value / price_now * 100, 2),
        }


class MacroeconomicData:
    """Handle macroeconomic indicators"""
    
    @staticmethod
    def get_inflation_estimate() -> float:
        """Get approximate current inflation rate (you could integrate with FRED API)"""
        # Placeholder - in production, integrate with FRED API
        return 3.5  # Example: 3.5% inflation
    
    @staticmethod
    def get_interest_rate_estimate() -> float:
        """Get approximate federal funds rate"""
        # Placeholder - in production, integrate with FRED API
        return 5.33  # Example: Fed funds rate
    
    @staticmethod
    def get_economic_indicators() -> dict:
        """Get multiple economic indicators"""
        return {
            'inflation': MacroeconomicData.get_inflation_estimate(),
            'interest_rate': MacroeconomicData.get_interest_rate_estimate(),
            'timestamp': datetime.now()
        }


def prepare_data_for_modeling(data: pd.DataFrame, lookback_period: int = 60) -> tuple:
    """
    Prepare data for time series modeling
    
    Args:
        data: Raw price data
        lookback_period: Number of days to use for training
    
    Returns:
        Tuple of (X, y) for modeling
    """
    close_col = 'adj close' if 'adj close' in data.columns else 'close'
    prices = data[close_col].values
    
    X, y = [], []
    for i in range(len(prices) - lookback_period):
        X.append(prices[i:i + lookback_period])
        y.append(prices[i + lookback_period])
    
    return np.array(X), np.array(y)
