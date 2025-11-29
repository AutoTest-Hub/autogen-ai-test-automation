"""
Unit tests for BaseTestAgent

Tests the unified LLM response generation, caching, and retry logic.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

import sys
sys.path.insert(0, '/home/user/autogen-ai-test-automation')

from agents.base_agent import BaseTestAgent
from config.settings import AgentRole, LLMProvider
from models.local_ai_provider import LocalAIProvider, ModelType


class ConcreteTestAgent(BaseTestAgent):
    """Concrete implementation for testing"""

    async def process_task(self, task_data):
        return {"status": "completed", "data": task_data}

    def get_capabilities(self):
        return ["test_capability"]


class TestBaseTestAgent:
    """Test suite for BaseTestAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        """Create a mock LocalAIProvider"""
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.get_status_report.return_value = {"status": "available"}
        provider.generate_response_async = AsyncMock(return_value={
            "response": "Mock LLM response",
            "success": True,
            "model": "test-model",
            "response_time": 0.5
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        """Create a test agent"""
        return ConcreteTestAgent(
            role=AgentRole.PLANNING,
            name="test_agent",
            local_ai_provider=mock_local_ai_provider
        )

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "test_agent"
        assert agent.role == AgentRole.PLANNING
        assert agent.state["status"] == "initialized"
        assert agent.state["tasks_completed"] == 0
        assert agent.state["errors"] == 0

    def test_agent_capabilities(self, agent):
        """Test agent returns capabilities"""
        caps = agent.get_capabilities()
        assert "test_capability" in caps

    def test_model_type_mapping(self, agent):
        """Test role to model type mapping"""
        assert agent.model_type == ModelType.PLANNING

    def test_state_update(self, agent):
        """Test state update functionality"""
        agent.update_state("processing", current_task="test")
        assert agent.state["status"] == "processing"

    def test_get_state(self, agent):
        """Test get_state returns a copy"""
        state = agent.get_state()
        state["modified"] = True
        assert "modified" not in agent.state

    def test_get_metrics(self, agent):
        """Test metrics calculation"""
        agent.state["tasks_completed"] = 10
        agent.state["errors"] = 2

        metrics = agent.get_metrics()

        assert metrics["tasks_completed"] == 10
        assert metrics["errors"] == 2
        assert metrics["success_rate"] == 0.8

    def test_cache_key_generation(self, agent):
        """Test cache key is deterministic"""
        key1 = agent._get_cache_key("test prompt", "system")
        key2 = agent._get_cache_key("test prompt", "system")
        key3 = agent._get_cache_key("different prompt", "system")

        assert key1 == key2
        assert key1 != key3

    def test_response_caching(self, agent):
        """Test response caching mechanism"""
        cache_key = "test_key"
        response = {"response": "cached", "success": True}

        agent._cache_response(cache_key, response)
        cached = agent._get_cached_response(cache_key)

        assert cached == response

    def test_cache_disabled(self, agent):
        """Test caching can be disabled"""
        agent.enable_caching = False

        cache_key = "test_key"
        agent._cache_response(cache_key, {"response": "test"})
        cached = agent._get_cached_response(cache_key)

        assert cached is None

    @pytest.mark.asyncio
    async def test_generate_llm_response_success(self, agent, mock_local_ai_provider):
        """Test successful LLM response generation"""
        result = await agent.generate_llm_response(
            prompt="Test prompt",
            use_cache=False
        )

        assert result["success"] is True
        assert result["response"] == "Mock LLM response"
        assert result["cached"] is False

    @pytest.mark.asyncio
    async def test_generate_llm_response_cached(self, agent, mock_local_ai_provider):
        """Test cached response is returned"""
        # First call - should hit the API
        result1 = await agent.generate_llm_response(
            prompt="Test prompt",
            use_cache=True
        )

        # Second call - should hit cache
        result2 = await agent.generate_llm_response(
            prompt="Test prompt",
            use_cache=True
        )

        assert result2["cached"] is True
        # API should only be called once
        assert mock_local_ai_provider.generate_response_async.call_count == 1

    @pytest.mark.asyncio
    async def test_generate_llm_response_retry(self, agent, mock_local_ai_provider):
        """Test retry logic on failure"""
        # First two calls fail, third succeeds
        mock_local_ai_provider.generate_response_async.side_effect = [
            {"success": False, "error": "Timeout"},
            {"success": False, "error": "Rate limit"},
            {"success": True, "response": "Success after retry"}
        ]

        result = await agent.generate_llm_response(
            prompt="Test prompt",
            use_cache=False
        )

        assert result["success"] is True
        assert result["response"] == "Success after retry"
        assert mock_local_ai_provider.generate_response_async.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_llm_response_all_retries_fail(self, agent, mock_local_ai_provider):
        """Test all retries exhausted"""
        mock_local_ai_provider.generate_response_async.return_value = {
            "success": False,
            "error": "Persistent error"
        }

        result = await agent.generate_llm_response(
            prompt="Test prompt",
            use_cache=False
        )

        assert result["success"] is False
        assert "Persistent error" in result["error"]
        assert agent.state["errors"] == 1

    def test_json_response_parsing(self, agent):
        """Test JSON response parsing"""
        result = {
            "response": '{"key": "value"}',
            "success": True
        }

        parsed = agent._parse_json_response(result)

        assert parsed["json_parse_success"] is True
        assert parsed["parsed_json"] == {"key": "value"}

    def test_json_response_parsing_with_markdown(self, agent):
        """Test JSON parsing handles markdown code blocks"""
        result = {
            "response": '```json\n{"key": "value"}\n```',
            "success": True
        }

        parsed = agent._parse_json_response(result)

        assert parsed["json_parse_success"] is True
        assert parsed["parsed_json"] == {"key": "value"}

    def test_json_response_parsing_failure(self, agent):
        """Test JSON parsing handles invalid JSON"""
        result = {
            "response": "Not valid JSON",
            "success": True
        }

        parsed = agent._parse_json_response(result)

        assert parsed["json_parse_success"] is False
        assert "json_parse_error" in parsed

    def test_clear_cache(self, agent):
        """Test cache clearing"""
        agent._cache_response("key1", {"response": "test1"})
        agent._cache_response("key2", {"response": "test2"})

        agent.clear_cache()

        assert agent._get_cached_response("key1") is None
        assert agent._get_cached_response("key2") is None

    def test_local_ai_status(self, agent, mock_local_ai_provider):
        """Test local AI status report"""
        status = agent.get_local_ai_status()

        assert status["agent_name"] == "test_agent"
        assert status["local_ai_enabled"] is True
        assert status["model_type"] == "planning"


class TestCacheSizeLimit:
    """Test cache size limiting"""

    @pytest.fixture
    def agent_with_small_cache(self, mock_local_ai_provider):
        """Create agent with small cache"""
        BaseTestAgent._cache_max_size = 5
        agent = ConcreteTestAgent(
            role=AgentRole.PLANNING,
            local_ai_provider=mock_local_ai_provider
        )
        return agent

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    def test_cache_eviction(self, agent_with_small_cache):
        """Test old cache entries are evicted"""
        agent = agent_with_small_cache

        # Fill cache beyond limit
        for i in range(10):
            agent._cache_response(f"key_{i}", {"response": f"value_{i}"})

        # Cache should be limited
        assert len(agent._response_cache) <= agent._cache_max_size + 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
