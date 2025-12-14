"""WebSocket handlers for real-time data updates."""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

from weather_stock_dashboard.core.app_manager import app_manager
from weather_stock_dashboard.core.agent_integration import agent_integration_service

logger = logging.getLogger(__name__)

# WebSocket router
websocket_router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for topic, connections in self.subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSockets."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_topic(self, topic: str, message: str):
        """Send a message to all subscribers of a topic."""
        if topic not in self.subscriptions:
            return
        
        disconnected = []
        
        for connection in self.subscriptions[topic]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending topic message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            if connection in self.subscriptions[topic]:
                self.subscriptions[topic].remove(connection)
    
    def subscribe_to_topic(self, websocket: WebSocket, topic: str):
        """Subscribe a WebSocket to a topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        
        if websocket not in self.subscriptions[topic]:
            self.subscriptions[topic].append(websocket)
            logger.info(f"WebSocket subscribed to topic '{topic}'")
    
    def unsubscribe_from_topic(self, websocket: WebSocket, topic: str):
        """Unsubscribe a WebSocket from a topic."""
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)
            logger.info(f"WebSocket unsubscribed from topic '{topic}'")


# Global connection manager
manager = ConnectionManager()


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
            except json.JSONDecodeError:
                await send_error(websocket, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await send_error(websocket, str(e))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # Subscribe to a topic
        topic = message.get("topic")
        if topic:
            manager.subscribe_to_topic(websocket, topic)
            await send_response(websocket, {
                "type": "subscription_confirmed",
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    elif message_type == "unsubscribe":
        # Unsubscribe from a topic
        topic = message.get("topic")
        if topic:
            manager.unsubscribe_from_topic(websocket, topic)
            await send_response(websocket, {
                "type": "unsubscription_confirmed",
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    elif message_type == "get_status":
        # Get system status
        status = await app_manager.get_system_status()
        await send_response(websocket, {
            "type": "status_update",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    elif message_type == "get_agent_status":
        # Get agent status
        agent_status = agent_integration_service.get_agent_status()
        await send_response(websocket, {
            "type": "agent_status_update",
            "data": agent_status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    elif message_type == "ping":
        # Ping/pong for connection health
        await send_response(websocket, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    else:
        await send_error(websocket, f"Unknown message type: {message_type}")


async def send_response(websocket: WebSocket, data: Dict[str, Any]):
    """Send a response to a WebSocket."""
    try:
        message = json.dumps(data)
        await manager.send_personal_message(message, websocket)
    except Exception as e:
        logger.error(f"Error sending WebSocket response: {e}")


async def send_error(websocket: WebSocket, error_message: str):
    """Send an error message to a WebSocket."""
    error_data = {
        "type": "error",
        "message": error_message,
        "timestamp": datetime.utcnow().isoformat()
    }
    await send_response(websocket, error_data)


# Real-time update functions

async def broadcast_system_update(update_data: Dict[str, Any]):
    """Broadcast system status update to all subscribers."""
    message = json.dumps({
        "type": "system_update",
        "data": update_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.send_to_topic("system_updates", message)


async def broadcast_data_update(data_type: str, data: Dict[str, Any]):
    """Broadcast data update to subscribers."""
    message = json.dumps({
        "type": "data_update",
        "data_type": data_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.send_to_topic("data_updates", message)


async def broadcast_agent_update(agent_data: Dict[str, Any]):
    """Broadcast agent status update to subscribers."""
    message = json.dumps({
        "type": "agent_update",
        "data": agent_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.send_to_topic("agent_updates", message)


async def broadcast_task_update(task_data: Dict[str, Any]):
    """Broadcast task execution update to subscribers."""
    message = json.dumps({
        "type": "task_update",
        "data": task_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.send_to_topic("task_updates", message)


# Background task for periodic updates
async def periodic_updates():
    """Send periodic updates to connected clients."""
    while True:
        try:
            # Send system status update every 30 seconds
            if manager.subscriptions.get("system_updates"):
                status = await app_manager.get_system_status()
                await broadcast_system_update(status)
            
            # Send agent status update every 60 seconds
            if manager.subscriptions.get("agent_updates"):
                agent_status = agent_integration_service.get_agent_status()
                await broadcast_agent_update(agent_status)
            
            await asyncio.sleep(30)  # Update every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in periodic updates: {e}")
            await asyncio.sleep(30)


# Start periodic updates task
_periodic_task: Optional[asyncio.Task] = None


async def start_periodic_updates():
    """Start the periodic updates task."""
    global _periodic_task
    if _periodic_task is None or _periodic_task.done():
        _periodic_task = asyncio.create_task(periodic_updates())
        logger.info("Started WebSocket periodic updates")


async def stop_periodic_updates():
    """Stop the periodic updates task."""
    global _periodic_task
    if _periodic_task and not _periodic_task.done():
        _periodic_task.cancel()
        try:
            await _periodic_task
        except asyncio.CancelledError:
            pass
        logger.info("Stopped WebSocket periodic updates")