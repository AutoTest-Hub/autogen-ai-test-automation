import asyncio
import json
from agents.base_agent import BaseTestAgent

class PerformanceAgent(BaseTestAgent):
    def __init__(self, api_key=None, ollama_config=None):
        super().__init__(api_key, ollama_config)

    async def predict_performance_bottlenecks(self, requirements_config, test_results):
        try:
            prediction = await self.analyze_performance_data(requirements_config, test_results)
            return {"status": "success", "prediction": prediction}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def analyze_performance_data(self, requirements_config, test_results):
        prompt = f"""Analyze the following requirements and test results to predict performance bottlenecks.

        **Requirements Configuration:**
        ```json
        {json.dumps(requirements_config, indent=2)}
        ```

        **Test Results:**
        ```json
        {json.dumps(test_results, indent=2)}
        ```

        **Performance Prediction:**
        1.  **Identify Slow Areas**: Pinpoint areas of the application with slow performance.
        2.  **Predict Bottlenecks**: Predict potential bottlenecks under load.
        3.  **Recommend Optimizations**: Suggest specific optimizations to improve performance.
        4.  **Confidence Score**: Assign a confidence score from 0.0 to 1.0.

        **Return JSON:**
        {{ 
            "slow_areas": ["..."],
            "predicted_bottlenecks": ["..."],
            "recommendations": ["..."],
            "confidence_score": 0.0-1.0
        }}
        """
        response = await self.get_completion(prompt)
        return json.loads(response)

    def get_capabilities(self):
        return {
            "name": "performance_agent",
            "description": "Predicts performance bottlenecks using AI.",
            "methods": {
                "predict_performance_bottlenecks": {
                    "description": "Analyzes test results to predict performance issues.",
                    "parameters": {
                        "requirements_config": "dict",
                        "test_results": "dict"
                    }
                }
            }
        }

