"""Data collector service with scheduling for weather and stock data."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config.settings import settings
from weather_stock_dashboard.mcp_servers.weather_server import weather_mcp_server
from weather_stock_dashboard.mcp_servers.stock_server import stock_mcp_server
from weather_stock_dashboard.services.chromadb_service import chromadb_service

logger = logging.getLogger(__name__)


class DataCollectorService:
    """Service for orchestrating data collection from MCP servers."""
    
    def __init__(self):
        """Initialize data collector service."""
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.retry_attempts = 3
        self.retry_delay = 60  # seconds
        
        # Default locations and symbols for collection
        self.weather_locations = [
            "New York,NY,US",
            "Los Angeles,CA,US", 
            "Chicago,IL,US",
            "Houston,TX,US",
            "Phoenix,AZ,US"
        ]
        
        self.stock_symbols = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "META", "NVDA", "JPM", "JNJ", "V"
        ]
    
    async def initialize(self):
        """Initialize the data collector service."""
        try:
            # Initialize MCP servers
            await weather_mcp_server.initialize()
            await stock_mcp_server.initialize()
            
            # Configure scheduled jobs
            self._configure_scheduled_jobs()
            
            logger.info("Data collector service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize data collector service: {e}")
            raise
    
    def _configure_scheduled_jobs(self):
        """Configure scheduled data collection jobs."""
        # Weather data collection - every hour
        self.scheduler.add_job(
            self._collect_weather_data_job,
            trigger=IntervalTrigger(seconds=settings.weather_collection_interval),
            id="weather_collection",
            name="Weather Data Collection",
            max_instances=1,
            coalesce=True
        )
        
        # Stock data collection - every 15 minutes during market hours
        self.scheduler.add_job(
            self._collect_stock_data_job,
            trigger=IntervalTrigger(seconds=settings.stock_collection_interval),
            id="stock_collection", 
            name="Stock Data Collection",
            max_instances=1,
            coalesce=True
        )
        
        # Daily cleanup job - remove old data
        self.scheduler.add_job(
            self._cleanup_old_data_job,
            trigger=CronTrigger(hour=2, minute=0),  # 2 AM daily
            id="data_cleanup",
            name="Data Cleanup",
            max_instances=1
        )
        
        logger.info("Scheduled jobs configured")
    
    async def start_scheduler(self):
        """Start the data collector scheduler."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Data collector scheduler started")
            
            # Collect initial data
            await self._collect_initial_data()
    
    async def start(self):
        """Start the data collector service (alias for start_scheduler)."""
        await self.start_scheduler()
    
    async def stop_scheduler(self):
        """Stop the data collector scheduler."""
        if self.is_running:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            
            # Close MCP servers
            await weather_mcp_server.close()
            await stock_mcp_server.close()
            
            logger.info("Data collector scheduler stopped")
    
    async def stop(self):
        """Stop the data collector service (alias for stop_scheduler)."""
        await self.stop_scheduler()
    
    async def _collect_initial_data(self):
        """Collect initial data on startup."""
        try:
            logger.info("Collecting initial data...")
            await self._collect_weather_data_job()
            await self._collect_stock_data_job()
            logger.info("Initial data collection completed")
        except Exception as e:
            logger.error(f"Error during initial data collection: {e}")
    
    async def _collect_weather_data_job(self):
        """Scheduled job for weather data collection."""
        try:
            logger.info("Starting weather data collection job")
            
            weather_data_list = await self._collect_weather_data_with_retry()
            
            # Store in ChromaDB
            stored_count = 0
            for weather_data in weather_data_list:
                try:
                    await chromadb_service.store_weather_data(weather_data)
                    stored_count += 1
                except Exception as e:
                    logger.error(f"Failed to store weather data: {e}")
            
            logger.info(f"Weather data collection job completed: {stored_count}/{len(weather_data_list)} stored")
            
        except Exception as e:
            logger.error(f"Weather data collection job failed: {e}")
    
    async def _collect_stock_data_job(self):
        """Scheduled job for stock data collection."""
        try:
            logger.info("Starting stock data collection job")
            
            # Only collect during market hours for real-time data
            if not stock_mcp_server._is_market_hours():
                logger.info("Market is closed, skipping stock data collection")
                return
            
            stock_data_list = await self._collect_stock_data_with_retry()
            
            # Store in ChromaDB
            stored_count = 0
            for stock_data in stock_data_list:
                try:
                    await chromadb_service.store_stock_data(stock_data)
                    stored_count += 1
                except Exception as e:
                    logger.error(f"Failed to store stock data: {e}")
            
            logger.info(f"Stock data collection job completed: {stored_count}/{len(stock_data_list)} stored")
            
        except Exception as e:
            logger.error(f"Stock data collection job failed: {e}")
    
    async def _collect_weather_data_with_retry(self) -> List[Dict[str, Any]]:
        """Collect weather data with retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                weather_data = await weather_mcp_server.collect_weather_data(self.weather_locations)
                if weather_data:
                    return weather_data
                else:
                    logger.warning(f"No weather data collected on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Weather data collection attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
        
        logger.error("All weather data collection attempts failed")
        return []
    
    async def _collect_stock_data_with_retry(self) -> List[Dict[str, Any]]:
        """Collect stock data with retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                stock_data = await stock_mcp_server.collect_stock_data(self.stock_symbols)
                if stock_data:
                    return stock_data
                else:
                    logger.warning(f"No stock data collected on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Stock data collection attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
        
        logger.error("All stock data collection attempts failed")
        return []
    
    async def _cleanup_old_data_job(self):
        """Scheduled job for cleaning up old data."""
        try:
            logger.info("Starting data cleanup job")
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=settings.data_retention_days)
            
            # Note: ChromaDB doesn't have built-in TTL, so this would need custom implementation
            # For now, just log the cleanup attempt
            logger.info(f"Data cleanup job completed (cutoff date: {cutoff_date})")
            
        except Exception as e:
            logger.error(f"Data cleanup job failed: {e}")
    
    async def collect_weather_data_manual(self, locations: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Manually trigger weather data collection."""
        try:
            locations = locations or self.weather_locations
            weather_data = await weather_mcp_server.collect_weather_data(locations)
            
            # Store in ChromaDB
            for data in weather_data:
                await chromadb_service.store_weather_data(data)
            
            logger.info(f"Manual weather data collection completed: {len(weather_data)} items")
            return weather_data
            
        except Exception as e:
            logger.error(f"Manual weather data collection failed: {e}")
            raise
    
    async def collect_stock_data_manual(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Manually trigger stock data collection."""
        try:
            symbols = symbols or self.stock_symbols
            stock_data = await stock_mcp_server.collect_stock_data(symbols)
            
            # Store in ChromaDB
            for data in stock_data:
                await chromadb_service.store_stock_data(data)
            
            logger.info(f"Manual stock data collection completed: {len(stock_data)} items")
            return stock_data
            
        except Exception as e:
            logger.error(f"Manual stock data collection failed: {e}")
            raise
    
    async def get_collection_status(self) -> Dict[str, Any]:
        """Get status of data collection jobs."""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            # Get ChromaDB stats
            collection_stats = await chromadb_service.get_collection_stats()
            
            return {
                "is_running": self.is_running,
                "scheduled_jobs": jobs,
                "collection_stats": collection_stats,
                "weather_locations": self.weather_locations,
                "stock_symbols": self.stock_symbols
            }
            
        except Exception as e:
            logger.error(f"Error getting collection status: {e}")
            raise
    
    def add_weather_location(self, location: str):
        """Add a new weather location for collection."""
        if location not in self.weather_locations:
            self.weather_locations.append(location)
            logger.info(f"Added weather location: {location}")
    
    def remove_weather_location(self, location: str):
        """Remove a weather location from collection."""
        if location in self.weather_locations:
            self.weather_locations.remove(location)
            logger.info(f"Removed weather location: {location}")
    
    def add_stock_symbol(self, symbol: str):
        """Add a new stock symbol for collection."""
        symbol = symbol.upper()
        if symbol not in self.stock_symbols:
            self.stock_symbols.append(symbol)
            logger.info(f"Added stock symbol: {symbol}")
    
    def remove_stock_symbol(self, symbol: str):
        """Remove a stock symbol from collection."""
        symbol = symbol.upper()
        if symbol in self.stock_symbols:
            self.stock_symbols.remove(symbol)
            logger.info(f"Removed stock symbol: {symbol}")


# Global data collector service instance
data_collector_service = DataCollectorService()