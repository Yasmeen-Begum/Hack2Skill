"""Stock data MCP server for external API integration."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime, timedelta
import json

from config.settings import settings

logger = logging.getLogger(__name__)


class StockMCPServer:
    """MCP server for stock data collection from external APIs."""
    
    def __init__(self):
        """Initialize stock MCP server."""
        self.session = None
        self.rate_limit_delay = 1.0  # Seconds between API calls
        self.last_request_time = {}
        
    async def initialize(self):
        """Initialize HTTP session for API calls."""
        self.session = aiohttp.ClientSession()
        logger.info("Stock MCP server initialized")
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
        logger.info("Stock MCP server closed")
    
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
    
    def _is_market_hours(self) -> bool:
        """Check if current time is during market hours (9:30 AM - 4:00 PM ET, Mon-Fri)."""
        now = datetime.now()
        
        # Simple check - in production would need proper timezone handling
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        hour = now.hour
        return 9 <= hour <= 16  # Simplified market hours check
    
    async def get_alpha_vantage_data(self, symbol: str) -> Dict[str, Any]:
        """Get stock data from Alpha Vantage API."""
        try:
            await self._rate_limit_check("alpha_vantage")
            
            if not settings.alpha_vantage_api_key:
                raise ValueError("Alpha Vantage API key not configured")
            
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": settings.alpha_vantage_api_key
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "Error Message" in data:
                        raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
                    
                    if "Note" in data:
                        raise ValueError("Alpha Vantage API rate limit exceeded")
                    
                    return self._normalize_alpha_vantage_data(data, symbol)
                else:
                    raise ValueError(f"Alpha Vantage API error: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling Alpha Vantage API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting Alpha Vantage data: {e}")
            raise
    
    def _normalize_alpha_vantage_data(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Normalize Alpha Vantage API response to standard format."""
        try:
            quote = data["Global Quote"]
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "symbol": symbol.upper(),
                "price": float(quote["05. price"]),
                "volume": int(quote["06. volume"]),
                "market_cap": None,  # Not provided by this endpoint
                "sector": "Unknown",  # Would need separate API call
                "change_percent": float(quote["10. change percent"].rstrip('%')),
                "source": "alpha_vantage",
                "raw_data": data
            }
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error normalizing Alpha Vantage data: {e}")
            raise ValueError(f"Invalid Alpha Vantage data format: {e}")
    
    async def get_yahoo_finance_data(self, symbol: str) -> Dict[str, Any]:
        """Get stock data from Yahoo Finance (unofficial API)."""
        try:
            await self._rate_limit_check("yahoo_finance")
            
            # Using Yahoo Finance's unofficial API
            base_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            async with self.session.get(base_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._normalize_yahoo_finance_data(data, symbol)
                else:
                    raise ValueError(f"Yahoo Finance API error: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling Yahoo Finance API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance data: {e}")
            raise
    
    def _normalize_yahoo_finance_data(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Normalize Yahoo Finance API response to standard format."""
        try:
            result = data["chart"]["result"][0]
            meta = result["meta"]
            
            # Get the latest price
            current_price = meta.get("regularMarketPrice", meta.get("previousClose", 0))
            
            # Calculate change percent
            previous_close = meta.get("previousClose", current_price)
            change_percent = ((current_price - previous_close) / previous_close * 100) if previous_close > 0 else 0
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "symbol": symbol.upper(),
                "price": float(current_price),
                "volume": int(meta.get("regularMarketVolume", 0)),
                "market_cap": meta.get("marketCap"),
                "sector": "Unknown",  # Not provided in this endpoint
                "change_percent": float(change_percent),
                "source": "yahoo_finance",
                "raw_data": data
            }
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error normalizing Yahoo Finance data: {e}")
            raise ValueError(f"Invalid Yahoo Finance data format: {e}")
    
    async def validate_stock_data(self, data: Dict[str, Any]) -> bool:
        """Validate stock data against expected ranges and market rules."""
        try:
            # Price validation (must be positive)
            price = data.get("price")
            if price is None or price <= 0:
                logger.warning(f"Invalid price: {price}")
                return False
            
            # Sanity check for extremely high prices
            if price > 100000:
                logger.warning(f"Suspiciously high price: {price}")
                return False
            
            # Volume validation (must be non-negative)
            volume = data.get("volume", 0)
            if volume < 0:
                logger.warning(f"Invalid volume: {volume}")
                return False
            
            # Symbol validation
            symbol = data.get("symbol")
            if not symbol or len(symbol) > 10:
                logger.warning(f"Invalid symbol: {symbol}")
                return False
            
            # Change percent validation (reasonable bounds)
            change_percent = data.get("change_percent", 0)
            if not (-100 <= change_percent <= 1000):
                logger.warning(f"Extreme change percent: {change_percent}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating stock data: {e}")
            return False
    
    async def collect_stock_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Collect stock data for multiple symbols."""
        stock_data = []
        
        for symbol in symbols:
            try:
                # Try Alpha Vantage first, fallback to Yahoo Finance
                try:
                    data = await self.get_alpha_vantage_data(symbol)
                except Exception as e:
                    logger.warning(f"Alpha Vantage failed for {symbol}, trying Yahoo Finance: {e}")
                    data = await self.get_yahoo_finance_data(symbol)
                
                if await self.validate_stock_data(data):
                    stock_data.append(data)
                    logger.info(f"Collected stock data for {symbol}")
                else:
                    logger.warning(f"Invalid stock data for {symbol}")
                    
            except Exception as e:
                logger.error(f"Failed to collect stock data for {symbol}: {e}")
                continue
        
        return stock_data
    
    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed stock information including sector and market cap."""
        try:
            await self._rate_limit_check("alpha_vantage_overview")
            
            if not settings.alpha_vantage_api_key:
                raise ValueError("Alpha Vantage API key not configured")
            
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": settings.alpha_vantage_api_key
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "Error Message" in data:
                        raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
                    
                    return {
                        "symbol": symbol.upper(),
                        "name": data.get("Name", "Unknown"),
                        "sector": data.get("Sector", "Unknown"),
                        "industry": data.get("Industry", "Unknown"),
                        "market_cap": int(data.get("MarketCapitalization", 0)) if data.get("MarketCapitalization", "0").isdigit() else None,
                        "description": data.get("Description", ""),
                        "source": "alpha_vantage_overview"
                    }
                else:
                    raise ValueError(f"Alpha Vantage overview API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting stock info: {e}")
            # Return minimal info if API fails
            return {
                "symbol": symbol.upper(),
                "name": "Unknown",
                "sector": "Unknown",
                "industry": "Unknown",
                "market_cap": None,
                "description": "",
                "source": "fallback"
            }
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical stock data."""
        try:
            await self._rate_limit_check("alpha_vantage_daily")
            
            if not settings.alpha_vantage_api_key:
                raise ValueError("Alpha Vantage API key not configured")
            
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": settings.alpha_vantage_api_key,
                "outputsize": "compact"  # Last 100 data points
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "Error Message" in data:
                        raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
                    
                    return self._normalize_historical_data(data, symbol, days)
                else:
                    raise ValueError(f"Alpha Vantage daily API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            raise
    
    def _normalize_historical_data(self, data: Dict[str, Any], symbol: str, days: int) -> List[Dict[str, Any]]:
        """Normalize historical data to standard format."""
        historical_data = []
        
        try:
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys(), reverse=True)[:days]
            
            for date in dates:
                day_data = time_series[date]
                
                open_price = float(day_data["1. open"])
                close_price = float(day_data["4. close"])
                change_percent = ((close_price - open_price) / open_price * 100) if open_price > 0 else 0
                
                historical_item = {
                    "timestamp": f"{date}T16:00:00Z",  # Market close time
                    "symbol": symbol.upper(),
                    "price": close_price,
                    "volume": int(day_data["5. volume"]),
                    "market_cap": None,
                    "sector": "Unknown",
                    "change_percent": change_percent,
                    "source": "alpha_vantage_daily",
                    "historical": True,
                    "open": float(day_data["1. open"]),
                    "high": float(day_data["2. high"]),
                    "low": float(day_data["3. low"])
                }
                historical_data.append(historical_item)
            
            return historical_data
            
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error normalizing historical data: {e}")
            raise ValueError(f"Invalid historical data format: {e}")


# Global stock MCP server instance
stock_mcp_server = StockMCPServer()