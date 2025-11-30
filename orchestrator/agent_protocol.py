"""
Agent Communication Protocol
============================

This module defines the message protocol for inter-agent communication
in the test automation pipeline. It enables:

- Structured message passing between agents
- Review-refinement loops
- Task delegation and coordination
- Status broadcasting and monitoring

Message Flow Examples:
    1. Review Loop:
        TestCreationAgent -> ReviewAgent (REVIEW_REQUEST)
        ReviewAgent -> TestCreationAgent (REVIEW_FEEDBACK)
        TestCreationAgent -> ReviewAgent (REFINEMENT_COMPLETE)

    2. Task Delegation:
        Orchestrator -> PlanningAgent (TASK_REQUEST)
        PlanningAgent -> Orchestrator (TASK_RESPONSE)

    3. Self-Healing:
        ExecutionAgent -> SelfHealingAgent (HEALING_REQUEST)
        SelfHealingAgent -> ExecutionAgent (HEALING_COMPLETE)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Awaitable
from uuid import UUID, uuid4
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages that can be sent between agents"""

    # Task-related messages
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"

    # Review-related messages
    REVIEW_REQUEST = "review_request"
    REVIEW_FEEDBACK = "review_feedback"
    REFINEMENT_REQUEST = "refinement_request"
    REFINEMENT_COMPLETE = "refinement_complete"

    # Self-healing messages
    HEALING_REQUEST = "healing_request"
    HEALING_COMPLETE = "healing_complete"
    HEALING_FAILED = "healing_failed"

    # Status messages
    STATUS_UPDATE = "status_update"
    STATUS_QUERY = "status_query"
    STATUS_RESPONSE = "status_response"

    # Error messages
    ERROR_REPORT = "error_report"
    ERROR_ACKNOWLEDGED = "error_acknowledged"

    # Coordination messages
    HANDOFF = "handoff"
    HANDOFF_ACCEPTED = "handoff_accepted"
    BROADCAST = "broadcast"


class MessagePriority(str, Enum):
    """Priority levels for messages"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class AgentMessage:
    """
    Represents a message sent between agents.

    This is the core data structure for all agent-to-agent communication.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    message_type: MessageType = MessageType.TASK_REQUEST
    sender_agent: str = ""
    recipient_agent: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    requires_response: bool = False
    correlation_id: Optional[str] = None  # Links related messages
    parent_message_id: Optional[str] = None  # For threaded conversations
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "id": self.id,
            "message_type": self.message_type.value,
            "sender_agent": self.sender_agent,
            "recipient_agent": self.recipient_agent,
            "payload": self.payload,
            "priority": self.priority.value,
            "requires_response": self.requires_response,
            "correlation_id": self.correlation_id,
            "parent_message_id": self.parent_message_id,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        return cls(
            id=data.get("id", str(uuid4())),
            message_type=MessageType(data.get("message_type", "task_request")),
            sender_agent=data.get("sender_agent", ""),
            recipient_agent=data.get("recipient_agent", ""),
            payload=data.get("payload", {}),
            priority=MessagePriority(data.get("priority", "normal")),
            requires_response=data.get("requires_response", False),
            correlation_id=data.get("correlation_id"),
            parent_message_id=data.get("parent_message_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            metadata=data.get("metadata", {})
        )

    def create_response(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        sender_agent: str
    ) -> "AgentMessage":
        """Create a response message linked to this message"""
        return AgentMessage(
            message_type=message_type,
            sender_agent=sender_agent,
            recipient_agent=self.sender_agent,
            payload=payload,
            correlation_id=self.correlation_id or self.id,
            parent_message_id=self.id,
            priority=self.priority
        )


@dataclass
class ReviewFeedback:
    """Structured feedback from a review agent"""
    approved: bool = False
    score: float = 0.0  # 0.0 to 1.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    requires_changes: bool = False
    change_requests: List[Dict[str, Any]] = field(default_factory=list)
    review_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "score": self.score,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "requires_changes": self.requires_changes,
            "change_requests": self.change_requests,
            "review_notes": self.review_notes
        }


@dataclass
class HealingRequest:
    """Request for self-healing agent to fix a test"""
    test_file_path: str = ""
    error_type: str = ""
    error_message: str = ""
    stack_trace: str = ""
    failed_selector: Optional[str] = None
    discovery_data: Dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 3
    current_attempt: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_file_path": self.test_file_path,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "failed_selector": self.failed_selector,
            "discovery_data": self.discovery_data,
            "max_attempts": self.max_attempts,
            "current_attempt": self.current_attempt
        }


class AgentMessageBus:
    """
    Central message bus for routing messages between agents.

    Provides:
    - Message routing and delivery
    - Subscription-based message handling
    - Message logging and auditing
    - Async message processing
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.message_log: List[AgentMessage] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.logger = logging.getLogger("agent_message_bus")
        self._lock = asyncio.Lock()

    def register_agent(self, agent_name: str, handler: Callable[[AgentMessage], Awaitable[Optional[AgentMessage]]]):
        """Register an agent's message handler"""
        self.message_handlers[agent_name] = handler
        self.logger.info(f"Registered agent: {agent_name}")

    def unregister_agent(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.message_handlers:
            del self.message_handlers[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")

    def subscribe(self, message_type: MessageType, callback: Callable[[AgentMessage], Awaitable[None]]):
        """Subscribe to a specific message type"""
        key = message_type.value
        if key not in self.subscribers:
            self.subscribers[key] = []
        self.subscribers[key].append(callback)

    async def send_message(
        self,
        message: AgentMessage,
        wait_for_response: bool = False,
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        """
        Send a message to an agent.

        Args:
            message: The message to send
            wait_for_response: If True, wait for a response message
            timeout: Timeout in seconds when waiting for response

        Returns:
            Response message if wait_for_response is True, otherwise None
        """
        async with self._lock:
            # Log the message
            self.message_log.append(message)
            self.logger.info(
                f"Message {message.id[:8]}: {message.sender_agent} -> {message.recipient_agent} "
                f"[{message.message_type.value}]"
            )

        # Notify subscribers
        await self._notify_subscribers(message)

        # Route to recipient
        if message.recipient_agent in self.message_handlers:
            handler = self.message_handlers[message.recipient_agent]

            if wait_for_response:
                # Create a future for the response
                response_future = asyncio.get_event_loop().create_future()
                self.pending_responses[message.id] = response_future

                try:
                    # Call the handler
                    response = await asyncio.wait_for(handler(message), timeout=timeout)

                    if response:
                        async with self._lock:
                            self.message_log.append(response)
                        return response

                    # Wait for response via pending_responses
                    return await asyncio.wait_for(response_future, timeout=timeout)

                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout waiting for response to message {message.id}")
                    return None
                finally:
                    self.pending_responses.pop(message.id, None)
            else:
                # Fire and forget
                asyncio.create_task(handler(message))
                return None
        else:
            self.logger.warning(f"No handler registered for agent: {message.recipient_agent}")
            return None

    async def send_response(self, original_message_id: str, response: AgentMessage):
        """Send a response to a pending request"""
        if original_message_id in self.pending_responses:
            future = self.pending_responses[original_message_id]
            if not future.done():
                future.set_result(response)

        async with self._lock:
            self.message_log.append(response)

    async def broadcast(self, message: AgentMessage, exclude: Optional[List[str]] = None):
        """Broadcast a message to all registered agents"""
        exclude = exclude or []
        tasks = []

        for agent_name, handler in self.message_handlers.items():
            if agent_name not in exclude:
                broadcast_msg = AgentMessage(
                    message_type=message.message_type,
                    sender_agent=message.sender_agent,
                    recipient_agent=agent_name,
                    payload=message.payload,
                    priority=message.priority,
                    correlation_id=message.id
                )
                tasks.append(handler(broadcast_msg))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _notify_subscribers(self, message: AgentMessage):
        """Notify all subscribers of a message type"""
        key = message.message_type.value
        if key in self.subscribers:
            tasks = [callback(message) for callback in self.subscribers[key]]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def get_message_history(
        self,
        agent_name: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """Get message history with optional filters"""
        messages = self.message_log

        if agent_name:
            messages = [
                m for m in messages
                if m.sender_agent == agent_name or m.recipient_agent == agent_name
            ]

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        return messages[-limit:]

    def get_conversation(self, correlation_id: str) -> List[AgentMessage]:
        """Get all messages in a conversation thread"""
        return [m for m in self.message_log if m.correlation_id == correlation_id or m.id == correlation_id]


# Factory functions for common message types

def create_task_request(
    sender: str,
    recipient: str,
    task_type: str,
    task_data: Dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL
) -> AgentMessage:
    """Create a task request message"""
    return AgentMessage(
        message_type=MessageType.TASK_REQUEST,
        sender_agent=sender,
        recipient_agent=recipient,
        payload={
            "task_type": task_type,
            "task_data": task_data
        },
        priority=priority,
        requires_response=True
    )


def create_review_request(
    sender: str,
    recipient: str,
    items_to_review: List[Dict[str, Any]],
    review_type: str = "code_review",
    context: Optional[Dict[str, Any]] = None
) -> AgentMessage:
    """Create a review request message"""
    return AgentMessage(
        message_type=MessageType.REVIEW_REQUEST,
        sender_agent=sender,
        recipient_agent=recipient,
        payload={
            "review_type": review_type,
            "items": items_to_review,
            "context": context or {}
        },
        priority=MessagePriority.HIGH,
        requires_response=True
    )


def create_review_feedback(
    sender: str,
    recipient: str,
    feedback: ReviewFeedback,
    original_message_id: str
) -> AgentMessage:
    """Create a review feedback message"""
    return AgentMessage(
        message_type=MessageType.REVIEW_FEEDBACK,
        sender_agent=sender,
        recipient_agent=recipient,
        payload=feedback.to_dict(),
        parent_message_id=original_message_id,
        requires_response=feedback.requires_changes
    )


def create_healing_request(
    sender: str,
    recipient: str,
    request: HealingRequest
) -> AgentMessage:
    """Create a healing request message"""
    return AgentMessage(
        message_type=MessageType.HEALING_REQUEST,
        sender_agent=sender,
        recipient_agent=recipient,
        payload=request.to_dict(),
        priority=MessagePriority.HIGH,
        requires_response=True
    )


def create_status_update(
    sender: str,
    status: str,
    progress: float = 0.0,
    details: Optional[Dict[str, Any]] = None
) -> AgentMessage:
    """Create a status update broadcast message"""
    return AgentMessage(
        message_type=MessageType.STATUS_UPDATE,
        sender_agent=sender,
        recipient_agent="*",  # Broadcast
        payload={
            "status": status,
            "progress": progress,
            "details": details or {}
        },
        priority=MessagePriority.LOW
    )
