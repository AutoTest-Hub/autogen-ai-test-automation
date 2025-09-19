#!/usr/bin/env python3
"""
Test Create Test Plan
=====================
This script tests the `_create_test_plan` method of the `ProperMultiAgentWorkflow` class,
ensuring that the `requirements.json` file is correctly parsed and used to generate a test plan.
"""

import asyncio
import json
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

# Since we are testing the workflow, we need to mock the agents
# to prevent them from actually running.
class MockAgent:
    def __init__(self, *args, **kwargs):
        pass
    async def process_task(self, *args, **kwargs):
        return {}

with patch.dict("sys.modules", {
    "agents.planning_agent": MagicMock(PlanningAgent=MockAgent),
    "agents.real_browser_discovery_agent_fixed": MagicMock(RealBrowserDiscoveryAgent=MockAgent),
    "agents.test_creation_agent": MagicMock(EnhancedTestCreationAgent=MockAgent),
    "agents.review_agent": MagicMock(ReviewAgent=MockAgent),
    "agents.execution_agent": MagicMock(ExecutionAgent=MockAgent),
    "agents.reporting_agent": MagicMock(ReportingAgent=MockAgent),
    "models.local_ai_provider": MagicMock(),
    "config.settings": MagicMock(),
}):
    from proper_multi_agent_workflow import ProperMultiAgentWorkflow

    class TestCreateTestPlan(unittest.TestCase):
        @patch("proper_multi_agent_workflow.Path")
        @patch("builtins.open")
        def test_create_test_plan_with_requirements(self, mock_open, mock_path):
            """Test that `_create_test_plan` correctly processes `requirements.json`."""
            # Mock requirements.json
            mock_requirements_json = {
                "application_url": "https://example.com",
                "test_scenarios": [
                    {
                        "name": "Test Scenario from requirements.json",
                        "steps": ["Do something"]
                    }
                ]
            }
            mock_path.return_value.exists.return_value = True
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_requirements_json)

            # Mock planning agent
            mock_planning_agent = AsyncMock()
            mock_planning_agent.process_task.return_value = mock_requirements_json

            # Instantiate workflow with mock agent
            workflow = ProperMultiAgentWorkflow(planning_agent=mock_planning_agent)

            # Run the method
            test_plan = asyncio.run(workflow._create_test_plan("https://example.com", "Example"))

            # Assertions
            mock_planning_agent.process_task.assert_called_once()
            call_args = mock_planning_agent.process_task.call_args[0][0]
            self.assertEqual(call_args["requirements_json"], mock_requirements_json)
            self.assertEqual(test_plan, mock_requirements_json)

if __name__ == "__main__":
    unittest.main()

