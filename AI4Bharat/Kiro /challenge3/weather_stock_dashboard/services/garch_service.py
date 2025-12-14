"""GARCH volatility modeling service."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from weather_stock_dashboard.services.timeseries_service import timeseries_service

logger = logging.getLogger(__name__)


class GARCHService:
    """Specialized service for GARCH volatility modeling."""
    
    def __init__(self):
        """Initialize GARCH service."""
        self.ts_service = timeseries_service
    
    def analyze_stock_volatility(self, stock_data: List[Dict[str, Any]], 
                                symbol: str) -> Dict[str, Any]:
        """Analyze stock volatility using GARCH models."""
        try:
            # Prepare price time series
            price_ts = self.ts_service.prepare_time_series(stock_data, "price")
            
            # Calculate returns
            returns = self.ts_service.calculate_returns(price_ts, method='log')
            
            # Fit different GARCH models
            garch_results = {}
            
            # Standard GARCH(1,1)
            try:
                garch_11 = self.ts_service.fit_garch_model(returns, 'GARCH', p=1, q=1)
                garch_results['GARCH_1_1'] = garch_11
            except Exception as e:
                logger.warning(f"Failed to fit GARCH(1,1) for {symbol}: {e}")
            
            # EGARCH(1,1)
            try:
                egarch_11 = self.ts_service.fit_garch_model(returns, 'EGARCH', p=1, q=1)
                garch_results['EGARCH_1_1'] = egarch_11
            except Exception as e:
                logger.warning(f"Failed to fit EGARCH(1,1) for {symbol}: {e}")
            
            # GJR-GARCH(1,1,1)
            try:
                gjr_garch = self.ts_service.fit_garch_model(returns, 'GJR-GARCH', p=1, q=1)
                garch_results['GJR_GARCH_1_1_1'] = gjr_garch
            except Exception as e:
                logger.warning(f"Failed to fit GJR-GARCH(1,1,1) for {symbol}: {e}")
            
            if not garch_results:
                raise ValueError(f"No GARCH models could be fitted for {symbol}")
            
            # Select best model based on AIC
            best_model_name = min(garch_results.keys(), 
                                key=lambda k: garch_results[k]['aic'])
            best_model = garch_results[best_model_name]
            
            # Calculate volatility statistics
            volatility_stats = self._calculate_volatility_statistics(
                best_model['conditional_volatility']
            )
            
            return {
                "symbol": symbol,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "returns_statistics": self._calculate_returns_statistics(returns),
                "garch_models": garch_results,
                "best_model": {
                    "name": best_model_name,
                    "results": best_model
                },
                "volatility_statistics": volatility_stats,
                "volatility_clustering": self._detect_volatility_clustering(
                    best_model['conditional_volatility']
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stock volatility for {symbol}: {e}")
            raise
    
    def _calculate_returns_statistics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate basic statistics for returns."""
        return {
            "mean": float(returns.mean()),
            "std": float(returns.std()),
            "skewness": float(returns.skew()),
            "kurtosis": float(returns.kurtosis()),
            "min": float(returns.min()),
            "max": float(returns.max()),
            "count": len(returns)
        }
    
    def _calculate_volatility_statistics(self, volatility: List[float]) -> Dict[str, float]:
        """Calculate statistics for conditional volatility."""
        vol_array = np.array(volatility)
        
        return {
            "mean_volatility": float(np.mean(vol_array)),
            "std_volatility": float(np.std(vol_array)),
            "min_volatility": float(np.min(vol_array)),
            "max_volatility": float(np.max(vol_array)),
            "volatility_of_volatility": float(np.std(vol_array) / np.mean(vol_array))
        }
    
    def _detect_volatility_clustering(self, volatility: List[float]) -> Dict[str, Any]:
        """Detect volatility clustering patterns."""
        vol_array = np.array(volatility)
        
        # Calculate rolling standard deviation to detect clustering
        vol_series = pd.Series(vol_array)
        rolling_std = vol_series.rolling(window=10).std()
        
        # Identify high volatility periods (above 75th percentile)
        high_vol_threshold = np.percentile(vol_array, 75)
        high_vol_periods = vol_array > high_vol_threshold
        
        # Calculate clustering metric
        clustering_score = self._calculate_clustering_score(high_vol_periods)
        
        return {
            "high_volatility_threshold": float(high_vol_threshold),
            "high_volatility_periods": int(np.sum(high_vol_periods)),
            "clustering_score": float(clustering_score),
            "interpretation": self._interpret_clustering_score(clustering_score)
        }
    
    def _calculate_clustering_score(self, high_vol_periods: np.ndarray) -> float:
        """Calculate a simple clustering score."""
        if len(high_vol_periods) < 2:
            return 0.0
        
        # Count consecutive high volatility periods
        consecutive_count = 0
        current_streak = 0
        
        for is_high_vol in high_vol_periods:
            if is_high_vol:
                current_streak += 1
            else:
                if current_streak > 1:
                    consecutive_count += current_streak
                current_streak = 0
        
        # Add final streak if it ends with high volatility
        if current_streak > 1:
            consecutive_count += current_streak
        
        # Normalize by total high volatility periods
        total_high_vol = np.sum(high_vol_periods)
        if total_high_vol == 0:
            return 0.0
        
        return consecutive_count / total_high_vol
    
    def _interpret_clustering_score(self, score: float) -> str:
        """Interpret clustering score."""
        if score > 0.7:
            return "Strong volatility clustering detected"
        elif score > 0.4:
            return "Moderate volatility clustering detected"
        elif score > 0.1:
            return "Weak volatility clustering detected"
        else:
            return "No significant volatility clustering"
    
    def compare_volatility_models(self, stock_data: List[Dict[str, Any]], 
                                 symbol: str) -> Dict[str, Any]:
        """Compare different volatility models for a stock."""
        try:
            analysis = self.analyze_stock_volatility(stock_data, symbol)
            
            models = analysis['garch_models']
            comparison = {}
            
            for model_name, model_results in models.items():
                comparison[model_name] = {
                    "aic": model_results['aic'],
                    "bic": model_results['bic'],
                    "mean_volatility": np.mean(model_results['conditional_volatility']),
                    "volatility_persistence": self._calculate_persistence(
                        model_results.get('fitted_model')
                    )
                }
            
            # Rank models by AIC
            ranked_models = sorted(comparison.items(), key=lambda x: x[1]['aic'])
            
            return {
                "symbol": symbol,
                "model_comparison": comparison,
                "ranking_by_aic": [model[0] for model in ranked_models],
                "best_model": ranked_models[0][0] if ranked_models else None,
                "recommendation": self._generate_model_recommendation(ranked_models)
            }
            
        except Exception as e:
            logger.error(f"Error comparing volatility models for {symbol}: {e}")
            raise
    
    def _calculate_persistence(self, fitted_model) -> Optional[float]:
        """Calculate volatility persistence from fitted GARCH model."""
        try:
            if fitted_model is None:
                return None
            
            # For GARCH models, persistence is typically alpha + beta
            params = fitted_model.params
            
            # Try to extract alpha and beta parameters
            alpha = 0.0
            beta = 0.0
            
            for param_name, param_value in params.items():
                if 'alpha' in param_name.lower():
                    alpha += param_value
                elif 'beta' in param_name.lower():
                    beta += param_value
            
            return float(alpha + beta) if (alpha + beta) > 0 else None
            
        except Exception:
            return None
    
    def _generate_model_recommendation(self, ranked_models: List[tuple]) -> str:
        """Generate recommendation based on model comparison."""
        if not ranked_models:
            return "No models could be fitted successfully"
        
        best_model = ranked_models[0][0]
        
        if 'EGARCH' in best_model:
            return f"EGARCH model recommended - captures asymmetric volatility effects"
        elif 'GJR' in best_model:
            return f"GJR-GARCH model recommended - accounts for leverage effects"
        elif 'GARCH' in best_model:
            return f"Standard GARCH model recommended - good baseline volatility model"
        else:
            return f"{best_model} recommended based on information criteria"


# Global GARCH service instance
garch_service = GARCHService()