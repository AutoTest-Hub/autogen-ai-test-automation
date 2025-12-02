# System Architecture Overview

## Vision

AutoGen AI QA Platform is an **AI-native test automation platform** where users "hire" AI agents to perform QA tasks, similar to hiring human contractors.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                │
│                    "Sarah, test my checkout flow"                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                                    │
│              Routes tasks, manages workflows, coordinates agents        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────┬───────────┼───────────┬───────────────┐
        ▼               ▼           ▼           ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  DISCOVERY  │ │  PLANNING   │ │  CREATION   │ │   REVIEW    │ │  EXECUTION  │
│   Agent     │ │   Agent     │ │   Agent     │ │   Agent     │ │   Agent     │
│             │ │             │ │             │ │             │ │             │
│ Finds UI    │ │ Creates     │ │ Generates   │ │ Reviews     │ │ Runs tests  │
│ elements    │ │ test plans  │ │ test code   │ │ quality     │ │ reports     │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
        │               │           │           │               │
        └───────────────┴───────────┼───────────┴───────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      APPLICATION CONTEXT                                │
│           Business rules, API specs, domain knowledge, credentials      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agents (`agents/`)

Specialized AI agents that perform specific QA tasks.

| Agent | Role | Key Capabilities |
|-------|------|------------------|
| **DiscoveryAgent** | Find UI elements | Crawl pages, extract selectors, map page structure |
| **PlanningAgent** | Create test plans | Analyze requirements, prioritize tests, assess risk |
| **TestCreationAgent** | Generate tests | Write Playwright/Selenium code, create assertions |
| **ReviewAgent** | Quality control | Review code, validate coverage, suggest improvements |
| **ExecutionAgent** | Run tests | Execute tests, capture results, handle retries |
| **SelfHealingAgent** | Fix broken tests | Update selectors, adapt to UI changes |
| **ReportingAgent** | Generate insights | Create reports, identify trends, recommend actions |

### 2. Orchestrator (`orchestrator/`)

Coordinates agent workflows and manages the pipeline.

```python
# Workflow templates
- standard_test_automation      # Plan → Create → Review → Execute
- quick_test_generation         # Create → Execute (skip review)
- iterative_test_generation     # Includes review-refinement loop
- comprehensive_quality_analysis # Full pipeline with insights
```

### 3. Message Protocol (`orchestrator/agent_protocol.py`)

Typed messages for agent communication.

```python
MessageType.TASK_REQUEST      # Assign work
MessageType.REVIEW_FEEDBACK   # Send improvement suggestions
MessageType.HEALING_REQUEST   # Request test fix
```

### 4. Application Context (`context/`) [Phase 0]

Per-customer application knowledge.

```python
ApplicationContext:
  - business_rules     # Domain-specific rules
  - api_specs          # OpenAPI documentation
  - domain_glossary    # Terminology dictionary
  - environments       # Dev/Staging/Prod configs
```

### 5. LLM Integration (`agents/base_agent.py`)

Provider chain for AI capabilities.

```
Local AI (Ollama) → OpenAI → Anthropic
```

## Data Flow

### Test Generation Pipeline

```
1. DISCOVER
   Input: Application URL
   Output: DiscoveryResult (selectors, page structure)

2. PLAN
   Input: Requirements + DiscoveryResult
   Output: TestPlan (prioritized test cases)

3. CREATE
   Input: TestPlan + DiscoveryResult
   Output: GeneratedTests (Playwright code)

4. REVIEW
   Input: GeneratedTests
   Output: ReviewFeedback (score, issues, suggestions)

5. REFINE (if needed)
   Input: GeneratedTests + ReviewFeedback
   Output: RefinedTests

6. EXECUTE
   Input: ApprovedTests
   Output: ExecutionResults

7. HEAL (if failures)
   Input: FailedTest + Error + DiscoveryResult
   Output: HealedTest

8. REPORT
   Input: ExecutionResults
   Output: TestReport + Insights
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Web Automation** | Playwright, Selenium |
| **LLM Providers** | Ollama (local), OpenAI, Anthropic |
| **Backend** | Python, FastAPI |
| **Frontend** | React, TypeScript |
| **Testing** | pytest, pytest-asyncio |

## Key Design Decisions

| Decision | Rationale | ADR |
|----------|-----------|-----|
| LLM provider chain | Cost, privacy, resilience | [ADR-001](../decisions/ADR-001-llm-provider-chain.md) |
| Message bus architecture | Decoupling, auditability | [ADR-002](../decisions/ADR-002-message-protocol.md) |
| Application context layer | Domain awareness | [ADR-003](../decisions/ADR-003-application-context.md) |

## Implementation Phases

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 0** | Application Context | 🔴 Proposed |
| **Phase 1** | Core Intelligence (LLM) | 🟡 88% |
| **Phase 2** | Agent Collaboration | 🟡 96% |
| **Phase 3** | Agent Personalities | 🔴 Not Started |
| **Phase 4** | Marketplace & Billing | 🔴 Not Started |
| **Phase 5** | AI-Native Storage | 🔴 Not Started |
| **Phase 6** | Consolidation | 🔴 Not Started |

## Directory Structure

```
autogen-ai-test-automation/
├── agents/                 # AI agent implementations
│   ├── base_agent.py      # Base class with LLM integration
│   ├── planning_agent.py  # Test planning
│   ├── test_creation_agent.py  # Test generation
│   └── ...
├── orchestrator/          # Workflow coordination
│   ├── workflow_orchestrator.py
│   └── agent_protocol.py  # Message types
├── context/               # Application context [Phase 0]
│   ├── application_context.py
│   └── knowledge_ingester.py
├── contracts/             # Data contracts
│   └── agent_contracts.py
├── config/                # Configuration
│   └── settings.py
├── docs/                  # Documentation
│   ├── architecture/
│   └── decisions/
└── tests/                 # Test suites
```

---

*Last Updated: 2025-12-01*
