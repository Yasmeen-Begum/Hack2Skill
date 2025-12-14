"""Main Gradio application for Weather Stock Dashboard."""

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

from .components import (
    DashboardComponents,
    VisualizationComponents, 
    QueryComponents,
    InsightComponents
)

logger = logging.getLogger(__name__)


class WeatherStockDashboard:
    """Main dashboard application class."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api", ui_integration=None):
        """Initialize dashboard with API configuration."""
        self.api_base_url = api_base_url
        self.ui_integration = ui_integration
        self.dashboard_components = DashboardComponents(api_base_url)
        self.viz_components = VisualizationComponents(api_base_url)
        self.query_components = QueryComponents(api_base_url)
        self.insight_components = InsightComponents(api_base_url)
        
    def create_app(self) -> gr.Blocks:
        """Create the main Gradio application."""
        
        with gr.Blocks(
            title="Weather Stock Dashboard",
            theme=gr.themes.Soft(),
            css=self._get_custom_css()
        ) as app:
            
            # Header
            gr.Markdown("# 🌤️📈 Weather Stock Dashboard")
            gr.Markdown("*Explore correlations between weather patterns and stock market performance*")
            
            # Status indicator
            with gr.Row():
                status_display = gr.HTML(value=self._get_status_html())
                refresh_btn = gr.Button("🔄 Refresh Status", size="sm")
            
            # Main navigation tabs
            with gr.Tabs() as tabs:
                
                # Tab 1: Real-time Dashboard
                with gr.Tab("📊 Dashboard", id="dashboard"):
                    self._create_dashboard_tab()
                
                # Tab 2: Data Visualization
                with gr.Tab("📈 Visualizations", id="visualizations"):
                    self._create_visualization_tab()
                
                # Tab 3: Natural Language Queries
                with gr.Tab("💬 Query Interface", id="queries"):
                    self._create_query_tab()
                
                # Tab 4: Correlation Insights
                with gr.Tab("🔍 Insights", id="insights"):
                    self._create_insights_tab()
                
                # Tab 5: Time Series Analysis
                with gr.Tab("📉 Time Series", id="timeseries"):
                    self._create_timeseries_tab()
            
            # Event handlers
            refresh_btn.click(
                fn=self._refresh_status,
                outputs=[status_display]
            )
            
        return app
    
    def _create_dashboard_tab(self):
        """Create the main dashboard tab with real-time data."""
        
        gr.Markdown("## Real-time Weather & Stock Data")
        
        with gr.Row():
            # Auto-refresh controls
            auto_refresh = gr.Checkbox(label="Auto-refresh", value=True)
            refresh_interval = gr.Slider(
                minimum=30, maximum=300, value=60, step=30,
                label="Refresh interval (seconds)"
            )
            manual_refresh = gr.Button("🔄 Refresh Now")
        
        with gr.Row():
            # Current weather panel
            with gr.Column(scale=1):
                gr.Markdown("### 🌤️ Current Weather")
                weather_display = gr.HTML()
                weather_chart = gr.Plot()
            
            # Current stock panel  
            with gr.Column(scale=1):
                gr.Markdown("### 📈 Current Stocks")
                stock_display = gr.HTML()
                stock_chart = gr.Plot()
        
        # System status panel
        with gr.Row():
            gr.Markdown("### 🔧 System Status")
            system_status = gr.HTML()
        
        # Load initial data
        def load_dashboard_data():
            return self.dashboard_components.get_current_data()
        
        # Event handlers for dashboard
        manual_refresh.click(
            fn=load_dashboard_data,
            outputs=[weather_display, weather_chart, stock_display, stock_chart, system_status]
        )
        
        # Auto-refresh timer (would need custom JS for real implementation)
        
    def _create_visualization_tab(self):
        """Create the data visualization tab."""
        
        gr.Markdown("## Interactive Data Visualizations")
        
        with gr.Row():
            # Visualization controls
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Chart Controls")
                
                chart_type = gr.Dropdown(
                    choices=["Time Series", "Correlation Heatmap", "Scatter Plot", "Distribution"],
                    value="Time Series",
                    label="Chart Type"
                )
                
                data_source = gr.Dropdown(
                    choices=["Weather Data", "Stock Data", "Combined"],
                    value="Combined",
                    label="Data Source"
                )
                
                # Note: DateRange not available in current Gradio version
                start_date = gr.Textbox(
                    value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    label="Start Date (YYYY-MM-DD)"
                )
                
                end_date = gr.Textbox(
                    value=datetime.now().strftime("%Y-%m-%d"),
                    label="End Date (YYYY-MM-DD)"
                )
                
                weather_vars = gr.CheckboxGroup(
                    choices=["Temperature", "Humidity", "Pressure", "Precipitation"],
                    value=["Temperature"],
                    label="Weather Variables"
                )
                
                stock_symbols = gr.Textbox(
                    value="AAPL,GOOGL,MSFT",
                    label="Stock Symbols (comma-separated)"
                )
                
                generate_chart = gr.Button("📊 Generate Chart", variant="primary")
            
            # Chart display
            with gr.Column(scale=2):
                chart_display = gr.Plot()
                chart_info = gr.HTML()
        
        # Event handler for chart generation
        def generate_chart_wrapper(chart_type, data_source, start_date, end_date, weather_vars, stock_symbols):
            # Convert date strings to datetime objects
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                date_range = (start_dt, end_dt)
            except ValueError:
                # Use default range if parsing fails
                date_range = (datetime.now() - timedelta(days=30), datetime.now())
            
            return self.viz_components.generate_chart(chart_type, data_source, date_range, weather_vars, stock_symbols)
        
        generate_chart.click(
            fn=generate_chart_wrapper,
            inputs=[chart_type, data_source, start_date, end_date, weather_vars, stock_symbols],
            outputs=[chart_display, chart_info]
        )
    
    def _create_query_tab(self):
        """Create the natural language query tab."""
        
        gr.Markdown("## Natural Language Query Interface")
        
        with gr.Row():
            # Query input section
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Ask Questions About Weather-Stock Relationships")
                
                query_input = gr.Textbox(
                    placeholder="e.g., 'How does temperature affect Apple stock prices?'",
                    label="Your Question",
                    lines=3
                )
                
                with gr.Row():
                    submit_query = gr.Button("🔍 Ask", variant="primary")
                    clear_query = gr.Button("🗑️ Clear")
                
                # Query suggestions
                gr.Markdown("### 💡 Example Questions")
                example_queries = [
                    "What's the correlation between rainfall and retail stocks?",
                    "How do temperature changes affect energy sector performance?",
                    "Show me weather patterns during market volatility periods",
                    "Which stocks are most sensitive to weather changes?"
                ]
                
                for query in example_queries:
                    example_btn = gr.Button(f"📝 {query}", size="sm")
                    example_btn.click(
                        fn=lambda q=query: q,
                        outputs=[query_input]
                    )
            
            # Query history sidebar
            with gr.Column(scale=1):
                gr.Markdown("### 📚 Query History")
                query_history = gr.HTML()
        
        # Query results section
        with gr.Row():
            query_results = gr.HTML()
            query_chart = gr.Plot()
        
        # Event handlers
        submit_query.click(
            fn=self.query_components.process_query,
            inputs=[query_input],
            outputs=[query_results, query_chart, query_history]
        )
        
        clear_query.click(
            fn=lambda: "",
            outputs=[query_input]
        )
    
    def _create_insights_tab(self):
        """Create the correlation insights tab."""
        
        gr.Markdown("## AI-Generated Correlation Insights")
        
        with gr.Row():
            # Insight generation controls
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Generate Insights")
                
                insight_weather_vars = gr.CheckboxGroup(
                    choices=["Temperature", "Humidity", "Pressure", "Precipitation", "Wind Speed"],
                    value=["Temperature", "Pressure"],
                    label="Weather Variables"
                )
                
                insight_stock_symbols = gr.Textbox(
                    value="AAPL,GOOGL,MSFT,TSLA",
                    label="Stock Symbols"
                )
                
                insight_period = gr.Dropdown(
                    choices=["Last 7 days", "Last 30 days", "Last 90 days", "Last year"],
                    value="Last 30 days",
                    label="Analysis Period"
                )
                
                confidence_threshold = gr.Slider(
                    minimum=0.1, maximum=0.99, value=0.95, step=0.05,
                    label="Confidence Threshold"
                )
                
                generate_insights = gr.Button("🧠 Generate Insights", variant="primary")
            
            # Insight display
            with gr.Column(scale=2):
                insights_display = gr.HTML()
                insights_chart = gr.Plot()
        
        # Statistical measures section
        with gr.Row():
            gr.Markdown("### 📊 Statistical Measures")
            correlation_matrix = gr.Plot()
            significance_table = gr.HTML()
        
        # Event handler
        generate_insights.click(
            fn=self.insight_components.generate_insights,
            inputs=[insight_weather_vars, insight_stock_symbols, insight_period, confidence_threshold],
            outputs=[insights_display, insights_chart, correlation_matrix, significance_table]
        )
    
    def _create_timeseries_tab(self):
        """Create the time series analysis tab."""
        
        gr.Markdown("## Time Series Modeling & Forecasting")
        
        with gr.Row():
            # Model configuration
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Model Configuration")
                
                ts_data_type = gr.Radio(
                    choices=["Weather", "Stock"],
                    value="Stock",
                    label="Data Type"
                )
                
                ts_variable = gr.Dropdown(
                    choices=["Temperature", "AAPL", "GOOGL", "MSFT"],
                    value="AAPL",
                    label="Variable/Symbol"
                )
                
                model_type = gr.Radio(
                    choices=["ARIMA", "GARCH", "Both"],
                    value="ARIMA",
                    label="Model Type"
                )
                
                forecast_horizon = gr.Slider(
                    minimum=1, maximum=90, value=30, step=1,
                    label="Forecast Horizon (days)"
                )
                
                fit_model = gr.Button("📈 Fit Model & Forecast", variant="primary")
            
            # Results display
            with gr.Column(scale=2):
                model_results = gr.HTML()
                forecast_chart = gr.Plot()
        
        # Model diagnostics section
        with gr.Row():
            gr.Markdown("### 🔬 Model Diagnostics")
            diagnostics_display = gr.HTML()
            residuals_chart = gr.Plot()
        
        # Event handler
        fit_model.click(
            fn=self.viz_components.fit_timeseries_model,
            inputs=[ts_data_type, ts_variable, model_type, forecast_horizon],
            outputs=[model_results, forecast_chart, diagnostics_display, residuals_chart]
        )
    
    def _get_custom_css(self) -> str:
        """Get custom CSS for the dashboard."""
        return """
        .gradio-container {
            max-width: 1200px !important;
        }
        
        .status-healthy {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }
        
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
        
        .metric-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 16px;
            margin: 8px;
        }
        
        .insight-panel {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 16px;
            margin: 8px 0;
        }
        """
    
    def _get_status_html(self) -> str:
        """Get system status HTML."""
        try:
            response = requests.get(f"{self.api_base_url}/status", timeout=5)
            if response.status_code == 200:
                return '<span class="status-healthy">🟢 System Online</span>'
            else:
                return '<span class="status-warning">🟡 System Issues</span>'
        except:
            return '<span class="status-error">🔴 System Offline</span>'
    
    def _refresh_status(self) -> str:
        """Refresh system status."""
        return self._get_status_html()


def create_gradio_app(
    api_base_url: str = "http://localhost:8000/api", 
    ui_integration = None
) -> gr.Blocks:
    """Create and return the Gradio application."""
    dashboard = WeatherStockDashboard(api_base_url, ui_integration)
    return dashboard.create_app()


if __name__ == "__main__":
    app = create_gradio_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )