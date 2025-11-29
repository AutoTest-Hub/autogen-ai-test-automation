"""
Agent Data Contracts Package

Provides standardized data structures for inter-agent communication.
"""

from .agent_contracts import (
    # Enums
    Priority,
    TestFramework,
    CoverageStatus,

    # Discovery contracts
    ElementSelector,
    DiscoveredElement,
    DiscoveredPage,
    DiscoveredWorkflow,
    DiscoveryResult,

    # Planning contracts
    TestStep,
    TestCase,
    RiskAssessment,
    TestPlan,

    # Test Creation contracts
    GeneratedTestFile,
    GeneratedTest,

    # Review contracts
    ReviewIssue,
    RequirementCoverage,
    ReviewResult,

    # Execution contracts
    TestResult,
    ExecutionResult,

    # Workflow context
    WorkflowContext,
    create_workflow_context,

    # Utilities
    serialize_contract,
    validate_discovery_result,
    validate_test_plan,
    validate_generated_test,
    validate_review_result,
    validate_execution_result,
)

__all__ = [
    # Enums
    "Priority",
    "TestFramework",
    "CoverageStatus",

    # Discovery
    "ElementSelector",
    "DiscoveredElement",
    "DiscoveredPage",
    "DiscoveredWorkflow",
    "DiscoveryResult",

    # Planning
    "TestStep",
    "TestCase",
    "RiskAssessment",
    "TestPlan",

    # Test Creation
    "GeneratedTestFile",
    "GeneratedTest",

    # Review
    "ReviewIssue",
    "RequirementCoverage",
    "ReviewResult",

    # Execution
    "TestResult",
    "ExecutionResult",

    # Workflow
    "WorkflowContext",
    "create_workflow_context",

    # Utilities
    "serialize_contract",
    "validate_discovery_result",
    "validate_test_plan",
    "validate_generated_test",
    "validate_review_result",
    "validate_execution_result",
]
