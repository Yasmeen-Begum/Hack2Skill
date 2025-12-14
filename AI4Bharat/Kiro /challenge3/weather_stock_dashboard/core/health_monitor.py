"""Health monitoring system for application services."""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check configuration."""
    name: str
    check_func: Callable[[], Awaitable[bool]]
    interval: int = 30  # seconds
    timeout: int = 10   # seconds
    retries: int = 3
    critical: bool = True
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    consecutive_failures: int = 0
    error_message: Optional[str] = None


@dataclass
class SystemHealth:
    """Overall system health information."""
    status: HealthStatus
    checks: Dict[str, Dict[str, Any]]
    last_updated: datetime
    uptime: timedelta
    version: str


class HealthMonitor:
    """Health monitoring system for tracking service health."""
    
    def __init__(self, check_interval: int = 30):
        """Initialize health monitor."""
        self.check_interval = check_interval
        self._checks: Dict[str, HealthCheck] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._start_time = datetime.utcnow()
        self._is_running = False
    
    def register_health_check(
        self,
        name: str,
        check_func: Callable[[], Awaitable[bool]],
        interval: int = 30,
        timeout: int = 10,
        retries: int = 3,
        critical: bool = True
    ) -> None:
        """Register a health check."""
        self._checks[name] = HealthCheck(
            name=name,
            check_func=check_func,
            interval=interval,
            timeout=timeout,
            retries=retries,
            critical=critical
        )
        logger.info(f"Registered health check: {name}")
    
    async def start_monitoring(self) -> None:
        """Start the health monitoring loop."""
        if self._is_running:
            logger.warning("Health monitoring is already running")
            return
        
        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop the health monitoring loop."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health monitoring stopped")
    
    async def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks immediately."""
        results = {}
        
        for name, check in self._checks.items():
            result = await self._run_single_check(check)
            results[name] = {
                "status": result["status"].value,
                "last_check": result["last_check"].isoformat() if result["last_check"] else None,
                "error_message": result["error_message"],
                "consecutive_failures": result["consecutive_failures"],
                "critical": check.critical
            }
        
        return results
    
    async def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""
        check_results = await self.run_all_checks()
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        critical_failures = 0
        total_failures = 0
        
        for check_name, result in check_results.items():
            check = self._checks[check_name]
            status = HealthStatus(result["status"])
            
            if status == HealthStatus.UNHEALTHY:
                total_failures += 1
                if check.critical:
                    critical_failures += 1
        
        if critical_failures > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif total_failures > 0:
            overall_status = HealthStatus.DEGRADED
        
        return SystemHealth(
            status=overall_status,
            checks=check_results,
            last_updated=datetime.utcnow(),
            uptime=datetime.utcnow() - self._start_time,
            version="0.1.0"
        )
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        logger.info("Health monitoring loop started")
        
        while self._is_running:
            try:
                # Run checks that are due
                for check in self._checks.values():
                    if self._is_check_due(check):
                        asyncio.create_task(self._run_single_check(check))
                
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
        
        logger.info("Health monitoring loop stopped")
    
    def _is_check_due(self, check: HealthCheck) -> bool:
        """Check if a health check is due to run."""
        if check.last_check is None:
            return True
        
        time_since_last = datetime.utcnow() - check.last_check
        return time_since_last.total_seconds() >= check.interval
    
    async def _run_single_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run a single health check with retries."""
        check.last_check = datetime.utcnow()
        
        for attempt in range(check.retries + 1):
            try:
                # Run check with timeout
                result = await asyncio.wait_for(
                    check.check_func(),
                    timeout=check.timeout
                )
                
                if result:
                    check.last_status = HealthStatus.HEALTHY
                    check.consecutive_failures = 0
                    check.error_message = None
                    break
                else:
                    raise Exception("Health check returned False")
                    
            except asyncio.TimeoutError:
                error_msg = f"Health check timed out after {check.timeout}s"
                logger.warning(f"Health check '{check.name}' timed out (attempt {attempt + 1})")
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Health check '{check.name}' failed (attempt {attempt + 1}): {e}")
            
            # If this was the last attempt, mark as failed
            if attempt == check.retries:
                check.last_status = HealthStatus.UNHEALTHY
                check.consecutive_failures += 1
                check.error_message = error_msg
                logger.error(f"Health check '{check.name}' failed after {check.retries + 1} attempts")
        
        return {
            "status": check.last_status,
            "last_check": check.last_check,
            "error_message": check.error_message,
            "consecutive_failures": check.consecutive_failures
        }


# Health check functions for common services
async def check_chromadb_health() -> bool:
    """Health check for ChromaDB service."""
    try:
        from weather_stock_dashboard.services.chromadb_service import chromadb_service
        # Try to get collection stats
        stats = await chromadb_service.get_collection_stats()
        return isinstance(stats, dict)
    except Exception:
        return False


async def check_data_collector_health() -> bool:
    """Health check for data collector service."""
    try:
        from weather_stock_dashboard.services.data_collector import data_collector_service
        # Check if scheduler is running
        status = await data_collector_service.get_collection_status()
        return status.get("scheduler_running", False)
    except Exception:
        return False


async def check_agents_health() -> bool:
    """Health check for AI agents."""
    try:
        from weather_stock_dashboard.agents import agent_orchestrator
        # Check if agents are responsive
        status = agent_orchestrator.get_all_agents_status()
        return len(status) > 0
    except Exception:
        return False


async def check_rag_engine_health() -> bool:
    """Health check for RAG engine."""
    try:
        from weather_stock_dashboard.services.rag_engine import rag_engine
        # Try a simple query
        result = await rag_engine.process_query("health check", "system")
        return result is not None
    except Exception:
        return False