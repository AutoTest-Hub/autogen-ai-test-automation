import asyncio
import json
from agents.base_agent import BaseTestAgent

class CrossBrowserAgent(BaseTestAgent):
    def __init__(self, api_key=None, ollama_config=None):
        super().__init__(api_key, ollama_config)

    async def generate_cross_browser_plan(self, requirements_config):
        try:
            plan = await self.analyze_browser_requirements(requirements_config)
            return {"status": "success", "plan": plan}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def analyze_browser_requirements(self, requirements_config):
        prompt = f"""Analyze the following requirements configuration to generate a cross-browser testing plan.

        **Requirements Configuration:**
        ```json
        {json.dumps(requirements_config, indent=2)}
        ```

        **Cross-Browser Testing Plan:**
        1.  **Target Browsers**: Identify the most important browsers to test (e.g., Chrome, Firefox, Safari, Edge).
        2.  **Device Types**: Recommend device types (e.g., desktop, mobile, tablet).
        3.  **Test Scope**: Suggest which tests are most critical for cross-browser validation.
        4.  **Rationale**: Explain the reasoning behind the recommendations.

        **Return JSON:**
        {{ 
            "target_browsers": ["chrome", "firefox", ...],
            "device_types": ["desktop", "mobile"],
            "critical_tests": ["test_login.py", "test_checkout.py", ...],
            "rationale": "..."
        }}
        """
        response = await self.get_completion(prompt)
        return json.loads(response)

    def get_capabilities(self):
        return {
            "name": "cross_browser_agent",
            "description": "Generates intelligent cross-browser testing plans.",
            "methods": {
                "generate_cross_browser_plan": {
                    "description": "Analyzes requirements to create a cross-browser testing plan.",
                    "parameters": {
                        "requirements_config": "dict"
                    }
                }
            }
        }

