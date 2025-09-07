"""
Agent Coordinator for AutoGen Test Automation Framework
Manages agent interactions, communication, and coordination
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
from concurrent.futures import ThreadPoolExecutor

from config.settings import settings, AgentRole


class MessageType(str, Enum):
    """Types of messages between agents"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    ERROR_NOTIFICATION = "error_notification"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_RESPONSE = "resource_response"
    BROADCAST = "broadcast"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AgentMessage:
    """Represents a message between agents"""
    id: str
    sender_role: AgentRole
    recipient_role: AgentRole
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    created_at: datetime
    delivered_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    response_id: Optional[str] = None
    correlation_id: Optional[str] = None


@dataclass
class AgentStatus:
    """Represents the current status of an agent"""
    role: AgentRole
    status: str  # "idle", "busy", "error", "offline"
    current_task: Optional[str]
    workload: int
    last_activity: datetime
    capabilities: List[str]
    performance_metrics: Dict[str, float]


@dataclass
class CollaborationSession:
    """Represents a collaboration session between agents"""
    id: str
    participants: List[AgentRole]
    topic: str
    created_at: datetime
    messages: List[AgentMessage]
    status: str  # "active", "completed", "failed"
    result: Optional[Dict[str, Any]] = None


class AgentCoordinator:
    """Coordinates interactions and communication between agents"""
    
    def __init__(self):
        self.logger = logging.getLogger("orchestrator.coordinator")
        
        # Agent management
        self.registered_agents: Dict[AgentRole, Any] = {}
        self.agent_statuses: Dict[AgentRole, AgentStatus] = {}
        self.agent_capabilities: Dict[AgentRole, List[str]] = {}
        
        # Message management
        self.message_queue: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []
        self.pending_responses: Dict[str, AgentMessage] = {}
        
        # Collaboration management
        self.active_collaborations: Dict[str, CollaborationSession] = {}
        self.collaboration_history: List[CollaborationSession] = []
        
        # Resource management
        self.shared_resources: Dict[str, Any] = {}
        self.resource_locks: Dict[str, AgentRole] = {}
        
        # Performance tracking
        self.coordination_metrics = {
            "total_messages": 0,
            "successful_collaborations": 0,
            "failed_collaborations": 0,
            "average_response_time": 0.0,
            "agent_utilization": {}
        }
        
        # Message processing
        self.message_processor = None
        self.processing_active = False
        
        # Initialize default agent capabilities
        self._initialize_agent_capabilities()
    
    def _initialize_agent_capabilities(self):
        """Initialize default capabilities for each agent role"""
        self.agent_capabilities = {
            AgentRole.ORCHESTRATOR: [
                "workflow_management",
                "agent_coordination",
                "resource_allocation",
                "status_monitoring"
            ],
            AgentRole.PLANNING: [
                "test_strategy_creation",
                "requirement_analysis",
                "risk_assessment",
                "test_planning",
                "coverage_analysis"
            ],
            AgentRole.TEST_CREATION: [
                "code_generation",
                "test_automation",
                "framework_integration",
                "data_preparation",
                "environment_setup"
            ],
            AgentRole.REVIEW: [
                "code_review",
                "quality_assessment",
                "best_practices_validation",
                "security_analysis",
                "performance_review"
            ],
            AgentRole.EXECUTION: [
                "test_execution",
                "environment_management",
                "result_collection",
                "error_handling",
                "parallel_execution"
            ],
            AgentRole.REPORTING: [
                "report_generation",
                "data_analysis",
                "visualization",
                "trend_analysis",
                "strategic_insights"
            ]
        }
    
    def register_agent(self, agent_role: AgentRole, agent_instance: Any, capabilities: Optional[List[str]] = None):
        """Register an agent with the coordinator"""
        
        self.registered_agents[agent_role] = agent_instance
        
        # Initialize agent status
        self.agent_statuses[agent_role] = AgentStatus(
            role=agent_role,
            status="idle",
            current_task=None,
            workload=0,
            last_activity=datetime.now(),
            capabilities=capabilities or self.agent_capabilities.get(agent_role, []),
            performance_metrics={
                "tasks_completed": 0,
                "average_task_time": 0.0,
                "success_rate": 100.0,
                "error_count": 0
            }
        )
        
        # Update capabilities if provided
        if capabilities:
            self.agent_capabilities[agent_role] = capabilities
        
        self.logger.info(f"Registered agent {agent_role} with capabilities: {self.agent_capabilities[agent_role]}")
    
    def unregister_agent(self, agent_role: AgentRole):
        """Unregister an agent"""
        
        if agent_role in self.registered_agents:
            del self.registered_agents[agent_role]
            
        if agent_role in self.agent_statuses:
            self.agent_statuses[agent_role].status = "offline"
            
        self.logger.info(f"Unregistered agent {agent_role}")
    
    async def send_message(
        self,
        sender_role: AgentRole,
        recipient_role: AgentRole,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> str:
        """Send a message between agents"""
        
        message_id = str(uuid.uuid4())
        
        message = AgentMessage(
            id=message_id,
            sender_role=sender_role,
            recipient_role=recipient_role,
            message_type=message_type,
            priority=priority,
            content=content,
            created_at=datetime.now(),
            correlation_id=correlation_id
        )
        
        # Add to message queue
        self.message_queue.append(message)
        self.coordination_metrics["total_messages"] += 1
        
        # Sort queue by priority
        self._sort_message_queue()
        
        self.logger.debug(f"Queued message {message_id} from {sender_role} to {recipient_role}")
        
        # Start message processing if not active
        if not self.processing_active:
            asyncio.create_task(self._process_message_queue())
        
        return message_id
    
    async def broadcast_message(
        self,
        sender_role: AgentRole,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        exclude_roles: Optional[List[AgentRole]] = None
    ) -> List[str]:
        """Broadcast a message to all registered agents"""
        
        message_ids = []
        exclude_roles = exclude_roles or []
        
        for agent_role in self.registered_agents:
            if agent_role != sender_role and agent_role not in exclude_roles:
                message_id = await self.send_message(
                    sender_role=sender_role,
                    recipient_role=agent_role,
                    message_type=message_type,
                    content=content,
                    priority=priority
                )
                message_ids.append(message_id)
        
        self.logger.info(f"Broadcast message from {sender_role} to {len(message_ids)} agents")
        return message_ids
    
    async def request_collaboration(
        self,
        initiator_role: AgentRole,
        participants: List[AgentRole],
        topic: str,
        context: Dict[str, Any]
    ) -> str:
        """Request a collaboration session between agents"""
        
        collaboration_id = str(uuid.uuid4())
        
        # Create collaboration session
        collaboration = CollaborationSession(
            id=collaboration_id,
            participants=[initiator_role] + participants,
            topic=topic,
            created_at=datetime.now(),
            messages=[],
            status="active"
        )
        
        self.active_collaborations[collaboration_id] = collaboration
        
        # Send collaboration requests to participants
        for participant in participants:
            await self.send_message(
                sender_role=initiator_role,
                recipient_role=participant,
                message_type=MessageType.COLLABORATION_REQUEST,
                content={
                    "collaboration_id": collaboration_id,
                    "topic": topic,
                    "context": context,
                    "participants": [role.value for role in collaboration.participants]
                },
                priority=MessagePriority.HIGH,
                correlation_id=collaboration_id
            )
        
        self.logger.info(f"Started collaboration {collaboration_id}: {topic}")
        return collaboration_id
    
    async def respond_to_collaboration(
        self,
        collaboration_id: str,
        agent_role: AgentRole,
        response: Dict[str, Any]
    ) -> bool:
        """Respond to a collaboration request"""
        
        if collaboration_id not in self.active_collaborations:
            self.logger.warning(f"Collaboration {collaboration_id} not found")
            return False
        
        collaboration = self.active_collaborations[collaboration_id]
        
        if agent_role not in collaboration.participants:
            self.logger.warning(f"Agent {agent_role} not part of collaboration {collaboration_id}")
            return False
        
        # Create response message
        message_id = str(uuid.uuid4())
        message = AgentMessage(
            id=message_id,
            sender_role=agent_role,
            recipient_role=AgentRole.ORCHESTRATOR,  # Responses go to orchestrator
            message_type=MessageType.COLLABORATION_RESPONSE,
            priority=MessagePriority.HIGH,
            content={
                "collaboration_id": collaboration_id,
                "response": response
            },
            created_at=datetime.now(),
            correlation_id=collaboration_id
        )
        
        collaboration.messages.append(message)
        
        self.logger.info(f"Agent {agent_role} responded to collaboration {collaboration_id}")
        return True
    
    async def complete_collaboration(
        self,
        collaboration_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """Complete a collaboration session"""
        
        if collaboration_id not in self.active_collaborations:
            return False
        
        collaboration = self.active_collaborations[collaboration_id]
        collaboration.status = "completed"
        collaboration.result = result
        
        # Move to history
        self.collaboration_history.append(collaboration)
        del self.active_collaborations[collaboration_id]
        
        # Update metrics
        self.coordination_metrics["successful_collaborations"] += 1
        
        self.logger.info(f"Completed collaboration {collaboration_id}")
        return True
    
    async def request_resource(
        self,
        requester_role: AgentRole,
        resource_name: str,
        resource_type: str,
        exclusive: bool = False
    ) -> Tuple[bool, Optional[Any]]:
        """Request access to a shared resource"""
        
        # Check if resource is locked exclusively
        if resource_name in self.resource_locks and exclusive:
            return False, None
        
        # Check if resource exists
        if resource_name not in self.shared_resources:
            self.logger.warning(f"Resource {resource_name} not found")
            return False, None
        
        # Grant access
        if exclusive:
            self.resource_locks[resource_name] = requester_role
        
        resource = self.shared_resources[resource_name]
        
        self.logger.debug(f"Granted {resource_type} access to resource {resource_name} for {requester_role}")
        return True, resource
    
    def release_resource(self, agent_role: AgentRole, resource_name: str) -> bool:
        """Release a shared resource"""
        
        if resource_name in self.resource_locks and self.resource_locks[resource_name] == agent_role:
            del self.resource_locks[resource_name]
            self.logger.debug(f"Released resource {resource_name} by {agent_role}")
            return True
        
        return False
    
    def add_shared_resource(self, resource_name: str, resource: Any):
        """Add a shared resource"""
        self.shared_resources[resource_name] = resource
        self.logger.debug(f"Added shared resource: {resource_name}")
    
    def remove_shared_resource(self, resource_name: str):
        """Remove a shared resource"""
        if resource_name in self.shared_resources:
            del self.shared_resources[resource_name]
            
        if resource_name in self.resource_locks:
            del self.resource_locks[resource_name]
            
        self.logger.debug(f"Removed shared resource: {resource_name}")
    
    async def _process_message_queue(self):
        """Process messages in the queue"""
        
        self.processing_active = True
        
        try:
            while self.message_queue:
                message = self.message_queue.pop(0)
                
                try:
                    await self._deliver_message(message)
                except Exception as e:
                    self.logger.error(f"Error delivering message {message.id}: {e}")
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
                
        finally:
            self.processing_active = False
    
    async def _deliver_message(self, message: AgentMessage):
        """Deliver a message to the recipient agent"""
        
        recipient_agent = self.registered_agents.get(message.recipient_role)
        if not recipient_agent:
            self.logger.warning(f"Recipient agent {message.recipient_role} not found for message {message.id}")
            return
        
        # Update delivery timestamp
        message.delivered_at = datetime.now()
        
        try:
            # Check if agent has a message handler
            if hasattr(recipient_agent, 'handle_message'):
                response = await recipient_agent.handle_message(message)
                
                # Handle response if provided
                if response:
                    response_message = AgentMessage(
                        id=str(uuid.uuid4()),
                        sender_role=message.recipient_role,
                        recipient_role=message.sender_role,
                        message_type=MessageType.TASK_RESPONSE,
                        priority=message.priority,
                        content=response,
                        created_at=datetime.now(),
                        correlation_id=message.id
                    )
                    
                    message.response_id = response_message.id
                    self.message_queue.append(response_message)
            
            # Update processing timestamp
            message.processed_at = datetime.now()
            
            # Move to history
            self.message_history.append(message)
            
            # Update agent status
            if message.recipient_role in self.agent_statuses:
                self.agent_statuses[message.recipient_role].last_activity = datetime.now()
            
            self.logger.debug(f"Delivered message {message.id} to {message.recipient_role}")
            
        except Exception as e:
            self.logger.error(f"Error processing message {message.id}: {e}")
            
            # Send error notification
            error_message = AgentMessage(
                id=str(uuid.uuid4()),
                sender_role=AgentRole.ORCHESTRATOR,
                recipient_role=message.sender_role,
                message_type=MessageType.ERROR_NOTIFICATION,
                priority=MessagePriority.HIGH,
                content={
                    "original_message_id": message.id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                },
                created_at=datetime.now()
            )
            
            self.message_queue.append(error_message)
    
    def _sort_message_queue(self):
        """Sort message queue by priority"""
        priority_order = {
            MessagePriority.URGENT: 0,
            MessagePriority.HIGH: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 3
        }
        
        self.message_queue.sort(key=lambda msg: (priority_order[msg.priority], msg.created_at))
    
    def update_agent_status(
        self,
        agent_role: AgentRole,
        status: str,
        current_task: Optional[str] = None,
        workload: Optional[int] = None
    ):
        """Update agent status"""
        
        if agent_role in self.agent_statuses:
            agent_status = self.agent_statuses[agent_role]
            agent_status.status = status
            agent_status.last_activity = datetime.now()
            
            if current_task is not None:
                agent_status.current_task = current_task
                
            if workload is not None:
                agent_status.workload = workload
            
            self.logger.debug(f"Updated status for {agent_role}: {status}")
    
    def get_agent_status(self, agent_role: AgentRole) -> Optional[AgentStatus]:
        """Get current status of an agent"""
        return self.agent_statuses.get(agent_role)
    
    def get_all_agent_statuses(self) -> Dict[AgentRole, AgentStatus]:
        """Get status of all agents"""
        return self.agent_statuses.copy()
    
    def find_capable_agents(self, required_capabilities: List[str]) -> List[AgentRole]:
        """Find agents with specific capabilities"""
        
        capable_agents = []
        
        for agent_role, capabilities in self.agent_capabilities.items():
            if all(cap in capabilities for cap in required_capabilities):
                # Check if agent is available
                status = self.agent_statuses.get(agent_role)
                if status and status.status in ["idle", "busy"]:  # Available agents
                    capable_agents.append(agent_role)
        
        # Sort by workload (prefer less busy agents)
        capable_agents.sort(key=lambda role: self.agent_statuses[role].workload)
        
        return capable_agents
    
    def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get coordination performance metrics"""
        
        metrics = self.coordination_metrics.copy()
        
        # Calculate additional metrics
        total_collaborations = metrics["successful_collaborations"] + metrics["failed_collaborations"]
        if total_collaborations > 0:
            metrics["collaboration_success_rate"] = (metrics["successful_collaborations"] / total_collaborations) * 100
        else:
            metrics["collaboration_success_rate"] = 0
        
        # Add current statistics
        metrics["active_collaborations"] = len(self.active_collaborations)
        metrics["queued_messages"] = len(self.message_queue)
        metrics["registered_agents"] = len(self.registered_agents)
        
        # Add agent utilization
        for agent_role, status in self.agent_statuses.items():
            metrics["agent_utilization"][agent_role.value] = {
                "status": status.status,
                "workload": status.workload,
                "tasks_completed": status.performance_metrics["tasks_completed"],
                "success_rate": status.performance_metrics["success_rate"]
            }
        
        return metrics
    
    def get_message_history(
        self,
        agent_role: Optional[AgentRole] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get message history with optional filtering"""
        
        messages = self.message_history
        
        # Apply filters
        if agent_role:
            messages = [msg for msg in messages 
                       if msg.sender_role == agent_role or msg.recipient_role == agent_role]
        
        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]
        
        # Sort by timestamp (newest first) and limit
        messages = sorted(messages, key=lambda msg: msg.created_at, reverse=True)[:limit]
        
        # Convert to dict format
        return [
            {
                "id": msg.id,
                "sender_role": msg.sender_role.value,
                "recipient_role": msg.recipient_role.value,
                "message_type": msg.message_type.value,
                "priority": msg.priority.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "delivered_at": msg.delivered_at.isoformat() if msg.delivered_at else None,
                "processed_at": msg.processed_at.isoformat() if msg.processed_at else None,
                "response_id": msg.response_id,
                "correlation_id": msg.correlation_id
            }
            for msg in messages
        ]
    
    def get_collaboration_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get collaboration history"""
        
        collaborations = sorted(
            self.collaboration_history,
            key=lambda c: c.created_at,
            reverse=True
        )[:limit]
        
        return [
            {
                "id": collab.id,
                "participants": [role.value for role in collab.participants],
                "topic": collab.topic,
                "status": collab.status,
                "created_at": collab.created_at.isoformat(),
                "message_count": len(collab.messages),
                "result": collab.result
            }
            for collab in collaborations
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on coordination system"""
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "message_queue_size": len(self.message_queue),
            "active_collaborations": len(self.active_collaborations),
            "issues": []
        }
        
        # Check agent health
        for agent_role, status in self.agent_statuses.items():
            agent_health = {
                "status": status.status,
                "last_activity": status.last_activity.isoformat(),
                "workload": status.workload,
                "responsive": True
            }
            
            # Check if agent is responsive (activity within last 5 minutes)
            if datetime.now() - status.last_activity > timedelta(minutes=5):
                agent_health["responsive"] = False
                health_status["issues"].append(f"Agent {agent_role.value} may be unresponsive")
            
            health_status["agents"][agent_role.value] = agent_health
        
        # Check message queue health
        if len(self.message_queue) > 100:
            health_status["issues"].append("Message queue is getting large")
            health_status["status"] = "warning"
        
        # Check for stuck collaborations
        current_time = datetime.now()
        for collab_id, collab in self.active_collaborations.items():
            if current_time - collab.created_at > timedelta(hours=1):
                health_status["issues"].append(f"Collaboration {collab_id} has been active for over 1 hour")
                health_status["status"] = "warning"
        
        if health_status["issues"]:
            health_status["status"] = "warning" if health_status["status"] == "healthy" else "unhealthy"
        
        return health_status

