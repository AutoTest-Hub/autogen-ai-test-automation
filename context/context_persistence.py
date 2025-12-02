"""
Context Persistence and Sync for AutoGen AI QA Platform

Provides storage, versioning, and continuous sync of application context.
"""

import json
import hashlib
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import asyncio

from .application_context import ApplicationContext, create_application_context
from .knowledge_ingester import KnowledgeIngester

logger = logging.getLogger(__name__)


class ContextStore:
    """
    Persistent storage for ApplicationContext.

    Stores context as JSON files with versioning support.
    In production, this would use a database.
    """

    def __init__(self, storage_dir: str = "./context_store"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.contexts_dir = self.storage_dir / "contexts"
        self.contexts_dir.mkdir(exist_ok=True)
        self.history_dir = self.storage_dir / "history"
        self.history_dir.mkdir(exist_ok=True)

    def save_context(self, context: ApplicationContext) -> str:
        """
        Save context to persistent storage.

        Args:
            context: ApplicationContext to save

        Returns:
            Version hash of the saved context
        """
        # Convert to serializable dict
        context_dict = self._context_to_dict(context)

        # Generate version hash
        content_hash = hashlib.sha256(
            json.dumps(context_dict, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]

        # Save current version
        current_file = self.contexts_dir / f"{context.app_id}.json"
        with open(current_file, 'w') as f:
            json.dump({
                "version": content_hash,
                "saved_at": datetime.utcnow().isoformat(),
                "context": context_dict
            }, f, indent=2, default=str)

        # Save to history
        history_file = self.history_dir / f"{context.app_id}_{content_hash}.json"
        if not history_file.exists():
            with open(history_file, 'w') as f:
                json.dump({
                    "version": content_hash,
                    "saved_at": datetime.utcnow().isoformat(),
                    "context": context_dict
                }, f, indent=2, default=str)

        logger.info(f"Saved context for {context.app_id} (version: {content_hash})")
        return content_hash

    def load_context(self, app_id: str) -> Optional[ApplicationContext]:
        """
        Load context from persistent storage.

        Args:
            app_id: Application ID to load

        Returns:
            ApplicationContext or None if not found
        """
        context_file = self.contexts_dir / f"{app_id}.json"
        if not context_file.exists():
            return None

        with open(context_file, 'r') as f:
            data = json.load(f)

        return self._dict_to_context(data["context"])

    def list_contexts(self) -> List[Dict[str, Any]]:
        """List all stored contexts with metadata."""
        contexts = []
        for context_file in self.contexts_dir.glob("*.json"):
            with open(context_file, 'r') as f:
                data = json.load(f)
            contexts.append({
                "app_id": context_file.stem,
                "version": data.get("version"),
                "saved_at": data.get("saved_at"),
                "app_name": data["context"].get("app_name"),
            })
        return contexts

    def get_context_history(self, app_id: str) -> List[Dict[str, Any]]:
        """Get version history for an application context."""
        history = []
        for history_file in self.history_dir.glob(f"{app_id}_*.json"):
            with open(history_file, 'r') as f:
                data = json.load(f)
            history.append({
                "version": data.get("version"),
                "saved_at": data.get("saved_at"),
            })
        return sorted(history, key=lambda x: x["saved_at"], reverse=True)

    def load_context_version(self, app_id: str, version: str) -> Optional[ApplicationContext]:
        """Load a specific version of context."""
        history_file = self.history_dir / f"{app_id}_{version}.json"
        if not history_file.exists():
            return None

        with open(history_file, 'r') as f:
            data = json.load(f)

        return self._dict_to_context(data["context"])

    def _context_to_dict(self, context: ApplicationContext) -> Dict[str, Any]:
        """Convert ApplicationContext to serializable dict."""
        return {
            "app_id": context.app_id,
            "app_name": context.app_name,
            "app_url": context.app_url,
            "tech_stack": asdict(context.tech_stack) if context.tech_stack else None,
            "business_rules": [asdict(r) for r in context.business_rules],
            "domain_glossary": {k: asdict(v) for k, v in context.domain_glossary.items()},
            "environments": {k: asdict(v) for k, v in context.environments.items()},
            "critical_journeys": [asdict(j) for j in context.critical_journeys],
            "api_endpoints": [asdict(e) for e in context.api_endpoints],
            "test_patterns": [asdict(p) for p in context.test_patterns],
            "created_at": context.created_at.isoformat() if context.created_at else None,
            "updated_at": context.updated_at.isoformat() if context.updated_at else None,
        }

    def _dict_to_context(self, data: Dict[str, Any]) -> ApplicationContext:
        """Convert dict back to ApplicationContext."""
        from .application_context import (
            TechStackInfo, BusinessRule, DomainTerm,
            EnvironmentConfig, UserJourney, APIEndpoint, TestPattern
        )

        context = create_application_context(
            app_name=data["app_name"],
            app_url=data["app_url"],
        )
        # Restore the original app_id
        if data.get("app_id"):
            context.app_id = data["app_id"]

        if data.get("tech_stack"):
            context.tech_stack = TechStackInfo(**data["tech_stack"])

        context.business_rules = [
            BusinessRule(**r) for r in data.get("business_rules", [])
        ]

        context.domain_glossary = {
            k: DomainTerm(**v) for k, v in data.get("domain_glossary", {}).items()
        }

        context.api_endpoints = [
            APIEndpoint(**e) for e in data.get("api_endpoints", [])
        ]

        context.test_patterns = [
            TestPattern(**p) for p in data.get("test_patterns", [])
        ]

        context.critical_journeys = [
            UserJourney(**j) for j in data.get("critical_journeys", [])
        ]

        return context


class ContextSyncManager:
    """
    Manages continuous synchronization of application context.

    Features:
    - Scheduled refresh from source systems
    - Change detection and notifications
    - Integration with CI/CD webhooks
    """

    def __init__(
        self,
        store: ContextStore,
        ingester: KnowledgeIngester,
        refresh_interval_hours: int = 24
    ):
        self.store = store
        self.ingester = ingester
        self.refresh_interval = timedelta(hours=refresh_interval_hours)
        self._sync_tasks: Dict[str, asyncio.Task] = {}
        self._running = False

    async def start_sync(self, app_id: str, project_path: str):
        """
        Start continuous sync for an application.

        Args:
            app_id: Application ID
            project_path: Path to project for re-ingestion
        """
        if app_id in self._sync_tasks:
            logger.warning(f"Sync already running for {app_id}")
            return

        self._running = True
        task = asyncio.create_task(self._sync_loop(app_id, project_path))
        self._sync_tasks[app_id] = task
        logger.info(f"Started sync for {app_id}")

    async def stop_sync(self, app_id: str):
        """Stop sync for an application."""
        if app_id in self._sync_tasks:
            self._sync_tasks[app_id].cancel()
            del self._sync_tasks[app_id]
            logger.info(f"Stopped sync for {app_id}")

    async def stop_all(self):
        """Stop all sync tasks."""
        self._running = False
        for task in self._sync_tasks.values():
            task.cancel()
        self._sync_tasks.clear()

    async def _sync_loop(self, app_id: str, project_path: str):
        """Background sync loop."""
        while self._running:
            try:
                await self.refresh_context(app_id, project_path)
                await asyncio.sleep(self.refresh_interval.total_seconds())
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Sync error for {app_id}")
                await asyncio.sleep(300)  # Retry after 5 minutes on error

    async def refresh_context(
        self,
        app_id: str,
        project_path: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Refresh context from source systems.

        Args:
            app_id: Application ID
            project_path: Path to project
            force: Force refresh even if not stale

        Returns:
            Dict with refresh results and changes detected
        """
        # Load existing context
        existing = self.store.load_context(app_id)
        existing_hash = None
        if existing:
            existing_hash = hashlib.sha256(
                json.dumps(self.store._context_to_dict(existing), sort_keys=True, default=str).encode()
            ).hexdigest()[:12]

        # Re-ingest from sources
        results = self.ingester.ingest_all(project_path)

        # Create or update context
        if existing:
            context = existing
        else:
            context = create_application_context(
                app_name=app_id,
                app_url="",  # Will need to be set
                app_id=app_id
            )

        # Apply ingested data
        changes = self._apply_ingestion_results(context, results)

        # Save updated context
        new_hash = self.store.save_context(context)

        changed = existing_hash != new_hash

        return {
            "app_id": app_id,
            "previous_version": existing_hash,
            "new_version": new_hash,
            "changed": changed,
            "changes": changes if changed else [],
            "refreshed_at": datetime.utcnow().isoformat(),
        }

    def _apply_ingestion_results(
        self,
        context: ApplicationContext,
        results: Dict[str, Any]
    ) -> List[str]:
        """Apply ingestion results to context, tracking changes."""
        changes = []

        # Apply tech stack
        if "tech_stack" in results and results["tech_stack"].success:
            new_stack = results["tech_stack"].data.get("tech_stack")
            if new_stack and new_stack != context.tech_stack:
                context.tech_stack = new_stack
                changes.append("tech_stack updated")

        # Apply test patterns
        if "tests" in results and results["tests"].success:
            patterns = results["tests"].data.get("patterns", [])
            if patterns != context.test_patterns:
                context.test_patterns = patterns
                changes.append(f"test_patterns updated ({len(patterns)} patterns)")

        # Update timestamp
        context.updated_at = datetime.utcnow()

        return changes

    async def handle_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook from CI/CD or version control.

        Triggers immediate context refresh on relevant events.

        Args:
            event_type: Type of event (push, pr_merged, etc.)
            payload: Event payload

        Returns:
            Result of handling the webhook
        """
        # Determine if refresh needed based on event
        refresh_events = ["push", "pr_merged", "release", "deployment"]

        if event_type not in refresh_events:
            return {"action": "ignored", "reason": f"Event type {event_type} doesn't trigger refresh"}

        # Extract app info from payload
        app_id = payload.get("repository", {}).get("name")
        project_path = payload.get("project_path")

        if not app_id or not project_path:
            return {"action": "skipped", "reason": "Missing app_id or project_path"}

        # Check if relevant files changed
        changed_files = payload.get("changed_files", [])
        relevant_patterns = [
            "README", "package.json", "requirements",
            "openapi", "swagger", "test", "spec"
        ]

        is_relevant = any(
            any(pattern.lower() in f.lower() for pattern in relevant_patterns)
            for f in changed_files
        )

        if not is_relevant:
            return {"action": "skipped", "reason": "No relevant files changed"}

        # Trigger immediate refresh
        result = await self.refresh_context(app_id, project_path, force=True)

        return {
            "action": "refreshed",
            "trigger": event_type,
            "result": result
        }


class ContextArtifactGenerator:
    """
    Generates artifacts from ApplicationContext for various uses.

    Artifacts:
    - JSON export for backup/transfer
    - Markdown documentation
    - Test configuration files
    - Agent prompt templates
    """

    def __init__(self, output_dir: str = "./artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self, context: ApplicationContext) -> Dict[str, Path]:
        """Generate all artifacts for a context."""
        artifacts = {}

        artifacts["json"] = self.generate_json_export(context)
        artifacts["markdown"] = self.generate_markdown_doc(context)
        artifacts["test_config"] = self.generate_test_config(context)
        artifacts["prompt_templates"] = self.generate_prompt_templates(context)

        logger.info(f"Generated {len(artifacts)} artifacts for {context.app_id}")
        return artifacts

    def generate_json_export(self, context: ApplicationContext) -> Path:
        """Generate JSON export of context."""
        store = ContextStore(str(self.output_dir / "exports"))
        store.save_context(context)
        return store.contexts_dir / f"{context.app_id}.json"

    def generate_markdown_doc(self, context: ApplicationContext) -> Path:
        """Generate markdown documentation."""
        doc_path = self.output_dir / f"{context.app_id}_context.md"

        content = f"""# Application Context: {context.app_name}

**Application ID**: {context.app_id}
**URL**: {context.app_url}
**Last Updated**: {context.updated_at or 'N/A'}

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | {context.tech_stack.frontend if context.tech_stack else 'Unknown'} |
| Backend | {context.tech_stack.backend if context.tech_stack else 'Unknown'} |
| Database | {context.tech_stack.database if context.tech_stack else 'Unknown'} |
| Testing | {context.tech_stack.testing if context.tech_stack else 'Unknown'} |
| CI/CD | {context.tech_stack.ci_cd if context.tech_stack else 'Unknown'} |

## Business Rules

"""
        for rule in context.business_rules:
            content += f"""### {rule.name}
- **ID**: {rule.rule_id}
- **Category**: {rule.category}
- **Description**: {rule.description}
- **Applies to**: {', '.join(rule.applies_to)}
- **Test Implications**: {rule.test_implications}

"""

        content += "## Domain Glossary\n\n"
        for term, defn in context.domain_glossary.items():
            content += f"- **{defn.term}**: {defn.definition}\n"

        content += "\n## API Endpoints\n\n"
        for endpoint in context.api_endpoints[:10]:  # Limit for readability
            content += f"- `{endpoint.method} {endpoint.path}`: {endpoint.description}\n"

        with open(doc_path, 'w') as f:
            f.write(content)

        return doc_path

    def generate_test_config(self, context: ApplicationContext) -> Path:
        """Generate test configuration file."""
        config_path = self.output_dir / f"{context.app_id}_test_config.json"

        config = {
            "app_id": context.app_id,
            "app_name": context.app_name,
            "base_url": context.app_url,
            "tech_stack": {
                "testing_framework": context.tech_stack.testing if context.tech_stack else "playwright",
            },
            "environments": {
                name: {
                    "url": env.base_url,
                    "type": env.env_type.value if hasattr(env.env_type, 'value') else str(env.env_type),
                }
                for name, env in context.environments.items()
            },
            "test_patterns": [
                {
                    "type": p.pattern_type,
                    "pattern": p.pattern,
                }
                for p in context.test_patterns
            ],
            "business_rules_to_test": [
                r.rule_id for r in context.business_rules
            ],
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        return config_path

    def generate_prompt_templates(self, context: ApplicationContext) -> Path:
        """Generate pre-built prompt templates for agents."""
        templates_dir = self.output_dir / f"{context.app_id}_prompts"
        templates_dir.mkdir(exist_ok=True)

        # Planning prompt
        planning_prompt = f"""You are testing {context.app_name} ({context.app_url}).

TECHNOLOGY STACK:
- Frontend: {context.tech_stack.frontend if context.tech_stack else 'Unknown'}
- Backend: {context.tech_stack.backend if context.tech_stack else 'Unknown'}
- Testing: {context.tech_stack.testing if context.tech_stack else 'Unknown'}

BUSINESS RULES TO CONSIDER:
"""
        for rule in context.business_rules[:5]:
            planning_prompt += f"- {rule.name}: {rule.description}\n"

        with open(templates_dir / "planning_prompt.txt", 'w') as f:
            f.write(planning_prompt)

        # Test creation prompt
        test_prompt = f"""Generate tests for {context.app_name}.

FOLLOW THESE PATTERNS (from existing tests):
"""
        for pattern in context.test_patterns[:5]:
            test_prompt += f"- {pattern.pattern_type}: {pattern.pattern}\n"

        with open(templates_dir / "test_creation_prompt.txt", 'w') as f:
            f.write(test_prompt)

        return templates_dir
