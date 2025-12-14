"""Tests for data models."""

import pytest
from datetime import datetime
from weather_stock_dashboard.models import (
    WeatherData,
    StockData,
    TimeSeriesAnalysis,
    WeatherStockRelationship,
    CorrelationInsight,
    NaturalLanguageQuery
)


class TestWeatherData:
    """Test WeatherData model."""
    
    def test_valid_weather_data(self):
        """Test creating valid weather data."""
        data = WeatherData(
            timestamp=datetime.now(),
            location="New York, NY",
            temperature=20.5,
            humidity=65.0,
            pressure=1013.25,
            precipitation=0.0,
            wind_speed=15.0,
            weather_condition="sunny"
        )
        assert data.location == "New York, NY"
        assert data.temperature == 20.5
    
    def test_temperature_validation(self):
        """Test temperature range validation."""
        with pytest.raises(ValueError):
            WeatherData(
                timestamp=datetime.now(),
                location="Test",
                temperature=-150,  # Too low
                humidity=50,
                pressure=1000,
                precipitation=0,
                wind_speed=10,
                weather_condition="cold"
            )
    
    def test_empty_location_validation(self):
        """Test empty location validation."""
        with pytest.raises(ValueError):
            WeatherData(
                timestamp=datetime.now(),
                location="   ",  # Whitespace only
                temperature=20,
                humidity=50,
                pressure=1000,
                precipitation=0,
                wind_speed=10,
                weather_condition="sunny"
            )


class TestStockData:
    """Test StockData model."""
    
    def test_valid_stock_data(self):
        """Test creating valid stock data."""
        data = StockData(
            timestamp=datetime.now(),
            symbol="AAPL",
            price=185.50,
            volume=45000000,
            sector="Technology",
            change_percent=2.5
        )
        assert data.symbol == "AAPL"
        assert data.price == 185.50
    
    def test_symbol_validation(self):
        """Test stock symbol validation."""
        data = StockData(
            timestamp=datetime.now(),
            symbol="aapl",  # Should be converted to uppercase
            price=100.0,
            volume=1000000,
            sector="Technology",
            change_percent=1.0
        )
        assert data.symbol == "AAPL"
    
    def test_negative_price_validation(self):
        """Test negative price validation."""
        with pytest.raises(ValueError):
            StockData(
                timestamp=datetime.now(),
                symbol="TEST",
                price=-10.0,  # Negative price
                volume=1000000,
                sector="Technology",
                change_percent=1.0
            )


class TestTimeSeriesAnalysis:
    """Test TimeSeriesAnalysis model."""
    
    def test_valid_timeseries_analysis(self):
        """Test creating valid time series analysis."""
        data = TimeSeriesAnalysis(
            id="ts_001",
            series_type="stock",
            arima_order=(1, 1, 1),
            arima_forecast=[100.0, 101.0, 102.0],
            arima_confidence_intervals=[(95.0, 105.0), (96.0, 106.0), (97.0, 107.0)],
            model_diagnostics={"aic": 1250.5, "bic": 1275.8},
            forecast_horizon=3,
            timestamp=datetime.now()
        )
        assert data.series_type == "stock"
        assert data.arima_order == (1, 1, 1)
    
    def test_invalid_series_type(self):
        """Test invalid series type validation."""
        with pytest.raises(ValueError):
            TimeSeriesAnalysis(
                id="ts_001",
                series_type="invalid",  # Invalid type
                arima_order=(1, 1, 1),
                arima_forecast=[100.0],
                arima_confidence_intervals=[(95.0, 105.0)],
                model_diagnostics={"aic": 1250.5, "bic": 1275.8},
                forecast_horizon=1,
                timestamp=datetime.now()
            )


class TestCorrelationInsight:
    """Test CorrelationInsight model."""
    
    def test_valid_correlation_insight(self):
        """Test creating valid correlation insight."""
        data = CorrelationInsight(
            id="insight_001",
            weather_pattern="High temperature",
            stock_pattern="Energy sector increase",
            correlation_coefficient=0.65,
            confidence_level=0.95,
            time_period="Summer 2023",
            statistical_significance=0.001,
            explanation="Strong positive correlation observed",
            supporting_data_points=120
        )
        assert data.correlation_coefficient == 0.65
        assert data.supporting_data_points == 120
    
    def test_correlation_coefficient_bounds(self):
        """Test correlation coefficient bounds validation."""
        with pytest.raises(ValueError):
            CorrelationInsight(
                id="insight_001",
                weather_pattern="Test",
                stock_pattern="Test",
                correlation_coefficient=1.5,  # Out of bounds
                confidence_level=0.95,
                time_period="Test",
                statistical_significance=0.001,
                explanation="Test",
                supporting_data_points=100
            )


class TestNaturalLanguageQuery:
    """Test NaturalLanguageQuery model."""
    
    def test_valid_query(self):
        """Test creating valid natural language query."""
        data = NaturalLanguageQuery(
            query_text="How does rain affect stock prices?",
            timestamp=datetime.now()
        )
        assert data.query_text == "How does rain affect stock prices?"
    
    def test_empty_query_validation(self):
        """Test empty query text validation."""
        with pytest.raises(ValueError):
            NaturalLanguageQuery(
                query_text="   ",  # Whitespace only
                timestamp=datetime.now()
            )