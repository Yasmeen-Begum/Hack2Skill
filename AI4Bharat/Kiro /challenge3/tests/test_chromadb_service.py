"""Tests for ChromaDB service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from weather_stock_dashboard.services.chromadb_service import ChromaDBService


class TestChromaDBService:
    """Test ChromaDB service functionality."""
    
    @pytest.fixture
    def service(self):
        """Create ChromaDB service instance."""
        return ChromaDBService()
    
    @pytest.fixture
    def mock_client(self):
        """Create mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        collection.count.return_value = 0
        client.get_or_create_collection.return_value = collection
        return client, collection
    
    def test_generate_embedding(self, service):
        """Test embedding generation."""
        with patch.object(service, 'embedding_model') as mock_model:
            mock_model.encode.return_value = Mock()
            mock_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
            
            result = service.generate_embedding("test text")
            
            assert result == [0.1, 0.2, 0.3]
            mock_model.encode.assert_called_once_with("test text")
    
    @pytest.mark.asyncio
    async def test_store_weather_data(self, service, mock_client):
        """Test storing weather data."""
        client, collection = mock_client
        service.client = client
        service.collections = {"weather_data": collection}
        service.generate_embedding = Mock(return_value=[0.1, 0.2, 0.3])
        
        weather_data = {
            "location": "New York",
            "timestamp": "2024-01-15T12:00:00Z",
            "temperature": 20.0,
            "humidity": 65.0,
            "pressure": 1013.25,
            "precipitation": 0.0,
            "wind_speed": 15.0,
            "weather_condition": "sunny"
        }
        
        result = await service.store_weather_data(weather_data)
        
        assert result.startswith("weather_New York_")
        collection.add.assert_called_once()
        
        # Check the call arguments
        call_args = collection.add.call_args
        assert len(call_args.kwargs["embeddings"]) == 1
        assert len(call_args.kwargs["documents"]) == 1
        assert len(call_args.kwargs["metadatas"]) == 1
        assert len(call_args.kwargs["ids"]) == 1
    
    @pytest.mark.asyncio
    async def test_search_weather_data(self, service, mock_client):
        """Test searching weather data."""
        client, collection = mock_client
        service.client = client
        service.collections = {"weather_data": collection}
        service.generate_embedding = Mock(return_value=[0.1, 0.2, 0.3])
        
        # Mock search results
        collection.query.return_value = {
            "ids": [["weather_1", "weather_2"]],
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"type": "weather"}, {"type": "weather"}]],
            "distances": [[0.1, 0.2]]
        }
        
        results = await service.search_weather_data("sunny weather")
        
        assert len(results) == 2
        assert results[0]["id"] == "weather_1"
        assert results[0]["document"] == "doc1"
        assert results[0]["distance"] == 0.1
        
        collection.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, service, mock_client):
        """Test hybrid search across collections."""
        client, collection = mock_client
        service.client = client
        service.collections = {
            "weather_data": collection,
            "stock_data": collection,
            "correlations": collection
        }
        service.generate_embedding = Mock(return_value=[0.1, 0.2, 0.3])
        
        # Mock search results
        collection.query.return_value = {
            "ids": [["test_1"]],
            "documents": [["test doc"]],
            "metadatas": [[{"type": "test"}]],
            "distances": [[0.1]]
        }
        
        results = await service.hybrid_search("test query")
        
        assert "weather" in results
        assert "stocks" in results
        assert "correlations" in results
        assert len(results["weather"]) == 1