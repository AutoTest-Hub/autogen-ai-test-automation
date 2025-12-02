"""
Context module for AutoGen AI QA Platform

This module provides application context management, enabling AI agents
to understand customer applications similar to human QA onboarding.
"""

from .application_context import (
    ApplicationContext,
    TechStackInfo,
    BusinessRule,
    EnvironmentConfig,
    EnvironmentType,
    AuthType,
    UserJourney,
    TestPattern,
    DomainTerm,
    APIEndpoint,
    create_application_context,
)

from .knowledge_ingester import (
    KnowledgeIngester,
    OpenAPIIngester,
    ReadmeIngester,
    TestPatternIngester,
    TechStackDetector,
    IngestionResult,
    IngestionSource,
)

from .context_persistence import (
    ContextStore,
    ContextSyncManager,
    ContextArtifactGenerator,
)

from .credential_vault import (
    CredentialVault,
    CredentialType,
    CredentialMetadata,
    CredentialReference,
)

__all__ = [
    # Application Context
    "ApplicationContext",
    "TechStackInfo",
    "BusinessRule",
    "EnvironmentConfig",
    "EnvironmentType",
    "AuthType",
    "UserJourney",
    "TestPattern",
    "DomainTerm",
    "APIEndpoint",
    "create_application_context",
    # Knowledge Ingestion
    "KnowledgeIngester",
    "OpenAPIIngester",
    "ReadmeIngester",
    "TestPatternIngester",
    "TechStackDetector",
    "IngestionResult",
    "IngestionSource",
    # Persistence & Sync
    "ContextStore",
    "ContextSyncManager",
    "ContextArtifactGenerator",
    # Credential Vault
    "CredentialVault",
    "CredentialType",
    "CredentialMetadata",
    "CredentialReference",
]
