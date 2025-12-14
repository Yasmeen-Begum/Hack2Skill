"""Agent integration service for connecting AI agents to API endpoints."""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from weather_stock_dashboard.agents import agent_orchestrator, initialize_agents

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Agent task information."""
    task_id: str
    agent_name: str
    crew_name: Optional[str]
    task_description: str
    context: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class AgentIntegrationService:
    """Service for integrating AI agents with API endpoints."""
    
    def __init__(self):
        """Initialize agent integration service."""
        self._tasks: Dict[str, AgentTask] = {}
        self._task_counter = 0
        self._is_initialized = False
        self._performance_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "agent_usage": {}
        }
    
    async def initialize(self) -> None:
        """Initialize the agent integration service."""
        if self._is_initialized:
            logger.warning("Agent integration service already initialized")
            return
        
        logger.info("Initializing agent integration service...")
        
        try:
            # Initialize agents and orchestrator
            initialize_agents()
            await agent_orchestrator.initialize_all_agents()
            
            self._is_initialized = True
            logger.info("Agent integration service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent integration service: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the agent integration service."""
        if not self._is_initialized:
            return
        
        logger.info("Shutting down agent integration service...")
        
        try:
            # Cancel all pending tasks
            for task in self._tasks.values():
                if task.status == TaskStatus.RUNNING:
                    task.status = TaskStatus.CANCELLED
            
            # Shutdown agent orchestrator
            await agent_orchestrator.shutdown_all_agents()
            
            self._is_initialized = False
            logger.info("Agent integration service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during agent integration service shutdown: {e}")
    
    async def execute_agent_task(
        self,
        agent_name: str,
        task_description: str,
        context: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute a task using a specific agent."""
        task_id = self._generate_task_id()
        
        task = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            crew_name=None,
            task_description=task_description,
            context=context
        )
        
        self._tasks[task_id] = task
        
        try:
            logger.info(f"Executing agent task {task_id} with agent '{agent_name}'")
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # Execute task with timeout
            if timeout:
                result = await asyncio.wait_for(
                    agent_orchestrator.execute_agent_task(agent_name, task_description, context),
                    timeout=timeout
                )
            else:
                result = await agent_orchestrator.execute_agent_task(agent_name, task_description, context)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            task.execution_time = (task.completed_at - task.started_at).total_seconds()
            
            # Update metrics
            self._update_metrics(task)
            
            logger.info(f"Agent task {task_id} completed successfully in {task.execution_time:.2f}s")
            
            return {
                "success": True,
                "task_id": task_id,
                "result": result,
                "execution_time": task.execution_time
            }
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error_message = f"Task timed out after {timeout}s"
            task.completed_at = datetime.utcnow()
            
            logger.error(f"Agent task {task_id} timed out")
            
            return {
                "success": False,
                "task_id": task_id,
                "error": task.error_message
            }
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            logger.error(f"Agent task {task_id} failed: {e}")
            
            return {
                "success": False,
                "task_id": task_id,
                "error": task.error_message
            }
    
    async def execute_crew_task(
        self,
        crew_name: str,
        task_description: str,
        context: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute a task using a crew of agents."""
        task_id = self._generate_task_id()
        
        task = AgentTask(
            task_id=task_id,
            agent_name="crew",
            crew_name=crew_name,
            task_description=task_description,
            context=context
        )
        
        self._tasks[task_id] = task
        
        try:
            logger.info(f"Executing crew task {task_id} with crew '{crew_name}'")
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # Execute crew task with timeout
            if timeout:
                result = await asyncio.wait_for(
                    agent_orchestrator.execute_crew_task(crew_name, task_description, context),
                    timeout=timeout
                )
            else:
                result = await agent_orchestrator.execute_crew_task(crew_name, task_description, context)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            task.execution_time = (task.completed_at - task.started_at).total_seconds()
            
            # Update metrics
            self._update_metrics(task)
            
            logger.info(f"Crew task {task_id} completed successfully in {task.execution_time:.2f}s")
            
            return {
                "success": True,
                "task_id": task_id,
                "result": result,
                "execution_time": task.execution_time
            }
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error_message = f"Task timed out after {timeout}s"
            task.completed_at = datetime.utcnow()
            
            logger.error(f"Crew task {task_id} timed out")
            
            return {
                "success": False,
                "task_id": task_id,
                "error": task.error_message
            }
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            logger.error(f"Crew task {task_id} failed: {e}")
            
            return {
                "success": False,
                "task_id": task_id,
                "error": task.error_message
            }
    
    # Specialized task execution methods for different analysis types
    
    async def analyze_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data quality using the data validator agent."""
        return await self.execute_agent_task(
            agent_name="data_validator",
            task_description="Analyze data quality and identify issues",
            context={"data": data, "analysis_type": "quality_check"},
            timeout=30.0
        )
    
    async def generate_forecast(
        self,
        data_type: str,
        series_data: List[Dict[str, Any]],
        forecast_horizon: int = 30
    ) -> Dict[str, Any]:
        """Generate time series forecast using the forecaster agent."""
        return await self.execute_agent_task(
            agent_name="timeseries_forecaster",
            task_description=f"Generate {forecast_horizon}-period forecast for {data_type} data",
            context={
                "data_type": data_type,
                "series_data": series_data,
                "forecast_horizon": forecast_horizon,
                "analysis_type": "forecast"
            },
            timeout=60.0
        )
    
    async def analyze_volatility(
        self,
        stock_data: List[Dict[str, Any]],
        weather_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Analyze volatility patterns using the volatility analyzer agent."""
        context = {
            "stock_data": stock_data,
            "analysis_type": "volatility"
        }
        
        if weather_data:
            context["weather_data"] = weather_data
            context["analysis_type"] = "weather_volatility_correlation"
        
        return await self.execute_agent_task(
            agent_name="volatility_analyzer",
            task_description="Analyze volatility patterns and weather correlations",
            context=context,
            timeout=45.0
        )
    
    async def generate_insights(
        self,
        analysis_data: Dict[str, Any],
        insight_type: str = "correlation"
    ) -> Dict[str, Any]:
        """Generate insights using the insight generator agent."""
        return await self.execute_agent_task(
            agent_name="insight_generator",
            task_description=f"Generate {insight_type} insights from analysis data",
            context={
                "analysis_data": analysis_data,
                "insight_type": insight_type,
                "analysis_type": "insight_generation"
            },
            timeout=30.0
        )
    
    async def perform_full_analysis(
        self,
        weather_data: List[Dict[str, Any]],
        stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform full analysis using the complete crew."""
        return await self.execute_crew_task(
            crew_name="full_analysis_crew",
            task_description="Perform comprehensive weather-stock correlation analysis",
            context={
                "weather_data": weather_data,
                "stock_data": stock_data,
                "analysis_type": "full_analysis"
            },
            timeout=120.0
        )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "agent_name": task.agent_name,
            "crew_name": task.crew_name,
            "task_description": task.task_description,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "execution_time": task.execution_time,
            "error_message": task.error_message
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task execution history."""
        # Sort tasks by creation time (most recent first)
        sorted_tasks = sorted(
            self._tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )
        
        return [
            self.get_task_status(task.task_id)
            for task in sorted_tasks[:limit]
        ]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents and crews."""
        try:
            agents_status = agent_orchestrator.get_all_agents_status()
            crews_status = {
                name: agent_orchestrator.get_crew_status(name)
                for name in agent_orchestrator.crews.keys()
            }
            
            return {
                "initialized": self._is_initialized,
                "agents": agents_status,
                "crews": crews_status,
                "performance_metrics": self._performance_metrics,
                "active_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.RUNNING])
            }
            
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {
                "initialized": self._is_initialized,
                "error": str(e)
            }
    
    async def health_check(self) -> bool:
        """Check if the agent integration service is healthy."""
        try:
            if not self._is_initialized:
                return False
            
            # Check if agents are responsive
            agents_status = agent_orchestrator.get_all_agents_status()
            if not agents_status:
                return False
            
            # Try a simple task execution
            test_result = await self.execute_agent_task(
                agent_name="data_validator",
                task_description="Health check test",
                context={"test": True},
                timeout=10.0
            )
            
            return test_result.get("success", False)
            
        except Exception as e:
            logger.error(f"Agent integration health check failed: {e}")
            return False
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        self._task_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"task_{timestamp}_{self._task_counter:04d}"
    
    def _update_metrics(self, task: AgentTask) -> None:
        """Update performance metrics."""
        self._performance_metrics["total_tasks"] += 1
        
        if task.status == TaskStatus.COMPLETED:
            self._performance_metrics["completed_tasks"] += 1
            
            # Update average execution time
            if task.execution_time:
                current_avg = self._performance_metrics["average_execution_time"]
                total_completed = self._performance_metrics["completed_tasks"]
                
                new_avg = ((current_avg * (total_completed - 1)) + task.execution_time) / total_completed
                self._performance_metrics["average_execution_time"] = new_avg
        
        elif task.status == TaskStatus.FAILED:
            self._performance_metrics["failed_tasks"] += 1
        
        # Update agent usage statistics
        agent_key = task.crew_name or task.agent_name
        if agent_key not in self._performance_metrics["agent_usage"]:
            self._performance_metrics["agent_usage"][agent_key] = 0
        self._performance_metrics["agent_usage"][agent_key] += 1


# Global agent integration service instance
agent_integration_service = AgentIntegrationService()