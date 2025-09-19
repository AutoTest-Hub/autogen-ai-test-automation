import unittest
import asyncio
import time
from unittest.mock import MagicMock

from proper_multi_agent_workflow import ProperMultiAgentWorkflow

class TestPerformance(unittest.TestCase):

    def test_concurrent_requests(self):
        # Arrange
        workflow = ProperMultiAgentWorkflow(
            planning_agent=MagicMock(),
            test_creation_agent=MagicMock(),
            execution_agent=MagicMock(),
            review_agent=MagicMock(),
            reporting_agent=MagicMock()
        )

        async def run_workflow():
            await workflow.run("requirements.json")

        # Act
        start_time = time.time()
        async def run_concurrently():
            tasks = [run_workflow() for _ in range(10)]
            await asyncio.gather(*tasks)
        asyncio.run(run_concurrently())
        end_time = time.time()

        # Assert
        self.assertLess(end_time - start_time, 60)  # Assert that 10 requests take less than 60 seconds

if __name__ == "__main__":
    unittest.main()

