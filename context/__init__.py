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

__all__ = [
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
]
