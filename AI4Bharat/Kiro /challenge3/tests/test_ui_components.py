"""Tests for UI components."""

import pytest
from unittest.mock import Mock, patch
import gradio as gr
import plotly.graph_objects as go

from weather_stock_dashboard.ui.components.dashboard import DashboardComponents
from weather_stock_dashboard.ui.components.visualization import VisualizationComponents
from weather_stock_dashboard.ui.components.query import QueryComponents
from weather_stock_dashboard.ui.components.insights import InsightComponents
from weather_stock_dashboard.ui.app import create_gradio_app


class TestDashboardComponents:
    """Test dashboard components."""
    
    def test_dashboard_components_init(self):
        """Test dashboard components initialization."""
        components = DashboardComponents("http://localhost:8000/api")
        assert components.api_base_url == "http://localhost:8000/api"
    
    @patch('requests.get')
    def test_get_current_data_success(self, mock_get):
        """Test successful data retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recent_weather": [
                {
                    "location": "New York",
                    "temperature": 22.5,
                    "humidity": 65,
                    "pressure": 1013.2,
                    "weather_condition": "Sunny",
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            ],
            "recent_stocks": [
                {
                    "symbol": "AAPL",
                    "price": 150.25,
                    "change_percent": 1.5,
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            ],
            "system_status": {
                "collections": {"weather_count": 100, "stock_count": 50}
            }
        }
        mock_get.return_value = mock_response
        
        components = DashboardComponents("http://localhost:8000/api")
        result = components.get_current_data()
        
        # Should return 5 elements: weather_html, weather_chart, stock_html, stock_chart, system_html
        assert len(result) == 5
        weather_html, weather_chart, stock_html, stock_chart, system_html = result
        
        # Check that HTML contains expected data
        assert "New York" in weather_html
        assert "22.5" in weather_html
        assert "AAPL" in stock_html
        assert "150.25" in stock_html
        
        # Check that charts are plotly figures
        assert isinstance(weather_chart, go.Figure)
        assert isinstance(stock_chart, go.Figure)
    
    @patch('requests.get')
    def test_get_current_data_api_error(self, mock_get):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        components = DashboardComponents("http://localhost:8000/api")
        result = components.get_current_data()
        
        # Should return error messages
        assert len(result) == 5
        weather_html, weather_chart, stock_html, stock_chart, system_html = result
        
        assert "API Error" in weather_html
        assert isinstance(weather_chart, go.Figure)


class TestVisualizationComponents:
    """Test visualization components."""
    
    def test_visualization_components_init(self):
        """Test visualization components initialization."""
        components = VisualizationComponents("http://localhost:8000/api")
        assert components.api_base_url == "http://localhost:8000/api"
    
    @patch('weather_stock_dashboard.ui.components.visualization.VisualizationComponents._fetch_visualization_data')
    def test_generate_chart_timeseries(self, mock_fetch):
        """Test time series chart generation."""
        # Mock data
        mock_fetch.return_value = (
            [{"timestamp": "2024-01-01", "temperature": 20}],
            [{"timestamp": "2024-01-01", "symbol": "AAPL", "price": 150}]
        )
        
        components = VisualizationComponents("http://localhost:8000/api")
        from datetime import datetime
        
        chart, info = components.generate_chart(
            "Time Series",
            "Combined", 
            (datetime(2024, 1, 1), datetime(2024, 1, 31)),
            ["Temperature"],
            "AAPL"
        )
        
        assert isinstance(chart, go.Figure)
        assert "Time series chart" in info
    
    @patch('requests.post')
    def test_fit_timeseries_model(self, mock_post):
        """Test time series model fitting."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "forecast_request": {
                "data_type": "stock",
                "series_id": "AAPL",
                "forecast_horizon": 30
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_post.return_value = mock_response
        
        components = VisualizationComponents("http://localhost:8000/api")
        result = components.fit_timeseries_model("Stock", "AAPL", "ARIMA", 30)
        
        assert len(result) == 4
        results_html, forecast_chart, diagnostics_html, residuals_chart = result
        
        assert "ARIMA Model Results" in results_html
        assert isinstance(forecast_chart, go.Figure)
        assert isinstance(residuals_chart, go.Figure)


class TestQueryComponents:
    """Test query components."""
    
    def test_query_components_init(self):
        """Test query components initialization."""
        components = QueryComponents("http://localhost:8000/api")
        assert components.api_base_url == "http://localhost:8000/api"
        assert components.query_history == []
    
    @patch('requests.post')
    def test_process_query_success(self, mock_post):
        """Test successful query processing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "query": "How does temperature affect Apple stock?",
            "result": {"analysis": "Temperature shows moderate correlation with AAPL"},
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_post.return_value = mock_response
        
        components = QueryComponents("http://localhost:8000/api")
        result = components.process_query("How does temperature affect Apple stock?")
        
        assert len(result) == 3
        response_html, response_chart, history_html = result
        
        assert "Query Results" in response_html
        assert isinstance(response_chart, go.Figure)
        assert len(components.query_history) == 1
        assert components.query_history[0]["success"] is True
    
    def test_process_empty_query(self):
        """Test processing empty query."""
        components = QueryComponents("http://localhost:8000/api")
        result = components.process_query("")
        
        response_html, response_chart, history_html = result
        assert "Please enter a question" in response_html


class TestInsightComponents:
    """Test insight components."""
    
    def test_insight_components_init(self):
        """Test insight components initialization."""
        components = InsightComponents("http://localhost:8000/api")
        assert components.api_base_url == "http://localhost:8000/api"
    
    @patch('requests.get')
    def test_generate_insights_success(self, mock_get):
        """Test successful insights generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "analysis_type": "correlation_insights",
            "result": {"insights": "Weather patterns show correlation with stock performance"}
        }
        mock_get.return_value = mock_response
        
        components = InsightComponents("http://localhost:8000/api")
        result = components.generate_insights(
            ["Temperature", "Humidity"],
            "AAPL,GOOGL",
            "Last 30 days",
            0.95
        )
        
        assert len(result) == 4
        insights_html, insights_chart, correlation_matrix, significance_table = result
        
        assert "AI-Generated Correlation Insights" in insights_html
        assert isinstance(insights_chart, go.Figure)
        assert isinstance(correlation_matrix, go.Figure)
        assert "Statistical Significance Analysis" in significance_table


class TestGradioApp:
    """Test Gradio app creation."""
    
    def test_create_gradio_app(self):
        """Test Gradio app creation."""
        app = create_gradio_app("http://localhost:8000/api")
        assert isinstance(app, gr.Blocks)
    
    @patch('requests.get')
    def test_gradio_app_with_mock_api(self, mock_get):
        """Test Gradio app with mocked API."""
        # Mock status endpoint
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        app = create_gradio_app("http://localhost:8000/api")
        assert isinstance(app, gr.Blocks)


if __name__ == "__main__":
    pytest.main([__file__])