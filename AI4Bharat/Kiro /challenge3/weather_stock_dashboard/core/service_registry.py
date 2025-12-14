"""Service registry for managing application services."""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """Information about a registered service."""
    name: str
    status: ServiceStatus = ServiceStatus.STOPPED
    instance: Optional[Any] = None
    startup_func: Optional[Callable[[], Awaitable[Any]]] = None
    shutdown_func: Optional[Callable[[Any], Awaitable[None]]] = None
    health_check_func: Optional[Callable[[Any], Awaitable[bool]]] = None
    dependencies: list = field(default_factory=list)
    started_at: Optional[datetime] = None
    error_message: Optional[str] = None
    restart_count: int = 0


class ServiceRegistry:
    """Registry for managing application services with dependency resolution."""
    
    def __init__(self):
        """Initialize service registry."""
        self._services: Dict[str, ServiceInfo] = {}
        self._startup_order: list = []
        self._shutdown_order: list = []
    
    def register_service(
        self,
        name: str,
        startup_func: Callable[[], Awaitable[Any]],
        shutdown_func: Optional[Callable[[Any], Awaitable[None]]] = None,
        health_check_func: Optional[Callable[[Any], Awaitable[bool]]] = None,
        dependencies: Optional[list] = None
    ) -> None:
        """Register a service with the registry."""
        if name in self._services:
            raise ValueError(f"Service '{name}' is already registered")
        
        self._services[name] = ServiceInfo(
            name=name,
            startup_func=startup_func,
            shutdown_func=shutdown_func,
            health_check_func=health_check_func,
            dependencies=dependencies or []
        )
        
        logger.info(f"Registered service: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service instance by name."""
        service_info = self._services.get(name)
        return service_info.instance if service_info else None
    
    def get_service_status(self, name: str) -> Optional[ServiceStatus]:
        """Get service status by name."""
        service_info = self._services.get(name)
        return service_info.status if service_info else None
    
    def get_all_services_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all services."""
        return {
            name: {
                "status": info.status.value,
                "started_at": info.started_at.isoformat() if info.started_at else None,
                "error_message": info.error_message,
                "restart_count": info.restart_count,
                "dependencies": info.dependencies
            }
            for name, info in self._services.items()
        }
    
    async def start_all_services(self) -> None:
        """Start all services in dependency order."""
        logger.info("Starting all services...")
        
        # Calculate startup order based on dependencies
        self._calculate_startup_order()
        
        for service_name in self._startup_order:
            await self._start_service(service_name)
        
        logger.info("All services started successfully")
    
    async def stop_all_services(self) -> None:
        """Stop all services in reverse dependency order."""
        logger.info("Stopping all services...")
        
        # Stop in reverse order
        for service_name in reversed(self._shutdown_order):
            await self._stop_service(service_name)
        
        logger.info("All services stopped")
    
    async def restart_service(self, name: str) -> None:
        """Restart a specific service."""
        logger.info(f"Restarting service: {name}")
        
        if name not in self._services:
            raise ValueError(f"Service '{name}' not found")
        
        await self._stop_service(name)
        await self._start_service(name)
        
        self._services[name].restart_count += 1
        logger.info(f"Service '{name}' restarted successfully")
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health checks on all services."""
        results = {}
        
        for name, info in self._services.items():
            if info.status == ServiceStatus.RUNNING and info.health_check_func:
                try:
                    results[name] = await info.health_check_func(info.instance)
                except Exception as e:
                    logger.error(f"Health check failed for service '{name}': {e}")
                    results[name] = False
            else:
                results[name] = info.status == ServiceStatus.RUNNING
        
        return results
    
    def _calculate_startup_order(self) -> None:
        """Calculate service startup order based on dependencies."""
        visited = set()
        temp_visited = set()
        self._startup_order = []
        
        def visit(service_name: str):
            if service_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving service '{service_name}'")
            
            if service_name not in visited:
                temp_visited.add(service_name)
                
                service_info = self._services.get(service_name)
                if service_info:
                    for dependency in service_info.dependencies:
                        if dependency not in self._services:
                            raise ValueError(f"Dependency '{dependency}' not found for service '{service_name}'")
                        visit(dependency)
                
                temp_visited.remove(service_name)
                visited.add(service_name)
                self._startup_order.append(service_name)
        
        for service_name in self._services:
            if service_name not in visited:
                visit(service_name)
        
        self._shutdown_order = self._startup_order.copy()
        logger.debug(f"Service startup order: {self._startup_order}")
    
    async def _start_service(self, name: str) -> None:
        """Start a specific service."""
        service_info = self._services[name]
        
        if service_info.status == ServiceStatus.RUNNING:
            logger.debug(f"Service '{name}' is already running")
            return
        
        logger.info(f"Starting service: {name}")
        service_info.status = ServiceStatus.STARTING
        service_info.error_message = None
        
        try:
            # Check dependencies are running
            for dependency in service_info.dependencies:
                dep_service = self._services[dependency]
                if dep_service.status != ServiceStatus.RUNNING:
                    raise RuntimeError(f"Dependency '{dependency}' is not running")
            
            # Start the service
            if service_info.startup_func:
                service_info.instance = await service_info.startup_func()
            
            service_info.status = ServiceStatus.RUNNING
            service_info.started_at = datetime.utcnow()
            
            logger.info(f"Service '{name}' started successfully")
            
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            service_info.error_message = str(e)
            logger.error(f"Failed to start service '{name}': {e}")
            raise
    
    async def _stop_service(self, name: str) -> None:
        """Stop a specific service."""
        service_info = self._services[name]
        
        if service_info.status == ServiceStatus.STOPPED:
            logger.debug(f"Service '{name}' is already stopped")
            return
        
        logger.info(f"Stopping service: {name}")
        service_info.status = ServiceStatus.STOPPING
        
        try:
            if service_info.shutdown_func and service_info.instance:
                await service_info.shutdown_func(service_info.instance)
            
            service_info.status = ServiceStatus.STOPPED
            service_info.instance = None
            service_info.started_at = None
            
            logger.info(f"Service '{name}' stopped successfully")
            
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            service_info.error_message = str(e)
            logger.error(f"Failed to stop service '{name}': {e}")
            raise