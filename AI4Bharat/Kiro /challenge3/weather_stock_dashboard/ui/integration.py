"""UI integration service for enhanced backend connectivity."""

import asyncio
import json
import logging
import websockets
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class UIIntegrationService:
    """Service for managing UI-backend integration with enhanced connectivity."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api"):
        """Initialize UI integration service."""
        self.api_base_url = api_base_url
        self.websocket_url = api_base_url.replace("http", "ws") + "/ws"
        
        # HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # WebSocket connection
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._websocket_task: Optional[asyncio.Task] = None
        self._is_connected = False
        
        # Callbacks for real-time updates
        self._update_callbacks: Dict[str, Callable] = {}
    
    async def connect_websocket(self):
        """Connect to WebSocket for real-time updates."""
        try:
            self._websocket = await websockets.connect(self.websocket_url)
            self._is_connected = True
            
            # Start WebSocket message handler
            self._websocket_task = asyncio.create_task(self._websocket_handler())
            
            # Subscribe to relevant topics
            await self._subscribe_to_topics()
            
            logger.info("WebSocket connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            self._is_connected = False
    
    async def disconnect_websocket(self):
        """Disconnect WebSocket."""
        if self._websocket_task:
            self._websocket_task.cancel()
            try:
                await self._websocket_task
            except asyncio.CancelledError:
                pass
        
        if self._websocket:
            await self._websocket.close()
        
        self._is_connected = False
        logger.info("WebSocket disconnected")
    
    def register_update_callback(self, update_type: str, callback: Callable):
        """Register a callback for real-time updates."""
        self._update_callbacks[update_type] = callback
        logger.info(f"Registered callback for update type: {update_type}")
    
    async def _websocket_handler(self):
        """Handle incoming WebSocket messages."""
        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    await self._handle_websocket_message(data)
                except json.JSONDecodeError:
                    logger.error("Received invalid JSON from WebSocket")
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            self._is_connected = False
    
    async def _handle_websocket_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        message_type = data.get("type")
        
        if message_type in self._update_callbacks:
            try:
                callback = self._update_callbacks[message_type]
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in update callback for {message_type}: {e}")
    
    async def _subscribe_to_topics(self):
        """Subscribe to WebSocket topics."""
        topics = ["system_updates", "data_updates", "agent_updates", "task_updates"]
        
        for topic in topics:
            await self._send_websocket_message({
                "type": "subscribe",
                "topic": topic
            })
    
    async def _send_websocket_message(self, message: Dict[str, Any]):
        """Send message to WebSocket."""
        if self._websocket and self._is_connected:
            try:
                await self._websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
    
    # Enhanced HTTP methods with error handling
    
    def get(self, endpoint: str, params: Optional[Dict] = None, timeout: int = 10) -> Dict[str, Any]:
        """Enhanced GET request with error handling."""
        try:
            url = f"{self.api_base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            return {"error": "Request timeout", "success": False}
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {endpoint}")
            return {"error": "Connection error - backend may be offline", "success": False}
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {e}")
            return {"error": f"HTTP error: {e}", "success": False}
        
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {e}")
            return {"error": f"Unexpected error: {e}", "success": False}
    
    def post(self, endpoint: str, data: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """Enhanced POST request with error handling."""
        try:
            url = f"{self.api_base_url}{endpoint}"
            response = self.session.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            return {"error": "Request timeout", "success": False}
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {endpoint}")
            return {"error": "Connection error - backend may be offline", "success": False}
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {e}")
            return {"error": f"HTTP error: {e}", "success": False}
        
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {e}")
            return {"error": f"Unexpected error: {e}", "success": False}
    
    # Specialized API methods
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return self.get("/status")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return self.get("/dashboard/current")
    
    def get_historical_data(self, data_type: str, limit: int = 100) -> Dict[str, Any]:
        """Get historical data."""
        return self.get("/data/historical", params={"data_type": data_type, "limit": limit})
    
    def process_natural_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process natural language query."""
        return self.post("/query/natural", {"query": query, "user_id": user_id})
    
    def get_correlation_insights(
        self, 
        weather_variables: list, 
        stock_symbols: list, 
        generate_insights: bool = True
    ) -> Dict[str, Any]:
        """Get AI-generated correlation insights."""
        params = {
            "weather_variables": weather_variables,
            "stock_symbols": stock_symbols,
            "generate_insights": generate_insights
        }
        return self.get("/insights/correlations", params=params)
    
    def create_forecast(
        self, 
        data_type: str, 
        series_id: str, 
        forecast_horizon: int = 30
    ) -> Dict[str, Any]:
        """Create time series forecast."""
        data = {
            "data_type": data_type,
            "series_id": series_id,
            "forecast_horizon": forecast_horizon
        }
        return self.post("/timeseries/forecast", data)
    
    def fit_arima_model(self, series_data: list, value_column: str) -> Dict[str, Any]:
        """Fit ARIMA model to time series data."""
        data = {
            "series_data": series_data,
            "value_column": value_column
        }
        return self.post("/models/arima", data)
    
    def fit_garch_model(self, stock_data: list, symbol: str) -> Dict[str, Any]:
        """Fit GARCH model for volatility analysis."""
        data = {
            "stock_data": stock_data,
            "symbol": symbol
        }
        return self.post("/models/garch", data)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get AI agents status."""
        return self.get("/agents/status")
    
    def get_agent_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get agent task history."""
        return self.get("/agents/history", params={"limit": limit})
    
    def trigger_data_collection(self, data_type: str, targets: list) -> Dict[str, Any]:
        """Manually trigger data collection."""
        params = {
            "data_type": data_type,
            "locations_or_symbols": targets
        }
        return self.post("/data/collection/trigger", params)
    
    def get_collection_status(self) -> Dict[str, Any]:
        """Get data collection status."""
        return self.get("/data/collection/status")
    
    # Health and monitoring methods
    
    def health_check(self) -> bool:
        """Check if backend is healthy."""
        try:
            response = self.get("/health")
            return response.get("status") == "healthy"
        except:
            return False
    
    def is_websocket_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._is_connected
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get connection status information."""
        return {
            "api_base_url": self.api_base_url,
            "websocket_url": self.websocket_url,
            "http_healthy": self.health_check(),
            "websocket_connected": self.is_websocket_connected(),
            "last_check": datetime.utcnow().isoformat()
        }


# Factory function for creating UI integration service
def create_ui_integration_service(api_base_url: str = "http://localhost:8000/api") -> UIIntegrationService:
    """Create and configure UI integration service."""
    return UIIntegrationService(api_base_url)