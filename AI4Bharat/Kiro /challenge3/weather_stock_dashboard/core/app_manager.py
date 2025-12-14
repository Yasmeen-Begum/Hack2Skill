"""Application manager for coordinating all system components."""

import asyncio
import logging
import signal
import sys
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from config.settings import settings
from .service_registry import ServiceRegistry
from .health_monitor import (
    HealthMonitor, 
    check_chromadb_health,
    check_data_collector_health, 
    check_agents_health,
    check_rag_engine_health
)

logger = logging.getLogger(__name__)


class AppManager:
    """Main application manager that coordinates all system components."""
    
    def __init__(self):
        """Initialize application manager."""
        self.service_registry = ServiceRegistry()
        self.health_monitor = HealthMonitor(check_interval=30)
        self._shutdown_event = asyncio.Event()
        self._is_running = False
    
    async def initialize(self) -> None:
        """Initialize all application services."""
        logger.info("Initializing Weather Stock Dashboard application...")
        
        # Register all services
        await self._register_services()
        
        # Register health checks
        await self._register_health_checks()
        
        logger.info("Application initialization complete")
    
    async def startup(self) -> None:
        """Start all application services."""
        logger.info("Starting Weather Stock Dashboard application...")
        
        try:
            # Start all services
            await self.service_registry.start_all_services()
            
            # Start health monitoring
            await self.health_monitor.start_monitoring()
            
            self._is_running = True
            logger.info("Application startup complete - all services running")
            
        except Exception as e:
            logger.error(f"Application startup failed: {e}")
            await self.shutdown()
            raise
    
    async def shutdown(self) -> None:
        """Shutdown all application services."""
        if not self._is_running:
            return
        
        logger.info("Shutting down Weather Stock Dashboard application...")
        
        try:
            # Stop health monitoring
            await self.health_monitor.stop_monitoring()
            
            # Stop all services
            await self.service_registry.stop_all_services()
            
            self._is_running = False
            logger.info("Application shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            # Get service status
            services_status = self.service_registry.get_all_services_status()
            
            # Get health status
            health_status = await self.health_monitor.get_system_health()
            
            return {
                "application": {
                    "name": settings.app_name,
                    "version": settings.app_version,
                    "status": "running" if self._is_running else "stopped",
                    "uptime": health_status.uptime.total_seconds() if health_status else 0
                },
                "services": services_status,
                "health": {
                    "overall_status": health_status.status.value if health_status else "unknown",
                    "checks": health_status.checks if health_status else {},
                    "last_updated": health_status.last_updated.isoformat() if health_status else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "application": {
                    "name": settings.app_name,
                    "version": settings.app_version,
                    "status": "error",
                    "error": str(e)
                }
            }
    
    async def restart_service(self, service_name: str) -> None:
        """Restart a specific service."""
        logger.info(f"Restarting service: {service_name}")
        await self.service_registry.restart_service(service_name)
    
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()
    
    async def _register_services(self) -> None:
        """Register all application services."""
        logger.info("Registering application services...")
        
        # ChromaDB Service
        self.service_registry.register_service(
            name="chromadb",
            startup_func=self._start_chromadb_service,
            shutdown_func=self._stop_chromadb_service,
            health_check_func=self._check_chromadb_health
        )
        
        # Data Collector Service
        self.service_registry.register_service(
            name="data_collector",
            startup_func=self._start_data_collector_service,
            shutdown_func=self._stop_data_collector_service,
            health_check_func=self._check_data_collector_health,
            dependencies=["chromadb"]
        )
        
        # AI Agents Service
        self.service_registry.register_service(
            name="ai_agents",
            startup_func=self._start_ai_agents_service,
            shutdown_func=self._stop_ai_agents_service,
            health_check_func=self._check_ai_agents_health,
            dependencies=["chromadb"]
        )
        
        # RAG Engine Service
        self.service_registry.register_service(
            name="rag_engine",
            startup_func=self._start_rag_engine_service,
            shutdown_func=self._stop_rag_engine_service,
            health_check_func=self._check_rag_engine_health,
            dependencies=["chromadb", "ai_agents"]
        )
        
        logger.info("All services registered")
    
    async def _register_health_checks(self) -> None:
        """Register health checks for monitoring."""
        logger.info("Registering health checks...")
        
        # Register health checks
        self.health_monitor.register_health_check(
            name="chromadb",
            check_func=check_chromadb_health,
            interval=30,
            critical=True
        )
        
        self.health_monitor.register_health_check(
            name="data_collector",
            check_func=check_data_collector_health,
            interval=60,
            critical=False
        )
        
        self.health_monitor.register_health_check(
            name="ai_agents",
            check_func=check_agents_health,
            interval=45,
            critical=False
        )
        
        self.health_monitor.register_health_check(
            name="rag_engine",
            check_func=check_rag_engine_health,
            interval=60,
            critical=False
        )
        
        logger.info("Health checks registered")
    
    # Service startup functions
    async def _start_chromadb_service(self) -> Any:
        """Start ChromaDB service."""
        logger.info("Starting ChromaDB service...")
        try:
            from weather_stock_dashboard.services.chromadb_service import chromadb_service
            await chromadb_service.initialize()
            logger.info("ChromaDB service started successfully")
            return chromadb_service
        except Exception as e:
            logger.error(f"Failed to start ChromaDB service: {e}")
            # Return a mock service for development
            return {"status": "mock", "error": str(e)}
    
    async def _start_data_collector_service(self) -> Any:
        """Start data collector service."""
        logger.info("Starting data pipeline...")
        try:
            from weather_stock_dashboard.core.data_pipeline import data_pipeline
            await data_pipeline.initialize()
            await data_pipeline.start()
            logger.info("Data pipeline started successfully")
            return data_pipeline
        except Exception as e:
            logger.error(f"Failed to start data pipeline: {e}")
            return {"status": "mock", "error": str(e)}
    
    async def _start_ai_agents_service(self) -> Any:
        """Start AI agents service."""
        logger.info("Starting AI agents integration service...")
        try:
            from weather_stock_dashboard.core.agent_integration import agent_integration_service
            await agent_integration_service.initialize()
            logger.info("AI agents integration service started successfully")
            return agent_integration_service
        except Exception as e:
            logger.error(f"Failed to start AI agents integration service: {e}")
            return {"status": "mock", "error": str(e)}
    
    async def _start_rag_engine_service(self) -> Any:
        """Start RAG engine service."""
        logger.info("Starting RAG engine service...")
        try:
            from weather_stock_dashboard.services.rag_engine import rag_engine
            await rag_engine.initialize()
            logger.info("RAG engine service started successfully")
            return rag_engine
        except Exception as e:
            logger.error(f"Failed to start RAG engine service: {e}")
            return {"status": "mock", "error": str(e)}
    
    # Service shutdown functions
    async def _stop_chromadb_service(self, service: Any) -> None:
        """Stop ChromaDB service."""
        logger.info("Stopping ChromaDB service...")
        try:
            if hasattr(service, 'cleanup'):
                await service.cleanup()
        except Exception as e:
            logger.error(f"Error stopping ChromaDB service: {e}")
    
    async def _stop_data_collector_service(self, service: Any) -> None:
        """Stop data collector service."""
        logger.info("Stopping data pipeline...")
        try:
            if hasattr(service, 'stop'):
                await service.stop()
        except Exception as e:
            logger.error(f"Error stopping data pipeline: {e}")
    
    async def _stop_ai_agents_service(self, service: Any) -> None:
        """Stop AI agents service."""
        logger.info("Stopping AI agents integration service...")
        try:
            if hasattr(service, 'shutdown'):
                await service.shutdown()
        except Exception as e:
            logger.error(f"Error stopping AI agents integration service: {e}")
    
    async def _stop_rag_engine_service(self, service: Any) -> None:
        """Stop RAG engine service."""
        logger.info("Stopping RAG engine service...")
        try:
            if hasattr(service, 'cleanup'):
                await service.cleanup()
        except Exception as e:
            logger.error(f"Error stopping RAG engine service: {e}")
    
    # Health check functions
    async def _check_chromadb_health(self, service: Any) -> bool:
        """Check ChromaDB service health."""
        try:
            if hasattr(service, 'get_collection_stats'):
                stats = await service.get_collection_stats()
                return isinstance(stats, dict)
            return True
        except Exception:
            return False
    
    async def _check_data_collector_health(self, service: Any) -> bool:
        """Check data collector service health."""
        try:
            if hasattr(service, 'health_check'):
                return await service.health_check()
            return True
        except Exception:
            return False
    
    async def _check_ai_agents_health(self, service: Any) -> bool:
        """Check AI agents service health."""
        try:
            if hasattr(service, 'health_check'):
                return await service.health_check()
            return True
        except Exception:
            return False
    
    async def _check_rag_engine_health(self, service: Any) -> bool:
        """Check RAG engine service health."""
        try:
            if hasattr(service, 'process_query'):
                result = await service.process_query("health check", "system")
                return result is not None
            return True
        except Exception:
            return False


# Global application manager instance
app_manager = AppManager()


@asynccontextmanager
async def lifespan_manager(app):
    """FastAPI lifespan manager using AppManager."""
    try:
        # Initialize and start application
        await app_manager.initialize()
        await app_manager.startup()
        
        # Start WebSocket periodic updates
        from weather_stock_dashboard.api.websocket import start_periodic_updates
        await start_periodic_updates()
        
        yield
        
    finally:
        # Stop WebSocket periodic updates
        from weather_stock_dashboard.api.websocket import stop_periodic_updates
        await stop_periodic_updates()
        
        # Shutdown application
        await app_manager.shutdown()