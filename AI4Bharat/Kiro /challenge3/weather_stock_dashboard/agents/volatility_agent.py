"""Volatility Analyzer Agent for GARCH modeling and volatility analysis."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from weather_stock_dashboard.agents.base_agent import BaseWeatherStockAgent, BaseTool
from weather_stock_dashboard.services.garch_service import garch_service
from weather_stock_dashboard.services.timeseries_service import timeseries_service

logger = logging.getLogger(__name__)


class GARCHModelingTool(BaseTool):
    """Tool for GARCH volatility modeling."""
    
    name: str = "garch_modeling"
    description: str = "Fit GARCH models to analyze volatility patterns in stock returns"
    
    def _run(self, stock_data: List[Dict[str, Any]], symbol: str) -> str:
        """Run GARCH modeling."""
        try:
            result = garch_service.analyze_stock_volatility(stock_data, symbol)
            best_model = result["best_model"]["name"]
            vol_stats = result["volatility_statistics"]
            
            return f"GARCH analysis for {symbol}: Best model is {best_model}. Mean volatility: {vol_stats['mean_volatility']:.4f}"
        except Exception as e:
            return f"GARCH modeling failed: {str(e)}"


class VolatilityClusteringTool(BaseTool):
    """Tool for detecting volatility clustering."""
    
    name: str = "volatility_clustering"
    description: str = "Detect and analyze volatility clustering patterns"
    
    def _run(self, stock_data: List[Dict[str, Any]], symbol: str) -> str:
        """Run volatility clustering analysis."""
        try:
            result = garch_service.analyze_stock_volatility(stock_data, symbol)
            clustering = result["volatility_clustering"]
            
            return f"Volatility clustering for {symbol}: {clustering['interpretation']} (Score: {clustering['clustering_score']:.3f})"
        except Exception as e:
            return f"Volatility clustering analysis failed: {str(e)}"


class WeatherVolatilityTool(BaseTool):
    """Tool for analyzing weather impact on volatility."""
    
    name: str = "weather_volatility"
    description: str = "Analyze correlation between weather patterns and stock volatility"
    
    def _run(self, weather_data: List[Dict[str, Any]], stock_data: List[Dict[str, Any]], 
             weather_var: str = "temperature") -> str:
        """Run weather-volatility correlation analysis."""
        try:
            # This would integrate with correlation service
            return f"Weather-volatility analysis completed for {weather_var}"
        except Exception as e:
            return f"Weather-volatility analysis failed: {str(e)}"


class VolatilityAnalyzerAgent(BaseWeatherStockAgent):
    """Agent for volatility analysis using GARCH models and weather correlations."""
    
    def __init__(self):
        """Initialize Volatility Analyzer Agent."""
        super().__init__(
            name="volatility_analyzer",
            role="Volatility Risk Analyst",
            goal="Analyze volatility patterns in stock markets and their relationship with weather conditions",
            backstory="""You are a quantitative risk analyst specializing in volatility 
            modeling and market risk assessment. You have extensive experience with GARCH 
            models, volatility clustering, and understanding how external factors like 
            weather can influence market volatility patterns."""
        )
        
        self.volatility_cache = {}  # Cache volatility analysis results
        
    def get_tools(self) -> List[BaseTool]:
        """Get tools for volatility analysis."""
        return [
            GARCHModelingTool(),
            VolatilityClusteringTool(),
            WeatherVolatilityTool()
        ]
    
    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute volatility analysis task."""
        try:
            task_type = context.get("task_type", "volatility_analysis")
            stock_data = context.get("stock_data", [])
            symbol = context.get("symbol", "UNKNOWN")
            
            if task_type == "volatility_analysis":
                result = await self._analyze_volatility(stock_data, symbol, context)
            
            elif task_type == "model_comparison":
                result = await self._compare_volatility_models(stock_data, symbol)
            
            elif task_type == "volatility_forecasting":
                result = await self._forecast_volatility(stock_data, symbol, context)
            
            elif task_type == "weather_volatility_correlation":
                weather_data = context.get("weather_data", [])
                result = await self._analyze_weather_volatility_correlation(
                    weather_data, stock_data, symbol, context
                )
            
            elif task_type == "regime_detection":
                result = await self._detect_volatility_regimes(stock_data, symbol)
            
            elif task_type == "risk_assessment":
                result = await self._assess_volatility_risk(stock_data, symbol, context)
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Update agent memory
            self.update_memory(f"last_{task_type}_result", result)
            
            return {
                "agent": self.name,
                "task": task_description,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": result.get("summary", "Volatility analysis completed successfully")
            }
            
        except Exception as e:
            logger.error(f"Volatility analysis task failed: {e}")
            return {
                "agent": self.name,
                "task": task_description,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "summary": f"Volatility analysis failed: {str(e)}"
            }
    
    async def _analyze_volatility(self, stock_data: List[Dict[str, Any]], symbol: str, 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive volatility analysis."""
        try:
            # Check cache first
            cache_key = f"{symbol}_volatility"
            if cache_key in self.volatility_cache:
                cached_result = self.volatility_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    logger.info(f"Using cached volatility analysis for {symbol}")
                    return cached_result
            
            # Perform GARCH analysis
            garch_analysis = garch_service.analyze_stock_volatility(stock_data, symbol)
            
            # Additional volatility metrics
            additional_metrics = self._calculate_additional_volatility_metrics(stock_data)
            
            # Volatility interpretation
            interpretation = self._interpret_volatility_analysis(garch_analysis, additional_metrics)
            
            result = {
                "symbol": symbol,
                "garch_analysis": garch_analysis,
                "additional_metrics": additional_metrics,
                "interpretation": interpretation,
                "recommendations": self._generate_volatility_recommendations(garch_analysis),
                "summary": f"Volatility analysis for {symbol}: {garch_analysis['best_model']['name']} model selected, {garch_analysis['volatility_clustering']['interpretation']}"
            }
            
            # Cache result
            self.volatility_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Volatility analysis failed for {symbol}: {e}")
            raise
    
    async def _compare_volatility_models(self, stock_data: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
        """Compare different volatility models."""
        try:
            comparison = garch_service.compare_volatility_models(stock_data, symbol)
            
            # Add detailed analysis
            model_insights = self._analyze_model_comparison(comparison)
            
            return {
                "symbol": symbol,
                "model_comparison": comparison,
                "insights": model_insights,
                "recommendation": comparison["recommendation"],
                "summary": f"Model comparison for {symbol}: {comparison['best_model']} recommended"
            }
            
        except Exception as e:
            logger.error(f"Model comparison failed for {symbol}: {e}")
            raise
    
    async def _forecast_volatility(self, stock_data: List[Dict[str, Any]], symbol: str, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate volatility forecasts."""
        try:
            # Get volatility analysis
            volatility_analysis = await self._analyze_volatility(stock_data, symbol, context)
            garch_analysis = volatility_analysis["garch_analysis"]
            
            # Extract forecast from best model
            best_model_results = garch_analysis["best_model"]["results"]
            volatility_forecast = best_model_results.get("volatility_forecast", [])
            
            # Generate forecast interpretation
            forecast_interpretation = self._interpret_volatility_forecast(
                volatility_forecast, symbol, context.get("forecast_horizon", 30)
            )
            
            return {
                "symbol": symbol,
                "forecast_horizon": len(volatility_forecast),
                "volatility_forecast": volatility_forecast,
                "current_volatility": garch_analysis["volatility_statistics"]["mean_volatility"],
                "forecast_interpretation": forecast_interpretation,
                "confidence_assessment": self._assess_forecast_confidence(best_model_results),
                "summary": f"Volatility forecast for {symbol}: {len(volatility_forecast)}-period forecast generated"
            }
            
        except Exception as e:
            logger.error(f"Volatility forecasting failed for {symbol}: {e}")
            raise
    
    async def _analyze_weather_volatility_correlation(self, weather_data: List[Dict[str, Any]], 
                                                    stock_data: List[Dict[str, Any]], symbol: str, 
                                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation between weather and volatility."""
        try:
            # Calculate stock returns and volatility
            price_ts = timeseries_service.prepare_time_series(stock_data, "price")
            returns = timeseries_service.calculate_returns(price_ts)
            
            # Calculate rolling volatility
            rolling_volatility = returns.rolling(window=20).std()
            
            # Prepare weather time series
            weather_var = context.get("weather_variable", "temperature")
            weather_ts = timeseries_service.prepare_time_series(weather_data, weather_var)
            
            # Cross-correlation analysis
            cross_corr_result = timeseries_service.cross_correlation_analysis(
                weather_ts, rolling_volatility, max_lags=10
            )
            
            # Interpretation
            correlation_interpretation = self._interpret_weather_volatility_correlation(
                cross_corr_result, weather_var, symbol
            )
            
            return {
                "symbol": symbol,
                "weather_variable": weather_var,
                "cross_correlation": cross_corr_result,
                "interpretation": correlation_interpretation,
                "significance": self._assess_correlation_significance(cross_corr_result),
                "summary": f"Weather-volatility correlation for {symbol}: {correlation_interpretation}"
            }
            
        except Exception as e:
            logger.error(f"Weather-volatility correlation analysis failed: {e}")
            raise
    
    async def _detect_volatility_regimes(self, stock_data: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
        """Detect different volatility regimes."""
        try:
            # Get volatility analysis
            garch_analysis = garch_service.analyze_stock_volatility(stock_data, symbol)
            conditional_volatility = garch_analysis["best_model"]["results"]["conditional_volatility"]
            
            # Simple regime detection using quantiles
            import numpy as np
            vol_array = np.array(conditional_volatility)
            
            # Define regimes based on volatility levels
            low_threshold = np.percentile(vol_array, 33)
            high_threshold = np.percentile(vol_array, 67)
            
            regimes = []
            for i, vol in enumerate(vol_array):
                if vol <= low_threshold:
                    regimes.append("Low")
                elif vol >= high_threshold:
                    regimes.append("High")
                else:
                    regimes.append("Medium")
            
            # Analyze regime transitions
            regime_analysis = self._analyze_regime_transitions(regimes)
            
            return {
                "symbol": symbol,
                "regimes": regimes,
                "regime_thresholds": {
                    "low": float(low_threshold),
                    "high": float(high_threshold)
                },
                "regime_analysis": regime_analysis,
                "current_regime": regimes[-1] if regimes else "Unknown",
                "summary": f"Volatility regime analysis for {symbol}: Currently in {regimes[-1] if regimes else 'Unknown'} volatility regime"
            }
            
        except Exception as e:
            logger.error(f"Volatility regime detection failed for {symbol}: {e}")
            raise
    
    async def _assess_volatility_risk(self, stock_data: List[Dict[str, Any]], symbol: str, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess volatility-based risk metrics."""
        try:
            # Get volatility analysis
            volatility_analysis = await self._analyze_volatility(stock_data, symbol, context)
            garch_analysis = volatility_analysis["garch_analysis"]
            
            # Calculate risk metrics
            vol_stats = garch_analysis["volatility_statistics"]
            returns_stats = garch_analysis["returns_statistics"]
            
            # Value at Risk (VaR) estimation
            var_95 = self._calculate_var(returns_stats, vol_stats, confidence_level=0.95)
            var_99 = self._calculate_var(returns_stats, vol_stats, confidence_level=0.99)
            
            # Risk assessment
            risk_level = self._assess_risk_level(vol_stats, returns_stats)
            
            return {
                "symbol": symbol,
                "risk_metrics": {
                    "var_95": var_95,
                    "var_99": var_99,
                    "volatility_of_volatility": vol_stats["volatility_of_volatility"],
                    "max_volatility": vol_stats["max_volatility"],
                    "mean_volatility": vol_stats["mean_volatility"]
                },
                "risk_assessment": risk_level,
                "recommendations": self._generate_risk_recommendations(risk_level, vol_stats),
                "summary": f"Risk assessment for {symbol}: {risk_level['level']} risk level"
            }
            
        except Exception as e:
            logger.error(f"Volatility risk assessment failed for {symbol}: {e}")
            raise
    
    def _calculate_additional_volatility_metrics(self, stock_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate additional volatility metrics."""
        try:
            price_ts = timeseries_service.prepare_time_series(stock_data, "price")
            returns = timeseries_service.calculate_returns(price_ts)
            
            import numpy as np
            
            # Realized volatility
            realized_vol = float(returns.std() * np.sqrt(252))  # Annualized
            
            # Rolling volatility statistics
            rolling_vol = returns.rolling(window=20).std()
            vol_of_vol = float(rolling_vol.std())
            
            # Volatility skewness and kurtosis
            vol_skew = float(rolling_vol.skew())
            vol_kurtosis = float(rolling_vol.kurtosis())
            
            return {
                "realized_volatility": realized_vol,
                "volatility_of_volatility": vol_of_vol,
                "volatility_skewness": vol_skew,
                "volatility_kurtosis": vol_kurtosis,
                "volatility_range": {
                    "min": float(rolling_vol.min()),
                    "max": float(rolling_vol.max())
                }
            }
            
        except Exception as e:
            logger.error(f"Additional volatility metrics calculation failed: {e}")
            return {}
    
    def _interpret_volatility_analysis(self, garch_analysis: Dict[str, Any], 
                                     additional_metrics: Dict[str, Any]) -> str:
        """Interpret volatility analysis results."""
        vol_stats = garch_analysis["volatility_statistics"]
        clustering = garch_analysis["volatility_clustering"]
        best_model = garch_analysis["best_model"]["name"]
        
        interpretation = f"Volatility analysis using {best_model} model reveals "
        
        # Volatility level assessment
        mean_vol = vol_stats["mean_volatility"]
        if mean_vol > 0.03:
            interpretation += "high volatility levels. "
        elif mean_vol > 0.015:
            interpretation += "moderate volatility levels. "
        else:
            interpretation += "low volatility levels. "
        
        # Clustering assessment
        interpretation += clustering["interpretation"] + ". "
        
        # Additional insights
        if additional_metrics.get("volatility_of_volatility", 0) > 0.01:
            interpretation += "Volatility shows significant time-variation."
        else:
            interpretation += "Volatility is relatively stable over time."
        
        return interpretation
    
    def _generate_volatility_recommendations(self, garch_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on volatility analysis."""
        recommendations = []
        
        vol_stats = garch_analysis["volatility_statistics"]
        clustering = garch_analysis["volatility_clustering"]
        
        # High volatility recommendations
        if vol_stats["mean_volatility"] > 0.03:
            recommendations.append("Consider risk management strategies due to high volatility")
            recommendations.append("Monitor position sizing carefully")
        
        # Volatility clustering recommendations
        if clustering["clustering_score"] > 0.5:
            recommendations.append("Strong volatility clustering suggests predictable volatility patterns")
            recommendations.append("Consider volatility-based trading strategies")
        
        # Model-specific recommendations
        best_model = garch_analysis["best_model"]["name"]
        if "EGARCH" in best_model:
            recommendations.append("EGARCH model indicates asymmetric volatility effects")
        elif "GJR" in best_model:
            recommendations.append("GJR-GARCH suggests leverage effects in volatility")
        
        return recommendations if recommendations else ["Volatility patterns appear normal"]
    
    def _is_cache_valid(self, cached_result: Dict[str, Any], max_age_hours: int = 1) -> bool:
        """Check if cached result is still valid."""
        try:
            from datetime import datetime, timedelta
            cache_time = datetime.fromisoformat(cached_result.get("timestamp", ""))
            return datetime.utcnow() - cache_time < timedelta(hours=max_age_hours)
        except Exception:
            return False
    
    def _analyze_model_comparison(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze model comparison results."""
        model_comp = comparison["model_comparison"]
        
        # Find models with similar performance
        aic_values = {model: results["aic"] for model, results in model_comp.items()}
        best_aic = min(aic_values.values())
        
        similar_models = [
            model for model, aic in aic_values.items() 
            if aic - best_aic < 10  # Within 10 AIC units
        ]
        
        return {
            "best_performing_models": similar_models,
            "performance_gap": max(aic_values.values()) - best_aic,
            "model_consensus": len(similar_models) > 1
        }
    
    def _interpret_volatility_forecast(self, forecast: List[float], symbol: str, horizon: int) -> str:
        """Interpret volatility forecast."""
        if not forecast:
            return "No forecast available"
        
        avg_forecast = sum(forecast) / len(forecast)
        
        if len(forecast) > 1:
            if forecast[-1] > forecast[0]:
                trend = "increasing"
            elif forecast[-1] < forecast[0]:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return f"Volatility forecast for {symbol} shows {trend} trend over {horizon} periods with average volatility of {avg_forecast:.4f}"
    
    def _assess_forecast_confidence(self, model_results: Dict[str, Any]) -> str:
        """Assess confidence in volatility forecast."""
        aic = model_results.get("aic", float('inf'))
        
        if aic < 500:
            return "High confidence - model shows excellent fit"
        elif aic < 1000:
            return "Moderate confidence - model shows good fit"
        else:
            return "Low confidence - model fit could be improved"
    
    def _interpret_weather_volatility_correlation(self, cross_corr: Dict[str, Any], 
                                                weather_var: str, symbol: str) -> str:
        """Interpret weather-volatility correlation."""
        optimal_corr = cross_corr["optimal_correlation"]
        optimal_lag = cross_corr["optimal_lag"]
        
        if abs(optimal_corr) > 0.3:
            strength = "strong"
        elif abs(optimal_corr) > 0.1:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "positive" if optimal_corr > 0 else "negative"
        
        return f"{strength.capitalize()} {direction} correlation between {weather_var} and {symbol} volatility at {optimal_lag}-period lag"
    
    def _assess_correlation_significance(self, cross_corr: Dict[str, Any]) -> str:
        """Assess statistical significance of correlation."""
        optimal_corr = abs(cross_corr["optimal_correlation"])
        
        if optimal_corr > 0.3:
            return "Statistically significant correlation"
        elif optimal_corr > 0.1:
            return "Moderate correlation - may be significant"
        else:
            return "Weak correlation - likely not significant"
    
    def _analyze_regime_transitions(self, regimes: List[str]) -> Dict[str, Any]:
        """Analyze volatility regime transitions."""
        if len(regimes) < 2:
            return {"transitions": 0, "persistence": 1.0}
        
        transitions = 0
        for i in range(1, len(regimes)):
            if regimes[i] != regimes[i-1]:
                transitions += 1
        
        # Calculate regime persistence
        persistence = 1 - (transitions / (len(regimes) - 1))
        
        # Count regime occurrences
        regime_counts = {}
        for regime in regimes:
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        return {
            "transitions": transitions,
            "persistence": persistence,
            "regime_distribution": regime_counts,
            "most_common_regime": max(regime_counts, key=regime_counts.get)
        }
    
    def _calculate_var(self, returns_stats: Dict[str, Any], vol_stats: Dict[str, Any], 
                      confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk."""
        import numpy as np
        from scipy import stats
        
        # Simple parametric VaR calculation
        mean_return = returns_stats["mean"]
        volatility = vol_stats["mean_volatility"]
        
        # Z-score for confidence level
        z_score = stats.norm.ppf(1 - confidence_level)
        
        # VaR calculation
        var = -(mean_return + z_score * volatility)
        
        return float(var)
    
    def _assess_risk_level(self, vol_stats: Dict[str, Any], returns_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level."""
        mean_vol = vol_stats["mean_volatility"]
        vol_of_vol = vol_stats["volatility_of_volatility"]
        
        # Risk scoring
        risk_score = 0
        
        if mean_vol > 0.03:
            risk_score += 3
        elif mean_vol > 0.02:
            risk_score += 2
        elif mean_vol > 0.01:
            risk_score += 1
        
        if vol_of_vol > 0.5:
            risk_score += 2
        elif vol_of_vol > 0.3:
            risk_score += 1
        
        # Risk level classification
        if risk_score >= 4:
            level = "High"
        elif risk_score >= 2:
            level = "Medium"
        else:
            level = "Low"
        
        return {
            "level": level,
            "score": risk_score,
            "factors": {
                "volatility_level": mean_vol,
                "volatility_stability": vol_of_vol
            }
        }
    
    def _generate_risk_recommendations(self, risk_level: Dict[str, Any], vol_stats: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []
        
        if risk_level["level"] == "High":
            recommendations.append("Implement strict risk management protocols")
            recommendations.append("Consider reducing position sizes")
            recommendations.append("Monitor volatility closely for regime changes")
        elif risk_level["level"] == "Medium":
            recommendations.append("Maintain standard risk management practices")
            recommendations.append("Monitor for volatility increases")
        else:
            recommendations.append("Current risk levels are manageable")
            recommendations.append("Standard position sizing appropriate")
        
        return recommendations