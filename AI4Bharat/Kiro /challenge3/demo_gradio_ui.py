"""Demo script to showcase the Gradio UI without requiring full backend."""

import gradio as gr
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple


# Mock data generators for demonstration
def generate_mock_weather_data():
    """Generate mock weather data for demo."""
    dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
    np.random.seed(42)
    
    data = []
    for date in dates:
        data.append({
            'timestamp': date.isoformat(),
            'location': 'New York',
            'temperature': 20 + 15 * np.sin(2 * np.pi * date.dayofyear / 365) + np.random.normal(0, 3),
            'humidity': 50 + 20 * np.random.random(),
            'pressure': 1013 + np.random.normal(0, 10),
            'weather_condition': np.random.choice(['Sunny', 'Cloudy', 'Rainy', 'Snowy'])
        })
    
    return data


def generate_mock_stock_data():
    """Generate mock stock data for demo."""
    dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
    np.random.seed(42)
    
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    data = []
    
    for symbol in symbols:
        price = 100 + np.random.random() * 100
        for date in dates:
            price += np.random.normal(0, 2)
            price = max(price, 10)  # Ensure positive price
            
            data.append({
                'timestamp': date.isoformat(),
                'symbol': symbol,
                'price': price,
                'volume': np.random.randint(1000000, 10000000),
                'change_percent': np.random.normal(0, 2)
            })
    
    return data


# Mock UI functions
def mock_get_current_data() -> Tuple[str, go.Figure, str, go.Figure, str]:
    """Mock current data retrieval."""
    weather_data = generate_mock_weather_data()[-5:]  # Last 5 days
    stock_data = generate_mock_stock_data()[-20:]  # Last 20 entries
    
    # Weather display - DARK BACKGROUND WITH WHITE TEXT
    current_weather = weather_data[-1]
    weather_html = f"""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                color: white; 
                border: 1px solid #3b82f6; 
                border-radius: 12px; 
                padding: 20px; 
                margin: 10px; 
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
        <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 1.4em;">🌤️ Current Weather - {current_weather['location']}</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 1.1em;">
            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px;">
                <strong style="color: #fbbf24;">Temperature:</strong> {current_weather['temperature']:.1f}°C
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px;">
                <strong style="color: #10b981;">Condition:</strong> {current_weather['weather_condition']}
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px;">
                <strong style="color: #3b82f6;">Humidity:</strong> {current_weather['humidity']:.1f}%
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px;">
                <strong style="color: #f59e0b;">Pressure:</strong> {current_weather['pressure']:.1f} hPa
            </div>
        </div>
    </div>
    """
    
    # Weather chart
    df_weather = pd.DataFrame(weather_data)
    df_weather['timestamp'] = pd.to_datetime(df_weather['timestamp'])
    
    weather_fig = go.Figure()
    weather_fig.add_trace(go.Scatter(
        x=df_weather['timestamp'],
        y=df_weather['temperature'],
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='red', width=2)
    ))
    weather_fig.update_layout(title="Recent Weather Trends", height=300)
    
    # Stock display - GREEN THEME WITH DARK TEXT
    stock_html = f'''
    <div style="background: linear-gradient(135deg, #166534 0%, #15803d 100%); 
                color: white; 
                border: 1px solid #22c55e; 
                border-radius: 12px; 
                padding: 20px; 
                margin: 10px; 
                box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);">
        <h3 style="color: #ffffff; margin: 0 0 20px 0; font-size: 1.4em;">📈 Current Stocks</h3>
    '''
    
    df_stock = pd.DataFrame(stock_data)
    latest_stocks = df_stock.groupby('symbol').last()
    
    for symbol, row in latest_stocks.iterrows():
        change_color = "#22c55e" if row['change_percent'] >= 0 else "#ef4444"
        change_symbol = "+" if row['change_percent'] >= 0 else ""
        
        stock_html += f'''
        <div style="display: flex; justify-content: space-between; 
                    margin: 12px 0; padding: 15px; 
                    background: rgba(255,255,255,0.15); 
                    border-radius: 8px; 
                    border-left: 4px solid {change_color};">
            <span style="font-weight: bold; font-size: 1.1em; color: #ffffff;">{symbol}</span>
            <span style="font-size: 1.2em; font-weight: bold; color: #fef3c7;">${row['price']:.2f}</span>
            <span style="font-weight: bold; color: {change_color}; font-size: 1.1em;">{change_symbol}{row['change_percent']:.2f}%</span>
        </div>
        '''
    
    stock_html += '</div>'
    
    # Stock chart
    stock_fig = go.Figure()
    for symbol in ['AAPL', 'GOOGL', 'MSFT', 'TSLA']:
        symbol_data = df_stock[df_stock['symbol'] == symbol].tail(10)
        symbol_data['timestamp'] = pd.to_datetime(symbol_data['timestamp'])
        
        stock_fig.add_trace(go.Scatter(
            x=symbol_data['timestamp'],
            y=symbol_data['price'],
            mode='lines+markers',
            name=symbol,
            line=dict(width=2)
        ))
    
    stock_fig.update_layout(title="Recent Stock Prices", height=300)
    
    # System status - BLUE THEME WITH WHITE TEXT
    system_html = """
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
                color: white; 
                border: 1px solid #3b82f6; 
                border-radius: 12px; 
                padding: 20px; 
                margin: 10px; 
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
        <h3 style="color: #ffffff; margin: 0 0 20px 0; font-size: 1.4em;">🔧 System Status</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
            <div style="background: rgba(59, 130, 246, 0.2); padding: 20px; border-radius: 10px; text-align: center;">
                <strong style="color: #60a5fa; font-size: 1.1em;">Weather Collection:</strong><br>
                <span style="color: #10b981; font-size: 1.3em; font-weight: bold;">✓ Active</span><br>
                <small style="color: #cbd5e1;">1,250 records</small>
            </div>
            <div style="background: rgba(59, 130, 246, 0.2); padding: 20px; border-radius: 10px; text-align: center;">
                <strong style="color: #60a5fa; font-size: 1.1em;">Stock Collection:</strong><br>
                <span style="color: #10b981; font-size: 1.3em; font-weight: bold;">✓ Active</span><br>
                <small style="color: #cbd5e1;">980 records</small>
            </div>
            <div style="background: rgba(59, 130, 246, 0.2); padding: 20px; border-radius: 10px; text-align: center;">
                <strong style="color: #60a5fa; font-size: 1.1em;">AI Agents:</strong><br>
                <span style="color: #10b981; font-size: 1.3em; font-weight: bold;">✓ Ready</span><br>
                <small style="color: #cbd5e1;">4 agents online</small>
            </div>
        </div>
    </div>
    """
    
    return weather_html, weather_fig, stock_html, stock_fig, system_html


def mock_process_query(query: str) -> Tuple[str, go.Figure]:
    """Mock query processing."""
    if not query.strip():
        return "Please enter a question.", go.Figure()
    
    # Generate mock response - DARK BLUE WITH WHITE TEXT
    response_html = f"""
    <div style="background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%); 
                color: white; 
                border-left: 5px solid #3b82f6; 
                padding: 25px; 
                margin: 15px 0; 
                border-radius: 10px; 
                box-shadow: 0 6px 20px rgba(30, 64, 175, 0.4);">
        <h3 style="color: #ffffff; margin: 0 0 20px 0; font-size: 1.5em;">🔍 Query Results</h3>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin: 20px 0;">
            <strong style="color: #fbbf24; font-size: 1.1em;">Your Question:</strong><br>
            <span style="color: #e0f2fe; font-size: 1.05em;">{query}</span>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin: 20px 0;">
            <strong style="color: #10b981; font-size: 1.1em;">Analysis:</strong><br>
            <span style="color: #e0f2fe;">Based on historical data analysis, there appears to be a moderate correlation between the queried weather patterns and stock performance. The analysis reveals interesting seasonal patterns that may influence market behavior during specific weather conditions.</span>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin: 20px 0;">
            <strong style="color: #f59e0b; font-size: 1.1em;">Key Findings:</strong>
            <ul style="color: #e0f2fe; margin: 15px 0; padding-left: 25px;">
                <li>Correlation coefficient ranges from -0.3 to 0.4 depending on the time period</li>
                <li>Strongest relationships observed during extreme weather events</li>
                <li>Sector-specific variations in weather sensitivity detected</li>
            </ul>
        </div>
    </div>
    """
    
    # Generate mock chart
    np.random.seed(hash(query) % 1000)
    x_data = np.random.normal(20, 5, 100)
    y_data = 150 + 2 * x_data + np.random.normal(0, 15, 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        name='Weather vs Stock Correlation',
        marker=dict(size=8, color=y_data, colorscale='Viridis', showscale=True)
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
    
    correlation = np.corrcoef(x_data, y_data)[0, 1]
    fig.update_layout(
        title=f"Correlation Analysis<br><sub>Correlation: {correlation:.3f}</sub>",
        xaxis_title="Weather Variable",
        yaxis_title="Stock Price ($)",
        height=400
    )
    
    return response_html, fig


def mock_generate_insights() -> Tuple[str, go.Figure]:
    """Mock insights generation."""
    insights_html = """
    <div style="background: linear-gradient(135deg, #7c2d12 0%, #dc2626 100%); 
                color: white; 
                border-left: 5px solid #f97316; 
                padding: 25px; 
                margin: 15px 0; 
                border-radius: 10px; 
                box-shadow: 0 6px 20px rgba(124, 45, 18, 0.4);">
        <h3 style="color: #ffffff; margin: 0 0 25px 0; font-size: 1.5em;">🧠 AI-Generated Correlation Insights</h3>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin: 25px 0;">
            <h4 style="color: #fbbf24; margin: 0 0 15px 0;">🔍 Key Findings:</h4>
            <div style="color: #fef3c7; line-height: 1.6;">
                • <strong style="color: #f59e0b;">Temperature</strong> shows moderate negative correlation (-0.23) with energy sector stocks during summer months<br>
                • <strong style="color: #f59e0b;">High humidity</strong> periods correlate with increased volatility in agricultural commodity stocks<br>
                • <strong style="color: #f59e0b;">Atmospheric pressure</strong> changes precede market volatility spikes by 2-3 days on average<br>
                • <strong style="color: #f59e0b;">AAPL:</strong> Weather sensitivity primarily during product launch seasons (correlation: 0.15)
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin: 25px 0; display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <h5 style="color: #34d399; margin: 0 0 15px 0;">📊 Statistical Summary:</h5>
                <div style="color: #fef3c7; font-size: 1.05em;">
                    <strong>Average Correlation:</strong> <span style="color: #f59e0b;">-0.127</span><br>
                    <strong>Strongest Positive:</strong> <span style="color: #10b981;">0.456</span><br>
                    <strong>Strongest Negative:</strong> <span style="color: #ef4444;">-0.389</span>
                </div>
            </div>
            <div>
                <h5 style="color: #34d399; margin: 0 0 15px 0;">📈 Analysis Details:</h5>
                <div style="color: #fef3c7; font-size: 1.05em;">
                    <strong>Significant Pairs:</strong> <span style="color: #10b981;">6</span><br>
                    <strong>Total Comparisons:</strong> <span style="color: #f59e0b;">16</span><br>
                    <strong>Confidence Level:</strong> <span style="color: #3b82f6;">95%</span>
                </div>
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; margin: 25px 0;">
            <h4 style="color: #10b981; margin: 0 0 15px 0;">💡 Insights & Recommendations:</h4>
            <div style="color: #fef3c7; line-height: 1.6; font-size: 1.05em;">
                • <strong style="color: #fbbf24;">Consider</strong> weather data as a supplementary indicator for short-term trading strategies<br>
                • <strong style="color: #fbbf24;">Focus</strong> on sector-specific weather relationships rather than broad market correlations<br>
                • <strong style="color: #fbbf24;">Monitor</strong> extreme weather events for potential volatility opportunities
            </div>
        </div>
    </div>
    """
    
    # Generate correlation heatmap
    variables = ['Temperature', 'Humidity', 'AAPL', 'GOOGL', 'MSFT']
    n_vars = len(variables)
    
    np.random.seed(42)
    correlation_matrix = np.random.rand(n_vars, n_vars)
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix, 1.0)
    correlation_matrix = (correlation_matrix - 0.5) * 0.8
    np.fill_diagonal(correlation_matrix, 1.0)
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=variables,
        y=variables,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=np.round(correlation_matrix, 3),
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Weather-Stock Correlation Matrix",
        height=400,
        width=500
    )
    
    return insights_html, fig


# Create the demo Gradio app
def create_demo_app():
    """Create demo Gradio application."""
    
    with gr.Blocks(
        title="Weather Stock Dashboard - Demo",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container { max-width: 1200px !important; }
        .status-healthy { color: #10b981 !important; font-weight: bold; }
        """
    ) as app:
        
        # Header
        gr.Markdown("# 🌤️📈 Weather Stock Dashboard - Demo")
        gr.Markdown("*Explore correlations between weather patterns and stock market performance*")
        gr.Markdown("**Note:** This is a demo version with mock data. The full version connects to live APIs.")
        
        # Main tabs
        with gr.Tabs():
            
            # Dashboard tab
            with gr.Tab("📊 Dashboard"):
                gr.Markdown("## Real-time Weather & Stock Data")
                
                refresh_btn = gr.Button("🔄 Refresh Data", variant="primary")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🌤️ Current Weather")
                        weather_display = gr.HTML()
                        weather_chart = gr.Plot()
                    
                    with gr.Column():
                        gr.Markdown("### 📈 Current Stocks")
                        stock_display = gr.HTML()
                        stock_chart = gr.Plot()
                
                gr.Markdown("### 🔧 System Status")
                system_status = gr.HTML()
                
                # Load initial data
                refresh_btn.click(
                    fn=mock_get_current_data,
                    outputs=[weather_display, weather_chart, stock_display, stock_chart, system_status]
                )
                
                # Load data on startup
                app.load(
                    fn=mock_get_current_data,
                    outputs=[weather_display, weather_chart, stock_display, stock_chart, system_status]
                )
            
            # Query tab
            with gr.Tab("💬 Query Interface"):
                gr.Markdown("## Natural Language Query Interface")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        query_input = gr.Textbox(
                            placeholder="e.g., 'How does temperature affect Apple stock prices?'",
                            label="Your Question",
                            lines=3
                        )
                    
                        with gr.Row():
                            submit_query = gr.Button("🔍 Ask", variant="primary")
                            clear_query = gr.Button("🗑️ Clear")
                        
                        gr.Markdown("### 💡 Example Questions")
                        examples = [
                            "What's the correlation between rainfall and retail stocks?",
                            "How do temperature changes affect energy sector performance?",
                            "Show me weather patterns during market volatility periods"
                        ]
                        
                        for example in examples:
                            example_btn = gr.Button(f"📝 {example}", size="sm")
                            example_btn.click(lambda ex=example: ex, outputs=[query_input])
                    
                    with gr.Column():
                        query_results = gr.HTML()
                        query_chart = gr.Plot()
                
                submit_query.click(
                    fn=mock_process_query,
                    inputs=[query_input],
                    outputs=[query_results, query_chart]
                )
                
                clear_query.click(lambda: "", outputs=[query_input])
            
            # Insights tab
            with gr.Tab("🔍 Insights"):
                gr.Markdown("## AI-Generated Correlation Insights")
                
                generate_btn = gr.Button("🧠 Generate Insights", variant="primary")
                
                with gr.Row():
                    insights_display = gr.HTML()
                    correlation_matrix = gr.Plot()
                
                generate_btn.click(
                    fn=mock_generate_insights,
                    outputs=[insights_display, correlation_matrix]
                )
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("*Weather Stock Dashboard - AI-powered correlation analysis between meteorological conditions and financial markets*")
    
    return app


if __name__ == "__main__":
    demo_app = create_demo_app()
    demo_app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        debug=True
    )
