import asyncio
import json
from agents.base_agent import BaseAgent
from utils.intelligent_flow_handler import IntelligentFlowHandler
from utils.step_generator import create_intelligent_steps

class SelfHealingAgent(BaseAgent):
    def __init__(self, api_key=None, ollama_config=None):
        super().__init__(api_key, ollama_config)
        self.flow_handler = IntelligentFlowHandler(self.get_llm_config())

    async def analyze_and_heal(self, test_file_path, error_log):
        try:
            with open(test_file_path, 'r') as f:
                test_code = f.read()

            analysis = await self.analyze_error(test_code, error_log)
            if not analysis or not analysis.get("is_fixable"):
                return {"status": "unfixable", "reason": analysis.get("reason", "Unknown")}

            healing_strategy = await self.generate_healing_strategy(test_code, error_log, analysis)
            if not healing_strategy:
                return {"status": "failed", "reason": "Could not generate healing strategy"}

            healed_code = await self.apply_healing_strategy(test_code, healing_strategy)
            if not healed_code:
                return {"status": "failed", "reason": "Could not apply healing strategy"}

            with open(test_file_path, 'w') as f:
                f.write(healed_code)

            return {"status": "healed", "file_path": test_file_path}

        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def analyze_error(self, test_code, error_log):
        prompt = f"""Analyze the following Playwright test code and error log to determine if the error is fixable.

        **Test Code:**
        ```python
        {test_code}
        ```

        **Error Log:**
        ```
        {error_log}
        ```

        **Analysis:**
        1.  **Error Type**: Identify the type of error (e.g., SelectorNotFound, TimeoutError, AssertionFailed).
        2.  **Root Cause**: Determine the likely root cause (e.g., UI change, dynamic element, timing issue).
        3.  **Fixability**: Assess if the error can be fixed programmatically (True/False).
        4.  **Reason**: Explain why it is or isn't fixable.

        **Return JSON:**
        {{ "error_type": "...", "root_cause": "...", "is_fixable": true/false, "reason": "..." }}
        """
        response = await self.get_completion(prompt)
        return json.loads(response)

    async def generate_healing_strategy(self, test_code, error_log, analysis):
        prompt = f"""Generate a healing strategy for the following Playwright test code based on the error analysis.

        **Test Code:**
        ```python
        {test_code}
        ```

        **Error Log:**
        ```
        {error_log}
        ```

        **Error Analysis:**
        {json.dumps(analysis, indent=2)}

        **Healing Strategy:**
        1.  **Identify Broken Line(s)**: Pinpoint the exact line(s) of code causing the error.
        2.  **Propose Changes**: Suggest specific code modifications (e.g., update selector, add wait condition, improve assertion).
        3.  **Explain Rationale**: Justify why the proposed changes will fix the error.

        **Return JSON:**
        {{ "broken_lines": [line_number, ...], "proposed_changes": [{{ "line": line_number, "new_code": "..." }}, ...], "rationale": "..." }}
        """
        response = await self.get_completion(prompt)
        return json.loads(response)

    async def apply_healing_strategy(self, test_code, healing_strategy):
        lines = test_code.split('\n')
        for change in healing_strategy.get("proposed_changes", []):
            line_number = change.get("line")
            new_code = change.get("new_code")
            if line_number and new_code:
                lines[line_number - 1] = new_code
        return '\n'.join(lines)

    def get_capabilities(self):
        return {
            "name": "self_healing_agent",
            "description": "Analyzes and heals broken Playwright tests automatically.",
            "methods": {
                "analyze_and_heal": {
                    "description": "Analyzes a broken test and applies a healing strategy.",
                    "parameters": {
                        "test_file_path": "string",
                        "error_log": "string"
                    }
                }
            }
        }

