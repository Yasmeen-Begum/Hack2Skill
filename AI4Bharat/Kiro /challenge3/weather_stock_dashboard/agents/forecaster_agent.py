"""Time Series Forecaster Agent for ARIMA modeling and forecasting."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from weather_stock_dashboard.agents.base_agent import BaseWeatherStockAgent, BaseTool
from weather_stock_dashboard.services.timeseries_service import timeseries_service

logger = logging.getLogger(__name__)


class ARIMAForecastTool(BaseTool):
    """Tool for ARIMA forecasting."""
    
    name: str = "arima_forecast"
    description: str = "Fit ARIMA model and generate forecasts for time series data"
    
    def _run(self, data: List[Dict[str, Any]], value_column: str, 
             order: Optional[tuple] = None) -> str:
        """Run ARIMA forecasting."""
        try:
            # Prepare time series
            ts = timeseries_service.prepare_time_series(data, value_column)
            
            # Fit ARIMA model
            result = timeseries_service.fit_arima_model(ts, order)
            
            forecast_summary = f"ARIMA{result['order']} fitted with AIC={result['aic']:.2f}. "
            forecast_summary += f"Generated {len(result['forecast'])} period forecast."
            
            return forecast_summary
        except Exception as e:
            return f"ARIMA forecasting failed: {str(e)}"


class ModelSelectionTool(BaseTool):
    """Tool for automatic model selection."""
    
    name: str = "model_selection"
    description: str = "Automatically select best ARIMA model parameters"
    
    def _run(self, data: List[Dict[str, Any]], value_column: str) -> str:
        """Run automatic model selection."""
        try:
            ts = timeseries_service.prepare_time_series(data, value_column)
            best_order = timeseries_service.auto_arima_order_selection(ts)
            
            return f"Selected optimal ARIMA order: {best_order}"
        except Exception as e:
            return f"Model selection failed: {str(e)}"


class StationarityTestTool(BaseTool):
    """Tool for stationarity testing."""
    
    name: str = "stationarity_test"
    description: str = "Test time series for stationarity using ADF test"
    
    def _run(self, data: List[Dict[str, Any]], value_column: str) -> str:
        """Run stationarity test."""
        try:
            ts = timeseries_service.prepare_time_series(data, value_column)
            result = timeseries_service.check_stationarity(ts)
            
            return f"Stationarity test: {result['interpretation']} (p-value: {result['p_value']:.4f})"
        except Exception as e:
            return f"Stationarity test failed: {str(e)}"


class TimeSeriesForecasterAgent(BaseWeatherStockAgent):
    """Agent for time series forecasting using ARIMA models."""
    
    def __init__(self):
        """Initialize Time Series Forecaster Agent."""
        super().__init__(
            name="timeseries_forecaster",
            role="Time Series Analyst",
            goal="Generate accurate forecasts for weather and stock time series using ARIMA models",
            backstory="""You are an expert time series analyst with deep knowledge of 
            ARIMA modeling, seasonal patterns, and forecasting techniques. You specialize 
            in analyzing both weather patterns and financial time series, understanding 
            the unique characteristics of each domain."""
        )
        
        self.model_cache = {}  # Cache fitted models for reuse
        
    def get_tools(self) -> List[BaseTool]:
        """Get tools for time series forecasting."""
        return [
            ARIMAForecastTool(),
            ModelSelectionTool(),
            StationarityTestTool()
        ]
    
    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute time series forecasting task."""
        try:
            task_type = context.get("task_type", "forecast")
            data = context.get("data", [])
            value_column = context.get("value_column", "value")
            series_id = context.get("series_id", "default")
            
            if task_type == "forecast":
                result = await self._generate_forecast(data, value_column, series_id, context)
            
            elif task_type == "model_selection":
                result = await self._select_best_model(data, value_column, series_id)
            
            elif task_type == "stationarity_analysis":
                result = await self._analyze_stationarity(data, value_column)
            
            elif task_type == "seasonal_decomposition":
                result = await self._decompose_series(data, value_column, context)
            
            elif task_type == "model_diagnostics":
                result = await self._run_model_diagnostics(data, value_column, series_id)
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Update agent memory
            self.update_memory(f"last_{task_type}_result", result)
            
            return {
                "agent": self.name,
                "task": task_description,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": result.get("summary", "Forecasting task completed successfully")
            }
            
        except Exception as e:
            logger.error(f"Time series forecasting task failed: {e}")
            return {
                "agent": self.name,
                "task": task_description,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "summary": f"Forecasting task failed: {str(e)}"
            }
    
    async def _generate_forecast(self, data: List[Dict[str, Any]], value_column: str, 
                               series_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ARIMA forecast for time series."""
        try:
            # Prepare time series
            ts = timeseries_service.prepare_time_series(data, value_column)
            
            if len(ts) < timeseries_service.min_data_points_arima:
                raise ValueError(f"Insufficient data points. Need at least {timeseries_service.min_data_points_arima}, got {len(ts)}")
            
            # Check if we have a cached model
            order = context.get("arima_order")
            cache_key = f"{series_id}_{value_column}_{order}"
            
            if cache_key in self.model_cache:
                logger.info(f"Using cached model for {cache_key}")
                arima_result = self.model_cache[cache_key]
            else:
                # Fit new ARIMA model
                arima_result = timeseries_service.fit_arima_model(ts, order)
                self.model_cache[cache_key] = arima_result
            
            # Generate forecast interpretation
            forecast_interpretation = self._interpret_forecast(
                arima_result, value_column, context.get("data_type", "unknown")
            )
            
            return {
                "series_id": series_id,
                "value_column": value_column,
                "data_points": len(ts),
                "arima_order": arima_result["order"],
                "model_quality": {
                    "aic": arima_result["aic"],
                    "bic": arima_result["bic"],
                    "ljung_box_p": arima_result["residuals_ljung_box_p"]
                },
                "forecast": arima_result["forecast"],
                "forecast_confidence_intervals": arima_result["forecast_confidence_intervals"],
                "forecast_horizon": len(arima_result["forecast"]),
                "interpretation": forecast_interpretation,
                "summary": f"Generated {len(arima_result['forecast'])}-period forecast using ARIMA{arima_result['order']} (AIC: {arima_result['aic']:.2f})"
            }
            
        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            raise
    
    async def _select_best_model(self, data: List[Dict[str, Any]], value_column: str, 
                               series_id: str) -> Dict[str, Any]:
        """Select best ARIMA model parameters."""
        try:
            ts = timeseries_service.prepare_time_series(data, value_column)
            
            # Check stationarity first
            stationarity_result = timeseries_service.check_stationarity(ts)
            
            # Auto-select ARIMA order
            best_order = timeseries_service.auto_arima_order_selection(ts)
            
            # Fit model with selected order
            arima_result = timeseries_service.fit_arima_model(ts, best_order)
            
            # Cache the selected model
            cache_key = f"{series_id}_{value_column}_{best_order}"
            self.model_cache[cache_key] = arima_result
            
            return {
                "series_id": series_id,
                "value_column": value_column,
                "stationarity": stationarity_result,
                "selected_order": best_order,
                "model_quality": {
                    "aic": arima_result["aic"],
                    "bic": arima_result["bic"]
                },
                "recommendation": self._generate_model_recommendation(arima_result, stationarity_result),
                "summary": f"Selected ARIMA{best_order} as optimal model (AIC: {arima_result['aic']:.2f})"
            }
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            raise
    
    async def _analyze_stationarity(self, data: List[Dict[str, Any]], value_column: str) -> Dict[str, Any]:
        """Analyze time series stationarity."""
        try:
            ts = timeseries_service.prepare_time_series(data, value_column)
            
            # Run ADF test
            stationarity_result = timeseries_service.check_stationarity(ts)
            
            # Additional analysis
            analysis = {
                "adf_test": stationarity_result,
                "recommendations": []
            }
            
            if not stationarity_result["is_stationary"]:
                analysis["recommendations"].append("Consider differencing the series")
                analysis["recommendations"].append("Check for seasonal patterns")
                
                # Suggest differencing order
                if stationarity_result["p_value"] > 0.1:
                    analysis["recommendations"].append("Series likely needs differencing (d=1 or d=2)")
            else:
                analysis["recommendations"].append("Series is stationary - suitable for ARIMA modeling")
            
            return {
                "value_column": value_column,
                "analysis": analysis,
                "summary": f"Stationarity analysis: {stationarity_result['interpretation']}"
            }
            
        except Exception as e:
            logger.error(f"Stationarity analysis failed: {e}")
            raise
    
    async def _decompose_series(self, data: List[Dict[str, Any]], value_column: str, 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform seasonal decomposition."""
        try:
            ts = timeseries_service.prepare_time_series(data, value_column)
            
            # Get decomposition parameters from context
            model_type = context.get("decomposition_model", "additive")
            period = context.get("seasonal_period")
            
            decomposition_result = timeseries_service.seasonal_decomposition(ts, model_type, period)
            
            # Analyze components
            trend_strength = self._calculate_component_strength(decomposition_result["trend"])
            seasonal_strength = self._calculate_component_strength(decomposition_result["seasonal"])
            
            return {
                "value_column": value_column,
                "decomposition": decomposition_result,
                "component_analysis": {
                    "trend_strength": trend_strength,
                    "seasonal_strength": seasonal_strength,
                    "model_type": model_type,
                    "period": decomposition_result["period"]
                },
                "interpretation": self._interpret_decomposition(decomposition_result, trend_strength, seasonal_strength),
                "summary": f"Seasonal decomposition completed using {model_type} model with period {decomposition_result['period']}"
            }
            
        except Exception as e:
            logger.error(f"Seasonal decomposition failed: {e}")
            raise
    
    async def _run_model_diagnostics(self, data: List[Dict[str, Any]], value_column: str, 
                                   series_id: str) -> Dict[str, Any]:
        """Run comprehensive model diagnostics."""
        try:
            ts = timeseries_service.prepare_time_series(data, value_column)
            
            # Fit ARIMA model
            arima_result = timeseries_service.fit_arima_model(ts)
            
            # Diagnostic analysis
            diagnostics = {
                "model_fit": {
                    "aic": arima_result["aic"],
                    "bic": arima_result["bic"],
                    "ljung_box_p": arima_result["residuals_ljung_box_p"]
                },
                "residual_analysis": {
                    "ljung_box_test": "PASS" if arima_result["residuals_ljung_box_p"] > 0.05 else "FAIL",
                    "interpretation": "Residuals appear random" if arima_result["residuals_ljung_box_p"] > 0.05 else "Residuals show autocorrelation"
                }
            }
            
            # Overall model assessment
            assessment = self._assess_model_quality(diagnostics)
            
            return {
                "series_id": series_id,
                "value_column": value_column,
                "arima_order": arima_result["order"],
                "diagnostics": diagnostics,
                "assessment": assessment,
                "summary": f"Model diagnostics completed: {assessment['overall_quality']}"
            }
            
        except Exception as e:
            logger.error(f"Model diagnostics failed: {e}")
            raise
    
    def _interpret_forecast(self, arima_result: Dict[str, Any], value_column: str, data_type: str) -> str:
        """Generate interpretation of forecast results."""
        forecast = arima_result["forecast"]
        order = arima_result["order"]
        
        # Basic trend analysis
        if len(forecast) >= 2:
            if forecast[-1] > forecast[0]:
                trend = "increasing"
            elif forecast[-1] < forecast[0]:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        interpretation = f"The ARIMA{order} model forecasts a {trend} trend for {value_column}. "
        
        # Add domain-specific interpretation
        if data_type == "weather":
            interpretation += "Weather patterns show typical seasonal variation with model capturing underlying trends."
        elif data_type == "stock":
            interpretation += "Stock price forecast reflects market dynamics and historical patterns."
        
        # Model quality assessment
        if arima_result["aic"] < 1000:
            interpretation += " Model shows good fit to historical data."
        else:
            interpretation += " Model fit is adequate but could be improved with more data or different parameters."
        
        return interpretation
    
    def _generate_model_recommendation(self, arima_result: Dict[str, Any], 
                                     stationarity_result: Dict[str, Any]) -> str:
        """Generate model recommendation based on results."""
        order = arima_result["order"]
        p, d, q = order
        
        recommendations = []
        
        if not stationarity_result["is_stationary"] and d == 0:
            recommendations.append("Consider increasing differencing order (d)")
        
        if arima_result["aic"] > 2000:
            recommendations.append("Model fit could be improved - try different parameters")
        
        if arima_result["residuals_ljung_box_p"] < 0.05:
            recommendations.append("Residuals show autocorrelation - consider higher order terms")
        
        if not recommendations:
            recommendations.append("Model appears well-specified for the data")
        
        return "; ".join(recommendations)
    
    def _calculate_component_strength(self, component: List[float]) -> float:
        """Calculate strength of a decomposition component."""
        if not component:
            return 0.0
        
        import numpy as np
        component_array = np.array(component)
        return float(np.std(component_array) / np.mean(np.abs(component_array))) if np.mean(np.abs(component_array)) > 0 else 0.0
    
    def _interpret_decomposition(self, decomposition: Dict[str, Any], 
                               trend_strength: float, seasonal_strength: float) -> str:
        """Interpret seasonal decomposition results."""
        interpretation = f"Series decomposed using {decomposition['model']} model with period {decomposition['period']}. "
        
        if trend_strength > 0.5:
            interpretation += "Strong trend component detected. "
        elif trend_strength > 0.2:
            interpretation += "Moderate trend component present. "
        else:
            interpretation += "Weak or no trend component. "
        
        if seasonal_strength > 0.3:
            interpretation += "Significant seasonal patterns identified."
        elif seasonal_strength > 0.1:
            interpretation += "Moderate seasonal variation present."
        else:
            interpretation += "Limited seasonal patterns."
        
        return interpretation
    
    def _assess_model_quality(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall model quality."""
        model_fit = diagnostics["model_fit"]
        residual_analysis = diagnostics["residual_analysis"]
        
        quality_score = 0
        issues = []
        
        # AIC assessment (lower is better)
        if model_fit["aic"] < 500:
            quality_score += 3
        elif model_fit["aic"] < 1000:
            quality_score += 2
        elif model_fit["aic"] < 2000:
            quality_score += 1
        else:
            issues.append("High AIC indicates poor model fit")
        
        # Ljung-Box test assessment
        if residual_analysis["ljung_box_test"] == "PASS":
            quality_score += 2
        else:
            issues.append("Residuals show autocorrelation")
        
        # Overall quality assessment
        if quality_score >= 4:
            overall_quality = "Excellent"
        elif quality_score >= 3:
            overall_quality = "Good"
        elif quality_score >= 2:
            overall_quality = "Fair"
        else:
            overall_quality = "Poor"
        
        return {
            "quality_score": quality_score,
            "overall_quality": overall_quality,
            "issues": issues,
            "recommendations": issues if issues else ["Model is well-specified"]
        }