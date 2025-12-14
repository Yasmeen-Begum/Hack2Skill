"""Main application entry point for Weather Stock Dashboard."""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from weather_stock_dashboard.api.routes import router as api_router
from weather_stock_dashboard.api.websocket import websocket_router, start_periodic_updates, stop_periodic_updates
from weather_stock_dashboard.api.middleware import (
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitingMiddleware,
    CacheControlMiddleware,
    SecurityHeadersMiddleware,
    metrics_middleware
)
from weather_stock_dashboard.core.app_manager import lifespan_manager, app_manager


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered dashboard correlating weather patterns with stock market performance",
    lifespan=lifespan_manager
)

# Add middleware in reverse order (last added = first executed)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitingMiddleware, calls_per_minute=120)  # 2 requests per second
app.add_middleware(CacheControlMiddleware, default_cache_seconds=300)
app.add_middleware(SecurityHeadersMiddleware)

# Set the metrics middleware app reference
metrics_middleware.app = app
app.add_middleware(type(metrics_middleware), app=app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Weather Stock Dashboard API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status."""
    try:
        system_status = await app_manager.get_system_status()
        return system_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": settings.app_version
        }


@app.get("/status")
async def system_status():
    """Get comprehensive system status."""
    return await app_manager.get_system_status()


@app.get("/metrics")
async def get_metrics():
    """Get API metrics."""
    return metrics_middleware.get_metrics()


@app.post("/admin/restart/{service_name}")
async def restart_service(service_name: str):
    """Restart a specific service (admin endpoint)."""
    try:
        await app_manager.restart_service(service_name)
        return {"success": True, "message": f"Service '{service_name}' restarted successfully"}
    except Exception as e:
        logger.error(f"Failed to restart service '{service_name}': {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )