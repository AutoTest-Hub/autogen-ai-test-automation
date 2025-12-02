# Phase 0: Application Context & Onboarding

## Overview

This phase addresses the fundamental question: **"How do AI agents understand my application?"**

Just as human QA engineers go through onboarding to learn about a system, AI agents need application context to generate relevant, business-aware tests.

## Problem Statement

### Current State
```
User: "Test the checkout flow"

Agent (without context):
- Generates generic e-commerce checkout tests
- Uses placeholder selectors
- Misses business rules (e.g., "$500 orders need approval")
- Doesn't know about edge cases
```

### Desired State
```
User: "Test the checkout flow"

Agent (with context):
- Knows the tech stack (React + Stripe + Django)
- Uses real selectors from discovery
- Applies business rule: orders > $500 need manager approval
- Tests the specific payment methods configured
- Follows existing test naming conventions
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         ONBOARDING WIZARD                            │
│  Step 1: App URL → Step 2: Tools → Step 3: Knowledge → Step 4: Rules │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       APPLICATION CONTEXT                            │
├────────────────────┬────────────────────┬────────────────────────────┤
│   KNOWLEDGE BASE   │   INTEGRATIONS     │   ENVIRONMENT CONFIG       │
├────────────────────┼────────────────────┼────────────────────────────┤
│ • API Specs        │ • GitHub           │ • Dev URL                  │
│ • Business Rules   │ • Jira             │ • Staging URL              │
│ • Domain Glossary  │ • Confluence       │ • Prod URL                 │
│ • Test Patterns    │ • CI/CD            │ • Credentials (vault)      │
│ • Tech Stack       │                    │ • Test Data Sources        │
└────────────────────┴────────────────────┴────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      CONTEXT INJECTION                               │
│                                                                      │
│   LLM Prompt = Application Context + Agent Role Context + User Task  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  CONTEXT-AWARE AGENTS     │
                    │  Planning | Creation |... │
                    └───────────────────────────┘
```

## Components

### 1. ApplicationContext (`context/application_context.py`)

The central class that holds all knowledge about a customer's application.

```python
@dataclass
class ApplicationContext:
    # Identity
    app_id: str
    app_name: str
    app_url: str

    # Technical
    tech_stack: TechStackInfo
    api_specs: Dict[str, OpenAPISpec]

    # Business
    business_rules: List[BusinessRule]
    domain_glossary: Dict[str, str]
    critical_journeys: List[UserJourney]

    # Patterns
    test_patterns: List[TestPattern]
    naming_conventions: NamingConventions

    # Environment
    environments: Dict[str, EnvironmentConfig]
```

### 2. Knowledge Ingester (`context/knowledge_ingester.py`)

Automatically extracts knowledge from various sources.

| Source | What We Extract |
|--------|-----------------|
| OpenAPI/Swagger | Endpoints, request/response schemas, auth requirements |
| README.md | Tech stack, setup instructions, architecture notes |
| Existing Tests | Naming patterns, assertion styles, fixture usage |
| Confluence | Business rules, user stories, domain terminology |

### 3. Tool Integrations (`integrations/`)

Read-only connections to customer tools.

| Integration | Purpose |
|-------------|---------|
| GitHub | Read codebase, PRs, issues for context |
| Jira | Read tickets, requirements, acceptance criteria |
| Confluence | Read documentation, business rules |

### 4. Context Injection (`agents/base_agent.py`)

Inject relevant context into every LLM prompt.

```python
async def generate_llm_response(self, prompt: str) -> Dict[str, Any]:
    context = self.application_context.get_context_for_agent(self.role)

    enhanced_prompt = f"""
    === APPLICATION CONTEXT ===
    {context}

    === YOUR TASK ===
    {prompt}
    """

    return await self._call_llm(enhanced_prompt)
```

## Data Models

### BusinessRule

```python
@dataclass
class BusinessRule:
    rule_id: str
    description: str
    category: str  # "validation", "workflow", "security", etc.
    applies_to: List[str]  # ["checkout", "orders", etc.]
    test_implications: str  # How this affects testing

# Example:
BusinessRule(
    rule_id="BR-001",
    description="Orders over $500 require manager approval",
    category="workflow",
    applies_to=["checkout", "orders"],
    test_implications="Must test approval flow for high-value orders"
)
```

### TechStackInfo

```python
@dataclass
class TechStackInfo:
    frontend: str  # "React 18"
    backend: str   # "Django 4.2"
    database: str  # "PostgreSQL 15"
    testing: str   # "Playwright + pytest"
    ci_cd: str     # "GitHub Actions"
```

### EnvironmentConfig

```python
@dataclass
class EnvironmentConfig:
    name: str      # "staging"
    base_url: str  # "https://staging.example.com"
    auth_type: str # "oauth2" | "basic" | "api_key"
    credentials_ref: str  # Reference to credential vault
    test_data_source: str  # "fixtures" | "api" | "database"
```

## Implementation Phases

### Phase 0.1: Core Context (Week 1)
- [ ] Create `ApplicationContext` dataclass
- [ ] Implement `get_context_for_agent()` method
- [ ] Add context injection to `base_agent.py`
- [ ] Create basic storage (JSON files initially)

### Phase 0.2: Knowledge Ingestion (Week 2)
- [ ] OpenAPI/Swagger parser
- [ ] README/Markdown analyzer
- [ ] Existing test pattern extractor
- [ ] Tech stack detector

### Phase 0.3: Tool Integrations (Week 3)
- [ ] GitHub integration (read-only)
- [ ] Jira integration (read-only)
- [ ] Confluence integration (read-only)

### Phase 0.4: Onboarding Flow (Week 4)
- [ ] Onboarding wizard API
- [ ] Credential vault (encrypted storage)
- [ ] Environment configuration UI
- [ ] Business rules editor

## API Endpoints

```
POST   /api/v1/apps                    # Create new application context
GET    /api/v1/apps/{app_id}           # Get application context
PUT    /api/v1/apps/{app_id}           # Update application context
DELETE /api/v1/apps/{app_id}           # Delete application context

POST   /api/v1/apps/{app_id}/onboard   # Start onboarding wizard
GET    /api/v1/apps/{app_id}/onboard/status  # Get onboarding progress

POST   /api/v1/apps/{app_id}/ingest/openapi  # Ingest OpenAPI spec
POST   /api/v1/apps/{app_id}/ingest/github   # Connect GitHub repo
POST   /api/v1/apps/{app_id}/ingest/jira     # Connect Jira project

POST   /api/v1/apps/{app_id}/rules     # Add business rule
GET    /api/v1/apps/{app_id}/rules     # List business rules

POST   /api/v1/apps/{app_id}/glossary  # Add glossary term
GET    /api/v1/apps/{app_id}/glossary  # Get domain glossary
```

## Success Metrics

| Metric | Target |
|--------|--------|
| Test relevance score | >80% tests address actual business needs |
| Selector accuracy | >95% generated selectors work on first run |
| Business rule coverage | >90% defined rules have corresponding tests |
| Onboarding completion | <30 minutes for basic setup |

## Dependencies

- Phase 1 (Core Intelligence) - Agents must have LLM integration
- Phase 2 (Agent Collaboration) - Message protocol for context sharing

## Open Questions

1. **Multi-tenant isolation**: How to securely separate customer contexts?
2. **Context size limits**: How to handle large knowledge bases vs. LLM token limits?
3. **Refresh strategy**: How often to re-sync from connected tools?
4. **Offline mode**: Can agents work with cached context if tools are unavailable?

---

*See also: [ADR-003: Application Context](../../decisions/ADR-003-application-context.md)*
