import asyncio
import json
from pathlib import Path

from agents.planning_agent import PlanningAgent
from agents.test_creation_agent import EnhancedTestCreationAgent
from agents.execution_agent import ExecutionAgent
from agents.review_agent import ReviewAgent
from agents.reporting_agent import ReportingAgent
from agents.real_browser_discovery_agent_fixed import RealBrowserDiscoveryAgent

class ProperMultiAgentWorkflow:
    def __init__(self, planning_agent=None, test_creation_agent=None, execution_agent=None, review_agent=None, reporting_agent=None, discovery_agent=None):
        self.planning_agent = planning_agent or PlanningAgent()
        self.test_creation_agent = test_creation_agent or EnhancedTestCreationAgent()
        self.execution_agent = execution_agent or ExecutionAgent()
        self.review_agent = review_agent or ReviewAgent()
        self.reporting_agent = reporting_agent or ReportingAgent()
        self.discovery_agent = discovery_agent or RealBrowserDiscoveryAgent()

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
    workflow = ProperMultiAgentWorkflow()
    await workflow.run("requirements.json")

if __name__ == "__main__":
    asyncio.run(main())

