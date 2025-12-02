"""
Confluence Integration for AutoGen AI QA Platform

READ-ONLY access to Confluence for:
- Pages and their content
- Space information
- Attachments metadata
- Labels and search
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiohttp
import logging
import re

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
class ConfluencePage:
    """Represents a Confluence Page."""
    id: str
    title: str
    space_key: str
    body: Optional[str]  # HTML or storage format
    body_plain: Optional[str]  # Plain text version
    version: int
    created: datetime
    updated: datetime
    created_by: str
    updated_by: str
    labels: List[str] = field(default_factory=list)
    ancestors: List[str] = field(default_factory=list)  # Parent page titles
    url: Optional[str] = None


@dataclass
class ConfluenceSpace:
    """Represents a Confluence Space."""
    key: str
    name: str
    description: Optional[str]
    type: str  # "global" or "personal"
    homepage_id: Optional[str] = None
    url: Optional[str] = None


@dataclass
class ConfluenceAttachment:
    """Represents a Confluence Attachment."""
    id: str
    title: str
    filename: str
    media_type: str
    file_size: int
    created: datetime
    download_url: Optional[str] = None


@dataclass
class ConfluenceSearchResult:
    """Represents a Confluence search result."""
    content_id: str
    title: str
    space_key: str
    content_type: str  # "page", "blogpost", "attachment"
    excerpt: Optional[str]
    url: Optional[str]
    last_modified: datetime


class ConfluenceIntegration(BaseIntegration):
    """
    Read-only Confluence integration.

    Provides access to:
    - Pages and content
    - Spaces
    - Search
    - Attachments metadata

    Does NOT provide:
    - Write access (no creating/updating pages)
    - Admin access
    - Attachment downloads (only metadata)
    """

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url = config.base_url or "https://confluence.atlassian.com"

    @property
    def integration_type(self) -> IntegrationType:
        return IntegrationType.CONFLUENCE

    async def connect(self) -> bool:
        """Establish connection to Confluence API."""
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            # Confluence Cloud uses email + API token as Basic Auth
            if self.config.api_token:
                import base64
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
                logger.info(f"Connected to Confluence: {self.config.name}")
                return True
            else:
                self.status = IntegrationStatus.ERROR
                return False

        except Exception as e:
            logger.exception("Failed to connect to Confluence")
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> None:
        """Close Confluence API connection."""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False
        self.status = IntegrationStatus.DISCONNECTED

    async def test_connection(self) -> IntegrationResult:
        """Test Confluence API connection."""
        try:
            if not self._session:
                return IntegrationResult(
                    success=False,
                    error_message="Not connected"
                )

            url = f"{self._base_url}/wiki/rest/api/user/current"
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return IntegrationResult(
                        success=True,
                        data={"user": data.get("displayName", data.get("username"))}
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
        """Execute a Confluence API operation."""
        operations = {
            "get_page": self._get_page,
            "get_page_by_title": self._get_page_by_title,
            "list_pages": self._list_pages,
            "get_space": self._get_space,
            "list_spaces": self._list_spaces,
            "search": self._search,
            "get_attachments": self._get_attachments,
            "get_page_children": self._get_page_children,
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
        """Make a Confluence API request."""
        if not self._session:
            raise IntegrationError(
                "Not connected to Confluence",
                IntegrationType.CONFLUENCE
            )

        url = f"{self._base_url}/wiki/rest/api/{endpoint.lstrip('/')}"

        async with self._session.get(url, params=params) as response:
            if response.status == 404:
                raise IntegrationError(
                    f"Resource not found: {endpoint}",
                    IntegrationType.CONFLUENCE,
                    recoverable=False
                )
            elif response.status == 401:
                raise IntegrationError(
                    "Authentication failed",
                    IntegrationType.CONFLUENCE,
                    recoverable=False
                )
            elif response.status == 429:
                retry_after = response.headers.get("Retry-After", "60")
                raise IntegrationError(
                    "Rate limit exceeded",
                    IntegrationType.CONFLUENCE,
                    retry_after=int(retry_after)
                )
            elif response.status != 200:
                raise IntegrationError(
                    f"API error: {response.status}",
                    IntegrationType.CONFLUENCE
                )

            return await response.json()

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Confluence datetime string."""
        if not date_str:
            return None
        try:
            # Confluence format: 2024-01-15T10:30:00.000Z
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    def _html_to_plain_text(self, html: Optional[str]) -> Optional[str]:
        """Convert HTML to plain text (simple conversion)."""
        if not html:
            return None
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # Page operations

    async def _get_page(self, page_id: str) -> IntegrationResult:
        """Get a page by ID."""
        try:
            data = await self._api_request(
                f"content/{page_id}",
                params={"expand": "body.storage,version,ancestors,space,metadata.labels"}
            )

            space_key = data.get("space", {}).get("key", "")
            if not self.is_resource_allowed(f"spaces/{space_key}"):
                return IntegrationResult(
                    success=False,
                    error_message="Access denied by configuration"
                )

            body_storage = data.get("body", {}).get("storage", {}).get("value", "")

            page = ConfluencePage(
                id=data["id"],
                title=data["title"],
                space_key=space_key,
                body=body_storage,
                body_plain=self._html_to_plain_text(body_storage),
                version=data.get("version", {}).get("number", 1),
                created=self._parse_datetime(data.get("history", {}).get("createdDate")),
                updated=self._parse_datetime(data.get("version", {}).get("when")),
                created_by=data.get("history", {}).get("createdBy", {}).get("displayName", "Unknown"),
                updated_by=data.get("version", {}).get("by", {}).get("displayName", "Unknown"),
                labels=[l.get("name") for l in data.get("metadata", {}).get("labels", {}).get("results", [])],
                ancestors=[a.get("title") for a in data.get("ancestors", [])],
                url=data.get("_links", {}).get("webui"),
            )

            return IntegrationResult(success=True, data=page)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _get_page_by_title(
        self,
        space_key: str,
        title: str
    ) -> IntegrationResult:
        """Get a page by space and title."""
        if not self.is_resource_allowed(f"spaces/{space_key}"):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(
                "content",
                params={
                    "spaceKey": space_key,
                    "title": title,
                    "expand": "body.storage,version,ancestors,metadata.labels"
                }
            )

            results = data.get("results", [])
            if not results:
                return IntegrationResult(
                    success=False,
                    error_message=f"Page not found: {title} in {space_key}"
                )

            page_data = results[0]
            body_storage = page_data.get("body", {}).get("storage", {}).get("value", "")

            page = ConfluencePage(
                id=page_data["id"],
                title=page_data["title"],
                space_key=space_key,
                body=body_storage,
                body_plain=self._html_to_plain_text(body_storage),
                version=page_data.get("version", {}).get("number", 1),
                created=self._parse_datetime(page_data.get("history", {}).get("createdDate")),
                updated=self._parse_datetime(page_data.get("version", {}).get("when")),
                created_by=page_data.get("history", {}).get("createdBy", {}).get("displayName", "Unknown"),
                updated_by=page_data.get("version", {}).get("by", {}).get("displayName", "Unknown"),
                labels=[l.get("name") for l in page_data.get("metadata", {}).get("labels", {}).get("results", [])],
                ancestors=[a.get("title") for a in page_data.get("ancestors", [])],
                url=page_data.get("_links", {}).get("webui"),
            )

            return IntegrationResult(success=True, data=page)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _list_pages(
        self,
        space_key: str,
        limit: int = 25
    ) -> IntegrationResult:
        """List pages in a space."""
        if not self.is_resource_allowed(f"spaces/{space_key}"):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(
                "content",
                params={
                    "spaceKey": space_key,
                    "type": "page",
                    "limit": min(limit, 100),
                    "expand": "version,metadata.labels"
                }
            )

            pages = []
            for item in data.get("results", []):
                pages.append(ConfluencePage(
                    id=item["id"],
                    title=item["title"],
                    space_key=space_key,
                    body=None,  # Not included in list
                    body_plain=None,
                    version=item.get("version", {}).get("number", 1),
                    created=None,
                    updated=self._parse_datetime(item.get("version", {}).get("when")),
                    created_by="",
                    updated_by=item.get("version", {}).get("by", {}).get("displayName", "Unknown"),
                    labels=[l.get("name") for l in item.get("metadata", {}).get("labels", {}).get("results", [])],
                ))

            return IntegrationResult(
                success=True,
                data=pages,
                has_more=len(data.get("results", [])) >= limit,
            )

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _get_page_children(
        self,
        page_id: str,
        limit: int = 25
    ) -> IntegrationResult:
        """Get child pages of a page."""
        try:
            data = await self._api_request(
                f"content/{page_id}/child/page",
                params={"limit": min(limit, 100), "expand": "version"}
            )

            children = []
            for item in data.get("results", []):
                children.append(ConfluencePage(
                    id=item["id"],
                    title=item["title"],
                    space_key=item.get("space", {}).get("key", ""),
                    body=None,
                    body_plain=None,
                    version=item.get("version", {}).get("number", 1),
                    created=None,
                    updated=self._parse_datetime(item.get("version", {}).get("when")),
                    created_by="",
                    updated_by=item.get("version", {}).get("by", {}).get("displayName", "Unknown"),
                ))

            return IntegrationResult(success=True, data=children)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Space operations

    async def _get_space(self, space_key: str) -> IntegrationResult:
        """Get space information."""
        if not self.is_resource_allowed(f"spaces/{space_key}"):
            return IntegrationResult(
                success=False,
                error_message="Access denied by configuration"
            )

        try:
            data = await self._api_request(
                f"space/{space_key}",
                params={"expand": "description.plain,homepage"}
            )

            space = ConfluenceSpace(
                key=data["key"],
                name=data["name"],
                description=data.get("description", {}).get("plain", {}).get("value"),
                type=data.get("type", "global"),
                homepage_id=data.get("homepage", {}).get("id"),
                url=data.get("_links", {}).get("webui"),
            )

            return IntegrationResult(success=True, data=space)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    async def _list_spaces(self, limit: int = 25) -> IntegrationResult:
        """List accessible spaces."""
        try:
            data = await self._api_request(
                "space",
                params={"limit": min(limit, 100), "expand": "description.plain"}
            )

            spaces = []
            for item in data.get("results", []):
                space_key = item["key"]
                if self.is_resource_allowed(f"spaces/{space_key}"):
                    spaces.append(ConfluenceSpace(
                        key=item["key"],
                        name=item["name"],
                        description=item.get("description", {}).get("plain", {}).get("value"),
                        type=item.get("type", "global"),
                        url=item.get("_links", {}).get("webui"),
                    ))

            return IntegrationResult(success=True, data=spaces)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Search operations

    async def _search(
        self,
        query: str,
        space_key: Optional[str] = None,
        limit: int = 25
    ) -> IntegrationResult:
        """Search Confluence content."""
        try:
            cql = f'text ~ "{query}"'
            if space_key:
                if not self.is_resource_allowed(f"spaces/{space_key}"):
                    return IntegrationResult(
                        success=False,
                        error_message="Access denied by configuration"
                    )
                cql += f' and space = "{space_key}"'

            data = await self._api_request(
                "content/search",
                params={"cql": cql, "limit": min(limit, 100)}
            )

            results = []
            for item in data.get("results", []):
                results.append(ConfluenceSearchResult(
                    content_id=item["id"],
                    title=item["title"],
                    space_key=item.get("space", {}).get("key", ""),
                    content_type=item.get("type", "page"),
                    excerpt=item.get("excerpt"),
                    url=item.get("_links", {}).get("webui"),
                    last_modified=self._parse_datetime(item.get("version", {}).get("when")),
                ))

            return IntegrationResult(
                success=True,
                data=results,
                total_count=data.get("totalSize"),
            )

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Attachment operations

    async def _get_attachments(
        self,
        page_id: str,
        limit: int = 25
    ) -> IntegrationResult:
        """Get attachments for a page."""
        try:
            data = await self._api_request(
                f"content/{page_id}/child/attachment",
                params={"limit": min(limit, 100)}
            )

            attachments = []
            for item in data.get("results", []):
                extensions = item.get("extensions", {})
                attachments.append(ConfluenceAttachment(
                    id=item["id"],
                    title=item["title"],
                    filename=item["title"],
                    media_type=extensions.get("mediaType", "application/octet-stream"),
                    file_size=extensions.get("fileSize", 0),
                    created=self._parse_datetime(item.get("version", {}).get("when")),
                    download_url=item.get("_links", {}).get("download"),
                ))

            return IntegrationResult(success=True, data=attachments)

        except IntegrationError as e:
            return IntegrationResult(success=False, error_message=str(e))

    # Convenience methods

    async def get_page(self, page_id: str) -> IntegrationResult:
        """Get page by ID (with caching)."""
        return await self.safe_request(
            "get_page",
            page_id,
            cache_key=f"page:{page_id}"
        )

    async def get_page_by_title(
        self,
        space_key: str,
        title: str
    ) -> IntegrationResult:
        """Get page by space and title (with caching)."""
        return await self.safe_request(
            "get_page_by_title",
            space_key,
            title,
            cache_key=f"page:{space_key}:{title}"
        )

    async def list_space_pages(
        self,
        space_key: str,
        limit: int = 25
    ) -> IntegrationResult:
        """List pages in a space."""
        return await self.safe_request("list_pages", space_key, limit)

    async def get_space(self, space_key: str) -> IntegrationResult:
        """Get space info (with caching)."""
        return await self.safe_request(
            "get_space",
            space_key,
            cache_key=f"space:{space_key}"
        )

    async def search_content(
        self,
        query: str,
        space_key: Optional[str] = None
    ) -> IntegrationResult:
        """Search Confluence content."""
        return await self.safe_request("search", query, space_key)

    async def get_documentation_pages(
        self,
        space_key: str,
        label: str = "documentation"
    ) -> IntegrationResult:
        """Get pages with a specific label."""
        cql = f'space = "{space_key}" and label = "{label}"'
        return await self._search(cql)

    async def get_business_rules(self, space_key: str) -> IntegrationResult:
        """Search for business rules documentation."""
        return await self.search_content("business rules OR acceptance criteria", space_key)

    async def get_api_documentation(self, space_key: str) -> IntegrationResult:
        """Search for API documentation."""
        return await self.search_content("API OR endpoint OR REST OR swagger", space_key)
