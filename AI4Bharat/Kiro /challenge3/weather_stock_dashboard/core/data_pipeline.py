"""Data pipeline integration for coordinating data flow between services."""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from weather_stock_dashboard.services.data_collector import data_collector_service
from weather_stock_dashboard.services.chromadb_service import chromadb_service
from weather_stock_dashboard.mcp_servers.weather_server import weather_mcp_server
from weather_stock_dashboard.mcp_servers.stock_server import stock_mcp_server

logger = logging.getLogger(__name__)


@dataclass
class PipelineMetrics:
    """Metrics for data pipeline performance."""
    weather_data_collected: int = 0
    stock_data_collected: int = 0
    weather_data_stored: int = 0
    stock_data_stored: int = 0
    collection_errors: int = 0
    storage_errors: int = 0
    last_collection_time: Optional[datetime] = None
    pipeline_uptime: timedelta = timedelta()


class DataPipeline:
    """Integrated data pipeline for weather and stock data."""
    
    def __init__(self):
        """Initialize data pipeline."""
        self.metrics = PipelineMetrics()
        self._start_time = datetime.utcnow()
        self._is_running = False
        
        # Pipeline configuration
        self.batch_size = 100
        self.embedding_batch_size = 50
        self.max_retries = 3
        self.retry_delay = 30  # seconds
    
    async def initialize(self) -> None:
        """Initialize the data pipeline."""
        logger.info("Initializing data pipeline...")
        
        try:
            # Initialize ChromaDB service first (dependency)
            await chromadb_service.initialize()
            
            # Initialize data collector service
            await data_collector_service.initialize()
            
            logger.info("Data pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize data pipeline: {e}")
            raise
    
    async def start(self) -> None:
        """Start the data pipeline."""
        if self._is_running:
            logger.warning("Data pipeline is already running")
            return
        
        logger.info("Starting data pipeline...")
        
        try:
            # Start data collector scheduler
            await data_collector_service.start_scheduler()
            
            self._is_running = True
            self._start_time = datetime.utcnow()
            
            logger.info("Data pipeline started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start data pipeline: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the data pipeline."""
        if not self._is_running:
            return
        
        logger.info("Stopping data pipeline...")
        
        try:
            # Stop data collector scheduler
            await data_collector_service.stop_scheduler()
            
            self._is_running = False
            
            logger.info("Data pipeline stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping data pipeline: {e}")
    
    async def collect_and_process_weather_data(
        self, 
        locations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Collect weather data and process through the pipeline."""
        logger.info("Starting weather data collection and processing...")
        
        start_time = datetime.utcnow()
        collected_count = 0
        stored_count = 0
        errors = []
        
        try:
            # Collect raw weather data
            weather_data = await weather_mcp_server.collect_weather_data(
                locations or data_collector_service.weather_locations
            )
            collected_count = len(weather_data)
            self.metrics.weather_data_collected += collected_count
            
            # Process and store data in batches
            for i in range(0, len(weather_data), self.batch_size):
                batch = weather_data[i:i + self.batch_size]
                
                # Generate embeddings for batch
                processed_batch = await self._generate_weather_embeddings(batch)
                
                # Store batch in ChromaDB
                batch_stored = await self._store_weather_batch(processed_batch)
                stored_count += batch_stored
            
            self.metrics.weather_data_stored += stored_count
            self.metrics.last_collection_time = datetime.utcnow()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Weather data processing completed: {stored_count}/{collected_count} stored in {processing_time:.2f}s")
            
            return {
                "success": True,
                "collected": collected_count,
                "stored": stored_count,
                "processing_time": processing_time,
                "errors": errors
            }
            
        except Exception as e:
            self.metrics.collection_errors += 1
            logger.error(f"Weather data collection and processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "collected": collected_count,
                "stored": stored_count
            }
    
    async def collect_and_process_stock_data(
        self, 
        symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Collect stock data and process through the pipeline."""
        logger.info("Starting stock data collection and processing...")
        
        start_time = datetime.utcnow()
        collected_count = 0
        stored_count = 0
        errors = []
        
        try:
            # Collect raw stock data
            stock_data = await stock_mcp_server.collect_stock_data(
                symbols or data_collector_service.stock_symbols
            )
            collected_count = len(stock_data)
            self.metrics.stock_data_collected += collected_count
            
            # Process and store data in batches
            for i in range(0, len(stock_data), self.batch_size):
                batch = stock_data[i:i + self.batch_size]
                
                # Generate embeddings for batch
                processed_batch = await self._generate_stock_embeddings(batch)
                
                # Store batch in ChromaDB
                batch_stored = await self._store_stock_batch(processed_batch)
                stored_count += batch_stored
            
            self.metrics.stock_data_stored += stored_count
            self.metrics.last_collection_time = datetime.utcnow()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Stock data processing completed: {stored_count}/{collected_count} stored in {processing_time:.2f}s")
            
            return {
                "success": True,
                "collected": collected_count,
                "stored": stored_count,
                "processing_time": processing_time,
                "errors": errors
            }
            
        except Exception as e:
            self.metrics.collection_errors += 1
            logger.error(f"Stock data collection and processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "collected": collected_count,
                "stored": stored_count
            }
    
    async def _generate_weather_embeddings(self, weather_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for weather data."""
        try:
            processed_data = []
            
            for data in weather_data:
                # Create text representation for embedding
                text_repr = f"Weather in {data.get('location', 'unknown')}: {data.get('weather_condition', 'unknown')} conditions, temperature {data.get('temperature', 'unknown')}°C, humidity {data.get('humidity', 'unknown')}%"
                
                # Generate embedding (mock implementation for now)
                embedding = await self._generate_embedding(text_repr)
                
                # Add embedding to data
                data_with_embedding = data.copy()
                data_with_embedding['embedding'] = embedding
                processed_data.append(data_with_embedding)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error generating weather embeddings: {e}")
            # Return original data without embeddings
            return weather_data
    
    async def _generate_stock_embeddings(self, stock_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for stock data."""
        try:
            processed_data = []
            
            for data in stock_data:
                # Create text representation for embedding
                text_repr = f"Stock {data.get('symbol', 'unknown')} in {data.get('sector', 'unknown')} sector: price ${data.get('price', 'unknown')}, volume {data.get('volume', 'unknown')}, change {data.get('change_percent', 'unknown')}%"
                
                # Generate embedding (mock implementation for now)
                embedding = await self._generate_embedding(text_repr)
                
                # Add embedding to data
                data_with_embedding = data.copy()
                data_with_embedding['embedding'] = embedding
                processed_data.append(data_with_embedding)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error generating stock embeddings: {e}")
            # Return original data without embeddings
            return stock_data
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (mock implementation)."""
        # Mock embedding generation - in real implementation, use sentence-transformers
        import hashlib
        import struct
        
        # Create deterministic "embedding" from text hash
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to list of floats (384 dimensions to match sentence-transformers)
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                value = struct.unpack('f', chunk)[0]
                embedding.append(float(value))
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    async def _store_weather_batch(self, weather_batch: List[Dict[str, Any]]) -> int:
        """Store a batch of weather data."""
        stored_count = 0
        
        for data in weather_batch:
            try:
                await chromadb_service.store_weather_data(data)
                stored_count += 1
            except Exception as e:
                self.metrics.storage_errors += 1
                logger.error(f"Failed to store weather data: {e}")
        
        return stored_count
    
    async def _store_stock_batch(self, stock_batch: List[Dict[str, Any]]) -> int:
        """Store a batch of stock data."""
        stored_count = 0
        
        for data in stock_batch:
            try:
                await chromadb_service.store_stock_data(data)
                stored_count += 1
            except Exception as e:
                self.metrics.storage_errors += 1
                logger.error(f"Failed to store stock data: {e}")
        
        return stored_count
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics."""
        self.metrics.pipeline_uptime = datetime.utcnow() - self._start_time
        
        return {
            "is_running": self._is_running,
            "uptime_seconds": self.metrics.pipeline_uptime.total_seconds(),
            "weather_data_collected": self.metrics.weather_data_collected,
            "stock_data_collected": self.metrics.stock_data_collected,
            "weather_data_stored": self.metrics.weather_data_stored,
            "stock_data_stored": self.metrics.stock_data_stored,
            "collection_errors": self.metrics.collection_errors,
            "storage_errors": self.metrics.storage_errors,
            "last_collection_time": self.metrics.last_collection_time.isoformat() if self.metrics.last_collection_time else None,
            "success_rate": {
                "weather": (self.metrics.weather_data_stored / max(self.metrics.weather_data_collected, 1)) * 100,
                "stock": (self.metrics.stock_data_stored / max(self.metrics.stock_data_collected, 1)) * 100
            }
        }
    
    async def health_check(self) -> bool:
        """Check if the data pipeline is healthy."""
        try:
            # Check if services are running
            if not self._is_running:
                return False
            
            # Check if data collector is running
            collector_status = await data_collector_service.get_collection_status()
            if not collector_status.get("is_running", False):
                return False
            
            # Check ChromaDB connectivity
            collection_stats = await chromadb_service.get_collection_stats()
            if not isinstance(collection_stats, dict):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data pipeline health check failed: {e}")
            return False


# Global data pipeline instance
data_pipeline = DataPipeline()