import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
import asyncio

from proper_multi_agent_workflow import ProperMultiAgentWorkflow

class TestE2EWorkflow(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("test_e2e_workflow_temp")
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

    @patch("proper_multi_agent_workflow.PlanningAgent")
    @patch("proper_multi_agent_workflow.TestCreationAgent")
    @patch("proper_multi_agent_workflow.ExecutionAgent")
    @patch("proper_multi_agent_workflow.ReviewAgent")
    @patch("proper_multi_agent_workflow.ReportingAgent")
    def test_e2e_workflow_with_mocks(self, mock_reporting_agent, mock_review_agent, mock_execution_agent, mock_test_creation_agent, mock_planning_agent):
        # Arrange
        mock_planning_agent.return_value.process_task.return_value = {
            "test_plan": {
                "test_scenarios": [
                    {
                        "name": "test_login_functionality_with_valid_credentials",
                        "steps": ["Navigate to the login page", "Enter valid credentials", "Click the login button"],
                        "validations": ["Verify that the user is redirected to the dashboard"]
                    }
                ]
            }
        }
        mock_test_creation_agent.return_value.process_task.return_value = {
            "generated_files": [
                {
                    "path": str(self.test_dir / "test_login.py"),
                    "content": "def test_login():\n    assert True"
                }
            ]
        }
        mock_execution_agent.return_value.process_task.return_value = {
            "results": [
                {
                    "test_file": "test_login.py",
                    "status": "passed"
                }
            ]
        }

        workflow = ProperMultiAgentWorkflow(
            planning_agent=mock_planning_agent(),
            test_creation_agent=mock_test_creation_agent(),
            execution_agent=mock_execution_agent(),
            review_agent=mock_review_agent(),
            reporting_agent=mock_reporting_agent()
        )

        # Act
        async def run_workflow():
            await workflow.run(str(self.requirements_path))

        asyncio.run(run_workflow())

        # Assert
        mock_planning_agent.return_value.process_task.assert_called_once()
        mock_test_creation_agent.return_value.process_task.assert_called_once()
        mock_execution_agent.return_value.process_task.assert_called_once()
        mock_review_agent.return_value.process_task.assert_called_once()
        mock_reporting_agent.return_value.process_task.assert_called_once()

if __name__ == "__main__":
    unittest.main()

