"""Weather-stock correlation and causality analysis service."""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from weather_stock_dashboard.services.timeseries_service import timeseries_service

logger = logging.getLogger(__name__)


class CorrelationService:
    """Service for analyzing correlations between weather and stock data."""
    
    def __init__(self):
        """Initialize correlation service."""
        self.ts_service = timeseries_service
    
    def analyze_weather_stock_correlation(self, weather_data: List[Dict[str, Any]], 
                                        stock_data: List[Dict[str, Any]],
                                        weather_variable: str = "temperature",
                                        stock_variable: str = "price") -> Dict[str, Any]:
        """Analyze correlation between weather and stock variables."""
        try:
            # Prepare time series
            weather_ts = self.ts_service.prepare_time_series(weather_data, weather_variable)
            stock_ts = self.ts_service.prepare_time_series(stock_data, stock_variable)
            
            # If analyzing stock prices, convert to returns for better stationarity
            if stock_variable == "price":
                stock_ts = self.ts_service.calculate_returns(stock_ts, method='log')
                stock_variable = "returns"
            
            # Cross-correlation analysis
            cross_corr_result = self.ts_service.cross_correlation_analysis(
                weather_ts, stock_ts, max_lags=20
            )
            
            # Granger causality test
            granger_result = self.ts_service.granger_causality_test(
                weather_ts, stock_ts, max_lags=5
            )
            
            # Simple correlation coefficient
            aligned_data = pd.concat([weather_ts, stock_ts], axis=1, join='inner').dropna()
            simple_correlation = aligned_data.corr().iloc[0, 1] if len(aligned_data) > 1 else 0.0
            
            # Statistical significance of correlation
            correlation_significance = self._test_correlation_significance(
                simple_correlation, len(aligned_data)
            )
            
            # Relationship strength classification
            relationship_strength = self._classify_relationship_strength(
                abs(simple_correlation)
            )
            
            return {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "weather_variable": weather_variable,
                "stock_variable": stock_variable,
                "data_points": len(aligned_data),
                "simple_correlation": float(simple_correlation),
                "correlation_significance": correlation_significance,
                "relationship_strength": relationship_strength,
                "cross_correlation": cross_corr_result,
                "granger_causality": granger_result,
                "interpretation": self._generate_interpretation(
                    simple_correlation, cross_corr_result, granger_result
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing weather-stock correlation: {e}")
            raise
    
    def _test_correlation_significance(self, correlation: float, n: int) -> Dict[str, Any]:
        """Test statistical significance of correlation coefficient."""
        if n < 3:
            return {"p_value": 1.0, "is_significant": False, "confidence_level": 0.0}
        
        # Calculate t-statistic for correlation
        t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2)) if abs(correlation) < 1 else np.inf
        
        # Approximate p-value (two-tailed test)
        from scipy import stats
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
        
        return {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "is_significant": p_value < 0.05,
            "confidence_level": 1 - p_value
        }
    
    def _classify_relationship_strength(self, abs_correlation: float) -> str:
        """Classify relationship strength based on correlation magnitude."""
        if abs_correlation >= 0.7:
            return "strong"
        elif abs_correlation >= 0.3:
            return "moderate"
        elif abs_correlation >= 0.1:
            return "weak"
        else:
            return "negligible"
    
    def _generate_interpretation(self, correlation: float, cross_corr: Dict[str, Any], 
                               granger: Dict[str, Any]) -> str:
        """Generate human-readable interpretation of the analysis."""
        # Correlation interpretation
        if abs(correlation) < 0.1:
            corr_desc = "negligible correlation"
        elif correlation > 0:
            corr_desc = f"positive correlation (r={correlation:.3f})"
        else:
            corr_desc = f"negative correlation (r={correlation:.3f})"
        
        # Lag interpretation
        optimal_lag = cross_corr.get("optimal_lag", 0)
        if optimal_lag == 0:
            lag_desc = "with no time delay"
        else:
            lag_desc = f"with {optimal_lag}-period lag"
        
        # Causality interpretation
        if granger.get("is_causal", False):
            causality_desc = f"Granger causality detected (p={granger.get('min_p_value', 1.0):.3f})"
        else:
            causality_desc = "No significant Granger causality"
        
        return f"Analysis shows {corr_desc} {lag_desc}. {causality_desc}."
    
    def batch_correlation_analysis(self, weather_data: List[Dict[str, Any]], 
                                 stock_data_dict: Dict[str, List[Dict[str, Any]]],
                                 weather_variables: List[str] = None) -> Dict[str, Any]:
        """Perform correlation analysis for multiple stocks and weather variables."""
        try:
            if weather_variables is None:
                weather_variables = ["temperature", "humidity", "pressure", "precipitation"]
            
            results = {}
            
            for symbol, stock_data in stock_data_dict.items():
                results[symbol] = {}
                
                for weather_var in weather_variables:
                    try:
                        analysis = self.analyze_weather_stock_correlation(
                            weather_data, stock_data, weather_var, "price"
                        )
                        results[symbol][weather_var] = analysis
                        
                    except Exception as e:
                        logger.warning(f"Failed analysis for {symbol}-{weather_var}: {e}")
                        results[symbol][weather_var] = {"error": str(e)}
            
            # Generate summary
            summary = self._generate_batch_summary(results)
            
            return {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "results": results,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error in batch correlation analysis: {e}")
            raise
    
    def _generate_batch_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from batch analysis."""
        all_correlations = []
        significant_relationships = []
        strong_relationships = []
        
        for symbol, symbol_results in results.items():
            for weather_var, analysis in symbol_results.items():
                if "error" not in analysis:
                    corr = analysis.get("simple_correlation", 0)
                    all_correlations.append(abs(corr))
                    
                    if analysis.get("correlation_significance", {}).get("is_significant", False):
                        significant_relationships.append({
                            "symbol": symbol,
                            "weather_variable": weather_var,
                            "correlation": corr,
                            "strength": analysis.get("relationship_strength", "unknown")
                        })
                    
                    if analysis.get("relationship_strength") in ["strong", "moderate"]:
                        strong_relationships.append({
                            "symbol": symbol,
                            "weather_variable": weather_var,
                            "correlation": corr,
                            "strength": analysis.get("relationship_strength")
                        })
        
        return {
            "total_analyses": len(all_correlations),
            "mean_absolute_correlation": float(np.mean(all_correlations)) if all_correlations else 0.0,
            "max_absolute_correlation": float(np.max(all_correlations)) if all_correlations else 0.0,
            "significant_relationships_count": len(significant_relationships),
            "strong_relationships_count": len(strong_relationships),
            "significant_relationships": significant_relationships,
            "strong_relationships": strong_relationships
        }
    
    def sector_weather_analysis(self, weather_data: List[Dict[str, Any]], 
                               stock_data_by_sector: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> Dict[str, Any]:
        """Analyze weather correlations by stock sector."""
        try:
            sector_results = {}
            
            for sector, sector_stocks in stock_data_by_sector.items():
                sector_analysis = self.batch_correlation_analysis(weather_data, sector_stocks)
                sector_results[sector] = sector_analysis
            
            # Compare sectors
            sector_comparison = self._compare_sectors(sector_results)
            
            return {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "sector_results": sector_results,
                "sector_comparison": sector_comparison
            }
            
        except Exception as e:
            logger.error(f"Error in sector weather analysis: {e}")
            raise
    
    def _compare_sectors(self, sector_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare weather sensitivity across sectors."""
        sector_stats = {}
        
        for sector, results in sector_results.items():
            summary = results.get("summary", {})
            sector_stats[sector] = {
                "mean_correlation": summary.get("mean_absolute_correlation", 0.0),
                "significant_count": summary.get("significant_relationships_count", 0),
                "strong_count": summary.get("strong_relationships_count", 0)
            }
        
        # Rank sectors by weather sensitivity
        sensitivity_ranking = sorted(
            sector_stats.items(), 
            key=lambda x: x[1]["mean_correlation"], 
            reverse=True
        )
        
        return {
            "sector_statistics": sector_stats,
            "sensitivity_ranking": [sector[0] for sector in sensitivity_ranking],
            "most_sensitive_sector": sensitivity_ranking[0][0] if sensitivity_ranking else None,
            "least_sensitive_sector": sensitivity_ranking[-1][0] if sensitivity_ranking else None
        }


# Global correlation service instance
correlation_service = CorrelationService()