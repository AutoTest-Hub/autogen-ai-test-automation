"""
Configuration package for AutoGen Test Automation Framework
"""

from .settings import settings, AutoGenTestFrameworkSettings, LLMProvider, TestFramework, AgentRole

__all__ = [
    "settings",
    "AutoGenTestFrameworkSettings", 
    "LLMProvider",
    "TestFramework",
    "AgentRole"
]

