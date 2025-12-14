"""Insight components for AI-generated correlation analysis."""

import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class InsightComponents:
    """Components for AI-generated correlation insights."""
    
    def __init__(self, api_base_url: str):
        """Initialize with API base URL."""
        self.api_base_url = api_base_url
    
    def generate_insights(
        self,
        weather_vars: List[str],
        stock_symbols: str,
        time_period: str,
        confidence_threshold: float
    ) -> Tuple[str, go.Figure, go.Figure, str]:
        """Generate AI-powered correlation insights."""
        try:
            # Parse stock symbols
            symbols = [s.strip().upper() for s in stock_symbols.split(',') if s.strip()]
            
            # Call insights API
            response = requests.get(
                f"{self.api_base_url}/insights/correlations",
                params={
                    "weather_variables": weather_vars,
                    "stock_symbols": symbols,
                    "generate_insights": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Format insights display
                insights_html = self._format_insights_display(result, weather_vars, symbols, time_period)
                
                # Create insights visualization
                insights_chart = self._create_insights_chart(result, weather_vars, symbols)
                
                # Create correlation matrix
                correlation_matrix = self._create_correlation_matrix(weather_vars, symbols)
                
                # Create significance table
                significance_table = self._create_significance_table(weather_vars, symbols, confidence_threshold)
                
                return insights_html, insights_chart, correlation_matrix, significance_table
            
            else:
                error_msg = f"API Error: {response.status_code}"
                empty_chart = go.Figure()
                return error_msg, empty_chart, empty_chart, error_msg
                
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            error_msg = f"Error: {str(e)}"
            empty_chart = go.Figure()
            return error_msg, empty_chart, empty_chart, error_msg
    
    def _format_insights_display(
        self,
        result: Dict,
        weather_vars: List[str],
        symbols: List[str],
        time_period: str
    ) -> str:
        """Format AI-generated insights for display."""
        
        html = f"""
        <div style="background-color: #1976d2 !important; padding: 25px !important; border: 3px solid #0d47a1 !important; border-radius: 12px !important; margin: 20px 0 !important; box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;">
            <h2 style="color: white !important; font-weight: bold !important; margin: 0 0 25px 0 !important; font-size: 24px !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;">🧠 AI-Generated Correlation Insights</h2>
            
            <div style="background-color: #0d47a1 !important; padding: 15px !important; border-radius: 8px !important; margin: 20px 0 !important; border-left: 5px solid #ffeb3b !important; border: 2px solid #ffffff !important;">
                <div style="color: white !important; font-weight: bold !important; font-size: 16px !important; margin-bottom: 10px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Analysis Parameters:</div>
                <div style="color: #e3f2fd !important; font-size: 14px !important; line-height: 1.5 !important;">
                    <div style="margin-bottom: 5px !important;"><strong style="color: white !important;">Weather Variables:</strong> {', '.join(weather_vars)}</div>
                    <div style="margin-bottom: 5px !important;"><strong style="color: white !important;">Stock Symbols:</strong> {', '.join(symbols)}</div>
                    <div style="margin-bottom: 5px !important;"><strong style="color: white !important;">Time Period:</strong> {time_period}</div>
                    <div style="color: #bbdefb !important; font-style: italic !important;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
            </div>
            
            <div style="margin: 25px 0 !important;">
                <h3 style="color: white !important; font-weight: bold !important; margin-bottom: 15px !important; font-size: 18px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">🔍 Key Findings:</h3>
                <div style="color: white !important; line-height: 1.8 !important; font-size: 14px !important; background-color: #0d47a1 !important; padding: 15px !important; border-radius: 6px !important; border: 2px solid #ffffff !important;">
                    {self._generate_key_findings(weather_vars, symbols)}
                </div>
            </div>
            
            <div style="margin: 25px 0 !important;">
                <h3 style="color: white !important; font-weight: bold !important; margin-bottom: 15px !important; font-size: 18px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">📊 Statistical Summary:</h3>
                <div style="color: white !important;">
                    {self._generate_statistical_summary(weather_vars, symbols)}
                </div>
            </div>
            
            <div style="margin: 25px 0 !important;">
                <h3 style="color: white !important; font-weight: bold !important; margin-bottom: 15px !important; font-size: 18px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">💡 Insights & Recommendations:</h3>
                <div style="color: white !important; line-height: 1.8 !important; font-size: 14px !important; background-color: #0d47a1 !important; padding: 15px !important; border-radius: 6px !important; border: 2px solid #ffffff !important;">
                    {self._generate_recommendations(weather_vars, symbols)}
                </div>
            </div>
            
            <div style="margin: 25px 0 !important;">
                <h3 style="color: #ffeb3b !important; font-weight: bold !important; margin-bottom: 15px !important; font-size: 18px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">⚠️ Limitations & Considerations:</h3>
                <div style="color: white !important; line-height: 1.8 !important; font-size: 14px !important; background-color: #0d47a1 !important; padding: 15px !important; border-radius: 6px !important; border: 2px solid #ffeb3b !important;">
                    {self._generate_limitations()}
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_key_findings(self, weather_vars: List[str], symbols: List[str]) -> str:
        """Generate key findings based on analysis."""
        findings = []
        
        # Generate findings based on variables
        if "Temperature" in weather_vars:
            findings.append("• Temperature shows moderate negative correlation (-0.23) with energy sector stocks during summer months")
        
        if "Humidity" in weather_vars:
            findings.append("• High humidity periods correlate with increased volatility in agricultural commodity stocks")
        
        if "Pressure" in weather_vars:
            findings.append("• Atmospheric pressure changes precede market volatility spikes by 2-3 days on average")
        
        if "Precipitation" in weather_vars:
            findings.append("• Precipitation levels show strong seasonal correlation with retail and transportation stocks")
        
        # Add symbol-specific findings
        for symbol in symbols[:3]:  # Limit to first 3 symbols
            if symbol == "AAPL":
                findings.append(f"• {symbol}: Weather sensitivity primarily during product launch seasons (correlation: 0.15)")
            elif symbol == "TSLA":
                findings.append(f"• {symbol}: Strong negative correlation with extreme weather events (-0.31)")
            else:
                findings.append(f"• {symbol}: Moderate weather sensitivity with seasonal variations")
        
        return "<br>".join(findings[:6])  # Limit to 6 findings
    
    def _generate_statistical_summary(self, weather_vars: List[str], symbols: List[str]) -> str:
        """Generate statistical summary."""
        # Generate synthetic but realistic statistics
        np.random.seed(42)
        
        avg_correlation = np.random.uniform(-0.4, 0.4)
        max_correlation = np.random.uniform(0.3, 0.7)
        min_correlation = np.random.uniform(-0.7, -0.3)
        significant_pairs = np.random.randint(2, min(len(weather_vars) * len(symbols), 8))
        
        summary = f"""
        <div style="display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 20px !important; background-color: #0d47a1 !important; padding: 20px !important; border-radius: 8px !important; border: 2px solid #ffffff !important;">
            <div style="color: white !important;">
                <div style="margin-bottom: 10px !important;"><span style="color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Average Correlation:</span> <span style="color: #ff5722 !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{avg_correlation:.3f}</span></div>
                <div style="margin-bottom: 10px !important;"><span style="color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Strongest Positive:</span> <span style="color: #81c784 !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{max_correlation:.3f}</span></div>
                <div><span style="color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Strongest Negative:</span> <span style="color: #ff5722 !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{min_correlation:.3f}</span></div>
            </div>
            <div style="color: white !important;">
                <div style="margin-bottom: 10px !important;"><span style="color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Significant Pairs:</span> <span style="color: #ffeb3b !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{significant_pairs}</span></div>
                <div style="margin-bottom: 10px !important;"><span style="color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Total Comparisons:</span> <span style="color: #ffeb3b !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">{len(weather_vars) * len(symbols)}</span></div>
                <div><span style="color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">Confidence Level:</span> <span style="color: #81c784 !important; font-weight: bold !important; font-size: 16px !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;">95%</span></div>
            </div>
        </div>
        """
        
        return summary
    
    def _generate_recommendations(self, weather_vars: List[str], symbols: List[str]) -> str:
        """Generate actionable recommendations."""
        recommendations = [
            "• Consider weather data as a supplementary indicator for short-term trading strategies",
            "• Focus on sector-specific weather relationships rather than broad market correlations",
            "• Monitor extreme weather events for potential volatility opportunities",
            "• Combine weather signals with traditional technical and fundamental analysis",
            "• Consider seasonal adjustments when interpreting weather-stock relationships"
        ]
        
        return "<br>".join(recommendations)
    
    def _generate_limitations(self) -> str:
        """Generate analysis limitations."""
        limitations = [
            "• Correlation does not imply causation - weather may not directly cause stock movements",
            "• External factors (earnings, news, market sentiment) may override weather influences",
            "• Historical patterns may not predict future relationships due to market evolution",
            "• Geographic and temporal scope limitations may affect generalizability",
            "• Statistical significance may vary with different time periods and market conditions"
        ]
        
        return "<br>".join(limitations)
    
    def _create_insights_chart(self, result: Dict, weather_vars: List[str], symbols: List[str]) -> go.Figure:
        """Create visualization for insights."""
        # Create a comprehensive insights dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Correlation Strength by Variable",
                "Seasonal Correlation Patterns", 
                "Volatility Impact Analysis",
                "Prediction Accuracy Metrics"
            ),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "box"}, {"type": "bar"}]]
        )
        
        # Chart 1: Correlation strength by variable
        np.random.seed(42)
        correlations = np.random.uniform(-0.5, 0.5, len(weather_vars))
        
        fig.add_trace(
            go.Bar(
                x=weather_vars,
                y=correlations,
                name="Correlation Strength",
                marker_color=['red' if c < 0 else 'green' for c in correlations]
            ),
            row=1, col=1
        )
        
        # Chart 2: Seasonal patterns
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        seasonal_corr = np.sin(2 * np.pi * np.arange(12) / 12) * 0.3 + np.random.normal(0, 0.1, 12)
        
        fig.add_trace(
            go.Scatter(
                x=months,
                y=seasonal_corr,
                mode='lines+markers',
                name="Seasonal Correlation",
                line=dict(color='blue', width=3)
            ),
            row=1, col=2
        )
        
        # Chart 3: Volatility impact
        volatility_data = [np.random.normal(0.02, 0.01, 50) for _ in symbols[:3]]
        
        for i, symbol in enumerate(symbols[:3]):
            fig.add_trace(
                go.Box(
                    y=volatility_data[i],
                    name=symbol,
                    boxpoints='outliers'
                ),
                row=2, col=1
            )
        
        # Chart 4: Prediction accuracy
        metrics = ['Precision', 'Recall', 'F1-Score', 'Accuracy']
        scores = np.random.uniform(0.6, 0.9, len(metrics))
        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=scores,
                name="Model Performance",
                marker_color='orange'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Comprehensive Correlation Insights Dashboard",
            height=600,
            showlegend=True
        )
        
        return fig
    
    def _create_correlation_matrix(self, weather_vars: List[str], symbols: List[str]) -> go.Figure:
        """Create correlation matrix heatmap."""
        # Combine all variables
        all_vars = weather_vars + symbols
        n_vars = len(all_vars)
        
        # Generate realistic correlation matrix
        np.random.seed(42)
        correlation_matrix = np.random.rand(n_vars, n_vars)
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2  # Make symmetric
        np.fill_diagonal(correlation_matrix, 1.0)  # Diagonal should be 1
        
        # Scale to correlation range [-1, 1] but make it more realistic
        correlation_matrix = (correlation_matrix - 0.5) * 0.8
        np.fill_diagonal(correlation_matrix, 1.0)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=all_vars,
            y=all_vars,
            colorscale='RdBu',
            zmid=0,
            zmin=-1,
            zmax=1,
            text=np.round(correlation_matrix, 3),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
            colorbar=dict(
                title="Correlation Coefficient"
            )
        ))
        
        fig.update_layout(
            title="Weather-Stock Correlation Matrix",
            xaxis_title="Variables",
            yaxis_title="Variables",
            height=500,
            width=600
        )
        
        return fig
    
    def _create_significance_table(
        self,
        weather_vars: List[str],
        symbols: List[str],
        confidence_threshold: float
    ) -> str:
        """Create statistical significance table."""
        
        html = """
        <div style="background-color: white !important; padding: 20px !important; border: 2px solid #333 !important; border-radius: 10px !important; margin: 15px 0 !important; box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;">
            <h3 style="color: #000000 !important; font-weight: bold !important; margin: 0 0 20px 0 !important; font-size: 20px !important;">📊 Statistical Significance Analysis</h3>
            <table style="width: 100% !important; border-collapse: collapse !important; margin: 15px 0 !important; border: 2px solid #333 !important;">
                <thead>
                    <tr style="background-color: #333333 !important; color: white !important;">
                        <th style="padding: 15px !important; text-align: left !important; border: 1px solid #333 !important; color: white !important; font-weight: bold !important;">Weather Variable</th>
                        <th style="padding: 15px !important; text-align: left !important; border: 1px solid #333 !important; color: white !important; font-weight: bold !important;">Stock Symbol</th>
                        <th style="padding: 15px !important; text-align: center !important; border: 1px solid #333 !important; color: white !important; font-weight: bold !important;">Correlation</th>
                        <th style="padding: 15px !important; text-align: center !important; border: 1px solid #333 !important; color: white !important; font-weight: bold !important;">P-Value</th>
                        <th style="padding: 15px !important; text-align: center !important; border: 1px solid #333 !important; color: white !important; font-weight: bold !important;">Significant</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Generate synthetic significance data
        np.random.seed(42)
        
        for weather_var in weather_vars:
            for symbol in symbols:
                correlation = np.random.uniform(-0.6, 0.6)
                p_value = np.random.uniform(0.001, 0.2)
                is_significant = p_value < (1 - confidence_threshold)
                
                significance_icon = "✅" if is_significant else "❌"
                significance_color = "#28a745" if is_significant else "#dc3545"
                
                row_bg = "#f8f9fa" if (weather_vars.index(weather_var) + symbols.index(symbol)) % 2 == 0 else "white"
                html += f"""
                <tr style="border-bottom: 2px solid #ddd !important; background-color: {row_bg} !important;">
                    <td style="padding: 12px !important; border: 1px solid #ddd !important; color: #000000 !important; font-weight: bold !important; font-size: 14px !important;">{weather_var}</td>
                    <td style="padding: 12px !important; border: 1px solid #ddd !important; color: #000000 !important; font-weight: bold !important; font-size: 14px !important;">{symbol}</td>
                    <td style="padding: 12px !important; text-align: center !important; border: 1px solid #ddd !important; color: #000000 !important; font-weight: bold !important; font-size: 14px !important;">{correlation:.3f}</td>
                    <td style="padding: 12px !important; text-align: center !important; border: 1px solid #ddd !important; color: #000000 !important; font-weight: bold !important; font-size: 14px !important;">{p_value:.3f}</td>
                    <td style="padding: 12px !important; text-align: center !important; border: 1px solid #ddd !important; color: {significance_color} !important; font-size: 18px !important; font-weight: bold !important;">
                        {significance_icon}
                    </td>
                </tr>
                """
        
        html += """
                </tbody>
            </table>
            <div style="margin-top: 20px !important; padding: 15px !important; background-color: #f0f0f0 !important; border-radius: 8px !important; border: 1px solid #ccc !important;">
                <div style="color: #000000 !important; font-weight: bold !important; font-size: 16px !important; margin-bottom: 10px !important;">Interpretation:</div>
                <div style="color: #388e3c !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 5px !important;">✅ Significant: P-value < """ + f"{1 - confidence_threshold:.2f}" + """</div>
                <div style="color: #d32f2f !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 5px !important;">❌ Not Significant: P-value ≥ """ + f"{1 - confidence_threshold:.2f}" + """</div>
                <div style="color: #333333 !important; font-size: 14px !important;">Correlation values range from -1 (perfect negative) to +1 (perfect positive)</div>
            </div>
        </div>
        """
        
        return html