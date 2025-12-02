"""
Tool Integrations for AutoGen AI QA Platform

Provides read-only integrations with development tools:
- GitHub: Read repos, PRs, issues
- Jira: Read tickets, requirements
- Confluence: Read documentation
"""

from .base_integration import (
    BaseIntegration,
    IntegrationConfig,
    IntegrationResult,
    IntegrationError,
)

from .github_integration import GitHubIntegration
from .jira_integration import JiraIntegration
from .confluence_integration import ConfluenceIntegration
from .integration_manager import IntegrationManager

__all__ = [
    # Base
    "BaseIntegration",
    "IntegrationConfig",
    "IntegrationResult",
    "IntegrationError",
    # Integrations
    "GitHubIntegration",
    "JiraIntegration",
    "ConfluenceIntegration",
    # Manager
    "IntegrationManager",
]
