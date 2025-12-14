"""ChromaDB vector store service for weather and stock data."""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)


class ChromaDBService:
    """Service for managing ChromaDB vector store operations."""
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model."""
        self.client = None
        self.embedding_model = None
        self.collections = {}
        
    async def initialize(self):
        """Initialize ChromaDB client and collections."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.HttpClient(
                host=settings.chromadb_host,
                port=settings.chromadb_port,
                settings=Settings(
                    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                    chroma_client_auth_credentials="test-token"
                )
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collections
            await self._create_collections()
            
            logger.info("ChromaDB service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB service: {e}")
            # Fallback to persistent client for development
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            await self._create_collections()
            logger.info("ChromaDB service initialized with persistent client")
    
    async def _create_collections(self):
        """Create ChromaDB collections for different data types."""
        collection_configs = [
            {
                "name": "weather_data",
                "metadata": {"description": "Weather observations with temporal embeddings"}
            },
            {
                "name": "stock_data", 
                "metadata": {"description": "Stock prices with market context embeddings"}
            },
            {
                "name": "correlations",
                "metadata": {"description": "Pre-computed correlation patterns"}
            }
        ]
        
        for config in collection_configs:
            try:
                collection = self.client.get_or_create_collection(
                    name=config["name"],
                    metadata=config["metadata"]
                )
                self.collections[config["name"]] = collection
                logger.info(f"Collection '{config['name']}' ready")
            except Exception as e:
                logger.error(f"Failed to create collection '{config['name']}': {e}")
                raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence transformer."""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def store_weather_data(self, weather_data: Dict[str, Any]) -> str:
        """Store weather data in ChromaDB with embedding."""
        try:
            collection = self.collections["weather_data"]
            
            # Generate embedding from weather description
            weather_text = f"{weather_data['weather_condition']} at {weather_data['location']} - {weather_data['temperature']}°C"
            embedding = self.generate_embedding(weather_text)
            
            # Create document ID
            doc_id = f"weather_{weather_data['location']}_{weather_data['timestamp']}"
            
            # Store in ChromaDB
            collection.add(
                embeddings=[embedding],
                documents=[weather_text],
                metadatas=[{
                    "type": "weather",
                    "location": weather_data["location"],
                    "timestamp": weather_data["timestamp"],
                    "temperature": weather_data["temperature"],
                    "humidity": weather_data["humidity"],
                    "pressure": weather_data["pressure"],
                    "precipitation": weather_data["precipitation"],
                    "wind_speed": weather_data["wind_speed"],
                    "weather_condition": weather_data["weather_condition"]
                }],
                ids=[doc_id]
            )
            
            logger.info(f"Stored weather data: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to store weather data: {e}")
            raise
    
    async def store_stock_data(self, stock_data: Dict[str, Any]) -> str:
        """Store stock data in ChromaDB with embedding."""
        try:
            collection = self.collections["stock_data"]
            
            # Generate embedding from stock context
            stock_text = f"{stock_data['symbol']} {stock_data['sector']} stock at ${stock_data['price']} - {stock_data['change_percent']}% change"
            embedding = self.generate_embedding(stock_text)
            
            # Create document ID
            doc_id = f"stock_{stock_data['symbol']}_{stock_data['timestamp']}"
            
            # Store in ChromaDB
            collection.add(
                embeddings=[embedding],
                documents=[stock_text],
                metadatas=[{
                    "type": "stock",
                    "symbol": stock_data["symbol"],
                    "timestamp": stock_data["timestamp"],
                    "price": stock_data["price"],
                    "volume": stock_data["volume"],
                    "market_cap": stock_data.get("market_cap"),
                    "sector": stock_data["sector"],
                    "change_percent": stock_data["change_percent"]
                }],
                ids=[doc_id]
            )
            
            logger.info(f"Stored stock data: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to store stock data: {e}")
            raise
    
    async def store_correlation(self, correlation_data: Dict[str, Any]) -> str:
        """Store correlation insight in ChromaDB with embedding."""
        try:
            collection = self.collections["correlations"]
            
            # Generate embedding from correlation description
            correlation_text = f"{correlation_data['weather_pattern']} correlates with {correlation_data['stock_pattern']} - {correlation_data['explanation']}"
            embedding = self.generate_embedding(correlation_text)
            
            # Create document ID
            doc_id = f"correlation_{correlation_data['id']}"
            
            # Store in ChromaDB
            collection.add(
                embeddings=[embedding],
                documents=[correlation_text],
                metadatas=[{
                    "type": "correlation",
                    "correlation_id": correlation_data["id"],
                    "weather_pattern": correlation_data["weather_pattern"],
                    "stock_pattern": correlation_data["stock_pattern"],
                    "correlation_coefficient": correlation_data["correlation_coefficient"],
                    "confidence_level": correlation_data["confidence_level"],
                    "time_period": correlation_data["time_period"],
                    "statistical_significance": correlation_data["statistical_significance"],
                    "supporting_data_points": correlation_data["supporting_data_points"]
                }],
                ids=[doc_id]
            )
            
            logger.info(f"Stored correlation: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to store correlation: {e}")
            raise
    
    async def search_weather_data(self, query: str, n_results: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search weather data using semantic similarity."""
        try:
            collection = self.collections["weather_data"]
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Prepare where clause for filtering
            where_clause = {"type": "weather"}
            if filters:
                where_clause.update(filters)
            
            # Perform semantic search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            logger.info(f"Found {len(formatted_results)} weather results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search weather data: {e}")
            raise
    
    async def search_stock_data(self, query: str, n_results: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search stock data using semantic similarity."""
        try:
            collection = self.collections["stock_data"]
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Prepare where clause for filtering
            where_clause = {"type": "stock"}
            if filters:
                where_clause.update(filters)
            
            # Perform semantic search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            logger.info(f"Found {len(formatted_results)} stock results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search stock data: {e}")
            raise
    
    async def search_correlations(self, query: str, n_results: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search correlation insights using semantic similarity."""
        try:
            collection = self.collections["correlations"]
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Prepare where clause for filtering
            where_clause = {"type": "correlation"}
            if filters:
                where_clause.update(filters)
            
            # Perform semantic search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            logger.info(f"Found {len(formatted_results)} correlation results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search correlations: {e}")
            raise
    
    async def hybrid_search(self, query: str, n_results: int = 10, include_weather: bool = True, 
                           include_stocks: bool = True, include_correlations: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """Perform hybrid search across all collections."""
        try:
            results = {}
            
            if include_weather:
                results["weather"] = await self.search_weather_data(query, n_results)
            
            if include_stocks:
                results["stocks"] = await self.search_stock_data(query, n_results)
            
            if include_correlations:
                results["correlations"] = await self.search_correlations(query, n_results)
            
            logger.info(f"Hybrid search completed for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform hybrid search: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all collections."""
        try:
            stats = {}
            
            for name, collection in self.collections.items():
                count = collection.count()
                stats[name] = {
                    "count": count,
                    "name": name
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            raise
    
    async def close(self):
        """Close ChromaDB connections."""
        try:
            # ChromaDB client doesn't need explicit closing
            logger.info("ChromaDB service closed")
        except Exception as e:
            logger.error(f"Error closing ChromaDB service: {e}")


# Global ChromaDB service instance
chromadb_service = ChromaDBService()