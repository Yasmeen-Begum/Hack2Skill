"""Weather data MCP server for external API integration."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime, timedelta
import json

from config.settings import settings

logger = logging.getLogger(__name__)


class WeatherMCPServer:
    """MCP server for weather data collection from external APIs."""
    
    def __init__(self):
        """Initialize weather MCP server."""
        self.session = None
        self.rate_limit_delay = 1.0  # Seconds between API calls
        self.last_request_time = {}
        
    async def initialize(self):
        """Initialize HTTP session for API calls."""
        self.session = aiohttp.ClientSession()
        logger.info("Weather MCP server initialized")
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
        logger.info("Weather MCP server closed")
    
    async def _rate_limit_check(self, api_name: str):
        """Check and enforce rate limits for API calls."""
        current_time = datetime.now()
        last_time = self.last_request_time.get(api_name)
        
        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            if time_diff < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - time_diff
                await asyncio.sleep(wait_time)
        
        self.last_request_time[api_name] = current_time
    
    async def get_openweather_data(self, location: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
        """Get weather data from OpenWeatherMap API."""
        try:
            await self._rate_limit_check("openweather")
            
            if not settings.openweather_api_key:
                raise ValueError("OpenWeatherMap API key not configured")
            
            # Build API URL
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "appid": settings.openweather_api_key,
                "units": "metric"
            }
            
            if lat is not None and lon is not None:
                params["lat"] = lat
                params["lon"] = lon
            else:
                params["q"] = location
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._normalize_openweather_data(data, location)
                elif response.status == 401:
                    raise ValueError("Invalid OpenWeatherMap API key")
                elif response.status == 404:
                    raise ValueError(f"Location not found: {location}")
                else:
                    raise ValueError(f"OpenWeatherMap API error: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling OpenWeatherMap API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting OpenWeatherMap data: {e}")
            raise
    
    def _normalize_openweather_data(self, data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Normalize OpenWeatherMap API response to standard format."""
        try:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "location": location,
                "temperature": float(data["main"]["temp"]),
                "humidity": float(data["main"]["humidity"]),
                "pressure": float(data["main"]["pressure"]),
                "precipitation": float(data.get("rain", {}).get("1h", 0.0)),
                "wind_speed": float(data["wind"].get("speed", 0.0)) * 3.6,  # Convert m/s to km/h
                "weather_condition": data["weather"][0]["description"].lower(),
                "source": "openweathermap",
                "raw_data": data
            }
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error normalizing OpenWeatherMap data: {e}")
            raise ValueError(f"Invalid OpenWeatherMap data format: {e}")
    
    async def get_noaa_data(self, station_id: str) -> Dict[str, Any]:
        """Get weather data from NOAA API."""
        try:
            await self._rate_limit_check("noaa")
            
            # NOAA API endpoint for current observations
            base_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
            
            headers = {
                "User-Agent": "WeatherStockDashboard/1.0 (contact@example.com)"
            }
            
            async with self.session.get(base_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._normalize_noaa_data(data, station_id)
                elif response.status == 404:
                    raise ValueError(f"NOAA station not found: {station_id}")
                else:
                    raise ValueError(f"NOAA API error: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling NOAA API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting NOAA data: {e}")
            raise
    
    def _normalize_noaa_data(self, data: Dict[str, Any], station_id: str) -> Dict[str, Any]:
        """Normalize NOAA API response to standard format."""
        try:
            properties = data["properties"]
            
            # Extract temperature (convert from Celsius if needed)
            temp_value = properties.get("temperature", {}).get("value")
            if temp_value is None:
                raise ValueError("Temperature data not available")
            
            # Extract other measurements
            humidity_value = properties.get("relativeHumidity", {}).get("value", 0.0)
            pressure_value = properties.get("barometricPressure", {}).get("value", 0.0)
            wind_speed_value = properties.get("windSpeed", {}).get("value", 0.0)
            
            # Convert pressure from Pa to hPa if needed
            if pressure_value > 10000:  # Likely in Pa
                pressure_value = pressure_value / 100
            
            # Convert wind speed from m/s to km/h if needed
            if wind_speed_value and wind_speed_value < 100:  # Likely in m/s
                wind_speed_value = wind_speed_value * 3.6
            
            return {
                "timestamp": properties.get("timestamp", datetime.utcnow().isoformat()),
                "location": f"NOAA Station {station_id}",
                "temperature": float(temp_value),
                "humidity": float(humidity_value or 0.0),
                "pressure": float(pressure_value or 1013.25),
                "precipitation": 0.0,  # NOAA current obs doesn't include precipitation
                "wind_speed": float(wind_speed_value or 0.0),
                "weather_condition": properties.get("textDescription", "unknown").lower(),
                "source": "noaa",
                "raw_data": data
            }
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error normalizing NOAA data: {e}")
            raise ValueError(f"Invalid NOAA data format: {e}")
    
    async def validate_weather_data(self, data: Dict[str, Any]) -> bool:
        """Validate weather data against expected ranges."""
        try:
            # Temperature validation (-100°C to 60°C)
            temp = data.get("temperature")
            if temp is None or not (-100 <= temp <= 60):
                logger.warning(f"Invalid temperature: {temp}")
                return False
            
            # Humidity validation (0% to 100%)
            humidity = data.get("humidity", 0)
            if not (0 <= humidity <= 100):
                logger.warning(f"Invalid humidity: {humidity}")
                return False
            
            # Pressure validation (800 hPa to 1200 hPa)
            pressure = data.get("pressure", 1013.25)
            if not (800 <= pressure <= 1200):
                logger.warning(f"Invalid pressure: {pressure}")
                return False
            
            # Wind speed validation (0 to 200 km/h)
            wind_speed = data.get("wind_speed", 0)
            if not (0 <= wind_speed <= 200):
                logger.warning(f"Invalid wind speed: {wind_speed}")
                return False
            
            # Precipitation validation (0 to 1000 mm)
            precipitation = data.get("precipitation", 0)
            if not (0 <= precipitation <= 1000):
                logger.warning(f"Invalid precipitation: {precipitation}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating weather data: {e}")
            return False
    
    async def collect_weather_data(self, locations: List[str]) -> List[Dict[str, Any]]:
        """Collect weather data from multiple locations."""
        weather_data = []
        
        for location in locations:
            try:
                # Try OpenWeatherMap first
                data = await self.get_openweather_data(location)
                
                if await self.validate_weather_data(data):
                    weather_data.append(data)
                    logger.info(f"Collected weather data for {location}")
                else:
                    logger.warning(f"Invalid weather data for {location}")
                    
            except Exception as e:
                logger.error(f"Failed to collect weather data for {location}: {e}")
                continue
        
        return weather_data
    
    async def get_weather_forecast(self, location: str, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast data."""
        try:
            await self._rate_limit_check("openweather_forecast")
            
            if not settings.openweather_api_key:
                raise ValueError("OpenWeatherMap API key not configured")
            
            base_url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": location,
                "appid": settings.openweather_api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._normalize_forecast_data(data, location)
                else:
                    raise ValueError(f"OpenWeatherMap forecast API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            raise
    
    def _normalize_forecast_data(self, data: Dict[str, Any], location: str) -> List[Dict[str, Any]]:
        """Normalize forecast data to standard format."""
        forecast_list = []
        
        try:
            for item in data["list"]:
                forecast_item = {
                    "timestamp": item["dt_txt"],
                    "location": location,
                    "temperature": float(item["main"]["temp"]),
                    "humidity": float(item["main"]["humidity"]),
                    "pressure": float(item["main"]["pressure"]),
                    "precipitation": float(item.get("rain", {}).get("3h", 0.0)),
                    "wind_speed": float(item["wind"].get("speed", 0.0)) * 3.6,
                    "weather_condition": item["weather"][0]["description"].lower(),
                    "source": "openweathermap_forecast",
                    "forecast": True
                }
                forecast_list.append(forecast_item)
            
            return forecast_list
            
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error normalizing forecast data: {e}")
            raise ValueError(f"Invalid forecast data format: {e}")


# Global weather MCP server instance
weather_mcp_server = WeatherMCPServer()