"""
Jira Integration for AutoGen AI QA Platform

READ-ONLY access to Jira for:
- Issues (user stories, bugs, tasks)
- Sprints and boards
- Project information
- Comments and attachments metadata
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiohttp
import logging

from .base_integration import (
    BaseIntegration,
    IntegrationConfig,
    IntegrationResult,
    IntegrationError,
    IntegrationType,
    IntegrationStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class JiraIssue:
    """Represents a Jira Issue."""
    key: str  # e.g., "PROJ-123"
    summary: str
    description: Optional[str]
    issue_type: str  # "Story", "Bug", "Task", etc.
    status: str
    priority: str
    assignee: Optional[str]
    reporter: str
    created: datetime
    updated: datetime
    labels: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    fix_versions: List[str] = field(default_factory=list)
    story_points: Optional[float] = None
    acceptance_criteria: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JiraSprint:
    """Represents a Jira Sprint."""
    id: int
    name: str
    state: str  # "active", "closed", "future"
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    goal: Optional[str]


@dataclass
class JiraProject:
    """Represents a Jira Project."""
    key: str
    name: str
    description: Optional[str]
    lead: str
    issue_types: List[str] = field(default_factory=list)


@dataclass
class JiraComment:
    """Represents a Jira Comment."""
    id: str
    body: str
    author: str
    created: datetime
    updated: datetime


class JiraIntegration(BaseIntegration):
    """
    Read-only Jira integration.

    Provides access to:
    - Issues (stories, bugs, tasks)
    - Sprint information
    - Project metadata
    - Comments

    Does NOT provide:
    - Write access (no creating/updating issues)
    - Admin access
    - Sensitive project configuration
    """

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url = config.base_url or "https://jira.atlassian.com"
        self._api_version = "2"  # Jira REST API version

    @property
    def integration_type(self) -> IntegrationType:
        return IntegrationType.JIRA

    async def connect(self) -> bool:
        """Establish connection to Jira API."""
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            # Jira Cloud uses email + API token as Basic Auth
            if self.config.api_token:
                import base64
                # For Jira Cloud: email:api_token
                # For Jira Server: username:password or just Bearer token
                if "@" in self.config.name:
                    # Cloud: email + token
                    auth_string = f"{self.config.name}:{self.config.api_token}"
                    encoded = base64.b64encode(auth_string.encode()).decode()
                    headers["Authorization"] = f"Basic {encoded}"
                else:
                    # Server: Bearer token
                    headers["Authorization"] = f"Bearer {self.config.api_token}"

            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )

            # Test connection
            result = await self.test_connection()
            if result.success:
                self._connected = True
                self.status = IntegrationStatus.CONNECTED
                logger.info(f"Connected to Jira: {self.config.name}")
                return True
            else:
                self.status = IntegrationStatus.ERROR
                return False

        except Exception as e:
            logger.exception("Failed to connect to Jira")
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> None:
        """Close Jira API connection."""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False
        self.status = IntegrationStatus.DISCONNECTED

    async def test_connection(self) -> IntegrationResult:
        """Test Jira API connection."""
        try:
            if not self._session:
                return IntegrationResult(
                    success=False,
                    error_message="Not connected"
                )

            url = f"{self._base_url}/rest/api/{self._api_version}/myself"
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return IntegrationResult(
                        success=True,
                        data={"user": data.get("displayName", data.get("name"))}
                    )
                elif response.status == 401:
                    return IntegrationResult(
                        success=False,
                        error_message="Authentication failed"
                    )
                else:
                    return IntegrationResult(
                        success=False,
                        error_message=f"API error: {response.status}"
                    )

        except Exception as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _execute_operation(
        self,
        operation: str,
        *args,
        **kwargs
    ) -> IntegrationResult:
        """Execute a Jira API operation."""
        operations = {
            "get_issue": self._get_issue,
            "search_issues": self._search_issues,
            "get_project": self._get_project,
            "list_projects": self._list_projects,
            "get_sprint": self._get_sprint,
            "list_sprints": self._list_sprints,
            "get_comments": self._get_comments,
        }

        handler = operations.get(operation)
        if not handler:
            return IntegrationResult(
                success=False,
                error_message=f"Unknown operation: {operation}"
            )

        return await handler(*args, **kwargs)

    async def _api_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a Jira API request."""
        if not self._session:
            raise IntegrationError(
                "Not connected to Jira",
                IntegrationType.JIRA
            )

        url = f"{self._base_url}/rest/api/{self._api_version}/{endpoint.lstrip('/')}"

        async with self._session.get(url, params=params) as response:
            if response.status == 404:
                raise IntegrationError(
                    f"Resource not found: {endpoint}",
                    IntegrationType.JIRA,
                    recoverable=False
                )
            elif response.status == 401:
                raise IntegrationError(
                    "Authentication failed",
                    IntegrationType.JIRA,
                    recoverable=False
                )
            elif response.status == 429:
                retry_after = response.headers.get("Retry-After", "60")
                raise IntegrationError(
                    "Rate limit exceeded",
                    IntegrationType.JIRA,
                    retry_after=int(retry_after)
                )
            elif response.status != 200:
                raise IntegrationError(
                    f"API error: {response.status}",
                    IntegrationType.JIRA
                )

            return await response.json()

    async def _agile_api_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a Jira Agile API request."""
        if not self._session:
            raise IntegrationError(
                "Not connected to Jira",
                IntegrationType.JIRA
            )

        url = f"{self._base_url}/rest/agile/1.0/{endpoint.lstrip('/')}"

        async with self._session.get(url, params=params) as response:
            if response.status != 200:
                raise IntegrationError(
                    f"Agile API error: {response.status}",
                    IntegrationType.JIRA
                )
            return await response.json()

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Jira datetime string."""
        if not date_str:
            return None
        try:
            # Jira format: 2024-01-15T10:30:00.000+0000
            return datetime.fromisoformat(date_str.replace("+0000", "+00:00"))
        except (ValueError, AttributeError):
            return None

    # Issue operations

    async def _get_issue(self, issue_key: str) -> IntegrationResult:
        """Get a specific issue."""
        project_key = issue_key.split("-")[0]
        if not self.is_resource_allowed(f"projects/{project_key}"):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(
                f"issue/{issue_key}",
                params={"expand": "names,renderedFields"}
            )

            fields = data.get("fields", {})

            issue = JiraIssue(
                key=data["key"],
                summary=fields.get("summary", ""),
                description=fields.get("description"),
                issue_type=fields.get("issuetype", {}).get("name", "Unknown"),
                status=fields.get("status", {}).get("name", "Unknown"),
                priority=fields.get("priority", {}).get("name", "Unknown"),
                assignee=fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                reporter=fields.get("reporter", {}).get("displayName", "Unknown"),
                created=self._parse_datetime(fields.get("created")),
                updated=self._parse_datetime(fields.get("updated")),
                labels=fields.get("labels", []),
                components=[c.get("name") for c in fields.get("components", [])],
                fix_versions=[v.get("name") for v in fields.get("fixVersions", [])],
                story_points=fields.get("customfield_10016"),  # Common story points field
                acceptance_criteria=fields.get("customfield_10020"),  # Common AC field
            )

            return IntegrationResult(success=True, data=issue)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _search_issues(
        self,
        jql: str,
        max_results: int = 50,
        start_at: int = 0
    ) -> IntegrationResult:
        """Search issues using JQL."""
        try:
            data = await self._api_request(
                "search",
                params={
                    "jql": jql,
                    "maxResults": max_results,
                    "startAt": start_at,
                    "fields": "summary,description,issuetype,status,priority,assignee,reporter,created,updated,labels,components"
                }
            )

            issues = []
            for item in data.get("issues", []):
                fields = item.get("fields", {})
                issues.append(JiraIssue(
                    key=item["key"],
                    summary=fields.get("summary", ""),
                    description=fields.get("description"),
                    issue_type=fields.get("issuetype", {}).get("name", "Unknown"),
                    status=fields.get("status", {}).get("name", "Unknown"),
                    priority=fields.get("priority", {}).get("name", "Unknown"),
                    assignee=fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                    reporter=fields.get("reporter", {}).get("displayName", "Unknown"),
                    created=self._parse_datetime(fields.get("created")),
                    updated=self._parse_datetime(fields.get("updated")),
                    labels=fields.get("labels", []),
                    components=[c.get("name") for c in fields.get("components", [])],
                ))

            return IntegrationResult(
                success=True,
                data=issues,
                total_count=data.get("total"),
                has_more=(start_at + len(issues)) < data.get("total", 0),
            )

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Project operations

    async def _get_project(self, project_key: str) -> IntegrationResult:
        """Get project information."""
        if not self.is_resource_allowed(f"projects/{project_key}"):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(f"project/{project_key}")

            project = JiraProject(
                key=data["key"],
                name=data["name"],
                description=data.get("description"),
                lead=data.get("lead", {}).get("displayName", "Unknown"),
                issue_types=[it.get("name") for it in data.get("issueTypes", [])],
            )

            return IntegrationResult(success=True, data=project)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _list_projects(self) -> IntegrationResult:
        """List accessible projects."""
        try:
            data = await self._api_request("project")

            projects = []
            for item in data:
                project_key = item["key"]
                if self.is_resource_allowed(f"projects/{project_key}"):
                    projects.append(JiraProject(
                        key=item["key"],
                        name=item["name"],
                        description=item.get("description"),
                        lead=item.get("lead", {}).get("displayName", "Unknown"),
                    ))

            return IntegrationResult(success=True, data=projects)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Sprint operations

    async def _get_sprint(self, sprint_id: int) -> IntegrationResult:
        """Get sprint information."""
        try:
            data = await self._agile_api_request(f"sprint/{sprint_id}")

            sprint = JiraSprint(
                id=data["id"],
                name=data["name"],
                state=data.get("state", "unknown"),
                start_date=self._parse_datetime(data.get("startDate")),
                end_date=self._parse_datetime(data.get("endDate")),
                goal=data.get("goal"),
            )

            return IntegrationResult(success=True, data=sprint)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _list_sprints(self, board_id: int) -> IntegrationResult:
        """List sprints for a board."""
        try:
            data = await self._agile_api_request(f"board/{board_id}/sprint")

            sprints = []
            for item in data.get("values", []):
                sprints.append(JiraSprint(
                    id=item["id"],
                    name=item["name"],
                    state=item.get("state", "unknown"),
                    start_date=self._parse_datetime(item.get("startDate")),
                    end_date=self._parse_datetime(item.get("endDate")),
                    goal=item.get("goal"),
                ))

            return IntegrationResult(success=True, data=sprints)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Comment operations

    async def _get_comments(self, issue_key: str) -> IntegrationResult:
        """Get comments for an issue."""
        project_key = issue_key.split("-")[0]
        if not self.is_resource_allowed(f"projects/{project_key}"):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(f"issue/{issue_key}/comment")

            comments = []
            for item in data.get("comments", []):
                comments.append(JiraComment(
                    id=item["id"],
                    body=item.get("body", ""),
                    author=item.get("author", {}).get("displayName", "Unknown"),
                    created=self._parse_datetime(item.get("created")),
                    updated=self._parse_datetime(item.get("updated")),
                ))

            return IntegrationResult(success=True, data=comments)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Convenience methods

    async def get_issue(self, issue_key: str) -> IntegrationResult:
        """Get issue details (with caching)."""
        return await self.safe_request(
            "get_issue",
            issue_key,
            cache_key=f"issue:{issue_key}"
        )

    async def search_issues(
        self,
        jql: str,
        max_results: int = 50
    ) -> IntegrationResult:
        """Search issues with JQL."""
        return await self.safe_request("search_issues", jql, max_results)

    async def get_project_issues(
        self,
        project_key: str,
        issue_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> IntegrationResult:
        """Get issues for a project."""
        jql_parts = [f"project = {project_key}"]
        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type}"')
        if status:
            jql_parts.append(f'status = "{status}"')

        jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"
        return await self.search_issues(jql)

    async def get_sprint_issues(self, sprint_id: int) -> IntegrationResult:
        """Get issues in a sprint."""
        jql = f"sprint = {sprint_id} ORDER BY rank"
        return await self.search_issues(jql)

    async def get_user_stories(self, project_key: str) -> IntegrationResult:
        """Get user stories for a project."""
        return await self.get_project_issues(project_key, issue_type="Story")

    async def get_bugs(self, project_key: str) -> IntegrationResult:
        """Get bugs for a project."""
        return await self.get_project_issues(project_key, issue_type="Bug")

    async def get_project(self, project_key: str) -> IntegrationResult:
        """Get project info (with caching)."""
        return await self.safe_request(
            "get_project",
            project_key,
            cache_key=f"project:{project_key}"
        )
