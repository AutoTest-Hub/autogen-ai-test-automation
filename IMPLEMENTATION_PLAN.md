# AutoGen AI Test Automation Platform
## Complete Implementation Plan - Achieving the Full Vision

**Document Version**: 1.0
**Created**: 2025-11-28
**Target Completion**: 5-Phase Incremental Delivery

---

## Overview

This document outlines the complete implementation plan to transform the Phase 9.5 codebase into a production-ready "QA-as-a-Service" platform. The plan is divided into 5 phases, each with specific deliverables, tasks, and success criteria.

---

## Current State Assessment

| Component | Status | Completeness |
|-----------|--------|--------------|
| Web Dashboard | Working | 85% |
| API Backend | Working | 80% |
| Database Schema | Complete | 95% |
| Agent System | Working | 70% |
| Real Discovery | Partial | 40% |
| Agent Collaboration | Basic | 30% |
| Subscription/Billing | Schema Only | 20% |
| Deployment | Ready | 90% |

---

# Phase 1: Consolidation
**Duration**: 3-5 days
**Priority**: Critical
**Goal**: Clean, maintainable codebase with single source of truth

## 1.1 Web Dashboard Cleanup

### Problem
Multiple variant files exist for the same functionality:
- 8 versions of CreateTest components
- 10 versions of TestManagement components
- 4 versions of App.jsx

### Tasks

#### 1.1.1 Consolidate CreateTest Components
**Files to Keep**: `CreateTest.jsx` (merge best features from all)
**Files to Archive/Remove**:
- `CreateTestAdvanced.jsx`
- `CreateTestComplete.jsx`
- `CreateTestEnhanced.jsx`
- `CreateTestRealTime.jsx`
- `CreateTestRealTimeEnhanced.jsx`
- `CreateTestRealTimeFixed.jsx`
- `CreateTestWorking.jsx`

**Action Items**:
```
1. Analyze each variant to identify unique features
2. Create feature matrix documenting what each variant adds
3. Merge all features into single CreateTest.jsx
4. Add feature flags for optional advanced features
5. Update all imports to use consolidated component
6. Move archived files to /web-dashboard/archive/
```

#### 1.1.2 Consolidate TestManagement Components
**Files to Keep**: `TestManagement.jsx`
**Files to Archive/Remove**:
- `TestManagementBasic.jsx`
- `TestManagementDynamic.jsx`
- `TestManagementEnhanced.jsx`
- `TestManagementFinal.jsx`
- `TestManagementFixed.jsx`
- `TestManagementNew.jsx`
- `TestManagementReal.jsx`
- `TestManagementSimple.jsx`
- `TestManagementTest.jsx`
- `TestManagementWorking.jsx`

#### 1.1.3 Consolidate App Entry Points
**File to Keep**: `App.jsx`
**Files to Archive**:
- `AppSimple.jsx`
- `AppTest.jsx`
- `AppWorking.jsx`

## 1.2 Agent System Cleanup

### Problem
Multiple versions of agents with overlapping functionality.

### Tasks

#### 1.2.1 Consolidate Discovery Agents
**File to Keep**: `real_browser_discovery_agent.py` (enhanced)
**Files to Archive**:
- `real_browser_discovery_agent_compatible.py`
- `real_browser_discovery_agent_fixed.py`

**Action Items**:
```
1. Merge compatibility fixes into main agent
2. Ensure all edge cases from "fixed" version are handled
3. Add comprehensive error handling
4. Update all imports
```

#### 1.2.2 Consolidate Test Creation Agents
**File to Keep**: `test_creation_agent.py`
**Files to Archive**:
- `test_creation_agent_original_backup.py`
- `autogen_test_creation_agent.py` (merge into main)

#### 1.2.3 Clean Up Root-Level Scripts
**Files to Consolidate**:
```
Root level scripts to organize:
├── workflows/
│   ├── complete_multi_agent_workflow.py
│   ├── proper_multi_agent_workflow.py
│   └── real_multi_agent_workflow.py
├── generators/
│   ├── dynamic_test_generator.py
│   ├── simple_test_generator.py
│   └── generate_complete_tests.py
└── archive/
    ├── *_fixed.py
    ├── *_compatible.py
    └── *_backup.py
```

## 1.3 API Module Organization

### Tasks

#### 1.3.1 Organize API Endpoints
**Current State**: 30+ Python files in /api/ root
**Target Structure**:
```
api/
├── main.py                    # Single entry point
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── database.py
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── applications.py
│   ├── tests.py
│   ├── agents.py
│   ├── execution.py
│   └── requirements.py
├── services/
│   ├── __init__.py
│   ├── agent_processor.py
│   ├── test_execution.py
│   ├── file_storage.py
│   └── duplicate_detection.py
├── models/
│   ├── __init__.py
│   ├── database.py
│   └── schemas.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

## 1.4 Success Criteria - Phase 1

- [ ] Single version of each major component
- [ ] Clear directory structure with logical organization
- [ ] All imports updated to use consolidated modules
- [ ] Archived files moved to dedicated archive directory
- [ ] All tests pass after consolidation
- [ ] No duplicate functionality in codebase

---

# Phase 2: Real Discovery Integration
**Duration**: 4-6 days
**Priority**: High
**Goal**: Agents use real browser automation to discover application structure

## 2.1 RealBrowserDiscoveryAgent Enhancement

### Current State
- Agent exists but returns simulated data in some code paths
- Playwright integration is present but incomplete

### Tasks

#### 2.1.1 Complete Playwright Integration
**File**: `agents/real_browser_discovery_agent.py`

```python
# Target implementation structure
class RealBrowserDiscoveryAgent:
    async def discover_application(self, url: str) -> DiscoveryResult:
        """
        1. Launch browser with Playwright
        2. Navigate to URL
        3. Extract all interactive elements
        4. Map page structure
        5. Identify user flows
        6. Return structured discovery data
        """
        pass

    async def extract_elements(self, page) -> List[Element]:
        """
        Extract all actionable elements:
        - Buttons, links, inputs
        - Forms and their fields
        - Navigation elements
        - Dynamic content areas
        """
        pass

    async def generate_selectors(self, element) -> List[Selector]:
        """
        Generate multiple selector strategies:
        - data-testid (preferred)
        - aria-label
        - CSS selectors
        - XPath (fallback)
        """
        pass

    async def map_user_flows(self, pages: List[Page]) -> List[UserFlow]:
        """
        Identify common user journeys:
        - Login flow
        - Registration flow
        - Main business flows
        - Navigation patterns
        """
        pass
```

#### 2.1.2 Implement Element Classification
**New File**: `agents/element_classifier.py`

```python
class ElementClassifier:
    """Classify discovered elements by purpose and interaction type"""

    ELEMENT_TYPES = {
        'authentication': ['login', 'password', 'signin', 'signup'],
        'navigation': ['nav', 'menu', 'sidebar', 'header'],
        'form': ['input', 'textarea', 'select', 'checkbox'],
        'action': ['button', 'submit', 'save', 'delete'],
        'display': ['table', 'list', 'card', 'modal']
    }

    def classify(self, element: Element) -> ElementClassification:
        """Determine element purpose based on attributes and context"""
        pass
```

#### 2.1.3 Wire Discovery into Agent Processor
**File**: `api/real_agent_processor.py`

```python
async def _discovery_phase(self, job_id, test_request):
    # REPLACE simulated discovery with real browser discovery
    from agents.real_browser_discovery_agent import RealBrowserDiscoveryAgent

    discovery_agent = RealBrowserDiscoveryAgent()

    # Real browser discovery
    discovery_result = await discovery_agent.discover_application(
        url=test_request.get('application_url'),
        headless=True
    )

    # Extract elements and flows
    elements = discovery_result.elements
    user_flows = discovery_result.user_flows
    page_structure = discovery_result.page_structure

    # Generate scenarios from real discovery
    test_scenarios = self._generate_scenarios_from_discovery(
        elements, user_flows, page_structure
    )

    return test_scenarios
```

## 2.2 Selector Generation Strategy

### Tasks

#### 2.2.1 Implement Multi-Strategy Selector Generator
**File**: `utils/selector_generator.py`

```python
class SelectorGenerator:
    """Generate robust selectors with fallback strategies"""

    def generate(self, element) -> SelectorSet:
        selectors = SelectorSet()

        # Priority 1: Test IDs
        if element.get('data-testid'):
            selectors.add(f"[data-testid='{element['data-testid']}']", priority=1)

        # Priority 2: Accessibility attributes
        if element.get('aria-label'):
            selectors.add(f"[aria-label='{element['aria-label']}']", priority=2)

        # Priority 3: Semantic selectors
        if element.get('id'):
            selectors.add(f"#{element['id']}", priority=3)

        # Priority 4: CSS with text content
        if element.get('text'):
            selectors.add(f"text={element['text']}", priority=4)

        # Priority 5: XPath fallback
        selectors.add(self._generate_xpath(element), priority=5)

        return selectors
```

## 2.3 Discovery Result Storage

### Tasks

#### 2.3.1 Store Discovery Results in Database
**New Table**: Add to schema

```sql
CREATE TABLE discovery_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES applications(id),
    customer_id UUID REFERENCES customers(id),
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    page_structure JSONB,
    elements JSONB,
    user_flows JSONB,
    selectors JSONB,
    screenshots JSONB,
    metadata JSONB
);
```

## 2.4 Success Criteria - Phase 2

- [ ] Discovery agent extracts real elements from live pages
- [ ] Multiple selector strategies generated for each element
- [ ] User flows identified from page navigation
- [ ] Discovery results stored in database
- [ ] Generated tests use real selectors (not hardcoded)
- [ ] Works across different application types (e-commerce, HRMS, banking)

---

# Phase 3: Agent Collaboration
**Duration**: 5-7 days
**Priority**: High
**Goal**: True multi-agent collaboration with back-and-forth refinement

## 3.1 Agent Communication Protocol

### Current State
- Agents run sequentially
- No inter-agent communication
- `handle_message()` not implemented

### Tasks

#### 3.1.1 Implement Message Protocol
**File**: `orchestrator/agent_protocol.py`

```python
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    REVIEW_REQUEST = "review_request"
    REVIEW_FEEDBACK = "review_feedback"
    REFINEMENT_REQUEST = "refinement_request"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class AgentMessage:
    id: UUID
    message_type: MessageType
    sender_agent: str
    recipient_agent: str
    payload: dict
    priority: MessagePriority = MessagePriority.NORMAL
    requires_response: bool = False
    correlation_id: Optional[UUID] = None  # For response tracking
    timestamp: datetime = field(default_factory=datetime.now)
```

#### 3.1.2 Implement Agent Message Handler
**File**: `agents/base_agent.py` - Update `handle_message()`

```python
async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
    """Process incoming messages from other agents"""

    handlers = {
        MessageType.TASK_REQUEST: self._handle_task_request,
        MessageType.REVIEW_REQUEST: self._handle_review_request,
        MessageType.REVIEW_FEEDBACK: self._handle_review_feedback,
        MessageType.REFINEMENT_REQUEST: self._handle_refinement_request,
    }

    handler = handlers.get(message.message_type)
    if handler:
        return await handler(message)

    return None

async def _handle_review_request(self, message: AgentMessage) -> AgentMessage:
    """Handle review requests from other agents"""
    # Subclasses override this
    raise NotImplementedError

async def send_message(self, recipient: str, message_type: MessageType,
                       payload: dict) -> AgentMessage:
    """Send message to another agent"""
    message = AgentMessage(
        id=uuid4(),
        message_type=message_type,
        sender_agent=self.name,
        recipient_agent=recipient,
        payload=payload
    )

    # Route through coordinator
    response = await self.coordinator.route_message(message)
    return response
```

#### 3.1.3 Implement Agent Coordinator
**File**: `orchestrator/agent_coordinator.py` - Enhance existing

```python
class AgentCoordinator:
    """Coordinates communication between agents"""

    def __init__(self):
        self.agents: Dict[str, BaseTestAgent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_responses: Dict[UUID, asyncio.Future] = {}

    async def route_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route message to recipient agent and wait for response if needed"""
        recipient = self.agents.get(message.recipient_agent)

        if not recipient:
            raise AgentNotFoundError(message.recipient_agent)

        # Log message for audit
        await self._log_message(message)

        # Process message
        response = await recipient.handle_message(message)

        # If response required, wait for it
        if message.requires_response and response:
            return response

        return None

    async def broadcast(self, sender: str, message_type: MessageType,
                       payload: dict, exclude: List[str] = None):
        """Broadcast message to all agents"""
        exclude = exclude or []
        for agent_name, agent in self.agents.items():
            if agent_name != sender and agent_name not in exclude:
                await self.route_message(AgentMessage(
                    id=uuid4(),
                    message_type=message_type,
                    sender_agent=sender,
                    recipient_agent=agent_name,
                    payload=payload
                ))
```

## 3.2 Collaborative Workflows

### Tasks

#### 3.2.1 Implement Review-Refinement Loop
**File**: `workflows/collaborative_workflow.py`

```python
class CollaborativeTestCreationWorkflow:
    """Workflow with agent collaboration and refinement"""

    async def execute(self, job_id: UUID, test_request: dict):
        # Phase 1: Discovery
        discovery_result = await self.discovery_agent.discover(test_request)

        # Phase 2: Planning with discovery input
        plan = await self.planning_agent.create_plan(discovery_result)

        # Phase 3: Test creation
        tests = await self.test_creation_agent.create_tests(plan, discovery_result)

        # Phase 4: Review loop (NEW - collaborative)
        review_result = await self._review_loop(tests, max_iterations=3)

        # Phase 5: Final execution
        return await self.execution_agent.execute(review_result.tests)

    async def _review_loop(self, tests: List[TestCase], max_iterations: int):
        """Collaborative review with refinement"""
        iteration = 0
        current_tests = tests

        while iteration < max_iterations:
            # Review Agent evaluates tests
            review = await self.review_agent.review(current_tests)

            if review.approved:
                return ReviewResult(tests=current_tests, iterations=iteration)

            # Send feedback to Test Creation Agent
            feedback_message = AgentMessage(
                message_type=MessageType.REVIEW_FEEDBACK,
                sender_agent="review_agent",
                recipient_agent="test_creation_agent",
                payload={
                    "tests": current_tests,
                    "issues": review.issues,
                    "suggestions": review.suggestions
                },
                requires_response=True
            )

            # Test Creation Agent refines based on feedback
            response = await self.coordinator.route_message(feedback_message)
            current_tests = response.payload.get("refined_tests")

            iteration += 1

        return ReviewResult(tests=current_tests, iterations=iteration)
```

#### 3.2.2 Implement Agent Specialization Requests
**Example**: Discovery Agent asking Planning Agent for priority

```python
# In DiscoveryAgent
async def discover_with_prioritization(self, url: str):
    # Initial discovery
    elements = await self.extract_elements(url)

    # Ask Planning Agent which elements to prioritize
    priority_request = await self.send_message(
        recipient="planning_agent",
        message_type=MessageType.TASK_REQUEST,
        payload={
            "request": "prioritize_elements",
            "elements": elements,
            "application_type": self.app_type
        }
    )

    # Use prioritized elements for deeper analysis
    priority_elements = priority_request.payload.get("prioritized")

    # Focus detailed discovery on high-priority elements
    return await self.detailed_discovery(priority_elements)
```

## 3.3 Success Criteria - Phase 3

- [ ] Agents can send and receive messages
- [ ] Review Agent can request test refinement
- [ ] Test Creation Agent responds to feedback
- [ ] Maximum 3 refinement iterations before approval
- [ ] All agent communications logged for audit
- [ ] Collaborative workflow produces higher quality tests

---

# Phase 4: Production Hardening
**Duration**: 5-7 days
**Priority**: High
**Goal**: Production-ready with security, monitoring, and reliability

## 4.1 Subscription & Billing Enforcement

### Tasks

#### 4.1.1 Implement Subscription Middleware
**File**: `api/middleware/subscription.py`

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SubscriptionMiddleware(BaseHTTPMiddleware):
    """Enforce subscription limits on API requests"""

    async def dispatch(self, request: Request, call_next):
        # Skip for auth endpoints
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        # Get current user from request
        user = getattr(request.state, 'user', None)
        if not user:
            return await call_next(request)

        # Check subscription status
        customer = await self.get_customer(user['customer_id'])

        if customer['subscription_status'] == 'expired':
            raise HTTPException(
                status_code=402,
                detail="Subscription expired. Please renew."
            )

        # Check API quota
        if customer['api_calls_used'] >= customer['api_calls_limit']:
            raise HTTPException(
                status_code=429,
                detail="API quota exceeded. Upgrade your plan."
            )

        # Increment API usage
        await self.increment_usage(customer['id'])

        return await call_next(request)
```

#### 4.1.2 Implement Usage Tracking
**File**: `api/services/usage_tracker.py`

```python
class UsageTracker:
    """Track API and agent usage for billing"""

    async def track_api_call(self, customer_id: UUID, endpoint: str):
        """Track individual API calls"""
        await db.execute("""
            UPDATE customers
            SET api_calls_used = api_calls_used + 1
            WHERE id = %s
        """, (customer_id,))

    async def track_agent_usage(self, customer_id: UUID, agent_type: str,
                                 duration_seconds: int):
        """Track agent execution time for billing"""
        await db.execute("""
            INSERT INTO agent_usage_logs
            (customer_id, agent_type, duration_seconds, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (customer_id, agent_type, duration_seconds))

    async def reset_monthly_quota(self):
        """Reset API quotas monthly (cron job)"""
        await db.execute("""
            UPDATE customers
            SET api_calls_used = 0,
                api_calls_reset_date = NOW()
            WHERE api_calls_reset_date < NOW() - INTERVAL '1 month'
        """)
```

## 4.2 Rate Limiting

### Tasks

#### 4.2.1 Implement Rate Limiter
**File**: `api/middleware/rate_limiter.py`

```python
from fastapi import Request, HTTPException
from redis import Redis
import time

class RateLimiter:
    """Token bucket rate limiting with Redis"""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_limits = {
            'free': {'requests': 100, 'window': 3600},      # 100/hour
            'starter': {'requests': 1000, 'window': 3600},   # 1000/hour
            'growth': {'requests': 5000, 'window': 3600},    # 5000/hour
            'enterprise': {'requests': 50000, 'window': 3600} # 50000/hour
        }

    async def check_limit(self, customer_id: str, tier: str) -> bool:
        """Check if request is within rate limit"""
        key = f"rate_limit:{customer_id}"
        limits = self.default_limits.get(tier, self.default_limits['free'])

        current = self.redis.get(key)
        if current is None:
            self.redis.setex(key, limits['window'], 1)
            return True

        if int(current) >= limits['requests']:
            return False

        self.redis.incr(key)
        return True
```

## 4.3 Error Handling & Retry Logic

### Tasks

#### 4.3.1 Implement Global Error Handler
**File**: `api/middleware/error_handler.py`

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback
import logging

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""

    # Log full traceback
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())

    # Log to security events if suspicious
    if isinstance(exc, (SecurityError, AuthenticationError)):
        await log_security_event(request, exc)

    # Return sanitized error to client
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request.state.request_id,
            "message": "An error occurred. Please try again."
        }
    )
```

#### 4.3.2 Implement Retry Decorator
**File**: `api/utils/retry.py`

```python
import asyncio
from functools import wraps

def with_retry(max_attempts=3, backoff_factor=2, exceptions=(Exception,)):
    """Decorator for automatic retry with exponential backoff"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor ** attempt
                        await asyncio.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator

# Usage
@with_retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
async def call_external_service():
    pass
```

## 4.4 Comprehensive Logging & Monitoring

### Tasks

#### 4.4.1 Structured Logging Setup
**File**: `api/config/logging.py`

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields if present
        if hasattr(record, 'customer_id'):
            log_obj['customer_id'] = record.customer_id
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id

        return json.dumps(log_obj)

def setup_logging():
    """Configure structured logging"""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logging.root.handlers = [handler]
    logging.root.setLevel(logging.INFO)
```

#### 4.4.2 Add Prometheus Metrics
**File**: `api/middleware/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ACTIVE_AGENT_JOBS = Gauge(
    'agent_jobs_active',
    'Number of active agent jobs'
)

TEST_GENERATION_COUNT = Counter(
    'tests_generated_total',
    'Total tests generated',
    ['application_type', 'customer_tier']
)
```

## 4.5 CI/CD Pipeline

### Tasks

#### 4.5.1 GitHub Actions Workflow
**File**: `.github/workflows/ci.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: pytest tests/ --cov=api --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linting
        run: |
          pip install ruff
          ruff check .

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t ai-test-automation-api -f Dockerfile.api .

      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          docker push ${{ secrets.REGISTRY }}/ai-test-automation-api
```

## 4.6 Success Criteria - Phase 4

- [ ] Subscription limits enforced on all API calls
- [ ] Rate limiting prevents abuse
- [ ] All errors handled gracefully with proper logging
- [ ] Retry logic for transient failures
- [ ] Prometheus metrics exposed
- [ ] CI/CD pipeline runs on every PR
- [ ] 80%+ test coverage

---

# Phase 5: Marketplace Features
**Duration**: 5-7 days
**Priority**: Medium
**Goal**: Agent marketplace with selection UI and "hiring" flow

## 5.1 Agent Registry

### Tasks

#### 5.1.1 Create Agent Registry Service
**File**: `api/services/agent_registry.py`

```python
class AgentRegistry:
    """Registry of available agents with capabilities and pricing"""

    AGENTS = {
        "discovery_agent": {
            "name": "Discovery Agent",
            "description": "Analyzes web applications to discover structure and elements",
            "tier": "basic",
            "capabilities": ["element_discovery", "page_mapping", "flow_detection"],
            "price_per_run": 0.10,
            "avg_duration_seconds": 30,
            "icon": "search",
            "category": "discovery"
        },
        "test_creation_agent": {
            "name": "Test Creation Agent",
            "description": "Generates Playwright test code from discovered elements",
            "tier": "basic",
            "capabilities": ["code_generation", "assertion_creation", "test_data"],
            "price_per_run": 0.25,
            "avg_duration_seconds": 60,
            "icon": "code",
            "category": "generation"
        },
        "self_healing_agent": {
            "name": "Self-Healing Agent",
            "description": "Automatically fixes broken tests using AI analysis",
            "tier": "premium",
            "capabilities": ["error_analysis", "code_repair", "selector_update"],
            "price_per_run": 0.50,
            "avg_duration_seconds": 45,
            "icon": "healing",
            "category": "maintenance"
        },
        "performance_agent": {
            "name": "Performance Agent",
            "description": "Analyzes application performance and generates load tests",
            "tier": "enterprise",
            "capabilities": ["load_testing", "performance_metrics", "bottleneck_detection"],
            "price_per_run": 1.00,
            "avg_duration_seconds": 120,
            "icon": "speed",
            "category": "performance"
        },
        "cross_browser_agent": {
            "name": "Cross-Browser Agent",
            "description": "Adapts tests for multiple browsers and devices",
            "tier": "premium",
            "capabilities": ["browser_adaptation", "device_testing", "compatibility"],
            "price_per_run": 0.75,
            "avg_duration_seconds": 90,
            "icon": "devices",
            "category": "compatibility"
        }
    }

    def get_available_agents(self, customer_tier: str) -> List[dict]:
        """Get agents available for customer's subscription tier"""
        tier_hierarchy = ['basic', 'premium', 'enterprise']
        customer_tier_index = tier_hierarchy.index(customer_tier)

        return [
            agent for agent in self.AGENTS.values()
            if tier_hierarchy.index(agent['tier']) <= customer_tier_index
        ]

    def get_agent_by_id(self, agent_id: str) -> Optional[dict]:
        return self.AGENTS.get(agent_id)
```

#### 5.1.2 Agent Marketplace API Endpoints
**File**: `api/routers/marketplace.py`

```python
from fastapi import APIRouter, Depends
from services.agent_registry import AgentRegistry

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])

@router.get("/agents")
async def list_available_agents(current_user: dict = Depends(get_current_user)):
    """List all agents available to the customer"""
    customer = await get_customer(current_user['customer_id'])
    registry = AgentRegistry()

    return {
        "status": "success",
        "data": registry.get_available_agents(customer['subscription_tier'])
    }

@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about an agent"""
    registry = AgentRegistry()
    agent = registry.get_agent_by_id(agent_id)

    if not agent:
        raise HTTPException(404, "Agent not found")

    return {"status": "success", "data": agent}

@router.post("/agents/{agent_id}/hire")
async def hire_agent(
    agent_id: str,
    job_request: AgentJobRequest,
    current_user: dict = Depends(get_current_user)
):
    """Hire an agent for a specific job"""
    registry = AgentRegistry()
    agent = registry.get_agent_by_id(agent_id)

    # Validate agent access based on subscription
    # Create job and queue for processing
    # Return job ID for tracking

    job_id = await create_agent_job(
        customer_id=current_user['customer_id'],
        agent_id=agent_id,
        job_config=job_request.dict()
    )

    return {
        "status": "success",
        "data": {
            "job_id": str(job_id),
            "agent": agent['name'],
            "estimated_duration": agent['avg_duration_seconds']
        }
    }
```

## 5.2 Marketplace UI

### Tasks

#### 5.2.1 Create Agent Marketplace Component
**File**: `web-dashboard/src/components/AgentMarketplace.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

const AgentMarketplace = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    const response = await fetch('/api/v1/marketplace/agents');
    const data = await response.json();
    setAgents(data.data);
    setLoading(false);
  };

  const hireAgent = async (agentId) => {
    // Implementation
  };

  const getTierBadgeColor = (tier) => {
    switch(tier) {
      case 'basic': return 'bg-green-100 text-green-800';
      case 'premium': return 'bg-blue-100 text-blue-800';
      case 'enterprise': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Agent Marketplace</h1>
      <p className="text-gray-600 mb-8">
        Hire specialized AI agents for your testing needs
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map(agent => (
          <Card key={agent.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{agent.name}</CardTitle>
                <Badge className={getTierBadgeColor(agent.tier)}>
                  {agent.tier}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">{agent.description}</p>

              <div className="mb-4">
                <h4 className="font-medium text-sm mb-2">Capabilities:</h4>
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities.map(cap => (
                    <Badge key={cap} variant="outline" className="text-xs">
                      {cap}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex justify-between items-center mt-4 pt-4 border-t">
                <span className="text-lg font-bold">
                  ${agent.price_per_run.toFixed(2)}/run
                </span>
                <Button onClick={() => hireAgent(agent.id)}>
                  Hire Agent
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AgentMarketplace;
```

#### 5.2.2 Create Agent Hiring Flow
**File**: `web-dashboard/src/components/HireAgentDialog.jsx`

```jsx
const HireAgentDialog = ({ agent, onHire, onClose }) => {
  const [config, setConfig] = useState({
    applicationId: '',
    priority: 'normal',
    options: {}
  });

  const handleHire = async () => {
    const response = await fetch(`/api/v1/marketplace/agents/${agent.id}/hire`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    const data = await response.json();
    onHire(data.data);
  };

  return (
    <Dialog open onClose={onClose}>
      <DialogTitle>Hire {agent.name}</DialogTitle>
      <DialogContent>
        {/* Configuration form */}
        <Select
          label="Application"
          value={config.applicationId}
          onChange={(v) => setConfig({...config, applicationId: v})}
        >
          {/* Application options */}
        </Select>

        <Select
          label="Priority"
          value={config.priority}
          onChange={(v) => setConfig({...config, priority: v})}
        >
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
        </Select>

        <div className="mt-4 p-4 bg-gray-50 rounded">
          <p className="font-medium">Estimated Cost: ${agent.price_per_run}</p>
          <p className="text-sm text-gray-600">
            Estimated Duration: {agent.avg_duration_seconds}s
          </p>
        </div>
      </DialogContent>
      <DialogActions>
        <Button variant="outline" onClick={onClose}>Cancel</Button>
        <Button onClick={handleHire}>Confirm & Hire</Button>
      </DialogActions>
    </Dialog>
  );
};
```

## 5.3 Agent Performance Metrics

### Tasks

#### 5.3.1 Create Agent Performance Dashboard
**File**: `web-dashboard/src/components/AgentPerformance.jsx`

```jsx
const AgentPerformance = () => {
  const [metrics, setMetrics] = useState(null);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Agent Performance</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Total Agent Runs"
          value={metrics?.totalRuns || 0}
          change="+12%"
        />
        <MetricCard
          title="Success Rate"
          value={`${metrics?.successRate || 0}%`}
          change="+5%"
        />
        <MetricCard
          title="Avg. Duration"
          value={`${metrics?.avgDuration || 0}s`}
          change="-8%"
        />
        <MetricCard
          title="Total Cost"
          value={`$${metrics?.totalCost || 0}`}
          change="+3%"
        />
      </div>

      {/* Charts and detailed metrics */}
    </div>
  );
};
```

## 5.4 Success Criteria - Phase 5

- [ ] Agent registry with full capability descriptions
- [ ] Marketplace UI showing available agents
- [ ] "Hire Agent" flow with configuration
- [ ] Agent usage tracked for billing
- [ ] Performance metrics dashboard
- [ ] Agents filterable by tier/capability
- [ ] Cost estimation before hiring

---

# Immediate Next Steps

## Starting Phase 1 Today

### Step 1: Create Archive Directory Structure
```bash
mkdir -p web-dashboard/archive
mkdir -p agents/archive
mkdir -p archive/scripts
```

### Step 2: Begin Component Analysis
1. Read each CreateTest variant
2. Document unique features in each
3. Create consolidation plan

### Step 3: Execute Consolidation
1. Merge features into main components
2. Update all imports
3. Move deprecated files to archive
4. Test thoroughly

### Step 4: Commit and Validate
1. Run all tests
2. Verify UI functionality
3. Commit with clear message

---

# Summary

| Phase | Duration | Priority | Key Deliverables |
|-------|----------|----------|------------------|
| 1 | 3-5 days | Critical | Clean codebase, single source of truth |
| 2 | 4-6 days | High | Real browser discovery, actual selectors |
| 3 | 5-7 days | High | Agent collaboration, refinement loops |
| 4 | 5-7 days | High | Production-ready, secure, monitored |
| 5 | 5-7 days | Medium | Marketplace UI, agent hiring flow |

**Total Estimated Duration**: 22-32 days

**End State**: A production-ready "QA-as-a-Service" platform where customers can:
1. Sign up and select a subscription plan
2. Register their applications
3. Browse and hire specialized AI agents
4. Generate comprehensive test suites automatically
5. Monitor agent progress in real-time
6. Execute tests and view results
7. Benefit from self-healing test maintenance

---

*Document will be updated as implementation progresses.*
