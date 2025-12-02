# ADR-002: Agent Message Protocol

## Status
Accepted

## Date
2025-11-30

## Context

Agents in the platform need to communicate with each other for:

1. **Task delegation**: Orchestrator assigns work to specialized agents
2. **Review feedback**: ReviewAgent sends improvement suggestions to TestCreationAgent
3. **Healing requests**: ExecutionAgent asks SelfHealingAgent to fix broken tests
4. **Status updates**: Agents broadcast progress to interested parties

Initial implementation had agents calling each other directly, which created:
- Tight coupling between agents
- No audit trail of communications
- Difficulty adding new message types
- No support for async responses

## Decision

We implement a **message bus architecture** with typed messages:

### Message Types (25 total)

```python
class MessageType(str, Enum):
    # Task lifecycle
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_PROGRESS = "task_progress"

    # Review cycle
    REVIEW_REQUEST = "review_request"
    REVIEW_FEEDBACK = "review_feedback"
    REFINEMENT_REQUEST = "refinement_request"

    # Self-healing
    HEALING_REQUEST = "healing_request"
    HEALING_RESPONSE = "healing_response"

    # ... and more
```

### Message Structure

```python
@dataclass
class AgentMessage:
    message_id: str
    message_type: MessageType
    sender: str
    recipient: str
    payload: Dict[str, Any]
    priority: MessagePriority
    timestamp: datetime
    correlation_id: Optional[str]  # For request/response pairing
    requires_response: bool
```

### Message Bus

```python
class AgentMessageBus:
    def __init__(self):
        self.message_handlers: Dict[str, Callable] = {}
        self.message_log: List[AgentMessage] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}

    async def send_message(
        self,
        message: AgentMessage,
        wait_for_response: bool = False,
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        # Route to recipient's handler
        # Log for audit
        # Optionally wait for response
```

### Agent Handler Pattern

Each agent implements `handle_message()`:

```python
class BaseTestAgent:
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        handlers = {
            MessageType.TASK_REQUEST: self._handle_task_request,
            MessageType.REVIEW_REQUEST: self._handle_review_request,
            MessageType.REVIEW_FEEDBACK: self._handle_review_feedback,
            # ...
        }
        handler = handlers.get(message.message_type)
        if handler:
            return await handler(message)
```

## Consequences

### Positive
- **Decoupled**: Agents don't need direct references to each other
- **Auditable**: All messages are logged with timestamps
- **Extensible**: New message types can be added without changing agents
- **Async-friendly**: Built-in support for request/response patterns
- **Testable**: Easy to mock message bus for unit tests

### Negative
- **Indirection**: Message passing adds conceptual complexity
- **Overhead**: Serialization/deserialization for each message
- **Learning curve**: Developers must understand the protocol

### Trade-offs Accepted
- Chose simplicity over distributed messaging (no Kafka/RabbitMQ)
- In-memory bus is sufficient for single-process deployment
- Can add persistence layer later if needed

## Related Files
- `orchestrator/agent_protocol.py` - Message types, bus, helpers
- `agents/base_agent.py` - `handle_message()` implementation
- `orchestrator/workflow_orchestrator.py` - Message bus integration

---

*Decision made by: Claude (AI Assistant)*
*Reviewed by: [Pending]*
