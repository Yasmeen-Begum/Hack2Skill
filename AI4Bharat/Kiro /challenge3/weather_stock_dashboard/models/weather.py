"""Weather data models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class WeatherData(BaseModel):
    """Weather data model with validation for meteorological ranges."""
    
    timestamp: datetime = Field(..., description="Timestamp of weather observation")
    location: str = Field(..., min_length=1, description="Location identifier")
    temperature: float = Field(..., ge=-100, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    pressure: float = Field(..., ge=800, le=1200, description="Atmospheric pressure in hPa")
    precipitation: float = Field(..., ge=0, le=1000, description="Precipitation in mm")
    wind_speed: float = Field(..., ge=0, le=200, description="Wind speed in km/h")
    weather_condition: str = Field(..., min_length=1, description="Weather condition description")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding of weather description")
    
    @validator('location')
    def validate_location(cls, v):
        """Validate location is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Location cannot be empty or whitespace')
        return v.strip()
    
    @validator('weather_condition')
    def validate_weather_condition(cls, v):
        """Validate weather condition is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Weather condition cannot be empty or whitespace')
        return v.strip()
    
    @validator('embedding')
    def validate_embedding(cls, v):
        """Validate embedding dimensions if provided."""
        if v is not None and len(v) == 0:
            raise ValueError('Embedding cannot be empty list')
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "timestamp": "2024-01-15T12:00:00Z",
                "location": "New York, NY",
                "temperature": 15.5,
                "humidity": 65.0,
                "pressure": 1013.25,
                "precipitation": 0.0,
                "wind_speed": 12.5,
                "weather_condition": "partly cloudy",
                "embedding": None
            }
        }