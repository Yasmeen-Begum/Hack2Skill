"""Application configuration settings."""

from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Database Configuration
    chromadb_host: str = Field(default="localhost", env="CHROMADB_HOST")
    chromadb_port: int = Field(default=8000, env="CHROMADB_PORT")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Application Configuration
    app_name: str = Field(default="Weather Stock Dashboard", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=False, env="API_RELOAD")
    
    # Data Collection Settings
    weather_collection_interval: int = Field(default=3600, env="WEATHER_COLLECTION_INTERVAL")
    stock_collection_interval: int = Field(default=900, env="STOCK_COLLECTION_INTERVAL")
    data_retention_days: int = Field(default=365, env="DATA_RETENTION_DAYS")
    
    # Time Series Analysis Settings
    min_data_points_arima: int = Field(default=50, env="MIN_DATA_POINTS_ARIMA")
    min_data_points_garch: int = Field(default=100, env="MIN_DATA_POINTS_GARCH")
    forecast_horizon_days: int = Field(default=30, env="FORECAST_HORIZON_DAYS")
    
    # UI Configuration
    gradio_host: str = Field(default="0.0.0.0", env="GRADIO_HOST")
    gradio_port: int = Field(default=7860, env="GRADIO_PORT")
    gradio_share: bool = Field(default=False, env="GRADIO_SHARE")
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Global settings instance
settings = Settings()