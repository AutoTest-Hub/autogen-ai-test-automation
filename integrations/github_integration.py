"""
GitHub Integration for AutoGen AI QA Platform

READ-ONLY access to GitHub for:
- Repository structure and file contents
- Pull requests and reviews
- Issues and comments
- Commit history
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiohttp
import base64
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
class GitHubFile:
    """Represents a file from GitHub."""
    path: str
    name: str
    content: Optional[str]  # Decoded content
    sha: str
    size: int
    type: str  # "file" or "dir"
    download_url: Optional[str] = None


@dataclass
class GitHubPR:
    """Represents a GitHub Pull Request."""
    number: int
    title: str
    body: Optional[str]
    state: str  # "open", "closed", "merged"
    author: str
    base_branch: str
    head_branch: str
    created_at: datetime
    updated_at: datetime
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    labels: List[str] = field(default_factory=list)


@dataclass
class GitHubIssue:
    """Represents a GitHub Issue."""
    number: int
    title: str
    body: Optional[str]
    state: str  # "open", "closed"
    author: str
    created_at: datetime
    updated_at: datetime
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)


@dataclass
class GitHubCommit:
    """Represents a GitHub Commit."""
    sha: str
    message: str
    author: str
    author_email: str
    date: datetime
    files_changed: List[str] = field(default_factory=list)


class GitHubIntegration(BaseIntegration):
    """
    Read-only GitHub integration.

    Provides access to:
    - Repository file structure
    - Pull requests and reviews
    - Issues
    - Commits

    Does NOT provide:
    - Write access (no creating/updating PRs, issues, etc.)
    - Admin access
    - Sensitive data (secrets, deploy keys)
    """

    GITHUB_API_URL = "https://api.github.com"

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def integration_type(self) -> IntegrationType:
        return IntegrationType.GITHUB

    async def connect(self) -> bool:
        """Establish connection to GitHub API."""
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AutoGen-AI-QA-Platform",
            }

            if self.config.api_token:
                headers["Authorization"] = f"token {self.config.api_token}"

            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )

            # Test connection
            result = await self.test_connection()
            if result.success:
                self._connected = True
                self.status = IntegrationStatus.CONNECTED
                logger.info(f"Connected to GitHub: {self.config.name}")
                return True
            else:
                self.status = IntegrationStatus.ERROR
                return False

        except Exception as e:
            logger.exception("Failed to connect to GitHub")
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> None:
        """Close GitHub API connection."""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False
        self.status = IntegrationStatus.DISCONNECTED

    async def test_connection(self) -> IntegrationResult:
        """Test GitHub API connection."""
        try:
            if not self._session:
                return IntegrationResult(
                    success=False,
                    error_message="Not connected"
                )

            async with self._session.get(f"{self.GITHUB_API_URL}/user") as response:
                if response.status == 200:
                    data = await response.json()
                    return IntegrationResult(
                        success=True,
                        data={"user": data.get("login"), "type": "authenticated"}
                    )
                elif response.status == 401:
                    # Try unauthenticated access
                    async with self._session.get(f"{self.GITHUB_API_URL}/rate_limit") as rate_response:
                        if rate_response.status == 200:
                            return IntegrationResult(
                                success=True,
                                data={"type": "unauthenticated"}
                            )
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
        """Execute a GitHub API operation."""
        operations = {
            "get_repo": self._get_repo,
            "get_file": self._get_file,
            "list_files": self._list_files,
            "get_pr": self._get_pr,
            "list_prs": self._list_prs,
            "get_issue": self._get_issue,
            "list_issues": self._list_issues,
            "list_commits": self._list_commits,
            "search_code": self._search_code,
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
        """Make a GitHub API request."""
        if not self._session:
            raise IntegrationError(
                "Not connected to GitHub",
                IntegrationType.GITHUB
            )

        url = f"{self.GITHUB_API_URL}/{endpoint.lstrip('/')}"

        async with self._session.get(url, params=params) as response:
            if response.status == 404:
                raise IntegrationError(
                    f"Resource not found: {endpoint}",
                    IntegrationType.GITHUB,
                    recoverable=False
                )
            elif response.status == 403:
                retry_after = response.headers.get("Retry-After")
                raise IntegrationError(
                    "Rate limit exceeded",
                    IntegrationType.GITHUB,
                    retry_after=int(retry_after) if retry_after else 60
                )
            elif response.status != 200:
                raise IntegrationError(
                    f"API error: {response.status}",
                    IntegrationType.GITHUB
                )

            return await response.json()

    # Repository operations

    async def _get_repo(self, owner: str, repo: str) -> IntegrationResult:
        """Get repository information."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(resource)
            return IntegrationResult(success=True, data=data)
        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main"
    ) -> IntegrationResult:
        """Get file contents from repository."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(
                f"repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref}
            )

            if data.get("type") != "file":
                return IntegrationResult(
                    success=False,
                    error_message=f"Not a file: {path}"
                )

            # Decode content
            content = None
            if data.get("content"):
                content = base64.b64decode(data["content"]).decode("utf-8")

            file = GitHubFile(
                path=data["path"],
                name=data["name"],
                content=content,
                sha=data["sha"],
                size=data["size"],
                type="file",
                download_url=data.get("download_url"),
            )

            return IntegrationResult(success=True, data=file)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _list_files(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: str = "main"
    ) -> IntegrationResult:
        """List files in a repository directory."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            endpoint = f"repos/{owner}/{repo}/contents/{path}" if path else f"repos/{owner}/{repo}/contents"
            data = await self._api_request(endpoint, params={"ref": ref})

            if not isinstance(data, list):
                data = [data]

            files = []
            for item in data:
                files.append(GitHubFile(
                    path=item["path"],
                    name=item["name"],
                    content=None,  # Not fetched in list
                    sha=item["sha"],
                    size=item.get("size", 0),
                    type=item["type"],
                    download_url=item.get("download_url"),
                ))

            return IntegrationResult(success=True, data=files)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Pull Request operations

    async def _get_pr(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> IntegrationResult:
        """Get a specific pull request."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(f"repos/{owner}/{repo}/pulls/{pr_number}")

            pr = GitHubPR(
                number=data["number"],
                title=data["title"],
                body=data.get("body"),
                state=data["state"],
                author=data["user"]["login"],
                base_branch=data["base"]["ref"],
                head_branch=data["head"]["ref"],
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                files_changed=data.get("changed_files", 0),
                additions=data.get("additions", 0),
                deletions=data.get("deletions", 0),
                labels=[l["name"] for l in data.get("labels", [])],
            )

            return IntegrationResult(success=True, data=pr)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _list_prs(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        limit: int = 30
    ) -> IntegrationResult:
        """List pull requests."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(
                f"repos/{owner}/{repo}/pulls",
                params={"state": state, "per_page": min(limit, 100)}
            )

            prs = []
            for item in data:
                prs.append(GitHubPR(
                    number=item["number"],
                    title=item["title"],
                    body=item.get("body"),
                    state=item["state"],
                    author=item["user"]["login"],
                    base_branch=item["base"]["ref"],
                    head_branch=item["head"]["ref"],
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
                    labels=[l["name"] for l in item.get("labels", [])],
                ))

            return IntegrationResult(success=True, data=prs)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Issue operations

    async def _get_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int
    ) -> IntegrationResult:
        """Get a specific issue."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(f"repos/{owner}/{repo}/issues/{issue_number}")

            issue = GitHubIssue(
                number=data["number"],
                title=data["title"],
                body=data.get("body"),
                state=data["state"],
                author=data["user"]["login"],
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                labels=[l["name"] for l in data.get("labels", [])],
                assignees=[a["login"] for a in data.get("assignees", [])],
            )

            return IntegrationResult(success=True, data=issue)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: Optional[List[str]] = None,
        limit: int = 30
    ) -> IntegrationResult:
        """List issues."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            params = {"state": state, "per_page": min(limit, 100)}
            if labels:
                params["labels"] = ",".join(labels)

            data = await self._api_request(
                f"repos/{owner}/{repo}/issues",
                params=params
            )

            issues = []
            for item in data:
                # Skip PRs (GitHub returns them in issues endpoint)
                if "pull_request" in item:
                    continue

                issues.append(GitHubIssue(
                    number=item["number"],
                    title=item["title"],
                    body=item.get("body"),
                    state=item["state"],
                    author=item["user"]["login"],
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00")),
                    labels=[l["name"] for l in item.get("labels", [])],
                    assignees=[a["login"] for a in item.get("assignees", [])],
                ))

            return IntegrationResult(success=True, data=issues)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Commit operations

    async def _list_commits(
        self,
        owner: str,
        repo: str,
        branch: str = "main",
        limit: int = 30
    ) -> IntegrationResult:
        """List recent commits."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(
                f"repos/{owner}/{repo}/commits",
                params={"sha": branch, "per_page": min(limit, 100)}
            )

            commits = []
            for item in data:
                commit_data = item["commit"]
                commits.append(GitHubCommit(
                    sha=item["sha"],
                    message=commit_data["message"],
                    author=commit_data["author"]["name"],
                    author_email=commit_data["author"]["email"],
                    date=datetime.fromisoformat(
                        commit_data["author"]["date"].replace("Z", "+00:00")
                    ),
                ))

            return IntegrationResult(success=True, data=commits)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Search operations

    async def _search_code(
        self,
        query: str,
        owner: str,
        repo: str,
        limit: int = 30
    ) -> IntegrationResult:
        """Search code in repository."""
        resource = f"repos/{owner}/{repo}"
        if not self.is_resource_allowed(resource):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            full_query = f"{query} repo:{owner}/{repo}"
            data = await self._api_request(
                "search/code",
                params={"q": full_query, "per_page": min(limit, 100)}
            )

            results = []
            for item in data.get("items", []):
                results.append({
                    "path": item["path"],
                    "name": item["name"],
                    "sha": item["sha"],
                    "url": item["html_url"],
                    "repository": item["repository"]["full_name"],
                })

            return IntegrationResult(
                success=True,
                data=results,
                total_count=data.get("total_count"),
            )

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Convenience methods

    async def get_repository(self, owner: str, repo: str) -> IntegrationResult:
        """Get repository info (with caching)."""
        return await self.safe_request(
            "get_repo",
            owner, repo,
            cache_key=f"repo:{owner}/{repo}"
        )

    async def get_file_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main"
    ) -> IntegrationResult:
        """Get file contents (with caching)."""
        return await self.safe_request(
            "get_file",
            owner, repo, path, ref,
            cache_key=f"file:{owner}/{repo}:{path}@{ref}"
        )

    async def list_directory(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: str = "main"
    ) -> IntegrationResult:
        """List directory contents (with caching)."""
        return await self.safe_request(
            "list_files",
            owner, repo, path, ref,
            cache_key=f"dir:{owner}/{repo}:{path}@{ref}"
        )

    async def get_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> IntegrationResult:
        """Get a pull request."""
        return await self.safe_request("get_pr", owner, repo, pr_number)

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open"
    ) -> IntegrationResult:
        """List pull requests."""
        return await self.safe_request("list_prs", owner, repo, state)

    async def get_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int
    ) -> IntegrationResult:
        """Get an issue."""
        return await self.safe_request("get_issue", owner, repo, issue_number)

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open"
    ) -> IntegrationResult:
        """List issues."""
        return await self.safe_request("list_issues", owner, repo, state)

    async def get_recent_commits(
        self,
        owner: str,
        repo: str,
        branch: str = "main"
    ) -> IntegrationResult:
        """Get recent commits."""
        return await self.safe_request("list_commits", owner, repo, branch)

    async def search_in_repo(
        self,
        owner: str,
        repo: str,
        query: str
    ) -> IntegrationResult:
        """Search code in repository."""
        return await self.safe_request("search_code", query, owner, repo)
