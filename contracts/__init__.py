"""
Agent Contracts Module
=====================

This module provides data contracts for communication between agents
in the test automation pipeline.
"""

from .agent_contracts import (
    # Enums
    ElementType,
    TestPriority,
    RiskLevel,
    ExecutionStatus,

    # Discovery contracts
    DiscoveredElement,
    DiscoveredPage,
    DiscoveryResult,

    # Planning contracts
    TestStep,
    TestCase,
    RiskAssessment,
    TestPlan,

    # Test creation contracts
    GeneratedTest,

    # Execution contracts
    TestExecutionResult,
    ExecutionReport,

    # Workflow context
    WorkflowContext,

    # Factory functions
    create_discovery_result,
    create_test_plan,
    create_workflow_context,
)

__all__ = [
    "ElementType",
    "TestPriority",
    "RiskLevel",
    "ExecutionStatus",
    "DiscoveredElement",
    "DiscoveredPage",
    "DiscoveryResult",
    "TestStep",
    "TestCase",
    "RiskAssessment",
    "TestPlan",
    "GeneratedTest",
    "TestExecutionResult",
    "ExecutionReport",
    "WorkflowContext",
    "create_discovery_result",
    "create_test_plan",
    "create_workflow_context",
]
