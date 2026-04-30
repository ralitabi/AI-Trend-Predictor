"""
Utility functions for AI Investment System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_price_data(data: pd.DataFrame) -> bool:
    """
    Validate price data quality
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        True if data is valid, False otherwise
    """
    
    if data.empty:
        logger.error("Data is empty")
        return False
    
    required_columns = ['close', 'adj close', 'high', 'low', 'volume']
    actual_columns = [col.lower() for col in data.columns]
    
    # Check for at least close price
    if not any(col in actual_columns for col in ['close', 'adj close']):
        logger.error("Missing price columns")
        return False
    
    # Check for NaN values
    close_col = 'adj close' if 'adj close' in actual_columns else 'close'
    if data[close_col].isna().sum() / len(data) > 0.1:
        logger.warning(f"More than 10% NaN values in {close_col}")
    
    # Check for negative prices
    if (data[close_col] < 0).any():
        logger.error("Negative prices found")
        return False
    
    logger.info(f"Data validation passed: {len(data)} records")
    return True


def calculate_accuracy_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    """
    Calculate prediction accuracy metrics
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        Dictionary with accuracy metrics
    """
    
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)
    
    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'mape': mape
    }


def format_currency(value: float, precision: int = 2) -> str:
    """Format value as currency"""
    return f"${value:,.{precision}f}"


def format_percentage(value: float, precision: int = 2) -> str:
    """Format value as percentage"""
    return f"{value:.{precision}f}%"


def get_date_range_description(start_date, end_date) -> str:
    """Get human-readable date range description"""
    delta = (end_date - start_date).days
    
    if delta < 1:
        return "Today"
    elif delta < 7:
        return f"{delta} days"
    elif delta < 30:
        return f"{delta // 7} weeks"
    elif delta < 365:
        return f"{delta // 30} months"
    else:
        return f"{delta // 365} years"


def save_analysis_results(results: dict, filename: str = None) -> str:
    """
    Save analysis results to JSON file
    
    Args:
        results: Analysis results dictionary
        filename: Output filename (if None, auto-generate)
    
    Returns:
        Path to saved file
    """
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to {filename}")
    return filename


def load_analysis_results(filename: str) -> dict:
    """Load analysis results from JSON file"""
    
    with open(filename, 'r') as f:
        results = json.load(f)
    
    logger.info(f"Results loaded from {filename}")
    return results


def calculate_optimal_forecast_length(data_length: int, min_ratio: float = 0.05) -> int:
    """
    Calculate optimal forecast length based on data availability
    
    Args:
        data_length: Length of historical data
        min_ratio: Minimum ratio of forecast to data length
    
    Returns:
        Recommended forecast length
    """
    
    max_forecast = int(data_length * min_ratio)
    return max(7, min(max_forecast, 30))  # Between 7 and 30 days


def create_model_comparison_table(predictions: dict, current_price: float) -> pd.DataFrame:
    """
    Create comparison table for model predictions
    
    Args:
        predictions: Dictionary with model predictions
        current_price: Current price
    
    Returns:
        DataFrame with comparison
    """
    
    data = {
        'Model': [],
        'Day 1 Price': [],
        'Day 1 Change': [],
        f'Final Price': [],
        'Total Change': []
    }
    
    for model_name, pred_values in predictions.items():
        if len(pred_values) > 0:
            data['Model'].append(model_name.capitalize())
            data['Day 1 Price'].append(f"${pred_values[0]:.2f}")
            data['Day 1 Change'].append(f"{((pred_values[0] - current_price) / current_price * 100):.2f}%")
            data[f'Final Price'].append(f"${pred_values[-1]:.2f}")
            data['Total Change'].append(f"{((pred_values[-1] - current_price) / current_price * 100):.2f}%")
    
    return pd.DataFrame(data)


def export_report_to_html(report_content: str, filename: str = None) -> str:
    """
    Export report to HTML file
    
    Args:
        report_content: HTML content
        filename: Output filename
    
    Returns:
        Path to saved file
    """
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"investment_report_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"Report saved to {filename}")
    return filename


def calculate_confidence_intervals(predictions: np.ndarray, std_error: float = None) -> dict:
    """
    Calculate confidence intervals for predictions
    
    Args:
        predictions: Array of predictions
        std_error: Standard error (if None, estimated from data)
    
    Returns:
        Dictionary with confidence intervals
    """
    
    if std_error is None:
        std_error = np.std(predictions) * 0.1
    
    z_90 = 1.645
    z_95 = 1.96
    z_99 = 2.576
    
    ci_90_lower = predictions - z_90 * std_error
    ci_90_upper = predictions + z_90 * std_error
    
    ci_95_lower = predictions - z_95 * std_error
    ci_95_upper = predictions + z_95 * std_error
    
    ci_99_lower = predictions - z_99 * std_error
    ci_99_upper = predictions + z_99 * std_error
    
    return {
        'ci_90': (ci_90_lower, ci_90_upper),
        'ci_95': (ci_95_lower, ci_95_upper),
        'ci_99': (ci_99_lower, ci_99_upper)
    }


def get_market_status(price_change_pct: float) -> str:
    """Get market status description"""
    
    if price_change_pct > 5:
        return "Strong Uptrend"
    elif price_change_pct > 2:
        return "Moderate Uptrend"
    elif price_change_pct > 0:
        return "Slight Uptrend"
    elif price_change_pct > -2:
        return "Slight Downtrend"
    elif price_change_pct > -5:
        return "Moderate Downtrend"
    else:
        return "Strong Downtrend"
