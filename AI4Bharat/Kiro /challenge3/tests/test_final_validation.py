"""
Final system validation tests for Task 13: Final system testing and validation.

This module provides comprehensive validation of the Weather Stock Dashboard system,
including end-to-end workflows, performance testing, and system integration validation.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path


class TestSystemValidation:
    """Comprehensive system validation tests."""
    
    def test_project_structure_completeness(self):
        """Validate that all required project components exist."""
        required_dirs = [
            "weather_stock_dashboard",
            "weather_stock_dashboard/models",
            "weather_stock_dashboard/services", 
            "weather_stock_dashboard/agents",
            "weather_stock_dashboard/api",
            "weather_stock_dashboard/ui",
            "weather_stock_dashboard/core",
            "weather_stock_dashboard/mcp_servers",
            "weather_stock_dashboard/utils",
            "tests",
            "config"
        ]
        
        for dir_path in required_dirs:
            assert Path(dir_path).exists(), f"Required directory {dir_path} is missing"
    
    def test_core_models_functionality(self):
        """Test that all core data models can be imported and instantiated."""
        from weather_stock_dashboard.models.weather import WeatherData
        from weather_stock_dashboard.models.stock import StockData
        from weather_stock_dashboard.models.timeseries import TimeSeriesAnalysis
        from weather_stock_dashboard.models.correlation import CorrelationInsight
        from weather_stock_dashboard.models.query import NaturalLanguageQuery
        
        # Test WeatherData
        weather = WeatherData(
            timestamp=datetime.now(),
            location="Test City",
            temperature=25.0,
            humidity=60.0,
            pressure=1013.25,
            precipitation=0.0,
            wind_speed=10.0,
            weather_condition="Clear",
            embedding=[0.1] * 384
        )
        assert weather.location == "Test City"
        
        # Test StockData
        stock = StockData(
            timestamp=datetime.now(),
            symbol="TEST",
            price=100.0,
            volume=1000000,
            market_cap=1000000000,
            sector="Technology",
            change_percent=2.5,
            embedding=[0.2] * 384
        )
        assert stock.symbol == "TEST"
        
        # Test TimeSeriesAnalysis
        analysis = TimeSeriesAnalysis(
            id="test_1",
            series_type="stock",
            arima_order=(1, 1, 1),
            arima_forecast=[101.0, 102.0, 103.0],
            arima_confidence_intervals=[(100.0, 102.0), (101.0, 103.0), (102.0, 104.0)],
            garch_volatility=[0.1, 0.1, 0.1],
            model_diagnostics={"aic": 100.0, "bic": 110.0},
            forecast_horizon=3,
            timestamp=datetime.now()
        )
        assert analysis.series_type == "stock"
        
        # Test CorrelationInsight
        insight = CorrelationInsight(
            id="insight_1",
            weather_pattern="temperature_rise",
            stock_pattern="price_increase",
            correlation_coefficient=0.75,
            statistical_significance=0.01,
            confidence_level=0.95,
            time_period="30_days",
            supporting_data_points=30,
            explanation="Strong positive correlation observed."
        )
        assert insight.correlation_coefficient == 0.75
        
        # Test NaturalLanguageQuery
        query = NaturalLanguageQuery(
            query_text="How does weather affect stock prices?",
            user_id="test_user",
            processed_intent="correlation_analysis",
            retrieved_context=["weather_data", "stock_data"]
        )
        assert query.user_id == "test_user"
    
    def test_service_layer_initialization(self):
        """Test that all service classes can be imported and initialized."""
        from weather_stock_dashboard.services.chromadb_service import ChromaDBService
        from weather_stock_dashboard.services.timeseries_service import TimeSeriesService
        from weather_stock_dashboard.services.garch_service import GARCHService
        from weather_stock_dashboard.services.correlation_service import CorrelationService
        from weather_stock_dashboard.services.rag_engine import RAGEngine
        
        # Test service initialization (with mocked dependencies)
        chromadb_service = ChromaDBService()
        assert chromadb_service is not None
        
        timeseries_service = TimeSeriesService()
        assert timeseries_service is not None
        
        garch_service = GARCHService()
        assert garch_service is not None
        
        correlation_service = CorrelationService()
        assert correlation_service is not None
        
        rag_engine = RAGEngine()
        assert rag_engine is not None
    
    def test_agent_system_initialization(self):
        """Test that all AI agents can be imported and initialized."""
        from weather_stock_dashboard.agents.data_validator_agent import DataValidatorAgent
        from weather_stock_dashboard.agents.forecaster_agent import TimeSeriesForecasterAgent
        from weather_stock_dashboard.agents.volatility_agent import VolatilityAnalyzerAgent
        from weather_stock_dashboard.agents.insight_agent import InsightGeneratorAgent
        
        # Test agent initialization
        data_validator = DataValidatorAgent()
        assert data_validator is not None
        
        forecaster = TimeSeriesForecasterAgent()
        assert forecaster is not None
        
        volatility_analyzer = VolatilityAnalyzerAgent()
        assert volatility_analyzer is not None
        
        insight_generator = InsightGeneratorAgent()
        assert insight_generator is not None
    
    def test_api_layer_structure(self):
        """Test that API components are properly structured."""
        from weather_stock_dashboard.api.middleware import setup_middleware
        from weather_stock_dashboard.api.websocket import websocket_endpoint
        
        # Test that API components can be imported
        assert setup_middleware is not None
        assert websocket_endpoint is not None
    
    def test_ui_components_initialization(self):
        """Test that UI components can be imported and initialized."""
        from weather_stock_dashboard.ui.components.dashboard import DashboardComponents
        from weather_stock_dashboard.ui.components.visualization import VisualizationComponents
        from weather_stock_dashboard.ui.components.query import QueryComponents
        from weather_stock_dashboard.ui.components.insights import InsightComponents
        
        # Test UI component initialization
        dashboard = DashboardComponents("http://localhost:8000")
        assert dashboard is not None
        
        visualization = VisualizationComponents("http://localhost:8000")
        assert visualization is not None
        
        query = QueryComponents("http://localhost:8000")
        assert query is not None
        
        insights = InsightComponents("http://localhost:8000")
        assert insights is not None
    
    def test_core_integration_layer(self):
        """Test that core integration components can be imported."""
        from weather_stock_dashboard.core.app_manager import AppManager
        from weather_stock_dashboard.core.service_registry import ServiceRegistry
        from weather_stock_dashboard.core.health_monitor import HealthMonitor
        from weather_stock_dashboard.core.data_pipeline import DataPipeline
        from weather_stock_dashboard.core.agent_integration import AgentIntegrationService
        
        # Test core component initialization
        service_registry = ServiceRegistry()
        assert service_registry is not None
        
        health_monitor = HealthMonitor()
        assert health_monitor is not None
        
        data_pipeline = DataPipeline()
        assert data_pipeline is not None
        
        agent_integration = AgentIntegrationService()
        assert agent_integration is not None
    
    def test_configuration_completeness(self):
        """Test that all configuration files are present and valid."""
        config_files = [
            "requirements.txt",
            "pyproject.toml",
            ".env.example",
            "config/settings.py",
            "main.py",
            "Makefile"
        ]
        
        for config_file in config_files:
            assert Path(config_file).exists(), f"Configuration file {config_file} is missing"
    
    def test_demo_functionality(self):
        """Test that demo components work correctly."""
        # Test demo Gradio UI
        assert Path("demo_gradio_ui.py").exists()
        
        # Test that demo can be imported
        try:
            import demo_gradio_ui
            assert demo_gradio_ui is not None
        except ImportError as e:
            # Expected if dependencies are missing
            assert "gradio" in str(e).lower() or "requests" in str(e).lower()


class TestSystemPerformanceValidation:
    """System performance validation tests."""
    
    def test_model_validation_performance(self):
        """Test that model validation performs within acceptable limits."""
        from weather_stock_dashboard.models.weather import WeatherData
        import time
        
        # Test validation performance with 100 weather data instances
        start_time = time.time()
        
        for i in range(100):
            weather = WeatherData(
                timestamp=datetime.now(),
                location=f"City_{i}",
                temperature=20.0 + i % 20,
                humidity=50.0 + i % 30,
                pressure=1013.0 + i % 10,
                precipitation=float(i % 5),
                wind_speed=5.0 + i % 15,
                weather_condition="Clear" if i % 2 == 0 else "Cloudy",
                embedding=[0.1] * 384
            )
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Should validate 100 instances in less than 1 second
        assert validation_time < 1.0, f"Model validation took {validation_time:.2f}s, expected < 1.0s"
    
    def test_service_initialization_performance(self):
        """Test that services initialize within acceptable time limits."""
        from weather_stock_dashboard.services.chromadb_service import ChromaDBService
        import time
        
        start_time = time.time()
        
        # Initialize multiple service instances
        for _ in range(10):
            service = ChromaDBService()
        
        end_time = time.time()
        init_time = end_time - start_time
        
        # Should initialize 10 services in less than 2 seconds
        assert init_time < 2.0, f"Service initialization took {init_time:.2f}s, expected < 2.0s"
    
    def test_memory_usage_stability(self):
        """Test that system doesn't have obvious memory leaks."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform some operations that might cause memory leaks
        from weather_stock_dashboard.models.weather import WeatherData
        
        data_instances = []
        for i in range(1000):
            weather = WeatherData(
                timestamp=datetime.now(),
                location=f"City_{i}",
                temperature=20.0,
                humidity=60.0,
                pressure=1013.25,
                precipitation=0.0,
                wind_speed=10.0,
                weather_condition="Clear",
                embedding=[0.1] * 384
            )
            data_instances.append(weather)
        
        # Clear references
        data_instances.clear()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (< 50MB for this test)
        assert memory_growth < 50, f"Memory grew by {memory_growth:.2f}MB, expected < 50MB"


class TestSystemIntegrationValidation:
    """System integration validation tests."""
    
    def test_data_flow_integration(self):
        """Test that data can flow through the system components."""
        from weather_stock_dashboard.models.weather import WeatherData
        from weather_stock_dashboard.models.stock import StockData
        from weather_stock_dashboard.services.chromadb_service import ChromaDBService
        
        # Create test data
        weather_data = WeatherData(
            timestamp=datetime.now(),
            location="Integration Test City",
            temperature=25.0,
            humidity=60.0,
            pressure=1013.25,
            precipitation=0.0,
            wind_speed=10.0,
            weather_condition="Clear",
            embedding=[0.1] * 384
        )
        
        stock_data = StockData(
            timestamp=datetime.now(),
            symbol="INTG",
            price=100.0,
            volume=1000000,
            market_cap=1000000000,
            sector="Technology",
            change_percent=2.5,
            embedding=[0.2] * 384
        )
        
        # Test that data can be serialized (important for API/storage)
        weather_dict = weather_data.model_dump()
        stock_dict = stock_data.model_dump()
        
        assert weather_dict["location"] == "Integration Test City"
        assert stock_dict["symbol"] == "INTG"
        
        # Test that data can be deserialized
        weather_restored = WeatherData(**weather_dict)
        stock_restored = StockData(**stock_dict)
        
        assert weather_restored.location == weather_data.location
        assert stock_restored.symbol == stock_data.symbol
    
    def test_error_handling_integration(self):
        """Test that the system handles errors gracefully."""
        from weather_stock_dashboard.models.weather import WeatherData
        from pydantic import ValidationError
        
        # Test invalid data handling
        with pytest.raises(ValidationError):
            WeatherData(
                timestamp=datetime.now(),
                location="",  # Invalid: empty location
                temperature=25.0,
                humidity=60.0,
                pressure=1013.25,
                precipitation=0.0,
                wind_speed=10.0,
                weather_condition="Clear"
            )
        
        # Test extreme values handling
        with pytest.raises(ValidationError):
            WeatherData(
                timestamp=datetime.now(),
                location="Test City",
                temperature=1000.0,  # Invalid: extreme temperature
                humidity=60.0,
                pressure=1013.25,
                precipitation=0.0,
                wind_speed=10.0,
                weather_condition="Clear"
            )
    
    def test_configuration_integration(self):
        """Test that configuration system works correctly."""
        from config.settings import Settings
        
        # Test that settings can be loaded
        settings = Settings()
        assert settings is not None
        
        # Test that required configuration attributes exist
        required_attrs = ['database_url', 'api_host', 'api_port', 'debug']
        for attr in required_attrs:
            assert hasattr(settings, attr), f"Settings missing required attribute: {attr}"


class TestSystemDocumentationValidation:
    """Validate system documentation and examples."""
    
    def test_readme_completeness(self):
        """Test that README.md exists and contains required sections."""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md file is missing"
        
        readme_content = readme_path.read_text()
        
        required_sections = [
            "Weather Stock Dashboard",
            "Features",
            "Installation", 
            "Usage",
            "API Documentation"
        ]
        
        for section in required_sections:
            assert section in readme_content, f"README.md missing section: {section}"
    
    def test_example_files_exist(self):
        """Test that example and demo files exist."""
        example_files = [
            ".env.example",
            "demo_gradio_ui.py"
        ]
        
        for example_file in example_files:
            assert Path(example_file).exists(), f"Example file {example_file} is missing"
    
    def test_makefile_targets(self):
        """Test that Makefile contains required targets."""
        makefile_path = Path("Makefile")
        assert makefile_path.exists(), "Makefile is missing"
        
        makefile_content = makefile_path.read_text()
        
        required_targets = [
            "install",
            "test", 
            "run",
            "clean"
        ]
        
        for target in required_targets:
            assert f"{target}:" in makefile_content, f"Makefile missing target: {target}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])