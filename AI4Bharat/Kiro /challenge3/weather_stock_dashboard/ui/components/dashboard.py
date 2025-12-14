"""Dashboard components for real-time data display."""

import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class DashboardComponents:
    """Components for the main dashboard tab."""
    
    def __init__(self, api_base_url: str):
        """Initialize with API base URL."""
        self.api_base_url = api_base_url
    
    def get_current_data(self) -> Tuple[str, go.Figure, str, go.Figure, str]:
        """Get current weather and stock data for dashboard display."""
        try:
            # Fetch current dashboard data
            response = requests.get(f"{self.api_base_url}/dashboard/current", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process weather data
                weather_html = self._format_weather_display(data.get("recent_weather", []))
                weather_chart = self._create_weather_chart(data.get("recent_weather", []))
                
                # Process stock data
                stock_html = self._format_stock_display(data.get("recent_stocks", []))
                stock_chart = self._create_stock_chart(data.get("recent_stocks", []))
                
                # System status
                system_html = self._format_system_status(data.get("system_status", {}))
                
                return weather_html, weather_chart, stock_html, stock_chart, system_html
            
            else:
                error_msg = f"API Error: {response.status_code}"
                empty_chart = go.Figure()
                return error_msg, empty_chart, error_msg, empty_chart, error_msg
                
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            error_msg = f"Connection Error: {str(e)}"
            empty_chart = go.Figure()
            return error_msg, empty_chart, error_msg, empty_chart, error_msg
    
    def _format_weather_display(self, weather_data: List[Dict]) -> str:
        """Format weather data for HTML display."""
        if not weather_data:
            return """
            <div style="background-color: white !important; padding: 20px !important; border: 2px solid #333 !important; border-radius: 10px !important; margin: 15px 0 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;">
                <h3 style="color: #000000 !important; font-weight: bold !important; margin: 0 0 10px 0 !important; font-size: 18px !important;">No Weather Data Available</h3>
                <p style="color: #333333 !important; font-weight: 500 !important; margin: 0 !important;">Weather data collection may be in progress...</p>
            </div>
            """
        
        # Use first weather entry as current
        current = weather_data[0] if weather_data else {}
        
        html = f"""
        <div style="background-color: #1976d2 !important; padding: 20px !important; border: 3px solid #0d47a1 !important; border-radius: 10px !important; margin: 15px 0 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;">
            <h3 style="color: white !important; font-weight: bold !important; margin: 0 0 20px 0 !important; font-size: 20px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">🌤️ Current Weather - {current.get('location', 'N/A')}</h3>
            
            <div style="display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 15px !important;">
                <div style="background-color: #0d47a1 !important; padding: 15px !important; border: 2px solid #ffffff !important; border-radius: 8px !important;">
                    <div style="color: white !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 8px !important;">Temperature:</div>
                    <div style="font-size: 24px !important; color: #ffeb3b !important; font-weight: bold !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{current.get('temperature', 'N/A')}°C</div>
                </div>
                <div style="background-color: #0d47a1 !important; padding: 15px !important; border: 2px solid #ffffff !important; border-radius: 8px !important;">
                    <div style="color: white !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 8px !important;">Condition:</div>
                    <div style="color: #81c784 !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{current.get('weather_condition', 'N/A')}</div>
                </div>
                <div style="background-color: #0d47a1 !important; padding: 15px !important; border: 2px solid #ffffff !important; border-radius: 8px !important;">
                    <div style="color: white !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 8px !important;">Humidity:</div>
                    <div style="color: #81c784 !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{current.get('humidity', 'N/A')}%</div>
                </div>
                <div style="background-color: #0d47a1 !important; padding: 15px !important; border: 2px solid #ffffff !important; border-radius: 8px !important;">
                    <div style="color: white !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 8px !important;">Pressure:</div>
                    <div style="color: #ffeb3b !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{current.get('pressure', 'N/A')} hPa</div>
                </div>
            </div>
            
            <div style="color: #e3f2fd !important; margin-top: 15px !important; font-size: 12px !important; font-style: italic !important;">Last updated: {current.get('timestamp', 'Unknown')}</div>
        </div>
        """
        
        return html
    
    def _format_stock_display(self, stock_data: List[Dict]) -> str:
        """Format stock data for HTML display."""
        if not stock_data:
            return """
            <div style="background-color: white !important; padding: 20px !important; border: 2px solid #333 !important; border-radius: 10px !important; margin: 15px 0 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;">
                <h3 style="color: #000000 !important; font-weight: bold !important; margin: 0 0 10px 0 !important; font-size: 18px !important;">No Stock Data Available</h3>
                <p style="color: #333333 !important; font-weight: 500 !important; margin: 0 !important;">Stock data collection may be in progress...</p>
            </div>
            """
        
        html = f"""
        <div style="background-color: #1976d2 !important; padding: 20px !important; border: 3px solid #0d47a1 !important; border-radius: 10px !important; margin: 15px 0 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;">
            <h3 style="color: white !important; font-weight: bold !important; margin: 0 0 20px 0 !important; font-size: 20px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">📈 Current Stocks</h3>
        """
        
        for stock in stock_data[:5]:  # Show top 5 stocks
            symbol = stock.get('symbol', 'N/A')
            price = stock.get('price', 'N/A')
            change = stock.get('change_percent', 0)
            
            change_color = "#d32f2f" if change < 0 else "#388e3c"
            change_symbol = "+" if change >= 0 else ""
            border_color = "#d32f2f" if change < 0 else "#388e3c"
            
            html += f"""
            <div style="display: flex !important; justify-content: space-between !important; align-items: center !important; margin: 10px 0 !important; padding: 15px !important; background-color: #0d47a1 !important; border-radius: 8px !important; border-left: 5px solid {border_color} !important; border: 2px solid #ffffff !important;">
                <div style="color: white !important; font-weight: bold !important; font-size: 18px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{symbol}</div>
                <div style="color: white !important; font-weight: bold !important; font-size: 18px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">${price}</div>
                <div style="color: {change_color} !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{change_symbol}{change:.2f}%</div>
            </div>
            """
        
        html += f"""
            <div style="color: #e3f2fd !important; margin-top: 15px !important; font-size: 12px !important; font-style: italic !important;">Showing {len(stock_data)} stocks</div>
        </div>
        """
        return html
    
    def _format_system_status(self, system_data: Dict) -> str:
        """Format system status for HTML display."""
        collections = system_data.get("collections", {})
        collector = system_data.get("data_collector", {})
        
        html = f"""
        <div style="background-color: #1976d2 !important; padding: 20px !important; border: 3px solid #0d47a1 !important; border-radius: 10px !important; margin: 15px 0 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;">
            <h3 style="color: white !important; font-weight: bold !important; margin: 0 0 20px 0 !important; font-size: 20px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">🔧 System Status</h3>
            
            <div style="display: grid !important; grid-template-columns: 1fr 1fr 1fr !important; gap: 15px !important; margin: 15px 0 !important;">
                <div style="background-color: #0d47a1 !important; padding: 15px !important; border: 2px solid #ffffff !important; border-radius: 8px !important; text-align: center !important;">
                    <div style="color: white !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 8px !important;">Weather Collection:</div>
                    <div style="color: #81c784 !important; font-weight: bold !important; font-size: 16px !important; margin-bottom: 5px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">✓ Active</div>
                    <div style="color: #e3f2fd !important; font-size: 12px !important;">{collections.get('weather_count', 0)} records</div>
                </div>
                <div style="background-color: #0d47a1 !important; padding: 15px !important; border: 2px solid #ffffff !important; border-radius: 8px !important; text-align: center !important;">
                    <div style="color: white !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 8px !important;">Stock Collection:</div>
                    <div style="color: #81c784 !important; font-weight: bold !important; font-size: 16px !important; margin-bottom: 5px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">✓ Active</div>
                    <div style="color: #e3f2fd !important; font-size: 12px !important;">{collections.get('stock_count', 0)} records</div>
                </div>
                <div style="background-color: #0d47a1 !important; padding: 15px !important; border: 2px solid #ffffff !important; border-radius: 8px !important; text-align: center !important;">
                    <div style="color: white !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 8px !important;">AI Agents:</div>
                    <div style="color: #81c784 !important; font-weight: bold !important; font-size: 16px !important; margin-bottom: 5px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">✓ Ready</div>
                    <div style="color: #e3f2fd !important; font-size: 12px !important;">4 agents online</div>
                </div>
            </div>
            
            <div style="margin-top: 20px !important; padding: 15px !important; background-color: #0d47a1 !important; border-radius: 8px !important; border: 2px solid #ffffff !important;">
                <div style="color: white !important; font-weight: bold !important; font-size: 16px !important; margin-bottom: 10px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Data Collection Status:</div>
                <div style="color: #e3f2fd !important; font-size: 14px !important; margin-bottom: 5px !important;">Last weather update: {collector.get('last_weather_update', 'Unknown')}</div>
                <div style="color: #e3f2fd !important; font-size: 14px !important;">Last stock update: {collector.get('last_stock_update', 'Unknown')}</div>
            </div>
        </div>
        """
        
        return html
    
    def _create_weather_chart(self, weather_data: List[Dict]) -> go.Figure:
        """Create weather trend chart."""
        if not weather_data:
            fig = go.Figure()
            fig.add_annotation(
                text="No weather data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(weather_data)
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        fig = go.Figure()
        
        # Temperature line
        if 'temperature' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['timestamp'] if 'timestamp' in df.columns else range(len(df)),
                y=df['temperature'],
                mode='lines+markers',
                name='Temperature (°C)',
                line=dict(color='red', width=2)
            ))
        
        # Humidity line
        if 'humidity' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['timestamp'] if 'timestamp' in df.columns else range(len(df)),
                y=df['humidity'],
                mode='lines+markers',
                name='Humidity (%)',
                line=dict(color='blue', width=2),
                yaxis='y2'
            ))
        
        fig.update_layout(
            title="Recent Weather Trends",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            yaxis2=dict(
                title="Humidity (%)",
                overlaying='y',
                side='right'
            ),
            height=300,
            showlegend=True
        )
        
        return fig
    
    def _create_stock_chart(self, stock_data: List[Dict]) -> go.Figure:
        """Create stock price chart."""
        if not stock_data:
            fig = go.Figure()
            fig.add_annotation(
                text="No stock data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Convert to DataFrame
        df = pd.DataFrame(stock_data)
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        fig = go.Figure()
        
        # Group by symbol and plot each stock
        if 'symbol' in df.columns and 'price' in df.columns:
            symbols = df['symbol'].unique()[:5]  # Limit to 5 stocks
            
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            
            for i, symbol in enumerate(symbols):
                symbol_data = df[df['symbol'] == symbol]
                
                fig.add_trace(go.Scatter(
                    x=symbol_data['timestamp'] if 'timestamp' in symbol_data.columns else range(len(symbol_data)),
                    y=symbol_data['price'],
                    mode='lines+markers',
                    name=symbol,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        
        fig.update_layout(
            title="Recent Stock Prices",
            xaxis_title="Time",
            yaxis_title="Price ($)",
            height=300,
            showlegend=True
        )
        
        return fig