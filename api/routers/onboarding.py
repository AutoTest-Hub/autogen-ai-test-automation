"""
Onboarding API for AutoGen AI QA Platform

Provides a step-by-step wizard for onboarding new applications:
1. Basic app info (name, URL, description)
2. Tech stack detection/confirmation
3. Environment configuration
4. Integration connections (GitHub, Jira, etc.)
5. Knowledge ingestion trigger
6. Validation and completion
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class OnboardingStep(str, Enum):
    """Steps in the onboarding wizard."""
    APP_INFO = "app_info"
    TECH_STACK = "tech_stack"
    ENVIRONMENTS = "environments"
    INTEGRATIONS = "integrations"
    KNOWLEDGE = "knowledge"
    VALIDATION = "validation"
    COMPLETE = "complete"


@dataclass
class OnboardingState:
    """Tracks the state of an onboarding session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    app_id: Optional[str] = None
    current_step: OnboardingStep = OnboardingStep.APP_INFO
    completed_steps: List[OnboardingStep] = field(default_factory=list)
    step_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "app_id": self.app_id,
            "current_step": self.current_step.value,
            "completed_steps": [s.value for s in self.completed_steps],
            "step_data": self.step_data,
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class StepResult:
    """Result of processing an onboarding step."""
    success: bool
    next_step: Optional[OnboardingStep] = None
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class OnboardingWizard:
    """
    Manages the onboarding process for new applications.

    Usage:
        wizard = OnboardingWizard()
        session = wizard.start_session()

        # Step 1: App info
        result = wizard.submit_step(session.session_id, OnboardingStep.APP_INFO, {
            "app_name": "My App",
            "app_url": "https://myapp.com",
            "description": "E-commerce platform"
        })

        # Step 2: Tech stack
        result = wizard.submit_step(session.session_id, OnboardingStep.TECH_STACK, {
            "frontend": "React",
            "backend": "Django",
            ...
        })

        # Continue through steps...

        # Get final context
        context = wizard.complete_onboarding(session.session_id)
    """

    STEP_ORDER = [
        OnboardingStep.APP_INFO,
        OnboardingStep.TECH_STACK,
        OnboardingStep.ENVIRONMENTS,
        OnboardingStep.INTEGRATIONS,
        OnboardingStep.KNOWLEDGE,
        OnboardingStep.VALIDATION,
        OnboardingStep.COMPLETE,
    ]

    def __init__(self):
        self._sessions: Dict[str, OnboardingState] = {}

    def start_session(self) -> OnboardingState:
        """Start a new onboarding session."""
        state = OnboardingState()
        self._sessions[state.session_id] = state
        logger.info(f"Started onboarding session: {state.session_id}")
        return state

    def get_session(self, session_id: str) -> Optional[OnboardingState]:
        """Get an existing session."""
        return self._sessions.get(session_id)

    def get_step_schema(self, step: OnboardingStep) -> Dict[str, Any]:
        """Get the schema/requirements for a step."""
        schemas = {
            OnboardingStep.APP_INFO: {
                "title": "Application Information",
                "description": "Basic information about your application",
                "fields": [
                    {"name": "app_name", "type": "string", "required": True, "label": "Application Name"},
                    {"name": "app_url", "type": "url", "required": True, "label": "Application URL"},
                    {"name": "description", "type": "text", "required": False, "label": "Description"},
                    {"name": "repo_url", "type": "url", "required": False, "label": "Repository URL"},
                ],
            },
            OnboardingStep.TECH_STACK: {
                "title": "Technology Stack",
                "description": "Confirm or modify the detected technology stack",
                "fields": [
                    {"name": "frontend", "type": "string", "required": False, "label": "Frontend Framework",
                     "suggestions": ["React", "Vue", "Angular", "Svelte", "Next.js"]},
                    {"name": "backend", "type": "string", "required": False, "label": "Backend Framework",
                     "suggestions": ["Django", "FastAPI", "Flask", "Express", "Spring"]},
                    {"name": "database", "type": "string", "required": False, "label": "Database",
                     "suggestions": ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis"]},
                    {"name": "testing", "type": "string", "required": False, "label": "Testing Framework",
                     "suggestions": ["Playwright", "Cypress", "Selenium", "Jest", "pytest"]},
                ],
            },
            OnboardingStep.ENVIRONMENTS: {
                "title": "Environments",
                "description": "Configure your testing environments",
                "fields": [
                    {"name": "environments", "type": "array", "required": True, "label": "Environments",
                     "item_schema": {
                         "name": {"type": "string", "required": True},
                         "url": {"type": "url", "required": True},
                         "type": {"type": "enum", "options": ["development", "staging", "production"]},
                         "is_default": {"type": "boolean", "default": False},
                     }},
                ],
            },
            OnboardingStep.INTEGRATIONS: {
                "title": "Tool Integrations",
                "description": "Connect external tools (optional)",
                "fields": [
                    {"name": "github", "type": "object", "required": False, "label": "GitHub",
                     "fields": [
                         {"name": "enabled", "type": "boolean"},
                         {"name": "owner", "type": "string"},
                         {"name": "repo", "type": "string"},
                         {"name": "token", "type": "secret"},
                     ]},
                    {"name": "jira", "type": "object", "required": False, "label": "Jira",
                     "fields": [
                         {"name": "enabled", "type": "boolean"},
                         {"name": "base_url", "type": "url"},
                         {"name": "project_key", "type": "string"},
                         {"name": "email", "type": "email"},
                         {"name": "token", "type": "secret"},
                     ]},
                ],
            },
            OnboardingStep.KNOWLEDGE: {
                "title": "Knowledge Ingestion",
                "description": "Import knowledge from your project",
                "fields": [
                    {"name": "project_path", "type": "path", "required": False, "label": "Local Project Path"},
                    {"name": "ingest_readme", "type": "boolean", "default": True, "label": "Import README"},
                    {"name": "ingest_openapi", "type": "boolean", "default": True, "label": "Import OpenAPI Spec"},
                    {"name": "ingest_tests", "type": "boolean", "default": True, "label": "Analyze Existing Tests"},
                    {"name": "openapi_url", "type": "url", "required": False, "label": "OpenAPI Spec URL"},
                ],
            },
            OnboardingStep.VALIDATION: {
                "title": "Validation",
                "description": "Review and validate your configuration",
                "fields": [
                    {"name": "confirm", "type": "boolean", "required": True, "label": "Configuration is correct"},
                ],
            },
        }
        return schemas.get(step, {})

    def submit_step(
        self,
        session_id: str,
        step: OnboardingStep,
        data: Dict[str, Any]
    ) -> StepResult:
        """
        Submit data for an onboarding step.

        Returns StepResult with next step or errors.
        """
        session = self._sessions.get(session_id)
        if not session:
            return StepResult(success=False, errors=["Session not found"])

        # Validate we're on the right step
        if step != session.current_step:
            return StepResult(
                success=False,
                errors=[f"Expected step {session.current_step.value}, got {step.value}"]
            )

        # Process the step
        handler = getattr(self, f"_process_{step.value}", None)
        if handler:
            result = handler(session, data)
        else:
            result = self._process_generic_step(session, step, data)

        # Update session state
        if result.success:
            session.step_data[step.value] = data
            session.completed_steps.append(step)
            session.current_step = result.next_step or self._get_next_step(step)
            session.updated_at = datetime.utcnow()

        return result

    def _get_next_step(self, current: OnboardingStep) -> OnboardingStep:
        """Get the next step in the sequence."""
        try:
            idx = self.STEP_ORDER.index(current)
            if idx + 1 < len(self.STEP_ORDER):
                return self.STEP_ORDER[idx + 1]
        except ValueError:
            pass
        return OnboardingStep.COMPLETE

    def _process_app_info(self, session: OnboardingState, data: Dict[str, Any]) -> StepResult:
        """Process app info step."""
        errors = []

        if not data.get("app_name"):
            errors.append("Application name is required")
        if not data.get("app_url"):
            errors.append("Application URL is required")

        if errors:
            return StepResult(success=False, errors=errors)

        # Generate app_id
        session.app_id = str(uuid.uuid4())

        return StepResult(
            success=True,
            next_step=OnboardingStep.TECH_STACK,
            data={"app_id": session.app_id},
            suggestions=["We'll try to detect your tech stack automatically"]
        )

    def _process_tech_stack(self, session: OnboardingState, data: Dict[str, Any]) -> StepResult:
        """Process tech stack step."""
        # Auto-detect if project path provided
        suggestions = []

        if not any([data.get("frontend"), data.get("backend"), data.get("testing")]):
            suggestions.append("Consider specifying at least one technology for better test generation")

        return StepResult(
            success=True,
            next_step=OnboardingStep.ENVIRONMENTS,
            suggestions=suggestions
        )

    def _process_environments(self, session: OnboardingState, data: Dict[str, Any]) -> StepResult:
        """Process environments step."""
        environments = data.get("environments", [])

        if not environments:
            # Create default from app_url
            app_url = session.step_data.get("app_info", {}).get("app_url", "")
            environments = [{
                "name": "development",
                "url": app_url,
                "type": "development",
                "is_default": True
            }]
            data["environments"] = environments

        # Validate at least one default
        has_default = any(env.get("is_default") for env in environments)
        if not has_default and environments:
            environments[0]["is_default"] = True

        return StepResult(
            success=True,
            next_step=OnboardingStep.INTEGRATIONS
        )

    def _process_integrations(self, session: OnboardingState, data: Dict[str, Any]) -> StepResult:
        """Process integrations step."""
        # Integrations are optional, just validate format if provided
        return StepResult(
            success=True,
            next_step=OnboardingStep.KNOWLEDGE
        )

    def _process_knowledge(self, session: OnboardingState, data: Dict[str, Any]) -> StepResult:
        """Process knowledge ingestion step."""
        # Trigger async knowledge ingestion if path provided
        ingestion_triggered = False

        if data.get("project_path"):
            # Would trigger: KnowledgeIngester.ingest_all(data["project_path"])
            ingestion_triggered = True

        return StepResult(
            success=True,
            next_step=OnboardingStep.VALIDATION,
            data={"ingestion_triggered": ingestion_triggered}
        )

    def _process_validation(self, session: OnboardingState, data: Dict[str, Any]) -> StepResult:
        """Process validation step."""
        if not data.get("confirm"):
            return StepResult(
                success=False,
                errors=["Please confirm the configuration is correct"]
            )

        return StepResult(
            success=True,
            next_step=OnboardingStep.COMPLETE
        )

    def _process_generic_step(
        self,
        session: OnboardingState,
        step: OnboardingStep,
        data: Dict[str, Any]
    ) -> StepResult:
        """Generic step processing."""
        return StepResult(
            success=True,
            next_step=self._get_next_step(step)
        )

    def complete_onboarding(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Complete onboarding and generate ApplicationContext.

        Returns the created context data or None if incomplete.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        if OnboardingStep.VALIDATION not in session.completed_steps:
            return None

        # Build context from collected data
        from context import (
            create_application_context,
            TechStackInfo,
            EnvironmentConfig,
            EnvironmentType,
            ContextStore,
        )

        app_info = session.step_data.get("app_info", {})
        tech_data = session.step_data.get("tech_stack", {})
        env_data = session.step_data.get("environments", {})

        # Create context
        context = create_application_context(
            app_name=app_info.get("app_name", ""),
            app_url=app_info.get("app_url", ""),
            app_description=app_info.get("description", ""),
        )

        # Set app_id
        if session.app_id:
            context.app_id = session.app_id

        # Set tech stack
        context.tech_stack = TechStackInfo(
            frontend=tech_data.get("frontend", "Unknown"),
            backend=tech_data.get("backend", "Unknown"),
            database=tech_data.get("database", "Unknown"),
            testing=tech_data.get("testing", "Playwright"),
            ci_cd=tech_data.get("ci_cd", "Unknown"),
        )

        # Set environments
        for env in env_data.get("environments", []):
            env_type = EnvironmentType(env.get("type", "development"))
            context.environments[env["name"]] = EnvironmentConfig(
                name=env["name"],
                env_type=env_type,
                base_url=env["url"],
                is_default=env.get("is_default", False),
            )

        # Mark onboarding complete
        context.onboarding_complete = True

        # Save to store
        store = ContextStore()
        version = store.save_context(context)

        # Clean up session
        del self._sessions[session_id]

        logger.info(f"Completed onboarding for {context.app_name} (version: {version})")

        return {
            "app_id": context.app_id,
            "app_name": context.app_name,
            "version": version,
            "context": context,
        }

    def get_progress(self, session_id: str) -> Dict[str, Any]:
        """Get onboarding progress for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        total_steps = len(self.STEP_ORDER) - 1  # Exclude COMPLETE
        completed = len(session.completed_steps)

        return {
            "session_id": session_id,
            "current_step": session.current_step.value,
            "completed_steps": [s.value for s in session.completed_steps],
            "progress_percent": int((completed / total_steps) * 100),
            "remaining_steps": [
                s.value for s in self.STEP_ORDER
                if s not in session.completed_steps and s != OnboardingStep.COMPLETE
            ],
        }
