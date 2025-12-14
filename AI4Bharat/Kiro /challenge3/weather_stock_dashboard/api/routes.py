"""API routes for Weather Stock Dashboard."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from weather_stock_dashboard.services.rag_engine import rag_engine
from weather_stock_dashboard.services.data_collector import data_collector_service
from weather_stock_dashboard.services.chromadb_service import chromadb_service
from weather_stock_dashboard.core.agent_integration import agent_integration_service
from weather_stock_dashboard.services.correlation_service import correlation_service
from weather_stock_dashboard.services.timeseries_service import timeseries_service
from weather_stock_dashboard.services.garch_service import garch_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class NaturalLanguageQueryRequest(BaseModel):
    """Request model for natural language queries."""
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class TimeSeriesForecastRequest(BaseModel):
    """Request model for time series forecasting."""
    data_type: str = Field(..., description="Type of data: 'weather' or 'stock'")
    series_id: str = Field(..., description="Series identifier")
    forecast_horizon: int = Field(default=30, ge=1, le=365, description="Forecast horizon in periods")
    arima_order: Optional[tuple] = Field(None, description="Optional ARIMA order (p,d,q)")


class CorrelationAnalysisRequest(BaseModel):
    """Request model for correlation analysis."""
    weather_variable: str = Field(default="temperature", description="Weather variable to analyze")
    stock_symbols: List[str] = Field(..., description="List of stock symbols")
    time_period: Optional[str] = Field(None, description="Time period for analysis")


class ARIMAModelRequest(BaseModel):
    """Request model for ARIMA model fitting."""
    series_data: List[Dict[str, Any]] = Field(..., description="Time series data")
    value_column: str = Field(..., description="Column name for values")
    order: Optional[tuple] = Field(None, description="ARIMA order (p,d,q)")


class GARCHModelRequest(BaseModel):
    """Request model for GARCH model fitting."""
    stock_data: List[Dict[str, Any]] = Field(..., description="Stock price data")
    symbol: str = Field(..., description="Stock symbol")
    model_type: str = Field(default="GARCH", description="GARCH model type")


# Middleware and Dependencies
async def get_api_stats():
    """Get API statistics for monitoring."""
    try:
        # Get collection stats from ChromaDB
        collection_stats = await chromadb_service.get_collection_stats()
        
        # Get data collector status
        collector_status = await data_collector_service.get_collection_status()
        
        # Get agent status
        agent_status = agent_orchestrator.get_all_agents_status()
        
        return {
            "collections": collection_stats,
            "data_collector": collector_status,
            "agents": agent_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        return {"error": str(e)}


# Core API Routes
@router.get("/status")
async def api_status():
    """API status endpoint with system health information."""
    try:
        stats = await get_api_stats()
        return {
            "status": "healthy",
            "version": "0.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "system_stats": stats
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "weather-stock-dashboard"
    }

# Dashboard Data Endpoints
@router.get("/dashboard/current")
async def get_current_dashboard_data():
    """Get current weather and stock data for dashboard."""
    try:
        # Get latest data from collections
        stats = await get_api_stats()
        
        # Get recent data samples
        weather_results = await chromadb_service.search_weather_data("current weather", n_results=5)
        stock_results = await chromadb_service.search_stock_data("current prices", n_results=5)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": stats,
            "recent_weather": weather_results,
            "recent_stocks": stock_results,
            "data_freshness": {
                "weather_count": len(weather_results),
                "stock_count": len(stock_results)
            }
        }
    except Exception as e:
        logger.error(f"Dashboard data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {str(e)}")


@router.get("/data/historical")
async def get_historical_data(
    data_type: str = Query(..., description="Data type: 'weather' or 'stock'"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to retrieve"),
    search_query: Optional[str] = Query(None, description="Optional search query")
):
    """Get historical weather and stock data."""
    try:
        if data_type == "weather":
            if search_query:
                results = await chromadb_service.search_weather_data(search_query, n_results=limit)
            else:
                results = await chromadb_service.search_weather_data("weather data", n_results=limit)
        elif data_type == "stock":
            if search_query:
                results = await chromadb_service.search_stock_data(search_query, n_results=limit)
            else:
                results = await chromadb_service.search_stock_data("stock data", n_results=limit)
        else:
            raise HTTPException(status_code=400, detail="data_type must be 'weather' or 'stock'")
        
        return {
            "data_type": data_type,
            "query": search_query or "all data",
            "count": len(results),
            "data": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Historical data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve historical data: {str(e)}")


# Natural Language Query Endpoints
@router.post("/query/natural")
async def process_natural_language_query(request: NaturalLanguageQueryRequest):
    """Process natural language queries using RAG."""
    try:
        result = await rag_engine.process_query(request.query, request.user_id)
        
        return {
            "success": True,
            "query": request.query,
            "user_id": request.user_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Natural language query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


# Time Series Analysis Endpoints
@router.post("/timeseries/forecast")
async def create_timeseries_forecast(request: TimeSeriesForecastRequest):
    """Create ARIMA/GARCH time series forecasts."""
    try:
        # Use agent orchestrator for forecasting
        context = {
            "task_type": "forecast",
            "data_type": request.data_type,
            "series_id": request.series_id,
            "forecast_horizon": request.forecast_horizon,
            "arima_order": request.arima_order
        }
        
        result = await agent_integration_service.execute_crew_task(
            "data_analysis_crew",
            f"Generate {request.forecast_horizon}-period forecast for {request.series_id}",
            context
        )
        
        return {
            "success": True,
            "forecast_request": request.dict(),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Time series forecasting failed: {e}")
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")


@router.get("/analysis/cross-correlation")
async def get_cross_correlation_analysis(
    weather_variable: str = Query(default="temperature", description="Weather variable"),
    stock_symbol: str = Query(..., description="Stock symbol"),
    max_lags: int = Query(default=20, ge=1, le=50, description="Maximum lags to analyze")
):
    """Get cross-correlation analysis between weather and stock series."""
    try:
        # This would need actual data - for now return mock analysis
        result = {
            "weather_variable": weather_variable,
            "stock_symbol": stock_symbol,
            "max_lags": max_lags,
            "analysis": "Cross-correlation analysis would be performed here with actual data",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return result
    except Exception as e:
        logger.error(f"Cross-correlation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Model Fitting Endpoints
@router.post("/models/arima")
async def fit_arima_model(request: ARIMAModelRequest):
    """Fit ARIMA models to time series data."""
    try:
        # Prepare time series
        ts = timeseries_service.prepare_time_series(request.series_data, request.value_column)
        
        # Fit ARIMA model
        arima_result = timeseries_service.fit_arima_model(ts, request.order)
        
        return {
            "success": True,
            "model_type": "ARIMA",
            "data_points": len(ts),
            "arima_order": arima_result["order"],
            "model_quality": {
                "aic": arima_result["aic"],
                "bic": arima_result["bic"]
            },
            "forecast": arima_result["forecast"],
            "forecast_confidence_intervals": arima_result["forecast_confidence_intervals"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"ARIMA model fitting failed: {e}")
        raise HTTPException(status_code=500, detail=f"ARIMA modeling failed: {str(e)}")


@router.post("/models/garch")
async def fit_garch_model(request: GARCHModelRequest):
    """Fit GARCH models for volatility analysis."""
    try:
        # Analyze stock volatility using GARCH service
        result = garch_service.analyze_stock_volatility(request.stock_data, request.symbol)
        
        return {
            "success": True,
            "model_type": "GARCH",
            "symbol": request.symbol,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"GARCH model fitting failed: {e}")
        raise HTTPException(status_code=500, detail=f"GARCH modeling failed: {str(e)}")


# Correlation and Insights Endpoints
@router.get("/insights/correlations")
async def get_correlation_insights(
    weather_variables: List[str] = Query(default=["temperature"], description="Weather variables to analyze"),
    stock_symbols: List[str] = Query(default=["AAPL"], description="Stock symbols to analyze"),
    generate_insights: bool = Query(default=True, description="Generate AI insights")
):
    """Get AI-generated correlation insights."""
    try:
        if generate_insights:
            # Use insight generation crew
            context = {
                "task_type": "generate_insights",
                "analysis_type": "correlation",
                "weather_variables": weather_variables,
                "stock_symbols": stock_symbols
            }
            
            result = await agent_integration_service.execute_crew_task(
                "insight_generation_crew",
                f"Generate correlation insights for {weather_variables} vs {stock_symbols}",
                context
            )
        else:
            result = {
                "message": "Correlation analysis would be performed here",
                "weather_variables": weather_variables,
                "stock_symbols": stock_symbols
            }
        
        return {
            "success": True,
            "analysis_type": "correlation_insights",
            "parameters": {
                "weather_variables": weather_variables,
                "stock_symbols": stock_symbols
            },
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Correlation insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")


# Data Collection Management Endpoints
@router.get("/data/collection/status")
async def get_data_collection_status():
    """Get status of data collection processes."""
    try:
        status = await data_collector_service.get_collection_status()
        return {
            "success": True,
            "collection_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get collection status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.post("/data/collection/trigger")
async def trigger_data_collection(
    data_type: str = Query(..., description="Data type: 'weather' or 'stock'"),
    locations_or_symbols: List[str] = Query(..., description="Locations for weather or symbols for stocks")
):
    """Manually trigger data collection."""
    try:
        if data_type == "weather":
            result = await data_collector_service.collect_weather_data_manual(locations_or_symbols)
        elif data_type == "stock":
            result = await data_collector_service.collect_stock_data_manual(locations_or_symbols)
        else:
            raise HTTPException(status_code=400, detail="data_type must be 'weather' or 'stock'")
        
        return {
            "success": True,
            "data_type": data_type,
            "targets": locations_or_symbols,
            "collected_count": len(result),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual data collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Data collection failed: {str(e)}")


# Agent Management Endpoints
@router.get("/agents/status")
async def get_agents_status():
    """Get status of all AI agents."""
    try:
        agent_status = agent_integration_service.get_agent_status()
        
        return {
            "success": True,
            "agent_status": agent_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get agents status: {e}")
        raise HTTPException(status_code=500, detail=f"Agent status retrieval failed: {str(e)}")


@router.get("/agents/history")
async def get_agent_task_history(limit: int = Query(default=10, ge=1, le=100)):
    """Get recent agent task execution history."""
    try:
        history = agent_integration_service.get_task_history(limit)
        return {
            "success": True,
            "task_count": len(history),
            "tasks": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get task history: {e}")
        raise HTTPException(status_code=500, detail=f"Task history retrieval failed: {str(e)}")