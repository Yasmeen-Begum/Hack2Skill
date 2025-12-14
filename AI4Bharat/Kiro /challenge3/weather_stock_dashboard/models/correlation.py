"""Correlation and insight data models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class CorrelationInsight(BaseModel):
    """Model for AI-generated correlation insights."""
    
    id: str = Field(..., description="Unique identifier for the insight")
    weather_pattern: str = Field(..., min_length=1, description="Description of weather pattern")
    stock_pattern: str = Field(..., min_length=1, description="Description of stock pattern")
    correlation_coefficient: float = Field(..., ge=-1, le=1, description="Correlation coefficient")
    confidence_level: float = Field(..., ge=0, le=1, description="Statistical confidence level")
    time_period: str = Field(..., min_length=1, description="Time period of analysis")
    statistical_significance: float = Field(..., ge=0, le=1, description="Statistical significance (p-value)")
    explanation: str = Field(..., min_length=1, description="Human-readable explanation")
    supporting_data_points: int = Field(..., gt=0, description="Number of data points supporting the insight")
    
    @validator('weather_pattern')
    def validate_weather_pattern(cls, v):
        """Validate weather pattern is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Weather pattern cannot be empty or whitespace')
        return v.strip()
    
    @validator('stock_pattern')
    def validate_stock_pattern(cls, v):
        """Validate stock pattern is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Stock pattern cannot be empty or whitespace')
        return v.strip()
    
    @validator('time_period')
    def validate_time_period(cls, v):
        """Validate time period is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Time period cannot be empty or whitespace')
        return v.strip()
    
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
                "id": "insight_001",
                "weather_pattern": "High temperature days (>30°C)",
                "stock_pattern": "Energy sector stock increases",
                "correlation_coefficient": 0.65,
                "confidence_level": 0.95,
                "time_period": "Summer 2023",
                "statistical_significance": 0.001,
                "explanation": "High temperature days show strong positive correlation with energy sector performance",
                "supporting_data_points": 120
            }
        }