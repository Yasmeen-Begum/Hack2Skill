# Weather Stock Dashboard - Gradio UI

This directory contains the Gradio-based web interface for the Weather Stock Dashboard application.

## Overview

The Gradio UI provides an intuitive web interface for exploring correlations between weather patterns and stock market performance. It features interactive visualizations, natural language query processing, and AI-generated insights.

## Architecture

### Main Components

1. **`app.py`** - Main Gradio application with dashboard layout and navigation
2. **`components/`** - Modular UI components for different functionality areas
3. **`launcher.py`** - Application launcher that runs both FastAPI backend and Gradio frontend

### Component Structure

```
ui/
├── __init__.py
├── app.py                 # Main Gradio application
├── launcher.py            # Application launcher
├── components/
│   ├── __init__.py
│   ├── dashboard.py       # Real-time dashboard components
│   ├── visualization.py   # Interactive charts and time series analysis
│   ├── query.py          # Natural language query interface
│   └── insights.py       # AI-generated correlation insights
└── README.md
```

## Features

### 1. Real-time Dashboard (`dashboard.py`)
- **Current Weather Display**: Live weather data with location, temperature, humidity, pressure
- **Current Stock Display**: Real-time stock prices with change indicators
- **System Status**: Health monitoring for data collection and AI agents
- **Interactive Charts**: Time series plots for weather and stock trends
- **Auto-refresh**: Configurable automatic data updates

### 2. Data Visualization (`visualization.py`)
- **Chart Types**: Time series, correlation heatmaps, scatter plots, distributions
- **Data Sources**: Weather data, stock data, or combined analysis
- **Time Series Modeling**: ARIMA/GARCH model fitting and forecasting
- **Interactive Controls**: Date ranges, variable selection, model parameters
- **Model Diagnostics**: Residual analysis and forecast accuracy metrics

### 3. Natural Language Queries (`query.py`)
- **Query Input**: Natural language question processing
- **Query History**: Track and revisit previous questions
- **Example Queries**: Pre-built questions for common use cases
- **Smart Visualization**: Automatic chart generation based on query content
- **Context-aware Responses**: Detailed explanations with supporting data

### 4. AI-Generated Insights (`insights.py`)
- **Correlation Analysis**: Statistical correlation between weather and stocks
- **Significance Testing**: P-values and confidence intervals
- **Key Findings**: AI-generated summaries of important relationships
- **Recommendations**: Actionable insights for trading strategies
- **Limitations**: Clear explanations of analysis constraints

## Usage

### Running the Full Application

```bash
# Start both backend and frontend
python weather_stock_dashboard/ui/launcher.py
```

This will start:
- FastAPI backend on `http://localhost:8000`
- Gradio frontend on `http://localhost:7860`

### Running Demo Version

```bash
# Run demo with mock data (no backend required)
python demo_gradio_ui.py
```

### Running Gradio Only

```bash
# Start just the Gradio interface
python weather_stock_dashboard/ui/app.py
```

## API Integration

The Gradio interface communicates with the FastAPI backend through REST API calls:

### Key Endpoints Used

- `GET /api/dashboard/current` - Real-time dashboard data
- `POST /api/query/natural` - Natural language query processing
- `GET /api/insights/correlations` - AI-generated correlation insights
- `POST /api/timeseries/forecast` - Time series forecasting
- `GET /api/data/historical` - Historical data retrieval

### Error Handling

The UI includes comprehensive error handling:
- **API Connection Errors**: Graceful degradation with error messages
- **Data Validation**: Input validation with user-friendly feedback
- **Timeout Handling**: Appropriate timeouts for long-running operations
- **Fallback Responses**: Mock data when backend is unavailable

## Customization

### Themes and Styling

The interface uses Gradio's Soft theme with custom CSS:

```python
theme = gr.themes.Soft()
css = """
.gradio-container { max-width: 1200px !important; }
.status-healthy { color: #28a745; font-weight: bold; }
.metric-card { background: #f8f9fa; border: 1px solid #dee2e6; }
"""
```

### Adding New Components

To add new UI components:

1. Create a new component class in `components/`
2. Import and initialize in `app.py`
3. Add new tab or section to the main interface
4. Connect to appropriate API endpoints

### Configuration

The UI can be configured through environment variables or the launcher:

```python
launcher = DashboardLauncher(
    api_host="127.0.0.1",
    api_port=8000,
    ui_host="127.0.0.1", 
    ui_port=7860,
    debug=True
)
```

## Testing

UI components are tested in `tests/test_ui_components.py`:

```bash
# Run UI tests
python -m pytest tests/test_ui_components.py -v
```

Tests cover:
- Component initialization
- API integration with mocked responses
- Error handling scenarios
- Chart generation functionality

## Dependencies

Key dependencies for the UI:

- **gradio**: Web interface framework
- **plotly**: Interactive charts and visualizations
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **requests**: HTTP client for API calls

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Charts generated on-demand
2. **Caching**: API responses cached where appropriate
3. **Pagination**: Large datasets handled with limits
4. **Async Operations**: Non-blocking API calls
5. **Error Boundaries**: Isolated component failures

### Resource Management

- **Memory**: Efficient data structures and cleanup
- **Network**: Request throttling and connection pooling
- **CPU**: Optimized chart rendering and calculations

## Deployment

### Production Deployment

For production deployment:

1. Set appropriate host/port configurations
2. Enable HTTPS for secure connections
3. Configure reverse proxy (nginx/Apache)
4. Set up monitoring and logging
5. Implement authentication if required

### Docker Deployment

```dockerfile
# Example Dockerfile snippet
COPY weather_stock_dashboard/ui/ /app/ui/
EXPOSE 7860
CMD ["python", "/app/ui/launcher.py"]
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Change default ports in launcher
2. **API Connection**: Verify backend is running and accessible
3. **Missing Dependencies**: Install requirements.txt
4. **Browser Compatibility**: Use modern browsers with JavaScript enabled

### Debug Mode

Enable debug mode for detailed error information:

```python
app.launch(debug=True, show_error=True)
```

## Future Enhancements

Planned improvements:

1. **Real-time Updates**: WebSocket connections for live data
2. **User Authentication**: Login and session management
3. **Custom Dashboards**: User-configurable layouts
4. **Export Features**: Download charts and reports
5. **Mobile Optimization**: Responsive design improvements
6. **Advanced Analytics**: More sophisticated statistical tools

## Contributing

When contributing to the UI:

1. Follow the component-based architecture
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure responsive design principles
5. Test across different browsers and devices