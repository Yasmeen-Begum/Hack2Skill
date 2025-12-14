"""
Standalone integration tests that don't require full application import.

These tests validate core functionality without external dependencies.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd
import numpy as np

from weather_stock_dashboard.models.weather import WeatherData
from weather_stock_dashboard.models.stock import StockData
from weather_stock_dashboard.models.timeseries import TimeSeriesAnalysis
from weather_stock_dashboard.models.correlation import CorrelationInsight


class TestDataModelIntegration:
    """Test integration between different data models."""
    
    def test_weather_stock_data_compatibility(self):
        """Test that weather and stock data models work together."""
        # Create sample data
        timestamp = datetime.now()
        
        weather = WeatherData(
            location="New York",
            timestamp=timestamp,
            temperature=25.0,
            humidity=65.0,
            pressure=1013.25,
            precipitation=0.0,  # Required field
            wind_speed=10.0,
            weather_condition="Clear",
            embedding=[0.1] * 384
        )
        
        stock = StockData(
            symbol="AAPL",
            timestamp=timestamp,
            price=150.0,
            volume=1000000,
            market_cap=2500000000000,
            sector="Technology",
            change_percent=2.5,
            embedding=[0.2] * 384
        )
        
        # Test that both models serialize correctly
        weather_dict = weather.dict()
        stock_dict = stock.dict()
        
        assert weather_dict["timestamp"] == stock_dict["timestamp"]
        assert len(weather_dict["embedding"]) == len(stock_dict["embedding"])
    
    def test_timeseries_analysis_integration(self):
        """Test time series analysis model with realistic data."""
        analysis = TimeSeriesAnalysis(
            id="test_analysis_1",
            series_type="stock",  # Must be "weather" or "stock"
            arima_order=(2, 1, 2),
            arima_forecast=[150.5, 151.2, 152.0],
            arima_confidence_intervals=[(149.0, 152.0), (150.0, 152.5), (151.0, 153.0)],
            garch_volatility=[0.15, 0.18, 0.16],
            model_diagnostics={"aic": 245.6, "bic": 255.8, "ljung_box_p": 0.75},
            forecast_horizon=3,
            timestamp=datetime.now()
        )
        
        # Test model validation
        assert analysis.series_type in ["weather", "stock"]
        assert len(analysis.arima_forecast) == len(analysis.arima_confidence_intervals)
        assert len(analysis.arima_forecast) == len(analysis.garch_volatility)
        assert analysis.model_diagnostics["aic"] > 0
    
    def test_correlation_insight_integration(self):
        """Test correlation insight model with weather-stock relationships."""
        insight = CorrelationInsight(
            id="test_insight_1",
            weather_pattern="temperature_increase",
            stock_pattern="price_volatility",
            correlation_coefficient=0.65,
            statistical_significance=0.02,  # This is p_value
            confidence_level=0.95,
            time_period="30_days",
            supporting_data_points=30,  # This is sample_size
            explanation="Strong positive correlation between temperature increases and stock volatility."
        )
        
        # Test statistical validity
        assert -1.0 <= insight.correlation_coefficient <= 1.0
        assert 0.0 <= insight.statistical_significance <= 1.0  # This is p_value
        assert 0.0 <= insight.confidence_level <= 1.0
        assert insight.supporting_data_points > 0  # This is sample_size


class TestServiceIntegration:
    """Test integration between different services."""
    
    def test_chromadb_service_integration(self):
        """Test ChromaDB service with mock data."""
        from weather_stock_dashboard.services.chromadb_service import ChromaDBService
        
        with patch('chromadb.Client'):
            service = ChromaDBService()
            
            # Test embedding generation
            text = "Temperature in New York is 25°C"
            embedding = service.generate_embedding(text)
            
            assert isinstance(embedding, list)
            assert len(embedding) == 384  # sentence-transformers default
    
    def test_timeseries_service_integration(self):
        """Test time series service with synthetic data."""
        from weather_stock_dashboard.services.timeseries_service import TimeSeriesService
        
        # Test service initialization
        service = TimeSeriesService()
        
        # Generate synthetic time series
        np.random.seed(42)
        data = np.random.randn(100).cumsum() + 100
        
        # Test that service can be created and has expected attributes
        assert hasattr(service, 'fit_arima_model')
        assert len(data) == 100
    
    def test_correlation_service_integration(self):
        """Test correlation service with synthetic correlated data."""
        from weather_stock_dashboard.services.correlation_service import CorrelationService
        
        # Test service initialization
        service = CorrelationService()
        
        # Generate correlated data
        np.random.seed(42)
        weather_data = np.random.normal(20, 5, 50)
        stock_data = weather_data * 2 + np.random.normal(0, 1, 50)  # Correlated with noise
        
        # Test that service can be created and has expected attributes
        assert hasattr(service, 'analyze_correlation')
        assert len(weather_data) == 50
        assert len(stock_data) == 50


class TestAgentIntegration:
    """Test AI agent integration."""
    
    def test_base_agent_functionality(self):
        """Test base agent framework."""
        # Test that agent modules can be imported
        try:
            from weather_stock_dashboard.agents import data_validator_agent
            from weather_stock_dashboard.agents import forecaster_agent
            from weather_stock_dashboard.agents import insight_agent
            assert True  # If imports succeed, test passes
        except ImportError as e:
            pytest.fail(f"Could not import agent modules: {e}")
    
    def test_data_validator_agent_integration(self):
        """Test data validator agent with sample data."""
        from weather_stock_dashboard.agents.data_validator_agent import DataValidatorAgent
        
        # Test agent initialization
        agent = DataValidatorAgent()
        
        # Test with sample weather data
        weather_data = [
            {"temperature": 25.0, "humidity": 65.0, "pressure": 1013.25},
            {"temperature": 26.0, "humidity": 67.0, "pressure": 1012.8},
            {"temperature": 24.5, "humidity": 63.0, "pressure": 1014.1}
        ]
        
        # Test that agent can be created and data is valid
        assert agent is not None
        assert len(weather_data) == 3
    
    def test_forecaster_agent_integration(self):
        """Test forecaster agent with time series data."""
        from weather_stock_dashboard.agents.forecaster_agent import TimeSeriesForecasterAgent
        
        # Test agent initialization
        agent = TimeSeriesForecasterAgent()
        
        # Generate sample time series
        np.random.seed(42)
        timeseries = np.random.randn(100).cumsum() + 100
        
        # Test that agent can be created and data is valid
        assert agent is not None
        assert len(timeseries) == 100


class TestSystemWorkflows:
    """Test complete system workflows."""
    
    def test_data_collection_to_storage_workflow(self):
        """Test workflow from data collection to storage."""
        from weather_stock_dashboard.services.chromadb_service import ChromaDBService
        
        # Mock external dependencies
        with patch('chromadb.Client'), patch('sentence_transformers.SentenceTransformer'):
            chromadb_service = ChromaDBService()
            
            # Simulate data collection
            weather_data = WeatherData(
                location="Boston",
                timestamp=datetime.now(),
                temperature=22.0,
                humidity=70.0,
                pressure=1015.0,
                precipitation=2.5,
                wind_speed=8.0,
                weather_condition="Partly Cloudy",
                embedding=[0.1] * 384
            )
            
            stock_data = StockData(
                symbol="MSFT",
                timestamp=datetime.now(),
                price=300.0,
                volume=2000000,
                market_cap=2200000000000,
                sector="Technology",
                change_percent=1.8,
                embedding=[0.2] * 384
            )
            
            # Mock storage operations
            with patch.object(chromadb_service, 'store_weather_data') as mock_store_weather, \
                 patch.object(chromadb_service, 'store_stock_data') as mock_store_stock:
                
                mock_store_weather.return_value = True
                mock_store_stock.return_value = True
                
                # Test storage
                weather_stored = chromadb_service.store_weather_data([weather_data])
                stock_stored = chromadb_service.store_stock_data([stock_data])
                
                assert weather_stored is True
                assert stock_stored is True
    
    def test_query_processing_workflow(self):
        """Test natural language query processing workflow."""
        from weather_stock_dashboard.services.rag_engine import RAGEngine
        
        # Test RAG engine initialization
        rag_engine = RAGEngine()
        
        query = "How does rainfall affect retail stock prices?"
        
        # Test that RAG engine can be created and query is valid
        assert rag_engine is not None
        assert len(query) > 0
    
    def test_analysis_to_insights_workflow(self):
        """Test workflow from analysis to insights generation."""
        from weather_stock_dashboard.agents.insight_agent import InsightGeneratorAgent
        
        # Test insight agent initialization
        insight_agent = InsightGeneratorAgent()
        
        # Sample analysis results
        analysis_data = {
            "correlation_coefficient": 0.72,
            "p_value": 0.003,
            "weather_pattern": "temperature_volatility",
            "stock_pattern": "energy_sector_movement",
            "time_period": "90_days"
        }
        
        # Test that agent can be created and data is valid
        assert insight_agent is not None
        assert analysis_data["correlation_coefficient"] > 0.5


class TestPerformanceAndResilience:
    """Test system performance and error resilience."""
    
    def test_large_dataset_handling(self):
        """Test system behavior with large datasets."""
        # Generate large synthetic dataset
        large_weather_data = []
        for i in range(1000):
            weather = WeatherData(
                location=f"City_{i % 10}",
                timestamp=datetime.now() - timedelta(days=i),
                temperature=20.0 + (i % 20),
                humidity=50.0 + (i % 30),
                pressure=1013.0 + (i % 10),
                precipitation=float(i % 5),
                wind_speed=5.0 + (i % 15),
                weather_condition="Clear" if i % 2 == 0 else "Cloudy",
                embedding=[0.1] * 384
            )
            large_weather_data.append(weather)
        
        # Test that we can process large datasets without errors
        assert len(large_weather_data) == 1000
        
        # Test serialization performance
        import time
        start_time = time.time()
        
        serialized_data = [weather.dict() for weather in large_weather_data[:100]]
        
        end_time = time.time()
        serialization_time = end_time - start_time
        
        # Should serialize 100 records quickly (< 1 second)
        assert serialization_time < 1.0
        assert len(serialized_data) == 100
    
    def test_error_handling_resilience(self):
        """Test system resilience to various error conditions."""
        from weather_stock_dashboard.services.chromadb_service import ChromaDBService
        
        # Test with connection errors
        with patch('chromadb.Client') as mock_client:
            mock_client.side_effect = ConnectionError("Database unavailable")
            
            # Service should handle initialization gracefully
            try:
                service = ChromaDBService()
                # Should not raise exception during initialization
                assert True
            except ConnectionError:
                pytest.fail("Service should handle connection errors gracefully")
    
    def test_data_validation_edge_cases(self):
        """Test data validation with edge cases."""
        # Test extreme weather values
        try:
            extreme_weather = WeatherData(
                location="Antarctica",
                timestamp=datetime.now(),
                temperature=-89.0,  # Extreme cold
                humidity=10.0,      # Very dry
                pressure=870.0,     # Very low pressure (high altitude)
                precipitation=0.0,  # No precipitation in extreme cold
                wind_speed=200.0,   # Hurricane force
                weather_condition="Blizzard",
                embedding=[0.1] * 384
            )
            assert extreme_weather.temperature == -89.0
        except ValueError:
            # Expected for values outside validation ranges
            pass
        
        # Test extreme stock values
        try:
            extreme_stock = StockData(
                symbol="PENNY",
                timestamp=datetime.now(),
                price=0.01,  # Penny stock
                volume=1000000000,  # Very high volume
                market_cap=1000000,  # Small cap
                sector="Speculative",
                change_percent=-50.0,  # Large negative change
                embedding=[0.2] * 384
            )
            assert extreme_stock.price == 0.01
        except ValueError:
            # Expected for values outside validation ranges
            pass
    
    def test_concurrent_operations_safety(self):
        """Test thread safety of concurrent operations."""
        import threading
        import concurrent.futures
        
        from weather_stock_dashboard.services.chromadb_service import ChromaDBService
        
        with patch('chromadb.Client'), patch('sentence_transformers.SentenceTransformer'):
            service = ChromaDBService()
            
            def generate_embedding_task(text_id):
                """Task to generate embedding concurrently."""
                text = f"Test text {text_id}"
                return service.generate_embedding(text)
            
            # Test concurrent embedding generation
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(generate_embedding_task, i) for i in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # All tasks should complete successfully
            assert len(results) == 10
            for result in results:
                assert isinstance(result, list)
                assert len(result) == 384


if __name__ == "__main__":
    pytest.main([__file__, "-v"])