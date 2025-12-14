"""Time series analysis models."""

from datetime import datetime
from typing import List, Tuple, Dict, Optional
from pydantic import BaseModel, Field, validator


class TimeSeriesAnalysis(BaseModel):
    """Time series analysis model for ARIMA and GARCH results."""
    
    id: str = Field(..., description="Unique identifier for the analysis")
    series_type: str = Field(..., description="Type of series: 'weather' or 'stock'")
    arima_order: Tuple[int, int, int] = Field(..., description="ARIMA (p, d, q) parameters")
    arima_forecast: List[float] = Field(..., description="ARIMA forecast values")
    arima_confidence_intervals: List[Tuple[float, float]] = Field(..., description="Confidence intervals for forecast")
    garch_volatility: Optional[List[float]] = Field(default=None, description="GARCH volatility estimates (for stock data)")
    model_diagnostics: Dict[str, float] = Field(..., description="Model diagnostics (AIC, BIC, etc.)")
    forecast_horizon: int = Field(..., gt=0, description="Number of periods forecasted")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    
    @validator('series_type')
    def validate_series_type(cls, v):
        """Validate series type is either weather or stock."""
        if v not in ['weather', 'stock']:
            raise ValueError('Series type must be either "weather" or "stock"')
        return v
    
    @validator('arima_order')
    def validate_arima_order(cls, v):
        """Validate ARIMA order parameters are non-negative."""
        p, d, q = v
        if p < 0 or d < 0 or q < 0:
            raise ValueError('ARIMA order parameters must be non-negative')
        if p > 10 or d > 2 or q > 10:
            raise ValueError('ARIMA order parameters seem unreasonably large')
        return v
    
    @validator('arima_forecast')
    def validate_arima_forecast(cls, v):
        """Validate forecast has reasonable values."""
        if len(v) == 0:
            raise ValueError('Forecast cannot be empty')
        return v
    
    @validator('arima_confidence_intervals')
    def validate_confidence_intervals(cls, v):
        """Validate confidence intervals format."""
        if len(v) == 0:
            raise ValueError('Confidence intervals cannot be empty')
        for lower, upper in v:
            if lower > upper:
                raise ValueError('Lower confidence bound cannot be greater than upper bound')
        return v
    
    @validator('garch_volatility')
    def validate_garch_volatility(cls, v):
        """Validate GARCH volatility values."""
        if v is not None:
            if len(v) == 0:
                raise ValueError('GARCH volatility cannot be empty list')
            if any(vol < 0 for vol in v):
                raise ValueError('Volatility values must be non-negative')
        return v
    
    @validator('model_diagnostics')
    def validate_model_diagnostics(cls, v):
        """Validate model diagnostics contain required metrics."""
        required_metrics = ['aic', 'bic']
        for metric in required_metrics:
            if metric not in v:
                raise ValueError(f'Model diagnostics must include {metric}')
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "ts_analysis_001",
                "series_type": "stock",
                "arima_order": [1, 1, 1],
                "arima_forecast": [185.2, 186.1, 184.8],
                "arima_confidence_intervals": [[180.1, 190.3], [181.0, 191.2], [179.5, 190.1]],
                "garch_volatility": [0.02, 0.025, 0.022],
                "model_diagnostics": {"aic": 1250.5, "bic": 1275.8},
                "forecast_horizon": 3,
                "timestamp": "2024-01-15T18:00:00Z"
            }
        }


class WeatherStockRelationship(BaseModel):
    """Model for weather-stock correlation relationships."""
    
    id: str = Field(..., description="Unique identifier for the relationship")
    weather_series_id: str = Field(..., description="ID of the weather time series")
    stock_series_id: str = Field(..., description="ID of the stock time series")
    cross_correlation: List[float] = Field(..., description="Cross-correlation at different lags")
    optimal_lag: int = Field(..., description="Lag with highest correlation")
    granger_causality_p_value: float = Field(..., ge=0, le=1, description="Granger causality test p-value")
    relationship_strength: str = Field(..., description="Relationship strength: weak, moderate, strong")
    explanation: str = Field(..., min_length=1, description="Human-readable explanation of the relationship")
    
    @validator('relationship_strength')
    def validate_relationship_strength(cls, v):
        """Validate relationship strength is one of allowed values."""
        allowed_strengths = ['weak', 'moderate', 'strong']
        if v not in allowed_strengths:
            raise ValueError(f'Relationship strength must be one of: {allowed_strengths}')
        return v
    
    @validator('cross_correlation')
    def validate_cross_correlation(cls, v):
        """Validate cross-correlation values are between -1 and 1."""
        if len(v) == 0:
            raise ValueError('Cross-correlation cannot be empty')
        for corr in v:
            if not -1 <= corr <= 1:
                raise ValueError('Cross-correlation values must be between -1 and 1')
        return v
    
    @validator('explanation')
    def validate_explanation(cls, v):
        """Validate explanation is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Explanation cannot be empty or whitespace')
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "id": "rel_001",
                "weather_series_id": "weather_nyc_temp",
                "stock_series_id": "stock_aapl",
                "cross_correlation": [0.1, 0.25, 0.15, -0.05],
                "optimal_lag": 1,
                "granger_causality_p_value": 0.03,
                "relationship_strength": "moderate",
                "explanation": "Temperature changes show moderate correlation with AAPL stock price with 1-day lag"
            }
        }