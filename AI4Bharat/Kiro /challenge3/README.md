# Weather Stock Dashboard

An AI-powered dashboard that correlates weather patterns with stock market performance to identify interesting relationships and insights.

## Features

- **Real-time Data Integration**: Continuous collection of weather and stock market data
- **AI-Powered Analysis**: CrewAI agents for intelligent correlation analysis
- **Natural Language Queries**: LangChain RAG engine for intuitive data exploration
- **Time Series Modeling**: ARIMA and GARCH models for forecasting and volatility analysis
- **Interactive Dashboard**: Gradio-based web interface with real-time visualizations
- **Vector Search**: ChromaDB for semantic search across historical patterns
- **Comprehensive UI**: Multi-tab interface with dashboard, visualizations, queries, and insights

## Architecture

The system employs a microservices architecture with:

- **FastAPI Backend**: RESTful API for data access and analysis
- **CrewAI Agents**: Autonomous agents for data validation, analysis, and insight generation
- **ChromaDB Vector Store**: Semantic storage and retrieval of weather-stock correlations
- **LangChain RAG**: Natural language processing for user queries
- **Gradio UI**: Interactive web interface for data exploration
- **MCP Servers**: Standardized data collection from external APIs

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd weather-stock-dashboard
   ```

2. **Create a Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## Configuration

Copy `.env.example` to `.env` and configure the following:

### Required API Keys
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key
- `ALPHA_VANTAGE_API_KEY`: Alpha Vantage API key for stock data
- `OPENAI_API_KEY`: OpenAI API key for AI agents

### Optional Configuration
- Database settings (ChromaDB, Redis)
- Data collection intervals
- Time series analysis parameters
- UI configuration

## Usage

### Start the API Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Start the Complete Application
```bash
# Start both FastAPI backend and Gradio frontend
python weather_stock_dashboard/ui/launcher.py
```

### Start Components Separately

**FastAPI Backend Only:**
```bash
python main.py
# Available at http://localhost:8000
```

**Gradio Frontend Only:**
```bash
python weather_stock_dashboard/ui/app.py
# Available at http://localhost:7860
```

**Demo Version (No Backend Required):**
```bash
python demo_gradio_ui.py
# Runs with mock data for demonstration
```

### API Endpoints

- `GET /`: Root endpoint with system status
- `GET /health`: Health check
- `GET /api/status`: API status
- `GET /api/dashboard/current`: Current dashboard data
- `POST /api/query/natural`: Natural language queries
- `GET /api/insights/correlations`: AI-generated insights

## Development

### Project Structure
```
weather_stock_dashboard/
├── agents/          # CrewAI agents
├── api/            # FastAPI routes and endpoints
├── models/         # Pydantic data models
├── mcp_servers/    # MCP server implementations
├── services/       # Core business logic
├── ui/             # Gradio interface components
│   ├── app.py      # Main Gradio application
│   ├── launcher.py # Application launcher
│   └── components/ # UI component modules
└── utils/          # Utility functions

config/             # Configuration management
tests/              # Test suite
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
mypy .
```

## Time Series Analysis

The system implements sophisticated time series modeling:

- **ARIMA Models**: Forecasting weather patterns and stock prices
- **GARCH Models**: Volatility analysis and clustering
- **Cross-Correlation**: Identifying optimal lag relationships
- **Granger Causality**: Testing predictive relationships
- **VAR Models**: Multivariate time series analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Requirements

- Python 3.9+
- API keys for weather and stock data sources
- Redis (optional, for caching)
- ChromaDB (for vector storage)