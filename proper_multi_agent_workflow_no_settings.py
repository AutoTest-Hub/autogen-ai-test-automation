import asyncio
import json
from pathlib import Path
import argparse

from agents.planning_agent import PlanningAgent
from agents.test_creation_agent import EnhancedTestCreationAgent
from agents.execution_agent import ExecutionAgent
from agents.review_agent import ReviewAgent
from agents.reporting_agent import ReportingAgent
from agents.real_browser_discovery_agent_fixed import RealBrowserDiscoveryAgent

class ProperMultiAgentWorkflowNoSettings:
    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.test_creation_agent = EnhancedTestCreationAgent()
        self.execution_agent = ExecutionAgent()
        self.review_agent = ReviewAgent()
        self.reporting_agent = ReportingAgent()
        self.discovery_agent = RealBrowserDiscoveryAgent()

    async def run(self, requirements_path: str):
        with open(requirements_path, "r") as f:
            requirements = json.load(f)

        test_plan_result = await self.planning_agent.process_task({"requirements": requirements})
        discovery_result = await self.discovery_agent.discover_elements(requirements["application_url"])
        test_creation_result = await self.test_creation_agent.process_task(test_plan_result)
        execution_result = await self.execution_agent.process_task(test_creation_result)
        review_result = await self.review_agent.process_task(execution_result)
        await self.reporting_agent.process_task(review_result)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", required=True, help="Path to the requirements.json file")
    args = parser.parse_args()

    workflow = ProperMultiAgentWorkflowNoSettings()
    await workflow.run(args.requirements)

if __name__ == "__main__":
    asyncio.run(main())

