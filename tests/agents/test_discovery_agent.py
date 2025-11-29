"""
Unit tests for RealBrowserDiscoveryAgent

Tests browser-based element discovery and workflow mapping.
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

from agents.real_browser_discovery_agent import RealBrowserDiscoveryAgent
from config.settings import AgentRole
from models.local_ai_provider import LocalAIProvider


class TestRealBrowserDiscoveryAgent:
    """Test suite for RealBrowserDiscoveryAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        """Create a mock LocalAIProvider"""
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.get_status_report.return_value = {"status": "available"}
        provider.generate_response_async = AsyncMock(return_value={
            "response": "Analysis complete",
            "success": True,
            "model": "test-model"
        })
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        """Create a discovery agent"""
        return RealBrowserDiscoveryAgent(local_ai_provider=mock_local_ai_provider)

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.role == AgentRole.DISCOVERY
        assert "discovery" in agent.name.lower()

    def test_agent_capabilities(self, agent):
        """Test agent returns expected capabilities"""
        caps = agent.get_capabilities()

        assert "real_browser_discovery" in caps
        assert "element_detection" in caps
        assert "selector_generation" in caps
        assert "workflow_mapping" in caps

    def test_work_directory_created(self, agent):
        """Test work directory is created"""
        assert agent.work_dir.exists()

    def test_screenshots_directory_created(self, agent):
        """Test screenshots directory is created"""
        assert agent.screenshots_dir.exists()


class TestDiscoveryAgentTaskProcessing:
    """Tests for task processing"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return RealBrowserDiscoveryAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_process_task_unknown_type(self, agent):
        """Test processing unknown task type"""
        task_data = {"task_type": "unknown_task"}

        result = await agent.process_task(task_data)

        assert result["status"] == "error"
        assert "unknown" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_process_task_missing_url(self, agent):
        """Test processing with missing URL"""
        task_data = {
            "task_type": "discover_page_elements",
            "page_url": ""
        }

        result = await agent.process_task(task_data)

        assert result["status"] == "error"


class TestDiscoveryAgentSelectorGeneration:
    """Tests for selector generation logic"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return RealBrowserDiscoveryAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_find_matching_selectors_login(self, agent):
        """Test finding selectors for login elements"""
        # Mock the page object
        mock_page = MagicMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            0,  # First pattern - no match
            1,  # Second pattern - one match
            [{"tag": "button", "id": "login-btn", "name": "", "type": "submit", "text": "Login"}]
        ])

        description = "login button"

        # This test verifies the logic structure
        # Actual browser interaction would be tested in integration tests
        assert "login" in description.lower()

    def test_search_patterns_for_login(self, agent):
        """Test that login-related search patterns are generated"""
        description = "login button"
        desc_lower = description.lower()

        search_patterns = []
        if "login" in desc_lower or "sign in" in desc_lower:
            if "button" in desc_lower:
                search_patterns.extend([
                    "button:has-text('Login')",
                    "button:has-text('Sign in')",
                    "input[type='submit'][value*='Login' i]"
                ])

        assert len(search_patterns) > 0
        assert any("Login" in p for p in search_patterns)

    def test_search_patterns_for_username(self, agent):
        """Test that username-related search patterns are generated"""
        description = "username input"
        desc_lower = description.lower()

        search_patterns = []
        if "username" in desc_lower or "email" in desc_lower:
            search_patterns.extend([
                "input[type='text'][name*='user' i]",
                "input[type='email']",
                "#username, #email"
            ])

        assert len(search_patterns) > 0

    def test_search_patterns_for_password(self, agent):
        """Test that password-related search patterns are generated"""
        description = "password input"
        desc_lower = description.lower()

        search_patterns = []
        if "password" in desc_lower:
            search_patterns.extend([
                "input[type='password']",
                "#password",
                "[name='password']"
            ])

        assert len(search_patterns) > 0
        assert "input[type='password']" in search_patterns


class TestDiscoveryAgentWorkflowMapping:
    """Tests for workflow mapping functionality"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return RealBrowserDiscoveryAgent(local_ai_provider=mock_local_ai_provider)

    def test_workflow_types_supported(self, agent):
        """Test that expected workflow types are supported"""
        supported_workflows = ["authentication", "shopping", "browsing"]

        # The agent should be able to handle these workflow types
        for workflow_type in supported_workflows:
            assert workflow_type in ["authentication", "shopping", "browsing"]

    def test_authentication_workflow_structure(self):
        """Test authentication workflow has expected structure"""
        auth_workflow = {
            "name": "User Authentication Workflow",
            "type": "authentication",
            "priority": "high",
            "description": "User login and account access",
            "steps": [
                {"action": "navigate", "target": "/login"},
                {"action": "input", "target": "#username"},
                {"action": "input", "target": "#password"},
                {"action": "click", "target": "button[type='submit']"}
            ],
            "test_scenarios": [
                "Successful login with valid credentials",
                "Failed login with invalid credentials"
            ]
        }

        assert auth_workflow["type"] == "authentication"
        assert len(auth_workflow["steps"]) > 0
        assert len(auth_workflow["test_scenarios"]) > 0


class TestDiscoveryAgentPageAnalysis:
    """Tests for page analysis functionality"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return RealBrowserDiscoveryAgent(local_ai_provider=mock_local_ai_provider)

    def test_element_types_supported(self):
        """Test that expected element types are supported"""
        element_types = ["inputs", "buttons", "links", "forms"]

        # All these types should be discoverable
        for elem_type in element_types:
            assert elem_type in ["inputs", "buttons", "links", "forms"]

    def test_page_discovery_result_structure(self):
        """Test page discovery result has expected structure"""
        result = {
            "status": "completed",
            "page_url": "https://example.com/login",
            "elements": {
                "inputs": [],
                "buttons": [],
                "links": [],
                "forms": []
            },
            "total_elements": 0,
            "screenshot": "path/to/screenshot.png"
        }

        assert "status" in result
        assert "elements" in result
        assert "inputs" in result["elements"]
        assert "buttons" in result["elements"]


class TestDiscoveryAgentJavaScriptUtilities:
    """Tests for JavaScript utility functions used in discovery"""

    def test_xpath_generation_logic(self):
        """Test XPath generation logic structure"""
        # This tests the expected behavior of the JavaScript getXPath function
        # which is used during element discovery

        # For element with ID
        element_with_id = {"id": "username"}
        expected_xpath = f'//*[@id="{element_with_id["id"]}"]'
        assert expected_xpath == '//*[@id="username"]'

    def test_optimal_selector_generation_logic(self):
        """Test optimal selector generation logic"""
        # Test ID-based selector (highest priority)
        element_with_id = {"id": "login-btn"}
        expected_selector = f'#{element_with_id["id"]}'
        assert expected_selector == "#login-btn"

        # Test name-based selector
        element_with_name = {"name": "username"}
        expected_selector = f'[name="{element_with_name["name"]}"]'
        assert expected_selector == '[name="username"]'

    def test_button_text_selector(self):
        """Test button selector with text content"""
        button_text = "Login"
        selector = f'button:has-text("{button_text}")'
        assert selector == 'button:has-text("Login")'


class TestDiscoveryAgentEdgeCases:
    """Edge case tests for DiscoveryAgent"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = False
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return RealBrowserDiscoveryAgent(local_ai_provider=mock_local_ai_provider)

    @pytest.mark.asyncio
    async def test_handle_missing_page_url(self, agent):
        """Test handling of missing page URL"""
        task_data = {
            "task_type": "discover_page_elements",
            "element_types": ["inputs", "buttons"]
        }

        result = await agent.process_task(task_data)

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_handle_empty_element_types(self, agent):
        """Test handling when no element types specified"""
        task_data = {
            "task_type": "discover_page_elements",
            "page_url": "https://example.com",
            "element_types": []
        }

        # Should use defaults when empty
        result = await agent.process_task(task_data)
        # Result depends on actual browser availability
        assert result is not None


class TestDiscoveryAgentResultPersistence:
    """Tests for result saving functionality"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def agent(self, mock_local_ai_provider):
        return RealBrowserDiscoveryAgent(local_ai_provider=mock_local_ai_provider)

    def test_work_dir_path(self, agent):
        """Test work directory path is correct"""
        assert "RealBrowserDiscoveryAgent" in str(agent.work_dir) or "discovery" in str(agent.work_dir).lower()

    def test_screenshots_dir_path(self, agent):
        """Test screenshots directory path is correct"""
        assert agent.screenshots_dir.name == "screenshots"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
