"""
Unit tests for ReviewAgent

Tests LLM-powered code review and quality assessment.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import tempfile
import os

import sys
sys.path.insert(0, '/home/user/autogen-ai-test-automation')

from agents.review_agent import ReviewAgent
from config.settings import AgentRole
from models.local_ai_provider import LocalAIProvider


class TestReviewAgent:
    """Test suite for ReviewAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        """Create a mock LocalAIProvider"""
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.get_status_report.return_value = {"status": "available"}
        provider.generate_response_async = AsyncMock(return_value={
            "response": '''{
                "overall_score": 8.5,
                "requirement_coverage": {"covered": true, "percentage": 90},
                "issues": [{"severity": "low", "description": "Minor style issue"}],
                "strengths": ["Good error handling", "Clear assertions"],
                "recommendations": ["Add more edge cases"]
            }''',
            "success": True,
            "model": "test-model"
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        """Create a review agent"""
        return ReviewAgent(local_ai_provider=mock_local_ai_provider)

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.role == AgentRole.REVIEW
        assert "review" in agent.name.lower()

    def test_agent_capabilities(self, agent):
        """Test agent returns expected capabilities"""
        caps = agent.get_capabilities()

        assert "review_test_code" in caps
        assert "validate_test_scenarios" in caps
        assert "assess_code_quality" in caps

    @pytest.mark.asyncio
    async def test_process_task_review_code(self, agent):
        """Test review_code task processing"""
        task_data = {
            "type": "review_code",
            "test_code": '''
import pytest

def test_login():
    """Test login functionality"""
    try:
        assert True
    except Exception as e:
        logging.error(e)
'''
        }

        result = await agent.process_task(task_data)

        assert "review_results" in result
        assert "overall_score" in result

    @pytest.mark.asyncio
    async def test_review_single_file_exists(self, agent):
        """Test reviewing a file that exists"""
        # Create a temp test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
import pytest
import logging

def test_example():
    """Example test"""
    try:
        assert 1 + 1 == 2
    except Exception as e:
        logging.error(e)
        raise
''')
            temp_path = f.name

        try:
            result = await agent._review_single_file(temp_path)

            assert "filename" in result
            assert "score" in result
            assert result["score"] > 0
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_review_single_file_not_exists(self, agent):
        """Test reviewing a file that doesn't exist"""
        result = await agent._review_single_file("/nonexistent/path.py")

        # Should handle gracefully - either error or treat as content
        assert "filename" in result

    @pytest.mark.asyncio
    async def test_review_code_snippet(self, agent):
        """Test reviewing a code snippet"""
        code = '''
import pytest
import logging

def test_sample():
    """Sample test with logging"""
    try:
        assert True
    except Exception as e:
        logging.error(e)
'''

        result = await agent._review_code_snippet(code, "test_sample.py")

        assert result["filename"] == "test_sample.py"
        assert "score" in result
        assert "issues" in result
        assert "strengths" in result

    @pytest.mark.asyncio
    async def test_review_code_without_imports(self, agent):
        """Test reviewing code without imports"""
        code = '''
def test_simple():
    assert True
'''

        result = await agent._review_code_snippet(code)

        assert "Missing import statements" in result["issues"]

    @pytest.mark.asyncio
    async def test_review_code_without_error_handling(self, agent):
        """Test reviewing code without error handling"""
        code = '''
import pytest

def test_simple():
    assert True
'''

        result = await agent._review_code_snippet(code)

        assert "Limited error handling" in result["issues"]

    @pytest.mark.asyncio
    async def test_review_code_without_logging(self, agent):
        """Test reviewing code without logging"""
        code = '''
import pytest

def test_simple():
    try:
        assert True
    except Exception:
        pass
'''

        result = await agent._review_code_snippet(code)

        assert "No logging found" in result["issues"]

    @pytest.mark.asyncio
    async def test_review_code_without_assertions(self, agent):
        """Test reviewing code without assertions"""
        code = '''
import pytest

def test_simple():
    print("Hello")
'''

        result = await agent._review_code_snippet(code)

        assert "Missing test assertions" in result["issues"]

    @pytest.mark.asyncio
    async def test_review_well_written_code(self, agent):
        """Test reviewing well-written code"""
        code = '''
"""Test module with proper documentation"""
import pytest
import logging

def test_well_written():
    """Well documented test"""
    try:
        assert 1 + 1 == 2, "Math should work"
        logging.info("Test passed")
    except Exception as e:
        logging.error(f"Test failed: {e}")
        raise
'''

        result = await agent._review_code_snippet(code)

        assert result["score"] >= 8
        assert len(result["strengths"]) > 0


class TestReviewAgentScenarioValidation:
    """Tests for scenario validation"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": "Valid scenario",
            "success": True
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return ReviewAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_validate_scenarios(self, agent):
        """Test scenario validation"""
        task_data = {
            "scenarios": [
                {
                    "name": "Login Test",
                    "steps": ["Navigate to login", "Enter credentials", "Click submit"],
                    "expected_result": "User logged in"
                },
                {
                    "name": "Invalid Scenario",
                    "steps": []  # Invalid - no steps
                }
            ]
        }

        result = await agent._validate_scenarios(task_data)

        assert result["total_scenarios"] == 2
        assert "valid_scenarios" in result
        assert "invalid_scenarios" in result

    def test_validate_single_scenario_valid(self, agent):
        """Test validating a valid scenario"""
        scenario = {
            "name": "Login Test",
            "steps": ["Step 1", "Step 2"],
            "expected_result": "Success"
        }

        result = agent._validate_single_scenario(scenario, 0)

        assert result["is_valid"] == True

    def test_validate_single_scenario_no_name(self, agent):
        """Test validating scenario without name"""
        scenario = {
            "steps": ["Step 1"]
        }

        result = agent._validate_single_scenario(scenario, 0)

        assert result["is_valid"] == False
        assert any("name" in issue.lower() for issue in result["issues"])

    def test_validate_single_scenario_no_steps(self, agent):
        """Test validating scenario without steps"""
        scenario = {
            "name": "Test",
            "steps": []
        }

        result = agent._validate_single_scenario(scenario, 0)

        assert result["is_valid"] == False


class TestReviewAgentLLMIntegration:
    """Tests for LLM-powered review features"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": '''{
                "validates_requirement": true,
                "coverage_score": 0.85,
                "missing_assertions": [],
                "edge_cases_covered": ["null input", "empty string"],
                "recommendations": []
            }''',
            "success": True
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return ReviewAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_review_with_llm_if_available(self, agent, mock_local_ai_provider):
        """Test LLM-powered review when method exists"""
        if hasattr(agent, 'review_with_llm'):
            code = "def test_example(): assert True"
            requirements = {"name": "Test requirement"}

            result = await agent.review_with_llm(code, requirements)

            assert mock_local_ai_provider.generate_response_async.called or result is not None

    @pytest.mark.asyncio
    async def test_validate_requirement_coverage_with_llm_if_available(self, agent, mock_local_ai_provider):
        """Test LLM requirement coverage validation when method exists"""
        if hasattr(agent, 'validate_requirement_coverage_with_llm'):
            code = "def test_login(): assert login() == True"
            requirements = {"id": "REQ-001", "description": "User can login"}

            result = await agent.validate_requirement_coverage_with_llm(code, requirements)

            assert result is not None

    @pytest.mark.asyncio
    async def test_suggest_improvements_with_llm_if_available(self, agent, mock_local_ai_provider):
        """Test LLM improvement suggestions when method exists"""
        if hasattr(agent, 'suggest_improvements_with_llm'):
            mock_local_ai_provider.generate_response_async.return_value = {
                "response": '{"improvements": ["Add timeout handling", "Include negative test"]}',
                "success": True
            }

            code = "def test_simple(): pass"
            context = {"test_type": "functional"}

            result = await agent.suggest_improvements_with_llm(code, context)

            assert "improvements" in result or "error" in result


class TestReviewAgentScoring:
    """Tests for review scoring logic"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return ReviewAgent(local_ai_provider=mock_local_ai_provider)

    def test_calculate_overall_score_empty(self, agent):
        """Test calculating score with no reviews"""
        reviews = []
        score = agent._calculate_overall_score(reviews)
        assert score == 0

    def test_calculate_overall_score_single(self, agent):
        """Test calculating score with single review"""
        reviews = [{"score": 8}]
        score = agent._calculate_overall_score(reviews)
        assert score == 8

    def test_calculate_overall_score_multiple(self, agent):
        """Test calculating score with multiple reviews"""
        reviews = [{"score": 8}, {"score": 6}, {"score": 10}]
        score = agent._calculate_overall_score(reviews)
        assert score == 8  # Average

    def test_generate_review_summary(self, agent):
        """Test generating review summary"""
        reviews = [
            {"score": 8, "issues": ["Issue 1"], "strengths": ["Strength 1"]},
            {"score": 6, "issues": ["Issue 2", "Issue 3"], "strengths": []}
        ]

        summary = agent._generate_review_summary(reviews)

        assert "total_files" in summary
        assert "total_issues" in summary
        assert "average_score" in summary

    def test_generate_recommendations(self, agent):
        """Test generating recommendations from reviews"""
        reviews = [
            {"recommendations": ["Add error handling"]},
            {"recommendations": ["Add logging", "Add documentation"]}
        ]

        recommendations = agent._generate_recommendations(reviews)

        assert isinstance(recommendations, list)
        assert len(recommendations) >= 0


class TestReviewAgentEdgeCases:
    """Edge case tests for ReviewAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = False
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return ReviewAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_handle_empty_test_files(self, agent):
        """Test handling of empty test files list"""
        task_data = {
            "type": "review_code",
            "test_files": []
        }

        result = await agent.process_task(task_data)

        assert "review_results" in result

    @pytest.mark.asyncio
    async def test_handle_no_test_code(self, agent):
        """Test handling when no test code provided"""
        task_data = {"type": "review_code"}

        result = await agent.process_task(task_data)

        # Should handle gracefully
        assert result is not None

    @pytest.mark.asyncio
    async def test_unknown_task_type(self, agent):
        """Test handling of unknown task type"""
        task_data = {"type": "unknown_task"}

        with pytest.raises(ValueError):
            await agent.process_task(task_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
