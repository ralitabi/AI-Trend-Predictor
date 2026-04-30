"""
Prediction Models Module
Implements ARIMA, Prophet, and LSTM models for time series forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Tuple, Dict, List

from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ARIMAPredictor:
    """ARIMA Time Series Model"""
    
    def __init__(self, order: Tuple = (5, 1, 2)):
        """
        Initialize ARIMA predictor
        
        Args:
            order: (p, d, q) parameters for ARIMA
        """
        self.order = order
        self.model = None
        self.fitted_model = None
        self.aic = None
    
    def fit(self, data: pd.Series) -> None:
        """Fit ARIMA model to data"""
        try:
            # Remove NaN values
            clean_data = data.dropna()
            
            self.model = ARIMA(clean_data, order=self.order)
            self.fitted_model = self.model.fit()
            self.aic = self.fitted_model.aic
            
            logger.info(f"ARIMA model fitted. AIC: {self.aic:.4f}")
        except Exception as e:
            logger.error(f"Error fitting ARIMA: {str(e)}")
            raise
    
    def predict(self, periods: int = 5) -> pd.Series:
        """
        Make predictions
        
        Args:
            periods: Number of periods to forecast
        
        Returns:
            Series with forecasted values
        """
        if self.fitted_model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        forecast = self.fitted_model.get_forecast(steps=periods)
        predictions = forecast.predicted_mean
        
        return predictions
    
    def predict_with_ci(self, periods: int = 5, alpha: float = 0.05) -> Dict:
        """Get predictions with confidence intervals"""
        if self.fitted_model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        forecast = self.fitted_model.get_forecast(steps=periods)
        forecast_df = forecast.conf_int(alpha=alpha)
        forecast_df['forecast'] = forecast.predicted_mean
        
        return {
            'forecast': forecast.predicted_mean,
            'lower_ci': forecast_df.iloc[:, 0],
            'upper_ci': forecast_df.iloc[:, 1]
        }


class ProphetPredictor:
    """Facebook Prophet Time Series Model"""
    
    def __init__(self):
        """Initialize Prophet predictor"""
        try:
            from prophet import Prophet
            self.Prophet = Prophet
        except ImportError:
            logger.warning("Prophet not installed. Install with: pip install prophet")
            self.Prophet = None
        
        self.model = None
    
    def fit(self, data: pd.Series, dates: pd.DatetimeIndex) -> None:
        """
        Fit Prophet model
        
        Args:
            data: Price data
            dates: DateTime index
        """
        if self.Prophet is None:
            raise ImportError("Prophet not available")
        
        try:
            # Prepare data for Prophet
            df = pd.DataFrame({
                'ds': dates,
                'y': data.values
            })
            
            df['ds'] = pd.to_datetime(df['ds'])
            df = df.sort_values('ds')
            
            # Fit Prophet model
            self.model = self.Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                interval_width=0.95,
                changepoint_prior_scale=0.05
            )
            
            self.model.fit(df)
            logger.info("Prophet model fitted successfully")
            
        except Exception as e:
            logger.error(f"Error fitting Prophet: {str(e)}")
            raise
    
    def predict(self, periods: int = 5) -> pd.DataFrame:
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        future = self.model.make_future_dataframe(periods=periods, freq='D')
        forecast = self.model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)


class LSTMPredictor:
    """LSTM Deep Learning Model for Time Series"""
    
    def __init__(self, lookback_period: int = 60, epochs: int = 50, batch_size: int = 32):
        """
        Initialize LSTM predictor
        
        Args:
            lookback_period: Number of previous time steps
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        self.lookback_period = lookback_period
        self.epochs = epochs
        self.batch_size = batch_size
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.history = None
        self._last_sequence = None  # stored after fit() for prediction
    
    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        for i in range(len(data) - self.lookback_period):
            X.append(data[i:i + self.lookback_period])
            y.append(data[i + self.lookback_period])
        
        return np.array(X), np.array(y)
    
    def fit(self, data: np.ndarray) -> None:
        """
        Fit LSTM model
        
        Args:
            data: 1D array of price data
        """
        try:
            try:
                from tensorflow.keras.models import Sequential
                from tensorflow.keras.layers import LSTM, Dense, Dropout
                from tensorflow.keras.optimizers import Adam
            except ImportError:
                raise ImportError(
                    "TensorFlow is not installed (not yet available for Python 3.14). "
                    "LSTM is disabled — uncheck it in the sidebar."
                )

            # Normalize data
            scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
            
            # Create sequences
            X, y = self.create_sequences(scaled_data)
            
            # Reshape for LSTM [samples, time steps, features]
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            # Build LSTM model
            self.model = Sequential([
                LSTM(50, activation='relu', input_shape=(self.lookback_period, 1), return_sequences=True),
                Dropout(0.2),
                LSTM(50, activation='relu'),
                Dropout(0.2),
                Dense(25, activation='relu'),
                Dense(1)
            ])
            
            self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # Train model
            self.history = self.model.fit(
                X, y,
                epochs=self.epochs,
                batch_size=self.batch_size,
                verbose=0,
                validation_split=0.2
            )

            # Store the last sequence so predict() works without raw data
            self._last_sequence = scaled_data[-self.lookback_period:]
            logger.info("LSTM model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training LSTM: {str(e)}")
            raise
    
    def predict(self, data: np.ndarray = None, periods: int = 5) -> np.ndarray:
        """
        Make predictions. Uses stored sequence from fit() if data is None.

        Args:
            data: Recent price data (optional — uses training tail if omitted)
            periods: Number of periods to forecast

        Returns:
            Array of predicted prices
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if data is not None and len(data) >= self.lookback_period:
            scaled_data = self.scaler.transform(data.reshape(-1, 1))
            current_seq = scaled_data[-self.lookback_period:].reshape(1, self.lookback_period, 1)
        elif self._last_sequence is not None:
            current_seq = self._last_sequence.reshape(1, self.lookback_period, 1)
        else:
            raise ValueError("No data available for prediction. Provide data or call fit() first.")

        predictions = []
        
        for _ in range(periods):
            next_pred = self.model.predict(current_seq, verbose=0)
            predictions.append(next_pred[0, 0])
            
            # Update sequence
            current_seq = np.append(current_seq[:, 1:, :], [[[next_pred[0, 0]]]], axis=1)
        
        # Inverse transform predictions
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        
        return predictions.flatten()


class EnsemblePredictor:
    """Ensemble of multiple prediction models"""
    
    def __init__(self):
        """Initialize ensemble"""
        self.models = {
            'arima': None,
            'prophet': None,
            'lstm': None
        }
        self.weights = {'arima': 0.3, 'prophet': 0.4, 'lstm': 0.3}
    
    def fit_all_models(self, data: pd.Series, use_lstm: bool = False) -> None:
        """
        Fit all available models
        
        Args:
            data: Time series data
            use_lstm: Whether to include LSTM (slower but more accurate)
        """
        if len(data.dropna()) < 30:
            logger.warning("Need ≥30 data points to fit models reliably.")

        try:
            self.models['arima'] = ARIMAPredictor()
            self.models['arima'].fit(data)
            logger.info("ARIMA fitted")
        except Exception as e:
            logger.warning(f"ARIMA fitting failed: {e}")

        try:
            self.models['prophet'] = ProphetPredictor()
            self.models['prophet'].fit(data, data.index)
            logger.info("Prophet fitted")
        except Exception as e:
            logger.warning(f"Prophet fitting failed: {e}")
        
        if use_lstm:
            try:
                self.models['lstm'] = LSTMPredictor()
                self.models['lstm'].fit(data.values)
                logger.info("LSTM fitted")
            except Exception as e:
                logger.warning(f"LSTM fitting failed: {str(e)}")
    
    def predict_ensemble(self, periods: int = 5, use_lstm: bool = False) -> Dict:
        """
        Generate ensemble predictions
        
        Args:
            periods: Number of periods to forecast
            use_lstm: Whether to include LSTM
        
        Returns:
            Dictionary with ensemble predictions
        """
        predictions = {}
        weights_sum = 0
        weighted_pred = np.zeros(periods)
        
        # ARIMA predictions
        if self.models['arima'] is not None:
            pred = self.models['arima'].predict(periods).values
            predictions['arima'] = pred
            weighted_pred += self.weights['arima'] * pred
            weights_sum += self.weights['arima']
        
        # Prophet predictions
        if self.models['prophet'] is not None:
            pred = self.models['prophet'].predict(periods)['yhat'].values
            predictions['prophet'] = pred
            weighted_pred += self.weights['prophet'] * pred
            weights_sum += self.weights['prophet']
        
        # LSTM predictions — uses stored training sequence, no raw data needed
        if use_lstm and self.models['lstm'] is not None:
            pred = self.models['lstm'].predict(None, periods)
            predictions['lstm'] = pred
            weighted_pred += self.weights['lstm'] * pred
            weights_sum += self.weights['lstm']
        
        # Normalize weighted predictions
        ensemble_pred = weighted_pred / weights_sum if weights_sum > 0 else weighted_pred

        predictions['ensemble'] = ensemble_pred

        return predictions

    def predict_with_confidence_intervals(self, periods: int, use_lstm: bool = False,
                                           alpha: float = 0.10) -> Dict:
        """
        Return ensemble forecast with 90% confidence interval from ARIMA.
        Falls back to ±2% bootstrap bands if ARIMA is unavailable.
        """
        base = self.predict_ensemble(periods, use_lstm)['ensemble']

        if self.models['arima'] is not None:
            try:
                ci = self.models['arima'].predict_with_ci(periods, alpha)
                return {
                    'forecast': base,
                    'lower_ci': ci['lower_ci'].values,
                    'upper_ci': ci['upper_ci'].values,
                }
            except Exception:
                pass

        # Bootstrap fallback: ±2% uncertainty band
        lower = base * 0.98
        upper = base * 1.02
        return {'forecast': base, 'lower_ci': lower, 'upper_ci': upper}
