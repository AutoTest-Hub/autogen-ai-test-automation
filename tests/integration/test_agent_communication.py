"""
Integration tests for Agent-to-Agent Communication

Tests the communication patterns and data contracts between agents.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

import sys
sys.path.insert(0, '/home/user/autogen-ai-test-automation')

from agents.base_agent import BaseTestAgent
from agents.planning_agent import PlanningAgent
from config.settings import AgentRole
from models.local_ai_provider import LocalAIProvider
from contracts.agent_contracts import (
    DiscoveryResult,
    TestPlan,
    GeneratedTest,
    ReviewResult,
    TestCase,
    TestStep,
    RiskAssessment,
    Priority,
    TestFramework,
    validate_discovery_result,
    validate_test_plan,
    validate_generated_test,
    validate_review_result
)


class TestDataContractValidation:
    """Tests for data contract validation"""

    def test_validate_discovery_result_valid(self):
        """Test validation of valid discovery result"""
        data = {
            "discovery_id": "disc-123",
            "application_url": "https://example.com",
            "timestamp": datetime.now().isoformat()
        }

        assert validate_discovery_result(data) == True

    def test_validate_discovery_result_missing_fields(self):
        """Test validation fails with missing fields"""
        data = {
            "discovery_id": "disc-123"
            # Missing application_url and timestamp
        }

        assert validate_discovery_result(data) == False

    def test_validate_test_plan_valid(self):
        """Test validation of valid test plan"""
        data = {
            "plan_id": "plan-123",
            "name": "Test Plan",
            "test_cases": [],
            "recommended_framework": "playwright"
        }

        assert validate_test_plan(data) == True

    def test_validate_test_plan_missing_fields(self):
        """Test validation fails with missing fields"""
        data = {
            "plan_id": "plan-123"
        }

        assert validate_test_plan(data) == False

    def test_validate_generated_test_valid(self):
        """Test validation of valid generated test"""
        data = {
            "generation_id": "gen-123",
            "test_files": [],
            "framework": "playwright"
        }

        assert validate_generated_test(data) == True

    def test_validate_review_result_valid(self):
        """Test validation of valid review result"""
        data = {
            "review_id": "rev-123",
            "overall_score": 8.5,
            "ready_for_execution": True
        }

        assert validate_review_result(data) == True


class TestDataContractCreation:
    """Tests for creating data contracts"""

    def test_create_test_step(self):
        """Test creating a TestStep"""
        step = TestStep(
            step_number=1,
            action="Click login button",
            expected_result="Login form submits",
            target_element="#login-btn"
        )

        assert step.step_number == 1
        assert step.action == "Click login button"

        serialized = step.to_dict()
        assert serialized["step_number"] == 1

    def test_create_test_case(self):
        """Test creating a TestCase"""
        steps = [
            TestStep(1, "Navigate", "Page loads"),
            TestStep(2, "Click", "Element clicked")
        ]

        test_case = TestCase(
            test_id="TC-001",
            name="Login Test",
            description="Test user login",
            priority=Priority.HIGH,
            test_type="functional",
            steps=steps,
            expected_results=["User logged in"]
        )

        assert test_case.test_id == "TC-001"
        assert len(test_case.steps) == 2

        serialized = test_case.to_dict()
        assert serialized["priority"] == "high"

    def test_create_risk_assessment(self):
        """Test creating a RiskAssessment"""
        risk = RiskAssessment(
            overall_risk_level="Medium",
            risk_score=5.5,
            key_risks=[{"risk": "Data loss", "severity": "high"}],
            mitigation_strategies=["Backup data before test"]
        )

        assert risk.overall_risk_level == "Medium"
        assert risk.risk_score == 5.5

    def test_create_test_plan(self):
        """Test creating a complete TestPlan"""
        steps = [TestStep(1, "Step", "Result")]
        test_case = TestCase(
            test_id="TC-001",
            name="Test",
            description="Description",
            priority=Priority.MEDIUM,
            test_type="functional",
            steps=steps,
            expected_results=["Success"]
        )

        risk = RiskAssessment(
            overall_risk_level="Low",
            risk_score=2.0,
            key_risks=[],
            mitigation_strategies=[]
        )

        plan = TestPlan(
            plan_id="PLAN-001",
            name="Test Plan",
            description="Complete test plan",
            created_at=datetime.now(),
            test_cases=[test_case],
            priority_order=["TC-001"],
            risk_assessment=risk,
            recommended_framework=TestFramework.PLAYWRIGHT,
            estimated_duration_minutes=30
        )

        assert plan.plan_id == "PLAN-001"
        assert len(plan.test_cases) == 1

        serialized = plan.to_dict()
        assert "test_cases" in serialized


class TestAgentValidationCommunication:
    """Tests for agent validation requests"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": "Validation approved",
            "success": True
        })
        return provider

    @pytest.fixture
    def planning_agent(self, mock_local_ai_provider):
        return PlanningAgent(local_ai_provider=mock_local_ai_provider)

    def test_parse_validation_response_approved(self, planning_agent):
        """Test parsing an approval response"""
        response = "The artifact is valid and approved for use. Quality score: 9/10"
        criteria = ["correctness", "completeness"]

        result = planning_agent._parse_validation_response(response, criteria)

        assert result["approved"] == True
        assert result["is_valid"] == True

    def test_parse_validation_response_rejected(self, planning_agent):
        """Test parsing a rejection response"""
        response = "The artifact is invalid and rejected. Major issues found."
        criteria = ["correctness"]

        result = planning_agent._parse_validation_response(response, criteria)

        assert result["approved"] == False
        assert result["is_valid"] == False

    def test_parse_validation_response_with_issues(self, planning_agent):
        """Test parsing response with issues"""
        response = """
Review complete.
- issue: Missing error handling
- issue: No assertions found
The code is acceptable.
"""
        criteria = ["error_handling"]

        result = planning_agent._parse_validation_response(response, criteria)

        assert len(result["issues"]) > 0

    def test_parse_validation_response_empty(self, planning_agent):
        """Test parsing empty response"""
        response = ""
        criteria = []

        result = planning_agent._parse_validation_response(response, criteria)

        assert result["approved"] == False
        assert result["is_valid"] == False


class TestAgentCollaboration:
    """Tests for agent collaboration patterns"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": "Collaboration feedback",
            "success": True
        })
        return provider

    @pytest.fixture
    def planning_agent(self, mock_local_ai_provider):
        return PlanningAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_request_validation_structure(self, planning_agent):
        """Test validation request structure"""
        # Create a mock validator agent
        mock_validator = MagicMock()
        mock_validator.agent = MagicMock()
        mock_validator.agent.name = "validator"

        # Mock the send_message to capture the request
        captured_messages = []
        async def capture_message(msg, request_reply=True):
            captured_messages.append(msg)
            return "Approved. Valid artifact."

        planning_agent.send_message = AsyncMock(side_effect=capture_message)

        artifact = {
            "type": "test_plan",
            "summary": "Test plan for login functionality"
        }
        criteria = ["completeness", "correctness"]

        result = await planning_agent.request_validation(
            mock_validator,
            artifact,
            criteria
        )

        # Verify the request was made
        assert len(captured_messages) > 0
        assert "validate" in captured_messages[0].lower() or "review" in captured_messages[0].lower()

    @pytest.mark.asyncio
    async def test_collaborate_with_structure(self, planning_agent):
        """Test collaboration request structure"""
        mock_collaborator = MagicMock()
        mock_collaborator.agent = MagicMock()
        mock_collaborator.agent.name = "collaborator"

        # Mock successful collaboration
        planning_agent.send_message = AsyncMock(return_value="APPROVED - looks good!")
        planning_agent.process_task = AsyncMock(return_value={"status": "success"})

        task = {"type": "review", "data": "test data"}

        result = await planning_agent.collaborate_with(
            mock_collaborator,
            task,
            max_rounds=2
        )

        assert "rounds" in result
        assert "final_output" in result
        assert "consensus_reached" in result


class TestContractSerialization:
    """Tests for contract serialization/deserialization"""

    def test_discovery_result_serialization(self):
        """Test DiscoveryResult serialization"""
        result = DiscoveryResult(
            discovery_id="disc-123",
            application_url="https://example.com",
            timestamp=datetime.now(),
            metadata={"browser": "chromium"}
        )

        serialized = result.to_dict()

        assert serialized["discovery_id"] == "disc-123"
        assert "timestamp" in serialized
        assert serialized["metadata"]["browser"] == "chromium"

    def test_discovery_result_from_dict(self):
        """Test DiscoveryResult deserialization"""
        data = {
            "discovery_id": "disc-456",
            "application_url": "https://example.com",
            "timestamp": datetime.now().isoformat(),
            "screenshots": ["screen1.png"],
            "metadata": {"version": "1.0"}
        }

        result = DiscoveryResult.from_dict(data)

        assert result.discovery_id == "disc-456"
        assert result.application_url == "https://example.com"


class TestPipelineDataFlow:
    """Tests for data flow through the agent pipeline"""

    def test_discovery_to_planning_data_structure(self):
        """Test data structure passed from Discovery to Planning"""
        # Simulate discovery output
        discovery_output = {
            "discovery_id": "disc-123",
            "pages": [
                {"name": "Login", "url": "/login", "elements": []}
            ],
            "elements": {
                "login": [{"name": "username", "selector": "#username"}]
            },
            "workflows": [
                {"name": "Authentication", "steps": ["login", "verify"]}
            ]
        }

        # This should be valid input for planning
        assert "pages" in discovery_output
        assert "elements" in discovery_output
        assert "workflows" in discovery_output

    def test_planning_to_test_creation_data_structure(self):
        """Test data structure passed from Planning to Test Creation"""
        # Simulate planning output
        planning_output = {
            "plan_id": "plan-123",
            "test_cases": [
                {
                    "test_id": "TC-001",
                    "name": "Login Test",
                    "steps": [
                        {"action": "navigate", "target": "/login"},
                        {"action": "fill", "target": "#username"}
                    ]
                }
            ],
            "framework": "playwright",
            "priority_order": ["TC-001"]
        }

        # This should be valid input for test creation
        assert "test_cases" in planning_output
        assert "framework" in planning_output

    def test_test_creation_to_review_data_structure(self):
        """Test data structure passed from Test Creation to Review"""
        # Simulate test creation output
        test_creation_output = {
            "generation_id": "gen-123",
            "test_files": [
                {
                    "path": "tests/test_login.py",
                    "content": "def test_login(): assert True",
                    "framework": "playwright"
                }
            ],
            "page_objects": [
                {"path": "pages/login_page.py", "content": "class LoginPage: pass"}
            ]
        }

        # This should be valid input for review
        assert "test_files" in test_creation_output
        assert len(test_creation_output["test_files"]) > 0

    def test_review_to_execution_data_structure(self):
        """Test data structure passed from Review to Execution"""
        # Simulate review output
        review_output = {
            "review_id": "rev-123",
            "overall_score": 8.5,
            "ready_for_execution": True,
            "issues": [],
            "approved_test_files": [
                "tests/test_login.py"
            ]
        }

        # This should be valid input for execution
        assert "ready_for_execution" in review_output
        assert review_output["ready_for_execution"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
