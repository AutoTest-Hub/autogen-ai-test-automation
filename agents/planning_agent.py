import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseTestAgent

class PlanningAgent(BaseTestAgent):
    def __init__(self, **kwargs):
        super().__init__(
            role="planning",
            system_message="You are the Planning Agent...",
            **kwargs
        )

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._create_test_plan(task_data)

    async def _create_test_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        requirements = task_data.get("requirements", {})
        test_cases = requirements.get("test_cases", [])

        test_scenarios = []
        for test_case in test_cases:
            scenario = {
                "name": test_case.lower().replace(" ", "_"),
                "description": test_case,
            }
            test_scenarios.append(scenario)

        test_plan = {
            "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "test_scenarios": test_scenarios,
        }

        return {
            "status": "success",
            "test_plan": test_plan,
        }

