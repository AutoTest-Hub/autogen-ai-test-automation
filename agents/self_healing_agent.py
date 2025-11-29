import json
import logging
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseTestAgent
from config.settings import AgentRole

class SelfHealingAgent(BaseTestAgent):
    """
    Self-Healing Agent that analyzes test failures and attempts to fix them automatically.
    """
    
    def __init__(self, local_ai_provider=None):
        super().__init__(
            role=AgentRole.EXECUTION,  # It works closely with execution
            name="SelfHealingAgent",
            system_message="You are a Self-Healing Agent capable of analyzing Playwright test failures and generating code fixes.",
            local_ai_provider=local_ai_provider
        )
        
        # Register functions
        self.register_function(self.analyze_and_heal, "Analyze and heal broken tests")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process self-healing task"""
        task_type = task_data.get("task_type", "heal_test")
        
        if task_type == "heal_test":
            test_file = task_data.get("test_file")
            error_log = task_data.get("error_log")
            if not test_file or not error_log:
                return {"status": "error", "error": "Missing test_file or error_log"}
            
            return await self.analyze_and_heal(test_file, error_log)
        else:
            return {"status": "error", "error": f"Unknown task type: {task_type}"}

    def get_capabilities(self) -> List[str]:
        return ["analyze_and_heal", "error_analysis", "code_repair"]

    async def analyze_and_heal(self, test_file_path: str, error_log: str) -> Dict[str, Any]:
        """Analyze a broken test and apply a healing strategy."""
        try:
            self.update_state("analyzing")
            
            # Read the broken test file
            try:
                with open(test_file_path, 'r') as f:
                    test_code = f.read()
            except FileNotFoundError:
                return {"status": "error", "reason": f"File not found: {test_file_path}"}

            # 1. Analyze the error
            analysis = await self._analyze_error(test_code, error_log)
            if not analysis or not analysis.get("is_fixable"):
                reason = analysis.get("reason", "Unknown or unfixable error") if analysis else "Analysis failed"
                return {
                    "status": "unfixable", 
                    "reason": reason,
                    "analysis": analysis
                }

            # 2. Generate healing strategy
            healing_strategy = await self._generate_healing_strategy(test_code, error_log, analysis)
            if not healing_strategy:
                return {"status": "failed", "reason": "Could not generate healing strategy"}

            # 3. Apply the fix
            healed_code = self._apply_healing_strategy(test_code, healing_strategy)
            if not healed_code:
                return {"status": "failed", "reason": "Could not apply healing strategy"}

            # 4. Save the fixed code
            # We save to a new file first to avoid overwriting if it's garbage
            # But for true self-healing, we might want to overwrite or create a _fixed.py version
            # For now, let's overwrite but keep a backup
            backup_path = f"{test_file_path}.bak"
            with open(backup_path, 'w') as f:
                f.write(test_code)
            
            with open(test_file_path, 'w') as f:
                f.write(healed_code)

            self.update_state("healed")
            return {
                "status": "healed", 
                "file_path": test_file_path,
                "backup_path": backup_path,
                "changes": healing_strategy.get("proposed_changes", [])
            }

        except Exception as e:
            self.logger.error(f"Self-healing failed: {e}")
            return {"status": "error", "reason": str(e)}

    async def _analyze_error(self, test_code: str, error_log: str) -> Dict[str, Any]:
        """Use LLM to analyze the error."""
        prompt = f"""Analyze the following Playwright test code and error log to determine if the error is fixable.

Test Code:
```python
{test_code}
```

Error Log:
```
{error_log}
```

Analysis Requirements:
1. Identify the Error Type (e.g., SelectorNotFound, TimeoutError).
2. Determine the Root Cause (e.g., selector changed, element not ready).
3. Assess Fixability (Can we fix it by changing the code?).
4. Explain the Reason.

Return ONLY a JSON object with this structure:
{{
    "error_type": "string",
    "root_cause": "string",
    "is_fixable": boolean,
    "reason": "string"
}}
"""
        response = await self.generate_llm_response(prompt, response_format="json")
        if response["success"]:
            return response["response"] if isinstance(response["response"], dict) else json.loads(response["response"])
        return None

    async def _generate_healing_strategy(self, test_code: str, error_log: str, analysis: Dict) -> Dict[str, Any]:
        """Use LLM to generate a fix."""
        prompt = f"""Generate a healing strategy for the broken Playwright test.

Test Code:
```python
{test_code}
```

Error Log:
```
{error_log}
```

Error Analysis:
{json.dumps(analysis, indent=2)}

Task:
1. Identify the exact lines of code that need changing.
2. Provide the NEW code for those lines.
3. Explain why this fixes the issue.

Return ONLY a JSON object with this structure:
{{
    "proposed_changes": [
        {{
            "original_code_snippet": "exact string of code to replace",
            "new_code": "the corrected code",
            "line_number_hint": int (optional)
        }}
    ],
    "rationale": "string"
}}
"""
        response = await self.generate_llm_response(prompt, response_format="json")
        if response["success"]:
            return response["response"] if isinstance(response["response"], dict) else json.loads(response["response"])
        return None

    def _apply_healing_strategy(self, test_code: str, healing_strategy: Dict) -> str:
        """Apply the changes to the code string."""
        healed_code = test_code
        changes = healing_strategy.get("proposed_changes", [])
        
        # Sort changes by length of original snippet (descending) to avoid partial replacements issues
        # though simple string replace might be risky if snippets are not unique.
        # A better approach is line-based if we trust the LLM's line numbers, but LLMs are bad at counting.
        # Let's try unique string replacement first.
        
        for change in changes:
            original = change.get("original_code_snippet")
            new = change.get("new_code")
            if original and new and original in healed_code:
                healed_code = healed_code.replace(original, new)
            else:
                self.logger.warning(f"Could not find code snippet to replace: {original}")
        
        return healed_code
