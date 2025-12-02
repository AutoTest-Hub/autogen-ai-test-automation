"""
Base Integration Framework for AutoGen AI QA Platform

Provides abstract base class and common utilities for tool integrations.
All integrations are READ-ONLY for security.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class IntegrationType(str, Enum):
    """Types of supported integrations."""
    GITHUB = "github"
    JIRA = "jira"
    CONFLUENCE = "confluence"


class IntegrationStatus(str, Enum):
    """Status of an integration connection."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class IntegrationConfig:
    """Configuration for a tool integration."""
    integration_type: IntegrationType
    name: str  # User-friendly name for this connection
    enabled: bool = True

    # Connection settings
    base_url: Optional[str] = None  # For self-hosted instances
    api_token: Optional[str] = None  # Stored securely, never logged

    # Rate limiting
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000

    # Caching
    cache_ttl_seconds: int = 300  # 5 minutes

    # Scope (what can be accessed)
    allowed_resources: List[str] = field(default_factory=list)  # e.g., ["repos/owner/*"]

    def __post_init__(self):
        """Mask API token in string representations."""
        pass

    def __repr__(self):
        """Safe repr that doesn't expose API token."""
        return (
            f"IntegrationConfig(type={self.integration_type}, "
            f"name={self.name}, enabled={self.enabled})"
        )


@dataclass
class IntegrationResult:
    """Result of an integration operation."""
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    cached: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Pagination info
    has_more: bool = False
    next_cursor: Optional[str] = None
    total_count: Optional[int] = None


class IntegrationError(Exception):
    """Exception raised by integrations."""

    def __init__(
        self,
        message: str,
        integration_type: IntegrationType,
        recoverable: bool = True,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message)
        self.integration_type = integration_type
        self.recoverable = recoverable
        self.retry_after = retry_after


class BaseIntegration(ABC):
    """
    Abstract base class for all tool integrations.

    Key principles:
    1. READ-ONLY: Never modify external systems
    2. RATE LIMITED: Respect API limits
    3. CACHED: Reduce redundant calls
    4. SECURE: Never log credentials
    """

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.status = IntegrationStatus.DISCONNECTED
        self._cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self._request_count = 0
        self._last_reset = datetime.utcnow()
        self._connected = False

    @property
    @abstractmethod
    def integration_type(self) -> IntegrationType:
        """Return the type of this integration."""
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the external service.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the external service."""
        pass

    @abstractmethod
    async def test_connection(self) -> IntegrationResult:
        """
        Test if the integration is working.

        Returns:
            IntegrationResult with success status and any diagnostic info
        """
        pass

    async def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns:
            True if request allowed, False if rate limited
        """
        now = datetime.utcnow()

        # Reset counters if an hour has passed
        if (now - self._last_reset).total_seconds() > 3600:
            self._request_count = 0
            self._last_reset = now

        if self._request_count >= self.config.max_requests_per_hour:
            self.status = IntegrationStatus.RATE_LIMITED
            logger.warning(
                f"Rate limit reached for {self.integration_type}: "
                f"{self._request_count}/{self.config.max_requests_per_hour}/hour"
            )
            return False

        return True

    async def _increment_request_count(self):
        """Increment the request counter."""
        self._request_count += 1

    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """
        Get cached data if not expired.

        Args:
            cache_key: Unique key for this cache entry

        Returns:
            Cached data or None if expired/missing
        """
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            age = (datetime.utcnow() - timestamp).total_seconds()
            if age < self.config.cache_ttl_seconds:
                return data
            else:
                del self._cache[cache_key]
        return None

    def _set_cached(self, cache_key: str, data: Any) -> None:
        """
        Store data in cache.

        Args:
            cache_key: Unique key for this cache entry
            data: Data to cache
        """
        self._cache[cache_key] = (data, datetime.utcnow())

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def is_resource_allowed(self, resource: str) -> bool:
        """
        Check if accessing a resource is allowed by config.

        Args:
            resource: Resource identifier (e.g., "repos/owner/repo")

        Returns:
            True if allowed, False otherwise
        """
        if not self.config.allowed_resources:
            return True  # No restrictions

        for pattern in self.config.allowed_resources:
            if self._matches_pattern(resource, pattern):
                return True

        logger.warning(
            f"Access denied to {resource} by integration config"
        )
        return False

    def _matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches an allowed pattern."""
        # Simple wildcard matching
        if pattern == "*":
            return True
        if pattern.endswith("/*"):
            prefix = pattern[:-1]
            return resource.startswith(prefix)
        return resource == pattern

    async def safe_request(
        self,
        operation: str,
        *args,
        cache_key: Optional[str] = None,
        **kwargs
    ) -> IntegrationResult:
        """
        Execute a request with rate limiting and caching.

        Args:
            operation: Name of the operation to perform
            cache_key: Optional key for caching the result
            *args, **kwargs: Arguments for the operation

        Returns:
            IntegrationResult with the operation outcome
        """
        # Check rate limit
        if not await self._check_rate_limit():
            return IntegrationResult(
                success=False,
                error_message="Rate limit exceeded"
            )

        # Check cache
        if cache_key:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return IntegrationResult(success=True, data=cached, cached=True)

        # Execute operation
        try:
            await self._increment_request_count()
            result = await self._execute_operation(operation, *args, **kwargs)

            # Cache successful results
            if result.success and cache_key:
                self._set_cached(cache_key, result.data)

            return result

        except Exception as e:
            logger.exception(f"Integration error in {operation}")
            return IntegrationResult(
                success=False,
                error_message=str(e)
            )

    @abstractmethod
    async def _execute_operation(
        self,
        operation: str,
        *args,
        **kwargs
    ) -> IntegrationResult:
        """
        Execute the actual operation. Implemented by subclasses.

        Args:
            operation: Name of the operation
            *args, **kwargs: Operation arguments

        Returns:
            IntegrationResult with operation outcome
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return {
            "type": self.integration_type.value,
            "name": self.config.name,
            "status": self.status.value,
            "enabled": self.config.enabled,
            "connected": self._connected,
            "request_count": self._request_count,
            "cache_size": len(self._cache),
        }
