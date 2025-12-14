"""CrewAI agents for intelligent data analysis and insight generation."""

from .base_agent import BaseWeatherStockAgent, AgentOrchestrator, agent_orchestrator
from .data_validator_agent import DataValidatorAgent
from .forecaster_agent import TimeSeriesForecasterAgent
from .volatility_agent import VolatilityAnalyzerAgent
from .insight_agent import InsightGeneratorAgent

__all__ = [
    "BaseWeatherStockAgent",
    "AgentOrchestrator", 
    "agent_orchestrator",
    "DataValidatorAgent",
    "TimeSeriesForecasterAgent",
    "VolatilityAnalyzerAgent",
    "InsightGeneratorAgent"
]


def initialize_agents():
    """Initialize and register all agents with the orchestrator."""
    # Create agent instances
    data_validator = DataValidatorAgent()
    forecaster = TimeSeriesForecasterAgent()
    volatility_analyzer = VolatilityAnalyzerAgent()
    insight_generator = InsightGeneratorAgent()
    
    # Register agents with orchestrator
    agent_orchestrator.register_agent(data_validator)
    agent_orchestrator.register_agent(forecaster)
    agent_orchestrator.register_agent(volatility_analyzer)
    agent_orchestrator.register_agent(insight_generator)
    
    # Create specialized crews
    agent_orchestrator.create_crew(
        "data_analysis_crew",
        ["data_validator", "timeseries_forecaster", "volatility_analyzer"],
        "sequential"
    )
    
    agent_orchestrator.create_crew(
        "insight_generation_crew", 
        ["volatility_analyzer", "insight_generator"],
        "sequential"
    )
    
    agent_orchestrator.create_crew(
        "full_analysis_crew",
        ["data_validator", "timeseries_forecaster", "volatility_analyzer", "insight_generator"],
        "sequential"
    )
    
    return agent_orchestrator