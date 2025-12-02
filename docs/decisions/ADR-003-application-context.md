# ADR-003: Application Context Layer

## Status
Proposed

## Date
2025-12-01

## Context

A fundamental gap exists between how human QA engineers and AI agents approach testing:

### Human QA Onboarding
When a human QA engineer joins a project, they:
1. Read documentation (Confluence, README, wikis)
2. Learn business rules and domain terminology
3. Understand the tech stack (React, Django, etc.)
4. Review existing test suites and patterns
5. Get access to tools (Jira, GitHub, CI/CD)
6. Learn about known issues and edge cases

### Current AI Agent State
Our AI agents only know:
1. What the Discovery Agent finds (UI elements, selectors)
2. What the user types in requirements
3. Generic knowledge from LLM training

This gap means agents:
- Generate generic tests that don't reflect business rules
- Miss domain-specific terminology and concepts
- Can't leverage existing test patterns
- Don't understand environment differences (dev/staging/prod)

## Decision

We introduce an **Application Context Layer** that provides agents with the same knowledge a human QA engineer would have after onboarding.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION CONTEXT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Knowledge Base │  │   Integrations  │  │   Environment   │ │
│  │  - API specs    │  │   - GitHub      │  │   - URLs        │ │
│  │  - Business     │  │   - Jira        │  │   - Credentials │ │
│  │    rules        │  │   - Confluence  │  │   - Test data   │ │
│  │  - Glossary     │  │   - CI/CD       │  │                 │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│           └────────────────────┼────────────────────┘          │
│                                ▼                               │
│                    ┌───────────────────────┐                   │
│                    │   Context Injection   │                   │
│                    │   into Agent Prompts  │                   │
│                    └───────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. ApplicationContext Class

```python
@dataclass
class ApplicationContext:
    """Per-customer application knowledge base"""
    app_id: str
    app_name: str
    tech_stack: TechStackInfo
    business_rules: List[BusinessRule]
    domain_glossary: Dict[str, str]
    api_specs: Dict[str, OpenAPISpec]
    environments: Dict[str, EnvironmentConfig]
    existing_test_patterns: List[TestPattern]

    def get_context_for_agent(self, role: AgentRole) -> str:
        """Generate role-specific context for LLM prompt injection."""
```

#### 2. Knowledge Ingestion

```python
class KnowledgeIngester:
    async def ingest_api_docs(self, swagger_url: str) -> OpenAPISpec
    async def ingest_confluence(self, space_key: str) -> List[Document]
    async def ingest_readme(self, repo_path: str) -> Document
    async def analyze_existing_tests(self, test_dir: str) -> List[TestPattern]
```

#### 3. Tool Integrations

```python
class IntegrationManager:
    github: GitHubIntegration      # Read repos, PRs, issues
    jira: JiraIntegration          # Read tickets, requirements
    confluence: ConfluenceIntegration  # Read documentation
```

#### 4. Context Injection

Modified LLM call to include context:

```python
# In base_agent.py
async def generate_llm_response(self, prompt: str, ...) -> Dict[str, Any]:
    # Inject application context
    if self.application_context:
        context = self.application_context.get_context_for_agent(self.role)
        enhanced_prompt = f"""
        APPLICATION CONTEXT:
        {context}

        ---
        TASK:
        {prompt}
        """
    else:
        enhanced_prompt = prompt

    return await self._call_llm(enhanced_prompt)
```

### Onboarding Flow

```
Step 1: Connect Application
├── Enter application URL
├── Provide authentication (stored in vault)
└── Initial discovery scan

Step 2: Connect Tools (Optional)
├── GitHub repository
├── Jira project
└── Confluence space

Step 3: Ingest Knowledge
├── Parse API documentation (OpenAPI/Swagger)
├── Import existing test suites
├── Extract patterns and conventions

Step 4: Define Business Rules
├── Add domain glossary terms
├── Define business rules in natural language
└── Mark critical user journeys

Step 5: Configure Environments
├── Dev/Staging/Prod URLs
├── Test data sources
└── Credential mappings
```

## Consequences

### Positive
- **Relevant tests**: Agents generate tests that reflect actual business rules
- **Domain awareness**: Tests use correct terminology and concepts
- **Pattern consistency**: New tests follow existing conventions
- **Environment-aware**: Tests can target specific environments
- **Reduced hallucination**: Context grounds LLM responses in reality

### Negative
- **Onboarding overhead**: Users must complete setup before using agents
- **Storage requirements**: Knowledge bases require persistent storage
- **Maintenance burden**: Context must be updated as apps change
- **Integration complexity**: Each tool integration needs maintenance

### Mitigations
- Progressive onboarding (minimal required, rest optional)
- Automated context refresh from connected tools
- Clear documentation on setup process
- Default context for quick-start scenarios

## Implementation Plan

### Phase 0.1: Core Context
1. `ApplicationContext` dataclass
2. `get_context_for_agent()` method
3. Context injection in `base_agent.py`

### Phase 0.2: Ingestion
1. OpenAPI/Swagger parser
2. README/Markdown parser
3. Existing test analyzer

### Phase 0.3: Integrations
1. GitHub read-only integration
2. Jira read-only integration
3. Confluence read-only integration

### Phase 0.4: Onboarding UI
1. Wizard API endpoints
2. Credential vault
3. Environment configuration

## Related Files (To Be Created)
- `context/application_context.py`
- `context/knowledge_ingester.py`
- `context/environment_config.py`
- `integrations/base_integration.py`
- `integrations/github_integration.py`
- `api/routers/onboarding.py`

## Open Questions

1. **Storage**: SQLite vs PostgreSQL for knowledge base?
2. **Vector DB**: Add semantic search with Chroma/Pinecone?
3. **Refresh**: How often to re-sync from connected tools?
4. **Multi-tenant**: How to isolate customer contexts?

---

*Decision made by: Claude (AI Assistant)*
*Reviewed by: [Pending human review required]*
