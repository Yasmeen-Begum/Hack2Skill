"""Natural language query models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class NaturalLanguageQuery(BaseModel):
    """Model for natural language queries and their processing."""
    
    query_text: str = Field(..., min_length=1, description="Original query text from user")
    user_id: Optional[str] = Field(default=None, description="User identifier (optional)")
    timestamp: datetime = Field(..., description="Query timestamp")
    processed_intent: Optional[str] = Field(default=None, description="Processed intent from LangChain")
    retrieved_context: Optional[List[str]] = Field(default=None, description="Context retrieved from ChromaDB")
    
    @validator('query_text')
    def validate_query_text(cls, v):
        """Validate query text is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Query text cannot be empty or whitespace')
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user ID format if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('User ID cannot be empty or whitespace if provided')
        return v.strip() if v else None
    
    @validator('processed_intent')
    def validate_processed_intent(cls, v):
        """Validate processed intent if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Processed intent cannot be empty or whitespace if provided')
        return v.strip() if v else None
    
    @validator('retrieved_context')
    def validate_retrieved_context(cls, v):
        """Validate retrieved context if provided."""
        if v is not None:
            if len(v) == 0:
                raise ValueError('Retrieved context cannot be empty list if provided')
            # Check that all context items are non-empty strings
            for context in v:
                if not context or not context.strip():
                    raise ValueError('Context items cannot be empty or whitespace')
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "query_text": "How does rainy weather affect tech stock prices?",
                "user_id": "user_123",
                "timestamp": "2024-01-15T14:30:00Z",
                "processed_intent": "correlation_analysis_weather_stock",
                "retrieved_context": [
                    "Historical data shows tech stocks decline 2% on average during rainy periods",
                    "Weather correlation with NASDAQ shows -0.15 coefficient for precipitation"
                ]
            }
        }