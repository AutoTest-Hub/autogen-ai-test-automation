"""
Integration Manager for AutoGen AI QA Platform

Coordinates multiple tool integrations and provides unified access
to external knowledge sources.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
import asyncio
import logging

from .base_integration import (
    BaseIntegration,
    IntegrationConfig,
    IntegrationResult,
    IntegrationType,
    IntegrationStatus,
)
from .github_integration import GitHubIntegration
from .jira_integration import JiraIntegration
from .confluence_integration import ConfluenceIntegration

logger = logging.getLogger(__name__)


@dataclass
class IntegrationHealth:
    """Health status of all integrations."""
    total: int
    connected: int
    error: int
    rate_limited: int
    details: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class IntegrationManager:
    """
    Manages all tool integrations for the platform.

    Features:
    - Unified connection management
    - Health monitoring
    - Cross-integration queries
    - Context extraction for agents
    """

    # Registry of available integration types
    INTEGRATION_CLASSES: Dict[IntegrationType, Type[BaseIntegration]] = {
        IntegrationType.GITHUB: GitHubIntegration,
        IntegrationType.JIRA: JiraIntegration,
        IntegrationType.CONFLUENCE: ConfluenceIntegration,
    }

    def __init__(self):
        self._integrations: Dict[str, BaseIntegration] = {}
        self._configs: Dict[str, IntegrationConfig] = {}

    def register_integration(
        self,
        integration_id: str,
        config: IntegrationConfig
    ) -> bool:
        """
        Register an integration configuration.

        Args:
            integration_id: Unique identifier for this integration instance
            config: Integration configuration

        Returns:
            True if registered successfully
        """
        if integration_id in self._integrations:
            logger.warning(f"Integration {integration_id} already registered")
            return False

        integration_class = self.INTEGRATION_CLASSES.get(config.integration_type)
        if not integration_class:
            logger.error(f"Unknown integration type: {config.integration_type}")
            return False

        try:
            integration = integration_class(config)
            self._integrations[integration_id] = integration
            self._configs[integration_id] = config
            logger.info(f"Registered integration: {integration_id} ({config.integration_type})")
            return True
        except Exception as e:
            logger.exception(f"Failed to register integration: {integration_id}")
            return False

    def unregister_integration(self, integration_id: str) -> bool:
        """
        Unregister an integration.

        Args:
            integration_id: ID of integration to remove

        Returns:
            True if removed successfully
        """
        if integration_id not in self._integrations:
            return False

        del self._integrations[integration_id]
        del self._configs[integration_id]
        logger.info(f"Unregistered integration: {integration_id}")
        return True

    def get_integration(self, integration_id: str) -> Optional[BaseIntegration]:
        """Get an integration by ID."""
        return self._integrations.get(integration_id)

    def get_integrations_by_type(
        self,
        integration_type: IntegrationType
    ) -> List[BaseIntegration]:
        """Get all integrations of a specific type."""
        return [
            i for i in self._integrations.values()
            if i.integration_type == integration_type
        ]

    async def connect_all(self) -> Dict[str, bool]:
        """
        Connect all registered integrations.

        Returns:
            Dict of integration_id to connection success
        """
        results = {}

        # Connect in parallel
        async def connect_one(integration_id: str) -> tuple:
            integration = self._integrations[integration_id]
            success = await integration.connect()
            return integration_id, success

        tasks = [connect_one(iid) for iid in self._integrations]
        for coro in asyncio.as_completed(tasks):
            integration_id, success = await coro
            results[integration_id] = success
            status = "connected" if success else "failed"
            logger.info(f"Integration {integration_id}: {status}")

        return results

    async def disconnect_all(self) -> None:
        """Disconnect all integrations."""
        for integration_id, integration in self._integrations.items():
            try:
                await integration.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting {integration_id}: {e}")

    async def connect_integration(self, integration_id: str) -> bool:
        """Connect a specific integration."""
        integration = self._integrations.get(integration_id)
        if not integration:
            return False
        return await integration.connect()

    async def disconnect_integration(self, integration_id: str) -> bool:
        """Disconnect a specific integration."""
        integration = self._integrations.get(integration_id)
        if not integration:
            return False
        await integration.disconnect()
        return True

    def get_health(self) -> IntegrationHealth:
        """Get health status of all integrations."""
        health = IntegrationHealth(
            total=len(self._integrations),
            connected=0,
            error=0,
            rate_limited=0,
        )

        for integration_id, integration in self._integrations.items():
            status_info = integration.get_status()
            health.details[integration_id] = status_info

            status = IntegrationStatus(status_info["status"])
            if status == IntegrationStatus.CONNECTED:
                health.connected += 1
            elif status == IntegrationStatus.ERROR:
                health.error += 1
            elif status == IntegrationStatus.RATE_LIMITED:
                health.rate_limited += 1

        return health

    # Cross-integration queries

    async def fetch_project_context(
        self,
        github_owner: Optional[str] = None,
        github_repo: Optional[str] = None,
        jira_project: Optional[str] = None,
        confluence_space: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch context from multiple integrations for a project.

        Returns a combined context dict with information from all sources.
        """
        context = {
            "github": None,
            "jira": None,
            "confluence": None,
        }

        tasks = []

        # GitHub context
        if github_owner and github_repo:
            github_integrations = self.get_integrations_by_type(IntegrationType.GITHUB)
            if github_integrations:
                async def get_github_context():
                    gh = github_integrations[0]
                    results = {}

                    # Get repo info
                    repo_result = await gh.get_repository(github_owner, github_repo)
                    if repo_result.success:
                        results["repository"] = repo_result.data

                    # Get recent PRs
                    prs_result = await gh.list_pull_requests(github_owner, github_repo)
                    if prs_result.success:
                        results["recent_prs"] = prs_result.data[:5]

                    # Get open issues
                    issues_result = await gh.list_issues(github_owner, github_repo)
                    if issues_result.success:
                        results["open_issues"] = issues_result.data[:10]

                    return results

                tasks.append(("github", get_github_context()))

        # Jira context
        if jira_project:
            jira_integrations = self.get_integrations_by_type(IntegrationType.JIRA)
            if jira_integrations:
                async def get_jira_context():
                    jira = jira_integrations[0]
                    results = {}

                    # Get project info
                    project_result = await jira.get_project(jira_project)
                    if project_result.success:
                        results["project"] = project_result.data

                    # Get user stories
                    stories_result = await jira.get_user_stories(jira_project)
                    if stories_result.success:
                        results["user_stories"] = stories_result.data[:10]

                    # Get bugs
                    bugs_result = await jira.get_bugs(jira_project)
                    if bugs_result.success:
                        results["bugs"] = bugs_result.data[:10]

                    return results

                tasks.append(("jira", get_jira_context()))

        # Confluence context
        if confluence_space:
            confluence_integrations = self.get_integrations_by_type(IntegrationType.CONFLUENCE)
            if confluence_integrations:
                async def get_confluence_context():
                    conf = confluence_integrations[0]
                    results = {}

                    # Get space info
                    space_result = await conf.get_space(confluence_space)
                    if space_result.success:
                        results["space"] = space_result.data

                    # Get business rules documentation
                    rules_result = await conf.get_business_rules(confluence_space)
                    if rules_result.success:
                        results["business_rules_pages"] = rules_result.data[:5]

                    # Get API documentation
                    api_result = await conf.get_api_documentation(confluence_space)
                    if api_result.success:
                        results["api_docs_pages"] = api_result.data[:5]

                    return results

                tasks.append(("confluence", get_confluence_context()))

        # Execute all tasks in parallel
        for key, task in tasks:
            try:
                context[key] = await task
            except Exception as e:
                logger.warning(f"Failed to fetch {key} context: {e}")
                context[key] = {"error": str(e)}

        return context

    async def search_across_integrations(
        self,
        query: str,
        limit_per_source: int = 10
    ) -> Dict[str, IntegrationResult]:
        """
        Search across all connected integrations.

        Args:
            query: Search query
            limit_per_source: Max results per integration

        Returns:
            Dict of integration_id to search results
        """
        results = {}

        async def search_one(integration_id: str, integration: BaseIntegration):
            try:
                if integration.integration_type == IntegrationType.GITHUB:
                    # GitHub needs repo context
                    return integration_id, IntegrationResult(
                        success=False,
                        error_message="GitHub search requires repo context"
                    )
                elif integration.integration_type == IntegrationType.JIRA:
                    jira = integration
                    return integration_id, await jira.search_issues(
                        f'text ~ "{query}"',
                        max_results=limit_per_source
                    )
                elif integration.integration_type == IntegrationType.CONFLUENCE:
                    conf = integration
                    return integration_id, await conf.search_content(query)
                else:
                    return integration_id, IntegrationResult(
                        success=False,
                        error_message="Search not supported"
                    )
            except Exception as e:
                return integration_id, IntegrationResult(
                    success=False,
                    error_message=str(e)
                )

        # Search connected integrations in parallel
        tasks = [
            search_one(iid, i)
            for iid, i in self._integrations.items()
            if i.status == IntegrationStatus.CONNECTED
        ]

        for coro in asyncio.as_completed(tasks):
            integration_id, result = await coro
            results[integration_id] = result

        return results

    def generate_context_summary(self, project_context: Dict[str, Any]) -> str:
        """
        Generate a summary of project context for agent prompts.

        Args:
            project_context: Context dict from fetch_project_context()

        Returns:
            Formatted string summary for LLM prompts
        """
        sections = []

        # GitHub summary
        if project_context.get("github"):
            gh = project_context["github"]
            if "repository" in gh:
                sections.append(f"GitHub Repository: {gh['repository'].get('full_name', 'Unknown')}")
            if "recent_prs" in gh:
                pr_titles = [pr.title for pr in gh["recent_prs"][:3]]
                if pr_titles:
                    sections.append(f"Recent PRs: {', '.join(pr_titles)}")
            if "open_issues" in gh:
                issue_titles = [i.title for i in gh["open_issues"][:3]]
                if issue_titles:
                    sections.append(f"Open Issues: {', '.join(issue_titles)}")

        # Jira summary
        if project_context.get("jira"):
            jira = project_context["jira"]
            if "project" in jira:
                sections.append(f"Jira Project: {jira['project'].name}")
            if "user_stories" in jira:
                story_titles = [s.summary for s in jira["user_stories"][:3]]
                if story_titles:
                    sections.append(f"User Stories: {', '.join(story_titles)}")
            if "bugs" in jira:
                bug_titles = [b.summary for b in jira["bugs"][:3]]
                if bug_titles:
                    sections.append(f"Known Bugs: {', '.join(bug_titles)}")

        # Confluence summary
        if project_context.get("confluence"):
            conf = project_context["confluence"]
            if "space" in conf:
                sections.append(f"Confluence Space: {conf['space'].name}")
            if "business_rules_pages" in conf:
                rule_pages = [p.title for p in conf["business_rules_pages"][:3]]
                if rule_pages:
                    sections.append(f"Business Rules Docs: {', '.join(rule_pages)}")

        if not sections:
            return "No external context available."

        return "\n".join(sections)

    def list_integrations(self) -> List[Dict[str, Any]]:
        """List all registered integrations with their status."""
        return [
            {
                "id": integration_id,
                **integration.get_status()
            }
            for integration_id, integration in self._integrations.items()
        ]

    def clear_all_caches(self) -> None:
        """Clear caches for all integrations."""
        for integration in self._integrations.values():
            integration.clear_cache()
