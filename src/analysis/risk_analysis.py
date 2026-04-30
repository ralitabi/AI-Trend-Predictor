"""
Risk & Volatility Analysis Module
Calculates risk metrics and portfolio statistics
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskAnalysis:
    """Calculate financial risk metrics"""
    
    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize Risk Analysis
        
        Args:
            risk_free_rate: Annual risk-free rate (e.g., US Treasury yield)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_volatility(self, returns: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate rolling volatility (standard deviation of returns)
        
        Args:
            returns: Series of daily returns (as decimal, not percentage)
            window: Rolling window size in days
        
        Returns:
            Series of rolling volatility (annualized)
        """
        rolling_vol = returns.rolling(window=window).std()
        annualized_vol = rolling_vol * np.sqrt(252)  # 252 trading days per year
        
        return annualized_vol
    
    def calculate_sharpe_ratio(self, returns: pd.Series, window: int = 252) -> pd.Series:
        """
        Calculate rolling Sharpe Ratio
        
        Args:
            returns: Series of daily returns (as decimal)
            window: Rolling window in days
        
        Returns:
            Series of Sharpe ratios
        """
        excess_returns = returns - (self.risk_free_rate / 252)  # Daily risk-free rate
        rolling_sharpe = excess_returns.rolling(window=window).mean() / \
                        excess_returns.rolling(window=window).std()
        rolling_sharpe *= np.sqrt(252)  # Annualize
        
        return rolling_sharpe
    
    def calculate_drawdown(self, prices: pd.Series) -> Tuple[pd.Series, float]:
        """
        Calculate drawdown from peak
        
        Args:
            prices: Series of prices
        
        Returns:
            Tuple of (drawdown series, maximum drawdown)
        """
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax * 100  # Percentage drawdown
        max_drawdown = drawdown.min()
        
        return drawdown, max_drawdown
    
    def calculate_max_drawdown_duration(self, prices: pd.Series) -> int:
        """
        Calculate the longest drawdown duration in days
        
        Args:
            prices: Series of prices
        
        Returns:
            Maximum drawdown duration in days
        """
        cummax = prices.cummax()
        is_drawdown = (prices < cummax)
        
        # Find transitions
        transitions = is_drawdown.astype(int).diff()
        drawdown_start = np.where(transitions == 1)[0]
        drawdown_end = np.where(transitions == -1)[0]
        
        if len(drawdown_start) == 0:
            return 0
        
        # Handle case where drawdown extends to end
        if len(drawdown_end) == 0:
            durations = [len(prices) - start for start in drawdown_start]
        elif len(drawdown_start) > len(drawdown_end):
            durations = list(drawdown_end - drawdown_start[:-1]) + \
                       [len(prices) - drawdown_start[-1]]
        else:
            durations = list(drawdown_end - drawdown_start)
        
        return max(durations) if durations else 0
    
    def calculate_return_metrics(self, prices: pd.Series, periods: int = 252) -> Dict:
        """
        Calculate comprehensive return metrics
        
        Args:
            prices: Series of prices
            periods: Period for annualization (252 for daily data)
        
        Returns:
            Dictionary of return metrics
        """
        returns = prices.pct_change()
        
        total_return = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
        daily_return = returns.mean() * 100
        annual_return = daily_return * 252
        
        metrics = {
            'total_return_pct': total_return,
            'daily_return_pct': daily_return,
            'annual_return_pct': annual_return,
            'volatility_pct': returns.std() * np.sqrt(252) * 100,
            'sharpe_ratio': self._calculate_overall_sharpe(returns),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis()
        }
        
        return metrics
    
    def _calculate_overall_sharpe(self, returns: pd.Series) -> float:
        """Calculate overall Sharpe ratio"""
        excess_return = returns.mean() - (self.risk_free_rate / 252)
        std_dev = returns.std()
        
        if std_dev == 0:
            return 0
        
        sharpe = (excess_return / std_dev) * np.sqrt(252)
        return sharpe
    
    def calculate_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate beta relative to a market index
        
        Args:
            asset_returns: Series of asset returns
            market_returns: Series of market returns
        
        Returns:
            Beta coefficient
        """
        covariance = asset_returns.cov(market_returns)
        market_variance = market_returns.var()
        
        if market_variance == 0:
            return 0
        
        beta = covariance / market_variance
        return beta
    
    def calculate_value_at_risk(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Series of returns
            confidence: Confidence level (0.95 for 95%)
        
        Returns:
            VaR as percentage
        """
        var = np.percentile(returns, (1 - confidence) * 100)
        return var * 100
    
    def calculate_conditional_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) - also called Expected Shortfall
        
        Args:
            returns: Series of returns
            confidence: Confidence level
        
        Returns:
            CVaR as percentage
        """
        var_threshold = np.percentile(returns, (1 - confidence) * 100)
        cvar = returns[returns <= var_threshold].mean()
        return cvar * 100


class VolatilityAnalysis:
    """Specialized volatility analysis"""
    
    @staticmethod
    def classify_volatility(volatility: float) -> str:
        """
        Classify volatility level
        
        Args:
            volatility: Annualized volatility as decimal
        
        Returns:
            Classification string
        """
        vol_pct = volatility * 100
        
        if vol_pct < 15:
            return "Low"
        elif vol_pct < 25:
            return "Moderate"
        elif vol_pct < 35:
            return "High"
        else:
            return "Very High"
    
    @staticmethod
    def calculate_volatility_forecast(returns: pd.Series, window: int = 20) -> float:
        """
        Forecast next period volatility using GARCH-like approach
        
        Args:
            returns: Series of returns
            window: Lookback window
        
        Returns:
            Forecasted volatility
        """
        recent_vol = returns.tail(window).std()
        historical_vol = returns.std()
        
        # Weighted average: 70% recent, 30% historical
        forecast_vol = 0.7 * recent_vol + 0.3 * historical_vol
        annualized = forecast_vol * np.sqrt(252)
        
        return annualized


class RiskMetrics:
    """Comprehensive risk assessment"""
    
    def __init__(self):
        self.risk_analysis = RiskAnalysis()
    
    def get_risk_summary(self, prices: pd.Series, asset_name: str = "Asset",
                         raw_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Get comprehensive risk summary
        
        Args:
            prices: Series of prices
            asset_name: Name of asset for reporting
        
        Returns:
            Dictionary with risk metrics
        """
        returns = prices.pct_change().dropna()
        close_prices = prices.dropna()

        if len(returns) < 10:
            logger.warning("Insufficient data for risk analysis (need ≥10 rows)")
            return {}

        drawdown, max_dd = self.risk_analysis.calculate_drawdown(close_prices)
        drawdown_duration = self.risk_analysis.calculate_max_drawdown_duration(close_prices)

        vol_series = self.risk_analysis.calculate_volatility(returns)
        volatility = float(vol_series.dropna().iloc[-1]) if not vol_series.dropna().empty else 0.0
        sharpe = self.risk_analysis._calculate_overall_sharpe(returns)
        var_95 = self.risk_analysis.calculate_value_at_risk(returns)
        cvar_95 = self.risk_analysis.calculate_conditional_var(returns)

        return_metrics = self.risk_analysis.calculate_return_metrics(close_prices)
        
        # ATR-based stop distance (from raw OHLC data if available, else proxy)
        if raw_data is not None and 'high' in raw_data.columns and 'low' in raw_data.columns:
            from data.market_data import MarketDataCollector
            atr_series = MarketDataCollector.calculate_atr(raw_data, period=14)
            atr_value  = float(atr_series.dropna().iloc[-1]) if not atr_series.dropna().empty else float(close_prices.iloc[-1]) * 0.015
        else:
            # Proxy: 14-day rolling range of close prices
            atr_value = float((close_prices.rolling(14).max() - close_prices.rolling(14).min()).dropna().iloc[-1] / 2)

        return {
            'asset': asset_name,
            'current_volatility': volatility,
            'volatility_pct': volatility * 100,
            'volatility_classification': VolatilityAnalysis.classify_volatility(volatility),
            'sharpe_ratio': sharpe,
            'annual_return': return_metrics['annual_return_pct'],
            'max_drawdown_pct': max_dd,
            'max_drawdown_duration_days': drawdown_duration,
            'var_95_pct': var_95,
            'cvar_95_pct': cvar_95,
            'skewness': return_metrics['skewness'],
            'kurtosis': return_metrics['kurtosis'],
            'atr': atr_value,
            'atr_pct': round(atr_value / float(close_prices.iloc[-1]) * 100, 2),
        }
