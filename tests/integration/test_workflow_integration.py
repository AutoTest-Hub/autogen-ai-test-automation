"""
Integration tests for WorkflowOrchestrator

Tests the complete workflow execution with agent coordination
and context passing between agents.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import json
import os

import sys
sys.path.insert(0, '/home/user/autogen-ai-test-automation')

from orchestrator.workflow_orchestrator import WorkflowOrchestrator, WorkflowStatus
from config.settings import AgentRole
from models.local_ai_provider import LocalAIProvider
from contracts.agent_contracts import (
    WorkflowContext,
    DiscoveryResult,
    TestPlan,
    create_workflow_context
)


class TestWorkflowIntegration:
    """Integration tests for complete workflow execution"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        """Create a mock LocalAIProvider for all agents"""
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.get_status_report.return_value = {"status": "available"}
        provider.generate_response_async = AsyncMock(return_value={
            "response": '{"status": "success", "data": {}}',
            "success": True,
            "model": "test-model"
        })
        return provider

    @pytest.fixture
    def orchestrator(self, mock_local_ai_provider):
        """Create a workflow orchestrator with mocked agents"""
        with patch('orchestrator.workflow_orchestrator.PlanningAgent') as mock_planning, \
             patch('orchestrator.workflow_orchestrator.EnhancedTestCreationAgent') as mock_test_creation, \
             patch('orchestrator.workflow_orchestrator.ReviewAgent') as mock_review, \
             patch('orchestrator.workflow_orchestrator.ExecutionAgent') as mock_execution, \
             patch('orchestrator.workflow_orchestrator.ReportingAgent') as mock_reporting:

            # Configure mocks
            for mock_cls in [mock_planning, mock_test_creation, mock_review, mock_execution, mock_reporting]:
                mock_instance = MagicMock()
                mock_instance.process_task = AsyncMock(return_value={"status": "success"})
                mock_cls.return_value = mock_instance

            orchestrator = WorkflowOrchestrator(local_ai_provider=mock_local_ai_provider)
            return orchestrator

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert len(orchestrator.workflow_templates) > 0

    def test_available_templates(self, orchestrator):
        """Test that workflow templates are available"""
        templates = orchestrator.get_workflow_templates()

        # Should have standard templates
        assert "web_ui_testing" in templates or len(templates) > 0

    def test_workflow_context_tracking(self, orchestrator):
        """Test workflow context dictionary is initialized"""
        assert hasattr(orchestrator, 'workflow_contexts')
        assert isinstance(orchestrator.workflow_contexts, dict)


class TestWorkflowCreation:
    """Tests for workflow creation"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def orchestrator(self, mock_local_ai_provider):
        with patch('orchestrator.workflow_orchestrator.PlanningAgent'), \
             patch('orchestrator.workflow_orchestrator.EnhancedTestCreationAgent'), \
             patch('orchestrator.workflow_orchestrator.ReviewAgent'), \
             patch('orchestrator.workflow_orchestrator.ExecutionAgent'), \
             patch('orchestrator.workflow_orchestrator.ReportingAgent'):
            return WorkflowOrchestrator(local_ai_provider=mock_local_ai_provider)

    def test_create_workflow_from_template(self, orchestrator):
        """Test creating a workflow from a template"""
        templates = orchestrator.get_workflow_templates()
        template_name = list(templates.keys())[0] if templates else "web_ui_testing"

        workflow_id = orchestrator.create_workflow(
            template_name=template_name,
            test_files=["test_example.py"],
            custom_config={"base_url": "https://example.com"}
        )

        assert workflow_id is not None
        assert workflow_id in orchestrator.active_workflows

    def test_workflow_context_created_with_workflow(self, orchestrator):
        """Test that workflow context is created when workflow is created"""
        templates = orchestrator.get_workflow_templates()
        template_name = list(templates.keys())[0] if templates else "web_ui_testing"

        workflow_id = orchestrator.create_workflow(
            template_name=template_name,
            test_files=["test_example.py"]
        )

        assert workflow_id in orchestrator.workflow_contexts
        context = orchestrator.workflow_contexts[workflow_id]
        assert context.workflow_id == workflow_id

    def test_get_workflow_context(self, orchestrator):
        """Test retrieving workflow context"""
        templates = orchestrator.get_workflow_templates()
        template_name = list(templates.keys())[0] if templates else "web_ui_testing"

        workflow_id = orchestrator.create_workflow(
            template_name=template_name,
            test_files=["test.py"]
        )

        context = orchestrator.get_workflow_context(workflow_id)

        assert context is not None
        assert "workflow_id" in context


class TestAgentCoordination:
    """Tests for agent coordination during workflow execution"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        provider.generate_response_async = AsyncMock(return_value={
            "response": "{}",
            "success": True
        })
        return provider

    @pytest.fixture
    def orchestrator_with_agents(self, mock_local_ai_provider):
        """Create orchestrator with mock agents that track calls"""
        with patch('orchestrator.workflow_orchestrator.PlanningAgent') as mock_planning, \
             patch('orchestrator.workflow_orchestrator.EnhancedTestCreationAgent') as mock_creation, \
             patch('orchestrator.workflow_orchestrator.ReviewAgent') as mock_review, \
             patch('orchestrator.workflow_orchestrator.ExecutionAgent') as mock_execution, \
             patch('orchestrator.workflow_orchestrator.ReportingAgent') as mock_reporting:

            # Track which agents were called
            agents_called = []

            for name, mock_cls in [
                ('planning', mock_planning),
                ('test_creation', mock_creation),
                ('review', mock_review),
                ('execution', mock_execution),
                ('reporting', mock_reporting)
            ]:
                mock_instance = MagicMock()
                mock_instance.process_task = AsyncMock(
                    side_effect=lambda data, n=name: (agents_called.append(n), {"status": "success"})[1]
                )
                mock_cls.return_value = mock_instance

            orchestrator = WorkflowOrchestrator(local_ai_provider=mock_local_ai_provider)
            orchestrator._agents_called = agents_called
            return orchestrator

    def test_agents_registered(self, orchestrator_with_agents):
        """Test that agents are registered in the orchestrator"""
        assert len(orchestrator_with_agents.available_agents) > 0


class TestContextPassing:
    """Tests for context passing between agents"""

    def test_workflow_context_creation(self):
        """Test WorkflowContext creation"""
        context = create_workflow_context("test-workflow-123")

        assert context.workflow_id == "test-workflow-123"
        assert context.current_stage == "initialized"
        assert context.discovery_result is None
        assert context.test_plan is None

    def test_workflow_context_serialization(self):
        """Test WorkflowContext can be serialized"""
        context = create_workflow_context("test-workflow")
        context.current_stage = "planning"
        context.metadata["custom_data"] = "test"

        serialized = context.to_dict()

        assert serialized["workflow_id"] == "test-workflow"
        assert serialized["current_stage"] == "planning"
        assert serialized["metadata"]["custom_data"] == "test"

    def test_workflow_context_error_tracking(self):
        """Test error tracking in WorkflowContext"""
        context = create_workflow_context("test-workflow")

        context.add_error("discovery", "Page not found", {"url": "https://example.com"})
        context.add_error("planning", "Invalid requirements")

        assert len(context.errors) == 2
        assert context.errors[0]["stage"] == "discovery"
        assert context.errors[1]["stage"] == "planning"

    def test_workflow_context_warning_tracking(self):
        """Test warning tracking in WorkflowContext"""
        context = create_workflow_context("test-workflow")

        context.add_warning("Slow page load detected")
        context.add_warning("Element selector may be fragile")

        assert len(context.warnings) == 2


class TestWorkflowExecution:
    """Tests for workflow execution"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def orchestrator(self, mock_local_ai_provider):
        with patch('orchestrator.workflow_orchestrator.PlanningAgent') as mock_planning, \
             patch('orchestrator.workflow_orchestrator.EnhancedTestCreationAgent') as mock_creation, \
             patch('orchestrator.workflow_orchestrator.ReviewAgent') as mock_review, \
             patch('orchestrator.workflow_orchestrator.ExecutionAgent') as mock_execution, \
             patch('orchestrator.workflow_orchestrator.ReportingAgent') as mock_reporting:

            for mock_cls in [mock_planning, mock_creation, mock_review, mock_execution, mock_reporting]:
                mock_instance = MagicMock()
                mock_instance.process_task = AsyncMock(return_value={
                    "status": "success",
                    "data": {"result": "ok"}
                })
                mock_cls.return_value = mock_instance

            return WorkflowOrchestrator(local_ai_provider=mock_local_ai_provider)

    def test_workflow_status_transitions(self, orchestrator):
        """Test workflow status changes during execution"""
        templates = orchestrator.get_workflow_templates()
        template_name = list(templates.keys())[0] if templates else "web_ui_testing"

        workflow_id = orchestrator.create_workflow(
            template_name=template_name,
            test_files=["test.py"]
        )

        workflow = orchestrator.active_workflows[workflow_id]
        assert workflow.status == WorkflowStatus.PENDING

    def test_get_workflow_status(self, orchestrator):
        """Test getting workflow status"""
        templates = orchestrator.get_workflow_templates()
        template_name = list(templates.keys())[0] if templates else "web_ui_testing"

        workflow_id = orchestrator.create_workflow(
            template_name=template_name,
            test_files=["test.py"]
        )

        status = orchestrator.get_workflow_status(workflow_id)

        assert status is not None
        assert "id" in status
        assert "status" in status


class TestWorkflowHistory:
    """Tests for workflow history tracking"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def orchestrator(self, mock_local_ai_provider):
        with patch('orchestrator.workflow_orchestrator.PlanningAgent'), \
             patch('orchestrator.workflow_orchestrator.EnhancedTestCreationAgent'), \
             patch('orchestrator.workflow_orchestrator.ReviewAgent'), \
             patch('orchestrator.workflow_orchestrator.ExecutionAgent'), \
             patch('orchestrator.workflow_orchestrator.ReportingAgent'):
            return WorkflowOrchestrator(local_ai_provider=mock_local_ai_provider)

    def test_workflow_history_initially_empty(self, orchestrator):
        """Test workflow history starts empty"""
        assert len(orchestrator.workflow_history) == 0

    def test_execution_stats_tracking(self, orchestrator):
        """Test execution statistics are tracked"""
        stats = orchestrator.execution_stats

        assert "total_workflows" in stats
        assert "successful_workflows" in stats
        assert "failed_workflows" in stats


class TestCustomTemplates:
    """Tests for custom workflow template creation"""

    @pytest.fixture
    def mock_local_ai_provider(self):
        provider = Mock(spec=LocalAIProvider)
        provider.is_available.return_value = True
        return provider

    @pytest.fixture
    def orchestrator(self, mock_local_ai_provider):
        with patch('orchestrator.workflow_orchestrator.PlanningAgent'), \
             patch('orchestrator.workflow_orchestrator.EnhancedTestCreationAgent'), \
             patch('orchestrator.workflow_orchestrator.ReviewAgent'), \
             patch('orchestrator.workflow_orchestrator.ExecutionAgent'), \
             patch('orchestrator.workflow_orchestrator.ReportingAgent'):
            return WorkflowOrchestrator(local_ai_provider=mock_local_ai_provider)

    def test_create_custom_template(self, orchestrator):
        """Test creating a custom workflow template"""
        custom_template = {
            "name": "Custom API Test Workflow",
            "description": "Custom workflow for API testing",
            "steps": [
                {
                    "id": "step1",
                    "name": "Plan API Tests",
                    "agent_role": AgentRole.PLANNING,
                    "task_type": "create_plan",
                    "dependencies": []
                },
                {
                    "id": "step2",
                    "name": "Generate API Tests",
                    "agent_role": AgentRole.TEST_CREATION,
                    "task_type": "generate_tests",
                    "dependencies": ["step1"]
                }
            ]
        }

        result = orchestrator.create_custom_template("custom_api_test", custom_template)

        assert result == True
        assert "custom_api_test" in orchestrator.workflow_templates

    def test_create_invalid_template_missing_fields(self, orchestrator):
        """Test creating template with missing required fields"""
        invalid_template = {
            "name": "Invalid Template"
            # Missing description and steps
        }

        result = orchestrator.create_custom_template("invalid", invalid_template)

        assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
