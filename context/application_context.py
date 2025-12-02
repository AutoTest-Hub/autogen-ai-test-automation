"""
Application Context Module for AutoGen AI QA Platform

This module provides the ApplicationContext class that stores all knowledge
about a customer's application, enabling AI agents to generate relevant,
business-aware tests.

See: docs/architecture/phase-0-application-context/README.md
See: docs/decisions/ADR-003-application-context.md
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import os
import uuid


class EnvironmentType(str, Enum):
    """Environment types for application deployment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"


class AuthType(str, Enum):
    """Authentication types supported"""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


@dataclass
class TechStackInfo:
    """Technology stack information for an application"""
    frontend: str = ""  # e.g., "React 18", "Vue 3", "Angular 16"
    backend: str = ""   # e.g., "Django 4.2", "FastAPI", "Node.js"
    database: str = ""  # e.g., "PostgreSQL 15", "MongoDB"
    testing: str = ""   # e.g., "Playwright + pytest", "Cypress"
    ci_cd: str = ""     # e.g., "GitHub Actions", "Jenkins"
    hosting: str = ""   # e.g., "AWS", "Vercel", "On-premise"
    additional: Dict[str, str] = field(default_factory=dict)

    def to_prompt_text(self) -> str:
        """Convert to text for LLM prompt injection"""
        parts = []
        if self.frontend:
            parts.append(f"Frontend: {self.frontend}")
        if self.backend:
            parts.append(f"Backend: {self.backend}")
        if self.database:
            parts.append(f"Database: {self.database}")
        if self.testing:
            parts.append(f"Testing: {self.testing}")
        if self.ci_cd:
            parts.append(f"CI/CD: {self.ci_cd}")
        if self.hosting:
            parts.append(f"Hosting: {self.hosting}")
        for key, value in self.additional.items():
            parts.append(f"{key}: {value}")
        return "\n".join(parts) if parts else "Not specified"


@dataclass
class BusinessRule:
    """A business rule that affects testing"""
    rule_id: str
    name: str
    description: str
    category: str  # "validation", "workflow", "security", "calculation", etc.
    applies_to: List[str] = field(default_factory=list)  # ["checkout", "orders"]
    test_implications: str = ""  # How this affects testing
    priority: str = "medium"  # "critical", "high", "medium", "low"
    examples: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_prompt_text(self) -> str:
        """Convert to text for LLM prompt injection"""
        text = f"[{self.category.upper()}] {self.name}: {self.description}"
        if self.test_implications:
            text += f"\n  → Test implication: {self.test_implications}"
        if self.examples:
            text += f"\n  → Examples: {', '.join(self.examples[:3])}"
        return text


@dataclass
class EnvironmentConfig:
    """Configuration for a specific environment (dev/staging/prod)"""
    name: str
    env_type: EnvironmentType
    base_url: str
    auth_type: AuthType = AuthType.NONE
    credentials_ref: Optional[str] = None  # Reference to credential vault
    api_base_url: Optional[str] = None
    test_data_source: str = "fixtures"  # "fixtures", "api", "database", "mock"
    additional_config: Dict[str, Any] = field(default_factory=dict)
    is_default: bool = False

    def to_prompt_text(self) -> str:
        """Convert to text for LLM prompt injection"""
        return f"{self.name} ({self.env_type.value}): {self.base_url}"


@dataclass
class UserJourney:
    """A critical user journey that must be tested"""
    journey_id: str
    name: str
    description: str
    steps: List[str] = field(default_factory=list)
    priority: str = "high"
    frequency: str = ""  # "every release", "daily", "weekly"
    owner: str = ""

    def to_prompt_text(self) -> str:
        """Convert to text for LLM prompt injection"""
        steps_text = "\n    ".join(f"{i+1}. {step}" for i, step in enumerate(self.steps))
        return f"[{self.priority.upper()}] {self.name}\n  {self.description}\n  Steps:\n    {steps_text}"


@dataclass
class TestPattern:
    """A pattern extracted from existing tests"""
    pattern_type: str  # "naming", "assertion", "fixture", "setup", "teardown"
    pattern: str
    examples: List[str] = field(default_factory=list)
    frequency: int = 1  # How often this pattern appears

    def to_prompt_text(self) -> str:
        """Convert to text for LLM prompt injection"""
        return f"{self.pattern_type}: {self.pattern}"


@dataclass
class DomainTerm:
    """A domain-specific term and its meaning"""
    term: str
    definition: str
    aliases: List[str] = field(default_factory=list)
    context: str = ""  # Where this term is used
    examples: List[str] = field(default_factory=list)


@dataclass
class APIEndpoint:
    """An API endpoint from OpenAPI/Swagger spec"""
    path: str
    method: str  # GET, POST, PUT, DELETE, etc.
    summary: str = ""
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Any] = field(default_factory=dict)
    auth_required: bool = False
    tags: List[str] = field(default_factory=list)

    def to_prompt_text(self) -> str:
        """Convert to text for LLM prompt injection"""
        auth_marker = " [AUTH]" if self.auth_required else ""
        return f"{self.method.upper()} {self.path}{auth_marker} - {self.summary}"


@dataclass
class ApplicationContext:
    """
    Central class that holds all knowledge about a customer's application.

    This context is injected into agent LLM prompts to provide domain awareness,
    similar to how a human QA engineer learns about an application during onboarding.
    """

    # Identity
    app_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    app_name: str = ""
    app_description: str = ""
    app_url: str = ""

    # Technical context
    tech_stack: TechStackInfo = field(default_factory=TechStackInfo)
    api_endpoints: List[APIEndpoint] = field(default_factory=list)

    # Business context
    business_rules: List[BusinessRule] = field(default_factory=list)
    domain_glossary: Dict[str, DomainTerm] = field(default_factory=dict)
    critical_journeys: List[UserJourney] = field(default_factory=list)

    # Patterns from existing tests
    test_patterns: List[TestPattern] = field(default_factory=list)
    naming_conventions: Dict[str, str] = field(default_factory=dict)

    # Environments
    environments: Dict[str, EnvironmentConfig] = field(default_factory=dict)
    default_environment: str = "development"

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    onboarding_complete: bool = False

    def get_context_for_agent(self, agent_role: str, max_tokens: int = 2000) -> str:
        """
        Generate role-specific context for LLM prompt injection.

        Different agents need different aspects of the context:
        - PlanningAgent: Business rules, critical journeys, tech stack
        - TestCreationAgent: Selectors, patterns, naming conventions, API endpoints
        - ReviewAgent: Business rules, test patterns, quality standards
        - DiscoveryAgent: Tech stack, known UI patterns

        Args:
            agent_role: The role of the agent requesting context
            max_tokens: Approximate max tokens for context (to avoid prompt overflow)

        Returns:
            Formatted context string for LLM prompt injection
        """
        sections = []

        # Header
        sections.append(f"=== APPLICATION CONTEXT: {self.app_name} ===")
        if self.app_description:
            sections.append(f"Description: {self.app_description}")
        sections.append(f"URL: {self.app_url}")
        sections.append("")

        # Tech Stack (all agents benefit from this)
        if self.tech_stack:
            sections.append("TECH STACK:")
            sections.append(self.tech_stack.to_prompt_text())
            sections.append("")

        # Role-specific context
        if agent_role in ["planning", "orchestrator"]:
            # Planning needs business context
            if self.business_rules:
                sections.append("BUSINESS RULES:")
                for rule in self.business_rules[:10]:  # Limit to top 10
                    sections.append(f"  • {rule.to_prompt_text()}")
                sections.append("")

            if self.critical_journeys:
                sections.append("CRITICAL USER JOURNEYS:")
                for journey in self.critical_journeys[:5]:  # Limit to top 5
                    sections.append(f"  {journey.to_prompt_text()}")
                sections.append("")

        elif agent_role in ["test_creation", "self_healing"]:
            # Test creation needs patterns and API endpoints
            if self.test_patterns:
                sections.append("TEST PATTERNS TO FOLLOW:")
                for pattern in self.test_patterns[:10]:
                    sections.append(f"  • {pattern.to_prompt_text()}")
                sections.append("")

            if self.naming_conventions:
                sections.append("NAMING CONVENTIONS:")
                for key, value in list(self.naming_conventions.items())[:5]:
                    sections.append(f"  • {key}: {value}")
                sections.append("")

            if self.api_endpoints:
                sections.append("API ENDPOINTS:")
                for endpoint in self.api_endpoints[:15]:
                    sections.append(f"  • {endpoint.to_prompt_text()}")
                sections.append("")

            # Also include key business rules
            if self.business_rules:
                sections.append("KEY BUSINESS RULES:")
                critical_rules = [r for r in self.business_rules if r.priority in ["critical", "high"]]
                for rule in critical_rules[:5]:
                    sections.append(f"  • {rule.to_prompt_text()}")
                sections.append("")

        elif agent_role == "review":
            # Review needs quality standards and business rules
            if self.business_rules:
                sections.append("BUSINESS RULES TO VERIFY:")
                for rule in self.business_rules[:10]:
                    sections.append(f"  • {rule.to_prompt_text()}")
                sections.append("")

            if self.test_patterns:
                sections.append("EXPECTED TEST PATTERNS:")
                for pattern in self.test_patterns[:5]:
                    sections.append(f"  • {pattern.to_prompt_text()}")
                sections.append("")

        elif agent_role == "discovery":
            # Discovery needs to know what to look for
            if self.critical_journeys:
                sections.append("CRITICAL JOURNEYS TO DISCOVER:")
                for journey in self.critical_journeys[:5]:
                    sections.append(f"  • {journey.name}: {journey.description}")
                sections.append("")

        # Domain glossary (useful for all agents)
        if self.domain_glossary:
            sections.append("DOMAIN TERMINOLOGY:")
            for term, definition in list(self.domain_glossary.items())[:10]:
                if isinstance(definition, DomainTerm):
                    sections.append(f"  • {term}: {definition.definition}")
                else:
                    sections.append(f"  • {term}: {definition}")
            sections.append("")

        # Current environment
        default_env = self.environments.get(self.default_environment)
        if default_env:
            sections.append(f"CURRENT ENVIRONMENT: {default_env.to_prompt_text()}")
            sections.append("")

        context = "\n".join(sections)

        # Truncate if too long (rough token estimate: 4 chars per token)
        max_chars = max_tokens * 4
        if len(context) > max_chars:
            context = context[:max_chars] + "\n... [Context truncated]"

        return context

    def add_business_rule(self, rule: BusinessRule) -> None:
        """Add a business rule to the context"""
        self.business_rules.append(rule)
        self.updated_at = datetime.now()

    def add_domain_term(self, term: str, definition: str, **kwargs) -> None:
        """Add a domain term to the glossary"""
        self.domain_glossary[term] = DomainTerm(
            term=term,
            definition=definition,
            **kwargs
        )
        self.updated_at = datetime.now()

    def add_environment(self, config: EnvironmentConfig) -> None:
        """Add an environment configuration"""
        self.environments[config.name] = config
        if config.is_default:
            self.default_environment = config.name
        self.updated_at = datetime.now()

    def add_api_endpoint(self, endpoint: APIEndpoint) -> None:
        """Add an API endpoint from spec"""
        self.api_endpoints.append(endpoint)
        self.updated_at = datetime.now()

    def add_test_pattern(self, pattern: TestPattern) -> None:
        """Add a test pattern from existing tests"""
        self.test_patterns.append(pattern)
        self.updated_at = datetime.now()

    def add_user_journey(self, journey: UserJourney) -> None:
        """Add a critical user journey"""
        self.critical_journeys.append(journey)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for storage"""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "app_description": self.app_description,
            "app_url": self.app_url,
            "tech_stack": {
                "frontend": self.tech_stack.frontend,
                "backend": self.tech_stack.backend,
                "database": self.tech_stack.database,
                "testing": self.tech_stack.testing,
                "ci_cd": self.tech_stack.ci_cd,
                "hosting": self.tech_stack.hosting,
                "additional": self.tech_stack.additional,
            },
            "business_rules": [
                {
                    "rule_id": r.rule_id,
                    "name": r.name,
                    "description": r.description,
                    "category": r.category,
                    "applies_to": r.applies_to,
                    "test_implications": r.test_implications,
                    "priority": r.priority,
                    "examples": r.examples,
                }
                for r in self.business_rules
            ],
            "domain_glossary": {
                term: {
                    "term": dt.term,
                    "definition": dt.definition,
                    "aliases": dt.aliases,
                    "context": dt.context,
                }
                for term, dt in self.domain_glossary.items()
            },
            "environments": {
                name: {
                    "name": env.name,
                    "env_type": env.env_type.value,
                    "base_url": env.base_url,
                    "auth_type": env.auth_type.value,
                    "api_base_url": env.api_base_url,
                    "is_default": env.is_default,
                }
                for name, env in self.environments.items()
            },
            "default_environment": self.default_environment,
            "onboarding_complete": self.onboarding_complete,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def save(self, filepath: str) -> None:
        """Save context to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'ApplicationContext':
        """Load context from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        context = cls(
            app_id=data.get("app_id", str(uuid.uuid4())),
            app_name=data.get("app_name", ""),
            app_description=data.get("app_description", ""),
            app_url=data.get("app_url", ""),
        )

        # Load tech stack
        if "tech_stack" in data:
            ts = data["tech_stack"]
            context.tech_stack = TechStackInfo(
                frontend=ts.get("frontend", ""),
                backend=ts.get("backend", ""),
                database=ts.get("database", ""),
                testing=ts.get("testing", ""),
                ci_cd=ts.get("ci_cd", ""),
                hosting=ts.get("hosting", ""),
                additional=ts.get("additional", {}),
            )

        # Load business rules
        for rule_data in data.get("business_rules", []):
            context.business_rules.append(BusinessRule(
                rule_id=rule_data["rule_id"],
                name=rule_data["name"],
                description=rule_data["description"],
                category=rule_data["category"],
                applies_to=rule_data.get("applies_to", []),
                test_implications=rule_data.get("test_implications", ""),
                priority=rule_data.get("priority", "medium"),
                examples=rule_data.get("examples", []),
            ))

        # Load domain glossary
        for term, dt_data in data.get("domain_glossary", {}).items():
            context.domain_glossary[term] = DomainTerm(
                term=dt_data["term"],
                definition=dt_data["definition"],
                aliases=dt_data.get("aliases", []),
                context=dt_data.get("context", ""),
            )

        # Load environments
        for name, env_data in data.get("environments", {}).items():
            context.environments[name] = EnvironmentConfig(
                name=env_data["name"],
                env_type=EnvironmentType(env_data["env_type"]),
                base_url=env_data["base_url"],
                auth_type=AuthType(env_data.get("auth_type", "none")),
                api_base_url=env_data.get("api_base_url"),
                is_default=env_data.get("is_default", False),
            )

        context.default_environment = data.get("default_environment", "development")
        context.onboarding_complete = data.get("onboarding_complete", False)

        return context


# Factory function for creating a new context
def create_application_context(
    app_name: str,
    app_url: str,
    app_description: str = "",
    tech_stack: Optional[Dict[str, str]] = None,
) -> ApplicationContext:
    """
    Create a new ApplicationContext with minimal required information.

    Args:
        app_name: Name of the application
        app_url: Base URL of the application
        app_description: Optional description
        tech_stack: Optional dict with tech stack info

    Returns:
        New ApplicationContext instance
    """
    context = ApplicationContext(
        app_name=app_name,
        app_url=app_url,
        app_description=app_description,
    )

    if tech_stack:
        context.tech_stack = TechStackInfo(
            frontend=tech_stack.get("frontend", ""),
            backend=tech_stack.get("backend", ""),
            database=tech_stack.get("database", ""),
            testing=tech_stack.get("testing", ""),
            ci_cd=tech_stack.get("ci_cd", ""),
            hosting=tech_stack.get("hosting", ""),
        )

    # Add default development environment
    context.add_environment(EnvironmentConfig(
        name="development",
        env_type=EnvironmentType.DEVELOPMENT,
        base_url=app_url,
        is_default=True,
    ))

    return context
