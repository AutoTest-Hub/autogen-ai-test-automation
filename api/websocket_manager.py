"""
WebSocket Manager for Real-Time Agent Activity
Handles WebSocket connections and real-time communication with clients
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum
import weakref

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    GENERATING = "generating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"

class AgentType(Enum):
    """Agent type enumeration"""
    DISCOVERY = "discovery"
    REQUIREMENTS = "requirements"
    TEST_GENERATION = "test_generation"
    CODE_GENERATION = "code_generation"
    VALIDATION = "validation"
    EXECUTION = "execution"
    REPORTING = "reporting"
    SELF_HEALING = "self_healing"
    PRIORITIZATION = "prioritization"
    CROSS_BROWSER = "cross_browser"
    PERFORMANCE = "performance"

class AgentActivity:
    """Represents an agent activity/task"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, task_id: str, user_id: str):
        self.id = str(uuid.uuid4())
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.task_id = task_id
        self.user_id = user_id
        self.status = AgentStatus.IDLE
        self.progress = 0
        self.current_step = ""
        self.steps_completed = 0
        self.total_steps = 0
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.logs: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
    def add_log(self, level: str, message: str, details: Optional[Dict] = None):
        """Add a log entry to the activity"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "details": details or {}
        }
        self.logs.append(log_entry)
        
    def update_progress(self, progress: int, current_step: str = ""):
        """Update the progress of the activity"""
        self.progress = min(100, max(0, progress))
        if current_step:
            self.current_step = current_step
        self.add_log("info", f"Progress: {self.progress}% - {current_step}")
        
    def complete_step(self, step_name: str):
        """Mark a step as completed"""
        self.steps_completed += 1
        if self.total_steps > 0:
            self.progress = int((self.steps_completed / self.total_steps) * 100)
        self.add_log("info", f"Completed step: {step_name}")
        
    def set_status(self, status: AgentStatus, message: str = ""):
        """Update the agent status"""
        self.status = status
        if status == AgentStatus.COMPLETED:
            self.end_time = datetime.utcnow()
            self.progress = 100
        elif status == AgentStatus.ERROR:
            self.end_time = datetime.utcnow()
            
        self.add_log("info" if status != AgentStatus.ERROR else "error", 
                    f"Status changed to {status.value}: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            "logs": self.logs[-10:],  # Only send last 10 logs to avoid overwhelming the client
            "metadata": self.metadata
        }

class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Agent activities by task_id
        self.activities: Dict[str, List[AgentActivity]] = {}
        # Agent activities by user_id for quick lookup
        self.user_activities: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket connected for user {user_id}")
        
        # Send current activities for this user
        await self.send_user_activities(user_id)
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
        
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections for a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Remove disconnected websockets
            for ws in disconnected:
                self.active_connections[user_id].discard(ws)
                
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected clients"""
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)
            
    def create_activity(self, agent_type: AgentType, task_id: str, user_id: str, 
                       total_steps: int = 0, metadata: Dict = None) -> AgentActivity:
        """Create a new agent activity"""
        agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
        activity = AgentActivity(agent_id, agent_type, task_id, user_id)
        activity.total_steps = total_steps
        activity.metadata = metadata or {}
        
        # Store activity
        if task_id not in self.activities:
            self.activities[task_id] = []
        self.activities[task_id].append(activity)
        
        # Track user activities
        if user_id not in self.user_activities:
            self.user_activities[user_id] = set()
        self.user_activities[user_id].add(activity.id)
        
        logger.info(f"Created activity {activity.id} for agent {agent_id}")
        return activity
        
    async def update_activity(self, activity_id: str, **kwargs):
        """Update an agent activity and broadcast changes"""
        activity = self.get_activity(activity_id)
        if not activity:
            return
            
        # Update activity properties
        for key, value in kwargs.items():
            if hasattr(activity, key):
                setattr(activity, key, value)
                
        # Broadcast update
        await self.send_personal_message({
            "type": "activity_update",
            "activity": activity.to_dict()
        }, activity.user_id)
        
    async def update_activity_progress(self, activity_id: str, progress: int, current_step: str = ""):
        """Update activity progress and broadcast"""
        activity = self.get_activity(activity_id)
        if activity:
            activity.update_progress(progress, current_step)
            await self.send_personal_message({
                "type": "progress_update",
                "activity_id": activity_id,
                "progress": progress,
                "current_step": current_step,
                "activity": activity.to_dict()
            }, activity.user_id)
            
    async def update_activity_status(self, activity_id: str, status: AgentStatus, message: str = ""):
        """Update activity status and broadcast"""
        activity = self.get_activity(activity_id)
        if activity:
            activity.set_status(status, message)
            await self.send_personal_message({
                "type": "status_update",
                "activity_id": activity_id,
                "status": status.value,
                "message": message,
                "activity": activity.to_dict()
            }, activity.user_id)
            
    async def add_activity_log(self, activity_id: str, level: str, message: str, details: Dict = None):
        """Add a log entry to an activity and broadcast"""
        activity = self.get_activity(activity_id)
        if activity:
            activity.add_log(level, message, details)
            await self.send_personal_message({
                "type": "log_update",
                "activity_id": activity_id,
                "log": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": level,
                    "message": message,
                    "details": details or {}
                }
            }, activity.user_id)
            
    def get_activity(self, activity_id: str) -> Optional[AgentActivity]:
        """Get an activity by ID"""
        for task_activities in self.activities.values():
            for activity in task_activities:
                if activity.id == activity_id:
                    return activity
        return None
        
    def get_task_activities(self, task_id: str) -> List[AgentActivity]:
        """Get all activities for a task"""
        return self.activities.get(task_id, [])
        
    def get_user_activities(self, user_id: str) -> List[AgentActivity]:
        """Get all activities for a user"""
        user_activity_ids = self.user_activities.get(user_id, set())
        activities = []
        for task_activities in self.activities.values():
            for activity in task_activities:
                if activity.id in user_activity_ids:
                    activities.append(activity)
        return sorted(activities, key=lambda x: x.start_time, reverse=True)
        
    async def send_user_activities(self, user_id: str):
        """Send current activities for a user"""
        activities = self.get_user_activities(user_id)
        await self.send_personal_message({
            "type": "activities_list",
            "activities": [activity.to_dict() for activity in activities]
        }, user_id)
        
    def cleanup_old_activities(self, hours: int = 24):
        """Clean up activities older than specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        for task_id in list(self.activities.keys()):
            activities = self.activities[task_id]
            # Keep activities that are still active or recent
            self.activities[task_id] = [
                activity for activity in activities
                if activity.status not in [AgentStatus.COMPLETED, AgentStatus.ERROR] 
                or activity.start_time > cutoff_time
            ]
            
            # Remove empty task entries
            if not self.activities[task_id]:
                del self.activities[task_id]

# Global connection manager instance
manager = ConnectionManager()

# Cleanup task
async def cleanup_task():
    """Background task to cleanup old activities"""
    while True:
        try:
            manager.cleanup_old_activities()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying
