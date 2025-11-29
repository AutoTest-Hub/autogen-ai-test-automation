"""
Unit tests for Agent Data Contracts

Tests the data structures and validation functions.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/user/autogen-ai-test-automation')

from contracts.agent_contracts import (
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


class TestEnums:
    """Test enum definitions"""

    def test_priority_values(self):
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"

    def test_framework_values(self):
        assert TestFramework.PLAYWRIGHT.value == "playwright"
        assert TestFramework.SELENIUM.value == "selenium"

    def test_coverage_status_values(self):
        assert CoverageStatus.COVERED.value == "covered"
        assert CoverageStatus.PARTIAL.value == "partial"
        assert CoverageStatus.NOT_COVERED.value == "not_covered"


class TestElementSelector:
    """Test ElementSelector contract"""

    def test_create_selector(self):
        selector = ElementSelector(
            primary="#login-button",
            fallbacks=["button.login", "button[type='submit']"],
            selector_type="css",
            confidence=0.95
        )

        assert selector.primary == "#login-button"
        assert len(selector.fallbacks) == 2

    def test_to_dict(self):
        selector = ElementSelector(primary="#test")
        data = selector.to_dict()

        assert data["primary"] == "#test"
        assert "fallbacks" in data
        assert "selector_type" in data


class TestDiscoveredElement:
    """Test DiscoveredElement contract"""

    def test_create_element(self):
        selector = ElementSelector(primary="#username")
        element = DiscoveredElement(
            element_id="elem_001",
            element_type="input",
            name="username",
            text="Enter username",
            selectors=selector,
            category="login"
        )

        assert element.element_id == "elem_001"
        assert element.is_interactive is True

    def test_to_dict(self):
        element = DiscoveredElement(
            element_id="elem_001",
            element_type="button",
            name="submit"
        )
        data = element.to_dict()

        assert data["element_id"] == "elem_001"
        assert data["element_type"] == "button"


class TestDiscoveredPage:
    """Test DiscoveredPage contract"""

    def test_create_page(self):
        page = DiscoveredPage(
            page_id="page_001",
            name="Login Page",
            url="/login",
            title="Sign In"
        )

        assert page.page_id == "page_001"
        assert page.elements == []

    def test_page_with_elements(self):
        element = DiscoveredElement(
            element_id="elem_001",
            element_type="input",
            name="username"
        )
        page = DiscoveredPage(
            page_id="page_001",
            name="Login Page",
            url="/login",
            elements=[element]
        )

        assert len(page.elements) == 1


class TestDiscoveryResult:
    """Test DiscoveryResult contract"""

    def test_create_discovery_result(self):
        result = DiscoveryResult(
            discovery_id="disc_001",
            application_url="https://example.com",
            timestamp=datetime.now()
        )

        assert result.discovery_id == "disc_001"
        assert result.pages == []

    def test_to_dict(self):
        result = DiscoveryResult(
            discovery_id="disc_001",
            application_url="https://example.com",
            timestamp=datetime.now()
        )
        data = result.to_dict()

        assert data["discovery_id"] == "disc_001"
        assert "timestamp" in data


class TestTestCase:
    """Test TestCase contract"""

    def test_create_test_case(self):
        step = TestStep(
            step_number=1,
            action="Click login button",
            expected_result="Login form appears"
        )
        test_case = TestCase(
            test_id="tc_001",
            name="Login Test",
            description="Test user login",
            priority=Priority.HIGH,
            test_type="functional",
            steps=[step],
            expected_results=["User is logged in"]
        )

        assert test_case.test_id == "tc_001"
        assert test_case.priority == Priority.HIGH

    def test_to_dict(self):
        test_case = TestCase(
            test_id="tc_001",
            name="Test",
            description="Desc",
            priority=Priority.MEDIUM,
            test_type="functional",
            steps=[],
            expected_results=[]
        )
        data = test_case.to_dict()

        assert data["priority"] == "medium"


class TestTestPlan:
    """Test TestPlan contract"""

    def test_create_test_plan(self):
        risk = RiskAssessment(
            overall_risk_level="Medium",
            risk_score=5.0,
            key_risks=[],
            mitigation_strategies=[]
        )
        plan = TestPlan(
            plan_id="plan_001",
            name="E2E Test Plan",
            description="Full end-to-end testing",
            created_at=datetime.now(),
            test_cases=[],
            priority_order=[],
            risk_assessment=risk,
            recommended_framework=TestFramework.PLAYWRIGHT,
            estimated_duration_minutes=60
        )

        assert plan.plan_id == "plan_001"
        assert plan.recommended_framework == TestFramework.PLAYWRIGHT


class TestGeneratedTest:
    """Test GeneratedTest contract"""

    def test_create_generated_test(self):
        test_file = GeneratedTestFile(
            file_id="file_001",
            file_path="/tests/test_login.py",
            file_name="test_login.py",
            content="import pytest...",
            framework=TestFramework.PLAYWRIGHT,
            test_cases_covered=["tc_001"],
            selectors_used=["#login"],
            llm_generated=True
        )
        generated = GeneratedTest(
            generation_id="gen_001",
            created_at=datetime.now(),
            test_files=[test_file],
            page_objects=[],
            config_files=[],
            framework=TestFramework.PLAYWRIGHT,
            plan_reference="plan_001"
        )

        assert generated.generation_id == "gen_001"
        assert len(generated.test_files) == 1
        assert generated.test_files[0].llm_generated is True


class TestReviewResult:
    """Test ReviewResult contract"""

    def test_create_review_result(self):
        issue = ReviewIssue(
            issue_id="issue_001",
            severity=Priority.MEDIUM,
            category="assertion",
            description="Missing assertion",
            file_path="test_login.py"
        )
        coverage = RequirementCoverage(
            requirement_id="req_001",
            coverage_status=CoverageStatus.PARTIAL,
            covering_tests=["tc_001"],
            gaps=["Edge case not covered"],
            confidence=0.8
        )
        result = ReviewResult(
            review_id="rev_001",
            created_at=datetime.now(),
            overall_score=7.5,
            issues=[issue],
            strengths=["Good structure"],
            requirement_coverage=[coverage],
            overall_coverage_percentage=75.0,
            ready_for_execution=True,
            recommendations=["Add more assertions"],
            generation_reference="gen_001"
        )

        assert result.overall_score == 7.5
        assert result.ready_for_execution is True


class TestExecutionResult:
    """Test ExecutionResult contract"""

    def test_create_execution_result(self):
        test_result = TestResult(
            test_id="tc_001",
            test_name="test_login",
            status="passed",
            duration_ms=1500
        )
        result = ExecutionResult(
            execution_id="exec_001",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            test_results=[test_result],
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            skipped_tests=0,
            success_rate=100.0,
            total_duration_ms=1500,
            environment={"browser": "chromium"},
            review_reference="rev_001"
        )

        assert result.success_rate == 100.0
        assert len(result.test_results) == 1


class TestWorkflowContext:
    """Test WorkflowContext"""

    def test_create_workflow_context(self):
        context = create_workflow_context("wf_001")

        assert context.workflow_id == "wf_001"
        assert context.current_stage == "initialized"
        assert context.discovery_result is None

    def test_add_error(self):
        context = create_workflow_context("wf_001")
        context.add_error("discovery", "Failed to connect", {"url": "example.com"})

        assert len(context.errors) == 1
        assert context.errors[0]["stage"] == "discovery"

    def test_add_warning(self):
        context = create_workflow_context("wf_001")
        context.add_warning("Some elements may be stale")

        assert len(context.warnings) == 1

    def test_to_dict(self):
        context = create_workflow_context("wf_001")
        data = context.to_dict()

        assert data["workflow_id"] == "wf_001"
        assert "started_at" in data


class TestValidationFunctions:
    """Test validation helper functions"""

    def test_validate_discovery_result_valid(self):
        data = {
            "discovery_id": "disc_001",
            "application_url": "https://example.com",
            "timestamp": "2024-01-01T00:00:00"
        }
        assert validate_discovery_result(data) is True

    def test_validate_discovery_result_invalid(self):
        data = {"discovery_id": "disc_001"}  # Missing required fields
        assert validate_discovery_result(data) is False

    def test_validate_test_plan_valid(self):
        data = {
            "plan_id": "plan_001",
            "name": "Test Plan",
            "test_cases": [],
            "recommended_framework": "playwright"
        }
        assert validate_test_plan(data) is True

    def test_validate_test_plan_invalid(self):
        data = {"plan_id": "plan_001"}
        assert validate_test_plan(data) is False

    def test_validate_generated_test_valid(self):
        data = {
            "generation_id": "gen_001",
            "test_files": [],
            "framework": "playwright"
        }
        assert validate_generated_test(data) is True

    def test_validate_review_result_valid(self):
        data = {
            "review_id": "rev_001",
            "overall_score": 8.0,
            "ready_for_execution": True
        }
        assert validate_review_result(data) is True

    def test_validate_execution_result_valid(self):
        data = {
            "execution_id": "exec_001",
            "test_results": [],
            "success_rate": 100.0
        }
        assert validate_execution_result(data) is True


class TestSerializeContract:
    """Test serialization utility"""

    def test_serialize_discovery_result(self):
        result = DiscoveryResult(
            discovery_id="disc_001",
            application_url="https://example.com",
            timestamp=datetime.now()
        )
        json_str = serialize_contract(result)

        assert "disc_001" in json_str
        assert "application_url" in json_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
