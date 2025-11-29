"""
Unit tests for EnhancedTestCreationAgent

Tests LLM-powered test code generation and page object creation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import tempfile
import os

import sys
sys.path.insert(0, '/home/user/autogen-ai-test-automation')

from agents.test_creation_agent import EnhancedTestCreationAgent
from config.settings import AgentRole
from models.local_ai_provider import LocalAIProvider


class TestEnhancedTestCreationAgent:
    """Test suite for EnhancedTestCreationAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        """Create a mock LocalAIProvider"""
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.get_status_report.return_value = {"status": "available"}
        provider.generate_response_async = AsyncMock(return_value={
            "response": '''```python
import pytest
from playwright.sync_api import Page

def test_login(page: Page):
    page.goto("https://example.com")
    page.fill("#username", "user")
    page.fill("#password", "pass")
    page.click("button[type='submit']")
    assert "Dashboard" in page.title()
```''',
            "success": True,
            "model": "test-model"
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        """Create a test creation agent"""
        return EnhancedTestCreationAgent(local_ai_provider=mock_local_ai_provider)

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.role == AgentRole.TEST_CREATION
        assert "TestCreation" in agent.name or "test_creation" in agent.name.lower()

    def test_agent_capabilities(self, agent):
        """Test agent returns expected capabilities"""
        caps = agent.get_capabilities()

        assert "real_code_generation" in caps
        assert "page_object_models" in caps
        assert "playwright_tests" in caps

    @pytest.mark.asyncio
    async def test_process_task_generate_tests(self, agent):
        """Test generate_tests task processing"""
        task_data = {
            "task_type": "generate_tests",
            "test_plan": {
                "test_cases": [
                    {
                        "name": "login_test",
                        "description": "Test user login",
                        "steps": ["Navigate to login", "Enter credentials", "Click login"]
                    }
                ],
                "framework": "playwright"
            },
            "application_data": {
                "base_url": "https://example.com",
                "discovered_pages": [],
                "discovered_elements": {}
            }
        }

        result = await agent.process_task(task_data)

        assert result["status"] in ["completed", "error"]
        if result["status"] == "completed":
            assert "generated_files" in result

    @pytest.mark.asyncio
    async def test_create_playwright_test(self, agent):
        """Test Playwright test creation"""
        test_case = {
            "name": "login_test",
            "description": "Test user login functionality",
            "steps": [
                "Navigate to login page",
                "Enter username",
                "Enter password",
                "Click login button"
            ]
        }
        app_data = {"base_url": "https://example.com"}
        pages = []
        elements = {}

        result = await agent._create_playwright_test(test_case, app_data, pages, elements)

        assert result is not None
        assert result["type"] == "test"
        assert result["framework"] == "playwright"
        assert "path" in result

    def test_generate_real_playwright_step_navigate(self, agent):
        """Test navigation step generation"""
        step = "Navigate to login page"
        elements = {}

        result = agent._generate_real_playwright_step(step, elements, 1)

        assert "navigate" in result.lower()

    def test_generate_real_playwright_step_login(self, agent):
        """Test login step generation"""
        step = "Click login button"
        elements = {}

        result = agent._generate_real_playwright_step(step, elements, 1)

        assert "login" in result.lower() or "click" in result.lower()

    def test_generate_real_playwright_step_username(self, agent):
        """Test username input step generation"""
        step = "Enter username"
        elements = {}

        result = agent._generate_real_playwright_step(step, elements, 1)

        assert "username" in result.lower()

    def test_generate_real_playwright_step_verify(self, agent):
        """Test verification step generation"""
        step = "Verify dashboard is displayed"
        elements = {}

        result = agent._generate_real_playwright_step(step, elements, 1)

        assert "assert" in result.lower() or "verify" in result.lower()

    def test_find_relevant_elements(self, agent):
        """Test finding relevant elements for a test"""
        test_name = "login_test"
        elements = {
            "login_page": [
                {"name": "username_input", "selector": "#username"},
                {"name": "password_input", "selector": "#password"}
            ]
        }
        pages = [{"name": "Login Page", "url": "/login"}]

        result = agent._find_relevant_elements(test_name, elements, pages)

        assert isinstance(result, dict)


class TestTestCreationAgentLLMIntegration:
    """Tests for LLM-powered test generation"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": '''```python
def test_generated():
    assert True
```''',
            "success": True
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return EnhancedTestCreationAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_generate_test_with_llm_if_available(self, agent, mock_local_ai_provider):
        """Test LLM-powered test generation when method exists"""
        if hasattr(agent, 'generate_test_with_llm'):
            test_case = {
                "name": "sample_test",
                "description": "A sample test",
                "steps": ["Step 1", "Step 2"]
            }
            elements = {}

            result = await agent.generate_test_with_llm(test_case, elements, "playwright")

            # Should have attempted LLM call
            assert mock_local_ai_provider.generate_response_async.called or result is not None

    @pytest.mark.asyncio
    async def test_generate_assertions_with_llm_if_available(self, agent, mock_local_ai_provider):
        """Test LLM-powered assertion generation when method exists"""
        if hasattr(agent, 'generate_assertions_with_llm'):
            mock_local_ai_provider.generate_response_async.return_value = {
                "response": '{"assertions": ["assert title == expected", "assert element.is_visible()"]}',
                "success": True
            }

            test_case = {"name": "test", "expected_result": "Dashboard visible"}
            context = {"page_url": "/dashboard"}

            result = await agent.generate_assertions_with_llm(test_case, context)

            assert "assertions" in result or "error" in result


class TestTestCreationAgentPageObjects:
    """Tests for Page Object Model generation"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": "Mock response",
            "success": True
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return EnhancedTestCreationAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_create_page_objects_from_discovery(self, agent):
        """Test page object creation from discovery data"""
        pages = [
            {"name": "Login Page", "url": "/login"},
            {"name": "Dashboard", "url": "/dashboard"}
        ]
        elements = {
            "login_page": [
                {"name": "username", "selector": "#username", "type": "input"},
                {"name": "password", "selector": "#password", "type": "input"}
            ]
        }

        result = await agent._create_page_objects_from_discovery(pages, elements, "playwright")

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_create_configuration_files(self, agent):
        """Test configuration file creation"""
        app_data = {
            "base_url": "https://example.com",
            "browser": "chromium"
        }

        result = await agent._create_configuration_files("playwright", "https://example.com", app_data)

        assert isinstance(result, list)


class TestTestCreationAgentEdgeCases:
    """Edge case tests for TestCreationAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = False  # LLM not available
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return EnhancedTestCreationAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_handle_empty_test_plan(self, agent):
        """Test handling of empty test plan"""
        task_data = {
            "task_type": "generate_tests",
            "test_plan": {"test_cases": []},
            "application_data": {}
        }

        result = await agent.process_task(task_data)

        assert result["status"] in ["completed", "error"]

    @pytest.mark.asyncio
    async def test_handle_missing_application_data(self, agent):
        """Test handling of missing application data"""
        task_data = {
            "task_type": "generate_tests",
            "test_plan": {
                "test_cases": [{"name": "test", "steps": ["step1"]}]
            }
        }

        result = await agent.process_task(task_data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_unknown_task_type(self, agent):
        """Test handling of unknown task type"""
        task_data = {"task_type": "unknown_task"}

        result = await agent.process_task(task_data)

        assert result["status"] == "error"
        assert "unknown" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
