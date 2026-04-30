"""
Example script showing how to use the AI Investment System programmatically
"""

import sys
sys.path.insert(0, 'src')

from data.market_data import MarketDataCollector, MacroeconomicData
from models.predictors import ARIMAPredictor, ProphetPredictor, EnsemblePredictor
from analysis.risk_analysis import RiskMetrics
from analysis.suggestions import SuggestionsEngine
from reporting.report_generator import AIReportGenerator
from utils import validate_price_data, format_currency, format_percentage
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_basic_analysis():
    """
    Example 1: Basic data collection and analysis
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Data Collection & Analysis")
    print("="*60)
    
    # Collect data
    collector = MarketDataCollector(lookback_days=365)
    gold_data = collector.get_gold_data()
    
    # Validate data
    if validate_price_data(gold_data):
        print(f"✓ Loaded {len(gold_data)} records for Gold")
        print(f"  Price range: ${gold_data['adj close'].min():.2f} - ${gold_data['adj close'].max():.2f}")
        
        # Calculate metrics
        current_price = gold_data['adj close'].iloc[-1]
        returns = collector.calculate_returns(gold_data)
        volatility = collector.calculate_volatility(gold_data).iloc[-1]
        
        print(f"\nCurrent Price: {format_currency(current_price)}")
        print(f"Current Volatility: {format_percentage(volatility * 100)}")
        print(f"Average Daily Return: {format_percentage(returns.mean())}")


def example_predictions():
    """
    Example 2: Generate predictions with multiple models
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Time Series Predictions")
    print("="*60)
    
    collector = MarketDataCollector(lookback_days=365)
    gold_data = collector.get_gold_data()
    
    if not validate_price_data(gold_data):
        return
    
    current_price = gold_data['adj close'].iloc[-1]
    prices = gold_data['adj close']
    
    print(f"Current Price: {format_currency(current_price)}")
    print(f"Generating 7-day forecast...\n")
    
    # Ensemble prediction
    ensemble = EnsemblePredictor()
    ensemble.fit_all_models(prices, use_lstm=False)
    predictions = ensemble.predict_ensemble(periods=7, use_lstm=False)
    
    # Display predictions
    print("MODEL PREDICTIONS (7-Day Forecast):")
    print("-" * 60)
    
    for model_name, pred_values in predictions.items():
        if len(pred_values) > 0:
            day1 = pred_values[0]
            day7 = pred_values[-1]
            change = ((day7 - current_price) / current_price * 100)
            
            print(f"{model_name.upper():12} | Day 1: {format_currency(day1)} | Day 7: {format_currency(day7)} | Change: {format_percentage(change)}")


def example_risk_analysis():
    """
    Example 3: Comprehensive risk analysis
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Risk & Volatility Analysis")
    print("="*60)
    
    collector = MarketDataCollector(lookback_days=365)
    gold_data = collector.get_gold_data()
    
    if not validate_price_data(gold_data):
        return
    
    # Get risk metrics
    risk_metrics = RiskMetrics()
    summary = risk_metrics.get_risk_summary(gold_data['adj close'], 'Gold')
    
    print("\nRISK METRICS:")
    print("-" * 60)
    print(f"Annual Return:           {format_percentage(summary['annual_return'])}")
    print(f"Volatility:              {format_percentage(summary['current_volatility'] * 100)} ({summary['volatility_classification']})")
    print(f"Sharpe Ratio:            {summary['sharpe_ratio']:.3f}")
    print(f"Max Drawdown:            {format_percentage(summary['max_drawdown_pct'])}")
    print(f"Max Drawdown Duration:   {summary['max_drawdown_duration_days']} days")
    print(f"Value at Risk (95%):     {format_percentage(summary['var_95_pct'])}")
    print(f"Conditional VaR (95%):   {format_percentage(summary['cvar_95_pct'])}")
    print(f"Skewness:                {summary['skewness']:.3f}")
    print(f"Kurtosis:                {summary['kurtosis']:.3f}")


def example_investment_suggestion():
    """
    Example 4: Generate investment recommendation
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Investment Recommendations")
    print("="*60)
    
    collector = MarketDataCollector(lookback_days=365)
    gold_data = collector.get_gold_data()
    
    if not validate_price_data(gold_data):
        return
    
    current_price = gold_data['adj close'].iloc[-1]
    prices = gold_data['adj close']
    
    # Generate predictions
    ensemble = EnsemblePredictor()
    ensemble.fit_all_models(prices, use_lstm=False)
    predictions_dict = ensemble.predict_ensemble(periods=30, use_lstm=False)
    ensemble_pred = predictions_dict['ensemble']
    
    # Get risk metrics
    risk_metrics = RiskMetrics()
    risk_summary = risk_metrics.get_risk_summary(prices, 'Gold')
    
    # Prepare data for suggestion engine
    pred_data = {
        'trend': 'bullish' if ensemble_pred[-1] > current_price else 'bearish',
        'confidence': 0.65,
        'price_target': ensemble_pred[-1],
        'volatility': risk_summary['current_volatility'] * 100,
        'sharpe_ratio': risk_summary['sharpe_ratio']
    }
    
    # Generate suggestion
    suggestion = SuggestionsEngine.generate_suggestion(
        asset_name='Gold',
        current_price=current_price,
        predictions=pred_data,
        risk_metrics=risk_summary,
        timeframe='mid-term'
    )
    
    # Display recommendation
    print("\nINVESTMENT RECOMMENDATION:")
    print("-" * 60)
    print(f"Action:           {suggestion.action}")
    print(f"Confidence:       {format_percentage(suggestion.confidence)}")
    print(f"Risk Level:       {suggestion.risk_level}")
    print(f"Current Price:    {format_currency(current_price)}")
    print(f"Entry Price:      {format_currency(suggestion.entry_price)}")
    print(f"Target Price:     {format_currency(suggestion.target_price)}")
    print(f"Stop Loss:        {format_currency(suggestion.stop_loss)}")
    print(f"Holding Period:   {suggestion.holding_period}")
    print(f"\nRationale: {suggestion.rationale}")


def example_multi_asset_comparison():
    """
    Example 5: Compare multiple assets
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Multi-Asset Comparison")
    print("="*60)
    
    collector = MarketDataCollector(lookback_days=365)
    
    assets = {
        'Gold': collector.get_gold_data(),
        'S&P 500': collector.get_sp500_data(),
        'Bitcoin': collector.get_bitcoin_data()
    }
    
    print("\nASSET PERFORMANCE COMPARISON:")
    print("-" * 80)
    print(f"{'Asset':<15} {'Current Price':<15} {'Volatility':<15} {'Annual Return':<15}")
    print("-" * 80)
    
    risk_metrics = RiskMetrics()
    
    for asset_name, data in assets.items():
        if not data.empty:
            close_col = 'adj close' if 'adj close' in data.columns else 'close'
            current_price = data[close_col].iloc[-1]
            
            summary = risk_metrics.get_risk_summary(data[close_col], asset_name)
            
            print(f"{asset_name:<15} ${current_price:<14.2f} {format_percentage(summary['current_volatility'] * 100):<14} {format_percentage(summary['annual_return']):<14}")


def example_ai_report():
    """
    Example 6: Generate AI-powered report
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: AI Report Generation")
    print("="*60)
    
    collector = MarketDataCollector(lookback_days=365)
    gold_data = collector.get_gold_data()
    
    if not validate_price_data(gold_data):
        return
    
    current_price = gold_data['adj close'].iloc[-1]
    prices = gold_data['adj close']
    
    # Generate predictions
    ensemble = EnsemblePredictor()
    ensemble.fit_all_models(prices, use_lstm=False)
    predictions_dict = ensemble.predict_ensemble(periods=30, use_lstm=False)
    ensemble_pred = predictions_dict['ensemble']
    
    # Get risk metrics
    risk_metrics = RiskMetrics()
    risk_summary = risk_metrics.get_risk_summary(prices, 'Gold')
    
    # Generate report
    report_gen = AIReportGenerator()
    
    analysis_data = {
        'short_term': 'bullish' if ensemble_pred[6] > current_price else 'bearish',
        'confidence': 0.65,
        'volatility': f"{risk_summary['current_volatility'] * 100:.1f}%",
        'sharpe_ratio': f"{risk_summary['sharpe_ratio']:.2f}",
        'max_drawdown': f"{risk_summary['max_drawdown_pct']:.1f}%"
    }
    
    report = report_gen.generate_trend_analysis(
        asset_name='Gold',
        predictions=analysis_data,
        current_price=current_price,
        historical_context="Based on 1-year analysis with strong uptrend"
    )
    
    print("\nAI-GENERATED MARKET ANALYSIS:")
    print("-" * 60)
    print(report)


def main():
    """Run all examples"""
    
    print("\n")
    print("*" * 60)
    print("*  AI INVESTMENT SYSTEM - USAGE EXAMPLES")
    print("*" * 60)
    
    try:
        example_basic_analysis()
        example_predictions()
        example_risk_analysis()
        example_investment_suggestion()
        example_multi_asset_comparison()
        example_ai_report()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
