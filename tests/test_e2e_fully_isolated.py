import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import json
from pathlib import Path

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
    from proper_multi_agent_workflow import ProperMultiAgentWorkflow

class TestE2EFullyIsolated(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("test_e2e_fully_isolated_temp")
        self.test_dir.mkdir(exist_ok=True)

        self.requirements_path = self.test_dir / "requirements.json"
        self.requirements_data = {
            "application_url": "http://testapp.com",
            "test_cases": [
                "Test the login functionality with valid credentials."
            ]
        }
        with open(self.requirements_path, "w") as f:
            json.dump(self.requirements_data, f)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def test_e2e_fully_isolated(self):
        # Arrange
        workflow = ProperMultiAgentWorkflow(
            planning_agent=mock_planning_agent,
            test_creation_agent=mock_test_creation_agent,
            execution_agent=mock_execution_agent,
            review_agent=mock_review_agent,
            reporting_agent=mock_reporting_agent,
            discovery_agent=mock_discovery_agent
        )

        # Act
        async def run_workflow():
            await workflow.run(str(self.requirements_path))

        asyncio.run(run_workflow())

        # Assert
        mock_planning_agent.process_task.assert_called_once()
        mock_test_creation_agent.process_task.assert_called_once()
        mock_execution_agent.process_task.assert_called_once()
        mock_review_agent.process_task.assert_called_once()
        mock_reporting_agent.process_task.assert_called_once()
        mock_discovery_agent.discover_elements.assert_called_once()


if __name__ == "__main__":
    unittest.main()
