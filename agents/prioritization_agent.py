import asyncio
import json
from agents.base_agent import BaseAgent

class PrioritizationAgent(BaseAgent):
    def __init__(self, api_key=None, ollama_config=None):
        super().__init__(api_key, ollama_config)

    async def prioritize_tests(self, test_files, requirements_config):
        try:
            test_priorities = []
            for test_file in test_files:
                with open(test_file, 'r') as f:
                    test_code = f.read()
                
                priority_analysis = await self.analyze_test_priority(test_code, requirements_config)
                test_priorities.append({
                    "test_file": test_file,
                    "priority": priority_analysis.get("priority", "Medium"),
                    "score": priority_analysis.get("score", 0.5),
                    "rationale": priority_analysis.get("rationale", "N/A")
                })
            
            # Sort tests by score in descending order
            sorted_tests = sorted(test_priorities, key=lambda x: x["score"], reverse=True)
            return {"status": "success", "prioritized_tests": sorted_tests}

        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def analyze_test_priority(self, test_code, requirements_config):
        prompt = f"""Analyze the following Playwright test and requirements configuration to determine its priority.

        **Test Code:**
        ```python
        {test_code}
        ```

        **Requirements Configuration:**
        ```json
        {json.dumps(requirements_config, indent=2)}
        ```

        **Priority Analysis:**
        1.  **Business Criticality**: How critical is this test to the business? (High/Medium/Low)
        2.  **Risk Factor**: What is the risk of this feature failing? (High/Medium/Low)
        3.  **User Impact**: How much does this feature impact users? (High/Medium/Low)
        4.  **Complexity**: How complex is the test? (High/Medium/Low)
        5.  **Priority Score**: Assign a score from 0.0 to 1.0 (1.0 being highest priority).

        **Return JSON:**
        {{ "priority": "High/Medium/Low", "score": 0.0-1.0, "rationale": "..." }}
        """
        response = await self.get_completion(prompt)
        return json.loads(response)

    def get_capabilities(self):
        return {
            "name": "prioritization_agent",
            "description": "Prioritizes tests based on business criticality, risk, and user impact.",
            "methods": {
                "prioritize_tests": {
                    "description": "Analyzes and prioritizes a list of test files.",
                    "parameters": {
                        "test_files": "list",
                        "requirements_config": "dict"
                    }
                }
            }
        }

