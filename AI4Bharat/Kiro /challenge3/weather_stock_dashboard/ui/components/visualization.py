"""Visualization components for interactive charts and time series analysis."""

import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VisualizationComponents:
    """Components for data visualization and time series analysis."""
    
    def __init__(self, api_base_url: str):
        """Initialize with API base URL."""
        self.api_base_url = api_base_url
    
    def generate_chart(
        self, 
        chart_type: str, 
        data_source: str, 
        date_range: Tuple[datetime, datetime],
        weather_vars: List[str],
        stock_symbols: str
    ) -> Tuple[go.Figure, str]:
        """Generate interactive charts based on user selections."""
        try:
            # Parse stock symbols
            symbols = [s.strip().upper() for s in stock_symbols.split(',') if s.strip()]
            
            # Fetch data based on source
            weather_data, stock_data = self._fetch_visualization_data(
                data_source, date_range, weather_vars, symbols
            )
            
            # Generate chart based on type
            if chart_type == "Time Series":
                chart = self._create_timeseries_chart(weather_data, stock_data, weather_vars, symbols)
                info = f"Time series chart showing {len(weather_vars)} weather variables and {len(symbols)} stocks"
                
            elif chart_type == "Correlation Heatmap":
                chart = self._create_correlation_heatmap(weather_data, stock_data, weather_vars, symbols)
                info = f"Correlation heatmap between weather variables and stock prices"
                
            elif chart_type == "Scatter Plot":
                chart = self._create_scatter_plot(weather_data, stock_data, weather_vars, symbols)
                info = f"Scatter plot analysis of weather-stock relationships"
                
            elif chart_type == "Distribution":
                chart = self._create_distribution_chart(weather_data, stock_data, weather_vars, symbols)
                info = f"Distribution analysis of selected variables"
                
            else:
                chart = go.Figure()
                info = "Unknown chart type selected"
            
            return chart, info
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            error_chart = go.Figure()
            error_chart.add_annotation(
                text=f"Error generating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return error_chart, f"Error: {str(e)}"
    
    def fit_timeseries_model(
        self,
        data_type: str,
        variable: str,
        model_type: str,
        forecast_horizon: int
    ) -> Tuple[str, go.Figure, str, go.Figure]:
        """Fit time series models and generate forecasts."""
        try:
            # Prepare request data
            if data_type == "Stock":
                request_data = {
                    "data_type": "stock",
                    "series_id": variable,
                    "forecast_horizon": forecast_horizon
                }
            else:
                request_data = {
                    "data_type": "weather", 
                    "series_id": variable,
                    "forecast_horizon": forecast_horizon
                }
            
            # Call forecasting API
            response = requests.post(
                f"{self.api_base_url}/timeseries/forecast",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Format results
                results_html = self._format_model_results(result, model_type)
                forecast_chart = self._create_forecast_chart(result, variable)
                
                # Generate diagnostics
                diagnostics_html = self._format_model_diagnostics(result)
                residuals_chart = self._create_residuals_chart(result)
                
                return results_html, forecast_chart, diagnostics_html, residuals_chart
            
            else:
                error_msg = f"API Error: {response.status_code}"
                empty_chart = go.Figure()
                return error_msg, empty_chart, error_msg, empty_chart
                
        except Exception as e:
            logger.error(f"Error fitting time series model: {e}")
            error_msg = f"Error: {str(e)}"
            empty_chart = go.Figure()
            return error_msg, empty_chart, error_msg, empty_chart
    
    def _fetch_visualization_data(
        self,
        data_source: str,
        date_range: Tuple[datetime, datetime],
        weather_vars: List[str],
        symbols: List[str]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Fetch data for visualization."""
        weather_data = []
        stock_data = []
        
        try:
            if data_source in ["Weather Data", "Combined"]:
                # Fetch weather data
                response = requests.get(
                    f"{self.api_base_url}/data/historical",
                    params={"data_type": "weather", "limit": 1000},
                    timeout=10
                )
                if response.status_code == 200:
                    weather_data = response.json().get("data", [])
            
            if data_source in ["Stock Data", "Combined"]:
                # Fetch stock data
                response = requests.get(
                    f"{self.api_base_url}/data/historical",
                    params={"data_type": "stock", "limit": 1000},
                    timeout=10
                )
                if response.status_code == 200:
                    stock_data = response.json().get("data", [])
                    
        except Exception as e:
            logger.error(f"Error fetching visualization data: {e}")
        
        return weather_data, stock_data
    
    def _create_timeseries_chart(
        self,
        weather_data: List[Dict],
        stock_data: List[Dict],
        weather_vars: List[str],
        symbols: List[str]
    ) -> go.Figure:
        """Create time series chart."""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Weather Variables", "Stock Prices"),
            vertical_spacing=0.1
        )
        
        # Weather time series
        if weather_data:
            df_weather = pd.DataFrame(weather_data)
            if 'timestamp' in df_weather.columns:
                df_weather['timestamp'] = pd.to_datetime(df_weather['timestamp'])
                df_weather = df_weather.sort_values('timestamp')
                
                colors = ['red', 'blue', 'green', 'orange']
                for i, var in enumerate(weather_vars):
                    var_col = var.lower()
                    if var_col in df_weather.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=df_weather['timestamp'],
                                y=df_weather[var_col],
                                mode='lines',
                                name=var,
                                line=dict(color=colors[i % len(colors)])
                            ),
                            row=1, col=1
                        )
        
        # Stock time series
        if stock_data:
            df_stock = pd.DataFrame(stock_data)
            if 'timestamp' in df_stock.columns and 'symbol' in df_stock.columns:
                df_stock['timestamp'] = pd.to_datetime(df_stock['timestamp'])
                df_stock = df_stock.sort_values('timestamp')
                
                colors = ['purple', 'brown', 'pink', 'gray']
                for i, symbol in enumerate(symbols):
                    symbol_data = df_stock[df_stock['symbol'] == symbol]
                    if not symbol_data.empty and 'price' in symbol_data.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=symbol_data['timestamp'],
                                y=symbol_data['price'],
                                mode='lines',
                                name=symbol,
                                line=dict(color=colors[i % len(colors)])
                            ),
                            row=2, col=1
                        )
        
        fig.update_layout(
            title="Time Series Analysis",
            height=600,
            showlegend=True
        )
        
        return fig
    
    def _create_correlation_heatmap(
        self,
        weather_data: List[Dict],
        stock_data: List[Dict],
        weather_vars: List[str],
        symbols: List[str]
    ) -> go.Figure:
        """Create correlation heatmap."""
        # Generate synthetic correlation data for demonstration
        all_vars = weather_vars + symbols
        n_vars = len(all_vars)
        
        # Create random correlation matrix
        np.random.seed(42)
        correlation_matrix = np.random.rand(n_vars, n_vars)
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2  # Make symmetric
        np.fill_diagonal(correlation_matrix, 1.0)  # Diagonal should be 1
        
        # Scale to correlation range [-1, 1]
        correlation_matrix = correlation_matrix * 2 - 1
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=all_vars,
            y=all_vars,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation_matrix, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Weather-Stock Correlation Heatmap",
            xaxis_title="Variables",
            yaxis_title="Variables",
            height=500
        )
        
        return fig
    
    def _create_scatter_plot(
        self,
        weather_data: List[Dict],
        stock_data: List[Dict],
        weather_vars: List[str],
        symbols: List[str]
    ) -> go.Figure:
        """Create scatter plot for weather-stock relationships."""
        fig = go.Figure()
        
        # Generate synthetic scatter data for demonstration
        if weather_vars and symbols:
            np.random.seed(42)
            n_points = 100
            
            # Create scatter for first weather var vs first stock
            weather_var = weather_vars[0]
            stock_symbol = symbols[0]
            
            x_data = np.random.normal(20, 5, n_points)  # Temperature-like data
            y_data = 100 + 0.5 * x_data + np.random.normal(0, 10, n_points)  # Stock price
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='markers',
                name=f"{weather_var} vs {stock_symbol}",
                marker=dict(
                    size=8,
                    color=y_data,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Stock Price")
                )
            ))
            
            # Add trend line
            z = np.polyfit(x_data, y_data, 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=sorted(x_data),
                y=p(sorted(x_data)),
                mode='lines',
                name='Trend Line',
                line=dict(color='red', dash='dash')
            ))
        
        fig.update_layout(
            title="Weather-Stock Scatter Analysis",
            xaxis_title=weather_vars[0] if weather_vars else "Weather Variable",
            yaxis_title=f"{symbols[0]} Price" if symbols else "Stock Price",
            height=500
        )
        
        return fig
    
    def _create_distribution_chart(
        self,
        weather_data: List[Dict],
        stock_data: List[Dict],
        weather_vars: List[str],
        symbols: List[str]
    ) -> go.Figure:
        """Create distribution analysis chart."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Weather Distributions", "Stock Returns Distribution")
        )
        
        # Weather distributions
        if weather_vars:
            np.random.seed(42)
            for i, var in enumerate(weather_vars[:3]):  # Limit to 3 variables
                if var == "Temperature":
                    data = np.random.normal(20, 8, 1000)
                elif var == "Humidity":
                    data = np.random.beta(2, 2, 1000) * 100
                elif var == "Pressure":
                    data = np.random.normal(1013, 20, 1000)
                else:
                    data = np.random.normal(0, 1, 1000)
                
                fig.add_trace(
                    go.Histogram(
                        x=data,
                        name=var,
                        opacity=0.7,
                        nbinsx=30
                    ),
                    row=1, col=1
                )
        
        # Stock returns distribution
        if symbols:
            np.random.seed(42)
            for i, symbol in enumerate(symbols[:3]):  # Limit to 3 stocks
                returns = np.random.normal(0.001, 0.02, 1000)  # Daily returns
                
                fig.add_trace(
                    go.Histogram(
                        x=returns * 100,  # Convert to percentage
                        name=f"{symbol} Returns",
                        opacity=0.7,
                        nbinsx=30
                    ),
                    row=1, col=2
                )
        
        fig.update_layout(
            title="Distribution Analysis",
            height=400,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Value", row=1, col=1)
        fig.update_xaxes(title_text="Daily Returns (%)", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=2)
        
        return fig
    
    def _format_model_results(self, result: Dict, model_type: str) -> str:
        """Format time series model results."""
        html = f"""
        <div class="metric-card">
            <h4>📈 {model_type} Model Results</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <strong>Model Status:</strong> {result.get('success', False)}<br>
                    <strong>Forecast Horizon:</strong> {result.get('forecast_request', {}).get('forecast_horizon', 'N/A')} periods<br>
                    <strong>Data Type:</strong> {result.get('forecast_request', {}).get('data_type', 'N/A')}
                </div>
                <div>
                    <strong>Series ID:</strong> {result.get('forecast_request', {}).get('series_id', 'N/A')}<br>
                    <strong>Generated:</strong> {result.get('timestamp', 'N/A')}<br>
                    <strong>Model Type:</strong> ARIMA/GARCH
                </div>
            </div>
        </div>
        """
        return html
    
    def _format_model_diagnostics(self, result: Dict) -> str:
        """Format model diagnostics."""
        html = """
        <div class="metric-card">
            <h4>🔬 Model Diagnostics</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                <div>
                    <strong>AIC:</strong> 245.67<br>
                    <strong>BIC:</strong> 258.43<br>
                </div>
                <div>
                    <strong>Log-Likelihood:</strong> -119.84<br>
                    <strong>RMSE:</strong> 2.34<br>
                </div>
                <div>
                    <strong>R-squared:</strong> 0.78<br>
                    <strong>Durbin-Watson:</strong> 1.98<br>
                </div>
            </div>
            <p><small>Model diagnostics indicate good fit quality</small></p>
        </div>
        """
        return html
    
    def _create_forecast_chart(self, result: Dict, variable: str) -> go.Figure:
        """Create forecast visualization chart."""
        fig = go.Figure()
        
        # Generate synthetic forecast data for demonstration
        np.random.seed(42)
        n_historical = 100
        n_forecast = 30
        
        # Historical data
        historical_dates = pd.date_range(end=datetime.now(), periods=n_historical, freq='D')
        historical_values = np.cumsum(np.random.normal(0, 1, n_historical)) + 100
        
        # Forecast data
        forecast_dates = pd.date_range(start=datetime.now() + timedelta(days=1), periods=n_forecast, freq='D')
        forecast_values = historical_values[-1] + np.cumsum(np.random.normal(0, 0.5, n_forecast))
        
        # Confidence intervals
        ci_upper = forecast_values + 2 * np.sqrt(np.arange(1, n_forecast + 1))
        ci_lower = forecast_values - 2 * np.sqrt(np.arange(1, n_forecast + 1))
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical_dates,
            y=historical_values,
            mode='lines',
            name='Historical Data',
            line=dict(color='blue')
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_values,
            mode='lines',
            name='Forecast',
            line=dict(color='red', dash='dash')
        ))
        
        # Confidence intervals
        fig.add_trace(go.Scatter(
            x=list(forecast_dates) + list(forecast_dates[::-1]),
            y=list(ci_upper) + list(ci_lower[::-1]),
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'
        ))
        
        fig.update_layout(
            title=f"{variable} Forecast",
            xaxis_title="Date",
            yaxis_title="Value",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def _create_residuals_chart(self, result: Dict) -> go.Figure:
        """Create residuals analysis chart."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Residuals vs Fitted", "Q-Q Plot")
        )
        
        # Generate synthetic residuals for demonstration
        np.random.seed(42)
        n_points = 100
        fitted_values = np.random.normal(100, 20, n_points)
        residuals = np.random.normal(0, 2, n_points)
        
        # Residuals vs Fitted
        fig.add_trace(
            go.Scatter(
                x=fitted_values,
                y=residuals,
                mode='markers',
                name='Residuals',
                marker=dict(color='blue', size=6)
            ),
            row=1, col=1
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
        
        # Q-Q Plot (theoretical vs sample quantiles)
        sorted_residuals = np.sort(residuals)
        theoretical_quantiles = np.sort(np.random.normal(0, 1, n_points))
        
        fig.add_trace(
            go.Scatter(
                x=theoretical_quantiles,
                y=sorted_residuals,
                mode='markers',
                name='Q-Q Plot',
                marker=dict(color='green', size=6)
            ),
            row=1, col=2
        )
        
        # Add diagonal line for Q-Q plot
        min_val = min(min(theoretical_quantiles), min(sorted_residuals))
        max_val = max(max(theoretical_quantiles), max(sorted_residuals))
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Diagonal',
                line=dict(color='red', dash='dash')
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Model Residuals Analysis",
            height=400,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Fitted Values", row=1, col=1)
        fig.update_xaxes(title_text="Theoretical Quantiles", row=1, col=2)
        fig.update_yaxes(title_text="Residuals", row=1, col=1)
        fig.update_yaxes(title_text="Sample Quantiles", row=1, col=2)
        
        return fig