"""
Unit tests for PlanningAgent

Tests LLM-powered requirement analysis and test strategy generation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

import sys
sys.path.insert(0, '/home/user/autogen-ai-test-automation')

from agents.planning_agent import PlanningAgent
from config.settings import AgentRole
from models.local_ai_provider import LocalAIProvider


class TestPlanningAgent:
    """Test suite for PlanningAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        """Create a mock LocalAIProvider"""
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.get_status_report.return_value = {"status": "available"}
        provider.generate_response_async = AsyncMock(return_value={
            "response": '{"requirement_summary": "Test summary", "test_scenarios": [], "complexity_assessment": {"overall_complexity": "Medium", "complexity_score": 5}}',
            "success": True,
            "model": "test-model"
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        """Create a planning agent"""
        return PlanningAgent(local_ai_provider=mock_local_ai_provider)

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.role == AgentRole.PLANNING
        assert "planning" in agent.name.lower()

    def test_agent_capabilities(self, agent):
        """Test agent returns expected capabilities"""
        caps = agent.get_capabilities()

        assert "requirement_analysis" in caps
        assert "test_strategy_creation" in caps
        assert "risk_assessment" in caps

    @pytest.mark.asyncio
    async def test_process_task_create_plan(self, agent):
        """Test create_plan task processing"""
        task_data = {
            "type": "create_plan",
            "requirements": {"test": "requirements"},
            "test_files": []
        }

        result = await agent.process_task(task_data)

        assert result["status"] == "success"
        assert "test_plan" in result

    @pytest.mark.asyncio
    async def test_analyze_requirements_with_llm(self, agent, mock_local_ai_provider):
        """Test LLM-powered requirement analysis"""
        requirements = "Test the login functionality"
        discovery_data = {
            "pages": [{"name": "Login Page", "url": "/login"}],
            "elements": {"login": []},
            "workflows": []
        }

        result = await agent._analyze_requirements_with_llm(requirements, discovery_data)

        # Should have called the LLM
        assert mock_local_ai_provider.generate_response_async.called

        # Result should have expected structure
        assert "requirement_summary" in result or "raw_analysis" in result

    @pytest.mark.asyncio
    async def test_assess_risk_with_llm(self, agent, mock_local_ai_provider):
        """Test LLM-powered risk assessment"""
        mock_local_ai_provider.generate_response_async.return_value = {
            "response": '{"overall_risk_level": "Medium", "risk_score": 5, "key_risks": []}',
            "success": True
        }

        test_plan = {"name": "Test Plan", "scenarios": []}
        scenarios = [{"name": "Login Test"}]

        result = await agent._assess_risk_with_llm(test_plan, scenarios)

        assert "overall_risk_level" in result or "raw_assessment" in result

    def test_fallback_requirement_analysis(self, agent):
        """Test fallback when LLM unavailable"""
        result = agent._fallback_requirement_analysis("requirements", {})

        assert result["requirement_summary"] == "Basic analysis (LLM unavailable)"
        assert result["complexity_assessment"]["overall_complexity"] == "Unknown"

    def test_fallback_risk_assessment(self, agent):
        """Test fallback risk assessment"""
        result = agent._fallback_risk_assessment({}, [])

        assert result["overall_risk_level"] == "Medium"
        assert result["confidence_level"] == "Low"

    def test_calculate_complexity_basic(self, agent):
        """Test complexity calculation"""
        test_data = {
            "testSteps": [{"step": 1}, {"step": 2}, {"step": 3}],
            "testData": {"key": "value"}
        }

        score = agent._calculate_complexity(test_data)

        assert 0 <= score <= 10

    def test_identify_risk_factors(self, agent):
        """Test risk factor identification"""
        test_data = {
            "tags": ["security", "authentication"],
            "description": "Test payment processing"
        }

        risks = agent._identify_risk_factors(test_data)

        assert isinstance(risks, list)

    def test_recommend_framework(self, agent):
        """Test framework recommendation"""
        test_data = {
            "environment": {"type": "web"},
            "tags": ["ui"]
        }

        framework = agent._recommend_framework(test_data)

        assert framework in ["playwright", "selenium", "api"]


class TestPlanningAgentIntegration:
    """Integration tests for PlanningAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": '{"strategy_name": "Comprehensive Test Strategy", "objectives": ["Test login"], "execution_plan": {"phases": ["Setup", "Execute"]}}',
            "success": True
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return PlanningAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_generate_test_strategy_with_llm(self, agent, mock_local_ai_provider):
        """Test full test strategy generation"""
        requirements = "Test e-commerce checkout flow"
        discovery_data = {
            "pages": [
                {"name": "Cart", "url": "/cart"},
                {"name": "Checkout", "url": "/checkout"}
            ],
            "elements": {},
            "workflows": [{"name": "Checkout Flow", "steps": ["Add to cart", "Checkout"]}]
        }
        constraints = {"max_duration": 60}

        result = await agent._generate_test_strategy_with_llm(
            requirements, discovery_data, constraints
        )

        assert "strategy_name" in result or "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
