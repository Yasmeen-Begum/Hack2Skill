"""Time series modeling service for ARIMA and GARCH models."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings

# Suppress statsmodels warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.stattools import adfuller, ccf, grangercausalitytests
    from statsmodels.tsa.vector_ar.var_model import VAR
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from arch import arch_model
    from arch.unitroot import ADF
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)


class TimeSeriesService:
    """Service for time series analysis using ARIMA and GARCH models."""
    
    def __init__(self):
        """Initialize time series service."""
        self.min_data_points_arima = settings.min_data_points_arima
        self.min_data_points_garch = settings.min_data_points_garch
        self.forecast_horizon = settings.forecast_horizon_days
        
        if not STATSMODELS_AVAILABLE:
            logger.warning("statsmodels not available - ARIMA functionality disabled")
        if not ARCH_AVAILABLE:
            logger.warning("arch not available - GARCH functionality disabled")
    
    def prepare_time_series(self, data: List[Dict[str, Any]], value_column: str, 
                           timestamp_column: str = "timestamp") -> pd.Series:
        """Prepare time series data from raw data."""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Convert timestamp to datetime
            df[timestamp_column] = pd.to_datetime(df[timestamp_column])
            
            # Sort by timestamp
            df = df.sort_values(timestamp_column)
            
            # Create time series
            ts = pd.Series(
                data=df[value_column].values,
                index=df[timestamp_column],
                name=value_column
            )
            
            # Remove duplicates and NaN values
            ts = ts.dropna().groupby(ts.index).last()
            
            logger.info(f"Prepared time series with {len(ts)} data points")
            return ts
            
        except Exception as e:
            logger.error(f"Error preparing time series: {e}")
            raise
    
    def check_stationarity(self, ts: pd.Series) -> Dict[str, Any]:
        """Check if time series is stationary using Augmented Dickey-Fuller test."""
        try:
            if not STATSMODELS_AVAILABLE:
                raise ValueError("statsmodels not available")
            
            result = adfuller(ts.dropna())
            
            return {
                "adf_statistic": result[0],
                "p_value": result[1],
                "critical_values": result[4],
                "is_stationary": result[1] < 0.05,
                "interpretation": "Stationary" if result[1] < 0.05 else "Non-stationary"
            }
            
        except Exception as e:
            logger.error(f"Error checking stationarity: {e}")
            raise
    
    def auto_arima_order_selection(self, ts: pd.Series, max_p: int = 5, max_d: int = 2, 
                                  max_q: int = 5) -> Tuple[int, int, int]:
        """Automatically select ARIMA order using AIC criterion."""
        try:
            if not STATSMODELS_AVAILABLE:
                raise ValueError("statsmodels not available")
            
            best_aic = float('inf')
            best_order = (0, 0, 0)
            
            for p in range(max_p + 1):
                for d in range(max_d + 1):
                    for q in range(max_q + 1):
                        try:
                            model = ARIMA(ts, order=(p, d, q))
                            fitted_model = model.fit()
                            
                            if fitted_model.aic < best_aic:
                                best_aic = fitted_model.aic
                                best_order = (p, d, q)
                                
                        except Exception:
                            continue
            
            logger.info(f"Selected ARIMA order: {best_order} with AIC: {best_aic}")
            return best_order
            
        except Exception as e:
            logger.error(f"Error in auto ARIMA order selection: {e}")
            # Return default order
            return (1, 1, 1)
    
    def fit_arima_model(self, ts: pd.Series, order: Optional[Tuple[int, int, int]] = None) -> Dict[str, Any]:
        """Fit ARIMA model to time series data."""
        try:
            if not STATSMODELS_AVAILABLE:
                raise ValueError("statsmodels not available")
            
            if len(ts) < self.min_data_points_arima:
                raise ValueError(f"Insufficient data points. Need at least {self.min_data_points_arima}, got {len(ts)}")
            
            # Auto-select order if not provided
            if order is None:
                order = self.auto_arima_order_selection(ts)
            
            # Fit ARIMA model
            model = ARIMA(ts, order=order)
            fitted_model = model.fit()
            
            # Generate forecast
            forecast_result = fitted_model.forecast(steps=self.forecast_horizon)
            forecast_ci = fitted_model.get_forecast(steps=self.forecast_horizon).conf_int()
            
            # Model diagnostics
            residuals = fitted_model.resid
            ljung_box = acorr_ljungbox(residuals, lags=10, return_df=True)
            
            return {
                "order": order,
                "aic": fitted_model.aic,
                "bic": fitted_model.bic,
                "forecast": forecast_result.tolist(),
                "forecast_confidence_intervals": [
                    (float(forecast_ci.iloc[i, 0]), float(forecast_ci.iloc[i, 1])) 
                    for i in range(len(forecast_ci))
                ],
                "model_summary": str(fitted_model.summary()),
                "residuals_ljung_box_p": float(ljung_box['lb_pvalue'].iloc[-1]),
                "fitted_model": fitted_model  # Keep for further analysis
            }
            
        except Exception as e:
            logger.error(f"Error fitting ARIMA model: {e}")
            raise
    
    def seasonal_decomposition(self, ts: pd.Series, model: str = 'additive', 
                              period: Optional[int] = None) -> Dict[str, Any]:
        """Perform seasonal decomposition of time series."""
        try:
            if not STATSMODELS_AVAILABLE:
                raise ValueError("statsmodels not available")
            
            # Auto-detect period if not provided
            if period is None:
                # Simple heuristic: daily data -> weekly (7), hourly -> daily (24)
                freq = pd.infer_freq(ts.index)
                if freq and 'D' in freq:
                    period = 7  # Weekly seasonality for daily data
                elif freq and 'H' in freq:
                    period = 24  # Daily seasonality for hourly data
                else:
                    period = min(12, len(ts) // 4)  # Default fallback
            
            decomposition = seasonal_decompose(ts, model=model, period=period)
            
            return {
                "trend": decomposition.trend.dropna().tolist(),
                "seasonal": decomposition.seasonal.dropna().tolist(),
                "residual": decomposition.resid.dropna().tolist(),
                "period": period,
                "model": model
            }
            
        except Exception as e:
            logger.error(f"Error in seasonal decomposition: {e}")
            raise
    
    def fit_garch_model(self, returns: pd.Series, model_type: str = 'GARCH', 
                       p: int = 1, q: int = 1) -> Dict[str, Any]:
        """Fit GARCH model for volatility analysis."""
        try:
            if not ARCH_AVAILABLE:
                raise ValueError("arch package not available")
            
            if len(returns) < self.min_data_points_garch:
                raise ValueError(f"Insufficient data points for GARCH. Need at least {self.min_data_points_garch}, got {len(returns)}")
            
            # Remove any infinite or NaN values
            returns_clean = returns.replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(returns_clean) < self.min_data_points_garch:
                raise ValueError("Insufficient clean data points after removing NaN/inf values")
            
            # Fit GARCH model
            if model_type.upper() == 'GARCH':
                model = arch_model(returns_clean, vol='Garch', p=p, q=q)
            elif model_type.upper() == 'EGARCH':
                model = arch_model(returns_clean, vol='EGARCH', p=p, q=q)
            elif model_type.upper() == 'GJR-GARCH':
                model = arch_model(returns_clean, vol='GARCH', p=p, o=1, q=q)
            else:
                raise ValueError(f"Unsupported GARCH model type: {model_type}")
            
            fitted_model = model.fit(disp='off')
            
            # Generate volatility forecast
            volatility_forecast = fitted_model.forecast(horizon=self.forecast_horizon)
            
            return {
                "model_type": model_type,
                "parameters": {"p": p, "q": q},
                "aic": fitted_model.aic,
                "bic": fitted_model.bic,
                "conditional_volatility": fitted_model.conditional_volatility.tolist(),
                "volatility_forecast": volatility_forecast.variance.iloc[-1].tolist(),
                "model_summary": str(fitted_model.summary()),
                "fitted_model": fitted_model
            }
            
        except Exception as e:
            logger.error(f"Error fitting GARCH model: {e}")
            raise
    
    def calculate_returns(self, prices: pd.Series, method: str = 'log') -> pd.Series:
        """Calculate returns from price series."""
        try:
            if method == 'log':
                returns = np.log(prices / prices.shift(1))
            elif method == 'simple':
                returns = prices.pct_change()
            else:
                raise ValueError(f"Unsupported return calculation method: {method}")
            
            return returns.dropna()
            
        except Exception as e:
            logger.error(f"Error calculating returns: {e}")
            raise
    
    def cross_correlation_analysis(self, ts1: pd.Series, ts2: pd.Series, 
                                  max_lags: int = 20) -> Dict[str, Any]:
        """Perform cross-correlation analysis between two time series."""
        try:
            if not STATSMODELS_AVAILABLE:
                raise ValueError("statsmodels not available")
            
            # Align time series
            aligned_data = pd.concat([ts1, ts2], axis=1, join='inner').dropna()
            if len(aligned_data) < 20:
                raise ValueError("Insufficient overlapping data points for cross-correlation")
            
            ts1_aligned = aligned_data.iloc[:, 0]
            ts2_aligned = aligned_data.iloc[:, 1]
            
            # Calculate cross-correlation
            cross_corr = ccf(ts1_aligned, ts2_aligned, adjusted=False)[:max_lags+1]
            
            # Find optimal lag
            optimal_lag = np.argmax(np.abs(cross_corr))
            optimal_correlation = cross_corr[optimal_lag]
            
            return {
                "cross_correlation": cross_corr.tolist(),
                "optimal_lag": int(optimal_lag),
                "optimal_correlation": float(optimal_correlation),
                "max_lags": max_lags
            }
            
        except Exception as e:
            logger.error(f"Error in cross-correlation analysis: {e}")
            raise
    
    def granger_causality_test(self, ts1: pd.Series, ts2: pd.Series, 
                              max_lags: int = 5) -> Dict[str, Any]:
        """Perform Granger causality test between two time series."""
        try:
            if not STATSMODELS_AVAILABLE:
                raise ValueError("statsmodels not available")
            
            # Align time series
            aligned_data = pd.concat([ts1, ts2], axis=1, join='inner').dropna()
            if len(aligned_data) < max_lags * 3:
                raise ValueError("Insufficient data points for Granger causality test")
            
            # Perform Granger causality test
            result = grangercausalitytests(aligned_data, maxlag=max_lags, verbose=False)
            
            # Extract p-values for different lags
            p_values = {}
            for lag in range(1, max_lags + 1):
                p_values[lag] = result[lag][0]['ssr_ftest'][1]  # F-test p-value
            
            # Find minimum p-value
            min_p_value = min(p_values.values())
            best_lag = min(p_values, key=p_values.get)
            
            return {
                "p_values_by_lag": p_values,
                "min_p_value": float(min_p_value),
                "best_lag": int(best_lag),
                "is_causal": min_p_value < 0.05,
                "interpretation": f"{'Significant' if min_p_value < 0.05 else 'No significant'} Granger causality at lag {best_lag}"
            }
            
        except Exception as e:
            logger.error(f"Error in Granger causality test: {e}")
            raise
    
    def var_model_analysis(self, data: pd.DataFrame, max_lags: int = 5) -> Dict[str, Any]:
        """Perform Vector Autoregression (VAR) analysis."""
        try:
            if not STATSMODELS_AVAILABLE:
                raise ValueError("statsmodels not available")
            
            # Remove NaN values
            data_clean = data.dropna()
            
            if len(data_clean) < max_lags * 3:
                raise ValueError("Insufficient data points for VAR analysis")
            
            # Fit VAR model
            model = VAR(data_clean)
            fitted_model = model.fit(maxlags=max_lags, ic='aic')
            
            # Generate forecast
            forecast = fitted_model.forecast(data_clean.values[-fitted_model.k_ar:], steps=self.forecast_horizon)
            
            # Impulse response analysis
            irf = fitted_model.irf(periods=10)
            
            return {
                "selected_lags": fitted_model.k_ar,
                "aic": fitted_model.aic,
                "bic": fitted_model.bic,
                "forecast": forecast.tolist(),
                "impulse_responses": irf.irfs.tolist(),
                "model_summary": str(fitted_model.summary()),
                "fitted_model": fitted_model
            }
            
        except Exception as e:
            logger.error(f"Error in VAR analysis: {e}")
            raise


# Global time series service instance
timeseries_service = TimeSeriesService()