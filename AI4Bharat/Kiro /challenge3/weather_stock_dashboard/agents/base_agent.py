"""Base agent framework for CrewAI agents."""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

try:
    from crewai import Agent, Task, Crew
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # Create mock classes for development
    class Agent:
        def __init__(self, **kwargs):
            pass
    
    class Task:
        def __init__(self, **kwargs):
            pass
    
    class Crew:
        def __init__(self, **kwargs):
            pass
    
    class BaseTool:
        def __init__(self, **kwargs):
            pass

from config.settings import settings

logger = logging.getLogger(__name__)


class BaseWeatherStockAgent(ABC):
    """Base class for weather-stock analysis agents."""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        """Initialize base agent."""
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.agent = None
        self.tools = []
        self.memory = {}
        
        if not CREWAI_AVAILABLE:
            logger.warning("CrewAI not available - agent functionality will be limited")
        
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the CrewAI agent."""
        try:
            if CREWAI_AVAILABLE:
                self.agent = Agent(
                    role=self.role,
                    goal=self.goal,
                    backstory=self.backstory,
                    tools=self.tools,
                    verbose=True,
                    allow_delegation=False
                )
                logger.info(f"Initialized agent: {self.name}")
            else:
                logger.warning(f"Mock agent created for {self.name}")
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.name}: {e}")
            raise
    
    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Get tools specific to this agent."""
        pass
    
    @abstractmethod
    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task."""
        pass
    
    def update_memory(self, key: str, value: Any):
        """Update agent memory."""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.debug(f"Updated memory for {self.name}: {key}")
    
    def get_memory(self, key: str) -> Optional[Any]:
        """Get value from agent memory."""
        memory_item = self.memory.get(key)
        return memory_item["value"] if memory_item else None
    
    def clear_memory(self):
        """Clear agent memory."""
        self.memory.clear()
        logger.info(f"Cleared memory for {self.name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "tools_count": len(self.tools),
            "memory_items": len(self.memory),
            "is_initialized": self.agent is not None,
            "crewai_available": CREWAI_AVAILABLE
        }


class AgentOrchestrator:
    """Orchestrator for managing multiple CrewAI agents."""
    
    def __init__(self):
        """Initialize agent orchestrator."""
        self.agents = {}
        self.crews = {}
        self.task_history = []
        self.shared_context = {}
        
    def register_agent(self, agent: BaseWeatherStockAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def create_crew(self, crew_name: str, agent_names: List[str], 
                   process_type: str = "sequential") -> bool:
        """Create a crew from registered agents."""
        try:
            if not CREWAI_AVAILABLE:
                logger.warning(f"CrewAI not available - mock crew created: {crew_name}")
                self.crews[crew_name] = {
                    "agents": agent_names,
                    "process_type": process_type,
                    "mock": True
                }
                return True
            
            # Get agents for the crew
            crew_agents = []
            for agent_name in agent_names:
                if agent_name in self.agents:
                    crew_agents.append(self.agents[agent_name].agent)
                else:
                    logger.error(f"Agent {agent_name} not found for crew {crew_name}")
                    return False
            
            # Create crew
            crew = Crew(
                agents=crew_agents,
                process=process_type,
                verbose=True
            )
            
            self.crews[crew_name] = {
                "crew": crew,
                "agents": agent_names,
                "process_type": process_type,
                "mock": False
            }
            
            logger.info(f"Created crew: {crew_name} with agents: {agent_names}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create crew {crew_name}: {e}")
            return False
    
    async def execute_crew_task(self, crew_name: str, task_description: str, 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task using a specific crew."""
        try:
            if crew_name not in self.crews:
                raise ValueError(f"Crew {crew_name} not found")
            
            crew_info = self.crews[crew_name]
            context = context or {}
            
            # Update shared context
            self.shared_context.update(context)
            
            # Record task start
            task_record = {
                "crew_name": crew_name,
                "task_description": task_description,
                "start_time": datetime.utcnow().isoformat(),
                "context": context
            }
            
            if crew_info.get("mock", False):
                # Mock execution for development
                result = await self._mock_crew_execution(crew_name, task_description, context)
            else:
                # Real CrewAI execution
                if not CREWAI_AVAILABLE:
                    raise ValueError("CrewAI not available for real execution")
                
                # Create task
                task = Task(
                    description=task_description,
                    expected_output="Detailed analysis and recommendations"
                )
                
                # Execute crew
                crew = crew_info["crew"]
                result = crew.kickoff(inputs=context)
            
            # Record task completion
            task_record.update({
                "end_time": datetime.utcnow().isoformat(),
                "result": result,
                "status": "completed"
            })
            
            self.task_history.append(task_record)
            logger.info(f"Completed crew task for {crew_name}")
            
            return {
                "crew_name": crew_name,
                "task_description": task_description,
                "result": result,
                "execution_time": task_record["end_time"],
                "agents_involved": crew_info["agents"]
            }
            
        except Exception as e:
            logger.error(f"Failed to execute crew task for {crew_name}: {e}")
            
            # Record failure
            task_record = {
                "crew_name": crew_name,
                "task_description": task_description,
                "start_time": datetime.utcnow().isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "error": str(e),
                "status": "failed"
            }
            self.task_history.append(task_record)
            
            raise
    
    async def _mock_crew_execution(self, crew_name: str, task_description: str, 
                                  context: Dict[str, Any]) -> str:
        """Mock crew execution for development/testing."""
        agent_names = self.crews[crew_name]["agents"]
        
        # Simulate agent collaboration
        results = []
        for agent_name in agent_names:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                try:
                    agent_result = await agent.execute_task(task_description, context)
                    results.append(f"{agent_name}: {agent_result.get('summary', 'Task completed')}")
                except Exception as e:
                    results.append(f"{agent_name}: Error - {str(e)}")
        
        return f"Mock crew execution completed. Results: {'; '.join(results)}"
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent."""
        if agent_name in self.agents:
            return self.agents[agent_name].get_status()
        return None
    
    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents."""
        return {name: agent.get_status() for name, agent in self.agents.items()}
    
    def get_crew_status(self, crew_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific crew."""
        if crew_name in self.crews:
            crew_info = self.crews[crew_name]
            return {
                "name": crew_name,
                "agents": crew_info["agents"],
                "process_type": crew_info["process_type"],
                "is_mock": crew_info.get("mock", False),
                "agent_count": len(crew_info["agents"])
            }
        return None
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task execution history."""
        return self.task_history[-limit:] if self.task_history else []
    
    def update_shared_context(self, key: str, value: Any):
        """Update shared context available to all agents."""
        self.shared_context[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.debug(f"Updated shared context: {key}")
    
    def get_shared_context(self) -> Dict[str, Any]:
        """Get current shared context."""
        return self.shared_context


# Global agent orchestrator instance
agent_orchestrator = AgentOrchestrator()