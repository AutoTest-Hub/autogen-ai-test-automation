"""
WebSocket Endpoints for Real-Time Agent Activity
Provides WebSocket endpoints for real-time communication
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from websocket_manager import manager, AgentType, AgentStatus
from auth import get_current_user_websocket

# Configure logging
logger = logging.getLogger(__name__)

# Create router for WebSocket endpoints
router = APIRouter()

@router.websocket("/ws/agent-activity/{user_id}")
async def websocket_agent_activity(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time agent activity updates
    """
    try:
        # Connect to the WebSocket manager
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to agent activity stream",
            "user_id": user_id
        }))
        
        # Listen for messages from client
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Respond to ping with pong
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }))
                    
                elif message_type == "get_activities":
                    # Send current activities for the user
                    await manager.send_user_activities(user_id)
                    
                elif message_type == "subscribe_task":
                    # Subscribe to updates for a specific task
                    task_id = message.get("task_id")
                    if task_id:
                        activities = manager.get_task_activities(task_id)
                        await websocket.send_text(json.dumps({
                            "type": "task_activities",
                            "task_id": task_id,
                            "activities": [activity.to_dict() for activity in activities]
                        }))
                        
                elif message_type == "get_activity_logs":
                    # Get detailed logs for a specific activity
                    activity_id = message.get("activity_id")
                    activity = manager.get_activity(activity_id)
                    if activity and activity.user_id == user_id:
                        await websocket.send_text(json.dumps({
                            "type": "activity_logs",
                            "activity_id": activity_id,
                            "logs": activity.logs
                        }))
                        
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from client")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Error processing message"
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        # Clean up connection
        manager.disconnect(websocket, user_id)

@router.websocket("/ws/system-status")
async def websocket_system_status(websocket: WebSocket):
    """
    WebSocket endpoint for system-wide status updates
    """
    try:
        await websocket.accept()
        
        # Send system status updates
        while True:
            try:
                # Get system statistics
                total_activities = sum(len(activities) for activities in manager.activities.values())
                active_activities = sum(
                    1 for activities in manager.activities.values()
                    for activity in activities
                    if activity.status not in [AgentStatus.COMPLETED, AgentStatus.ERROR]
                )
                connected_users = len(manager.active_connections)
                
                system_status = {
                    "type": "system_status",
                    "timestamp": datetime.utcnow().isoformat(),
                    "statistics": {
                        "total_activities": total_activities,
                        "active_activities": active_activities,
                        "connected_users": connected_users,
                        "total_connections": sum(len(connections) for connections in manager.active_connections.values())
                    }
                }
                
                await websocket.send_text(json.dumps(system_status))
                
                # Wait 10 seconds before next update
                await asyncio.sleep(10)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in system status WebSocket: {e}")
                break
                
    except Exception as e:
        logger.error(f"System status WebSocket error: {e}")

# Helper functions for creating and managing activities
async def create_agent_activity(agent_type: AgentType, task_id: str, user_id: str, 
                               total_steps: int = 0, metadata: dict = None):
    """Create a new agent activity and notify connected clients"""
    activity = manager.create_activity(agent_type, task_id, user_id, total_steps, metadata)
    
    # Notify the user about the new activity
    await manager.send_personal_message({
        "type": "activity_created",
        "activity": activity.to_dict()
    }, user_id)
    
    return activity

async def simulate_agent_work(activity_id: str, steps: list, delay_between_steps: float = 1.0):
    """
    Simulate agent work with realistic progress updates
    This is a helper function for testing and demonstration
    """
    import asyncio
    
    activity = manager.get_activity(activity_id)
    if not activity:
        return
        
    try:
        # Set status to processing
        await manager.update_activity_status(activity_id, AgentStatus.PROCESSING, "Starting work...")
        
        for i, step in enumerate(steps):
            # Update current step
            progress = int(((i + 1) / len(steps)) * 100)
            await manager.update_activity_progress(activity_id, progress, step)
            
            # Add log entry
            await manager.add_activity_log(activity_id, "info", f"Executing: {step}")
            
            # Simulate work delay
            await asyncio.sleep(delay_between_steps)
            
        # Mark as completed
        await manager.update_activity_status(activity_id, AgentStatus.COMPLETED, "Work completed successfully")
        
    except Exception as e:
        logger.error(f"Error in agent simulation: {e}")
        await manager.update_activity_status(activity_id, AgentStatus.ERROR, f"Error: {str(e)}")

# Import required modules
import asyncio
from datetime import datetime
