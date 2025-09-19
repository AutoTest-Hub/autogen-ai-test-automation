
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

# Mock the agents before importing the workflow
mock_planning_agent = AsyncMock()
mock_test_creation_agent = AsyncMock()
mock_execution_agent = AsyncMock()
mock_review_agent = AsyncMock()
mock_reporting_agent = AsyncMock()
mock_discovery_agent = AsyncMock()

modules = {
    "agents.planning_agent": mock_planning_agent,
    "agents.test_creation_agent": mock_test_creation_agent,
    "agents.execution_agent": mock_execution_agent,
    "agents.review_agent": mock_review_agent,
    "agents.reporting_agent": mock_reporting_agent,
    "agents.real_browser_discovery_agent_fixed": mock_discovery_agent,
}

with patch.dict("sys.modules", modules):
    from proper_multi_agent_workflow_no_settings import ProperMultiAgentWorkflowNoSettings

class TestErrorHandling(unittest.TestCase):

    def test_agent_failure(self):
        # Arrange
        mock_planning_agent.process_task.side_effect = Exception("Test Exception")

        workflow = ProperMultiAgentWorkflowNoSettings()

        # Act & Assert
        with self.assertRaises(Exception):
            async def run_workflow():
                await workflow.run("requirements.json")

            asyncio.run(run_workflow())

if __name__ == "__main__":
    unittest.main()

