"""Stock data models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class StockData(BaseModel):
    """Stock data model with validation for financial data ranges."""
    
    timestamp: datetime = Field(..., description="Timestamp of stock data")
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    price: float = Field(..., gt=0, description="Stock price in USD")
    volume: int = Field(..., ge=0, description="Trading volume")
    market_cap: Optional[float] = Field(default=None, ge=0, description="Market capitalization in USD")
    sector: str = Field(..., min_length=1, description="Stock sector")
    change_percent: float = Field(..., ge=-100, le=1000, description="Price change percentage")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding of market context")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format."""
        if not v or not v.strip():
            raise ValueError('Stock symbol cannot be empty or whitespace')
        symbol = v.strip().upper()
        if not symbol.isalnum():
            raise ValueError('Stock symbol must contain only alphanumeric characters')
        return symbol
    
    @validator('sector')
    def validate_sector(cls, v):
        """Validate sector is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Sector cannot be empty or whitespace')
        return v.strip()
    
    @validator('embedding')
    def validate_embedding(cls, v):
        """Validate embedding dimensions if provided."""
        if v is not None and len(v) == 0:
            raise ValueError('Embedding cannot be empty list')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price is reasonable."""
        if v > 100000:  # Sanity check for extremely high prices
            raise ValueError('Price seems unreasonably high')
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "timestamp": "2024-01-15T16:00:00Z",
                "symbol": "AAPL",
                "price": 185.50,
                "volume": 45000000,
                "market_cap": 2800000000000,
                "sector": "Technology",
                "change_percent": 2.5,
                "embedding": None
            }
        }