"""
Mock AI Provider for testing
"""

import logging
from typing import Dict, Any, Optional
from .local_ai_provider import LocalAIProvider, ModelType

class MockAIProvider(LocalAIProvider):
    """
    Mock AI Provider for testing purposes
    Simulates responses without requiring actual Ollama service
    """
    
    def __init__(self):
        """Initialize the mock AI provider"""
        # Skip parent initialization to avoid checking for Ollama service
        self.base_url = "mock://localhost"
        self.available_models = {
            "tinyllama:latest": {"name": "tinyllama:latest"},
            "phi3:mini": {"name": "phi3:mini"}
        }
        self.model_configs = self._initialize_model_configs()
        logging.info("Initialized MockAIProvider")
    
    def _check_service_status(self) -> bool:
        """Mock service status check"""
        return True
    
    def is_available(self) -> bool:
        """Mock availability check"""
        return True
    
    async def generate_response_async(self, 
                                    prompt: str, 
                                    model_type: ModelType,
                                    system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate mock AI response (async version)
        
        Args:
            prompt: User prompt for the AI model
            model_type: Type of model to use based on agent role
            system_prompt: Optional system prompt for context
            
        Returns:
            Dictionary containing mock response and metadata
        """
        config = self.model_configs.get(model_type)
        model_to_use = config.ollama_model if config else "mock-model"
        
        # Generate mock response based on model type
        if model_type == ModelType.CODE_GENERATION:
            response = self._generate_mock_code_response(prompt)
        elif model_type == ModelType.PLANNING:
            response = self._generate_mock_planning_response(prompt)
        else:
            response = f"Mock response for {model_type.value}: {prompt[:50]}..."
        
        return {
            "response": response,
            "model": model_to_use,
            "model_type": model_type.value,
            "response_time": 0.1,
            "tokens_generated": len(response.split()),
            "success": True,
            "metadata": {
                "temperature": config.temperature if config else 0.7,
                "max_tokens": config.max_tokens if config else 1024,
                "actual_model": model_to_use,
                "requested_model": model_to_use,
                "mock": True
            }
        }
    
    def generate_response_sync(self, 
                              prompt: str, 
                              model_type: ModelType,
                              system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate mock AI response (sync version)
        
        Args:
            prompt: User prompt for the AI model
            model_type: Type of model to use based on agent role
            system_prompt: Optional system prompt for context
            
        Returns:
            Dictionary containing mock response and metadata
        """
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.generate_response_async(prompt, model_type, system_prompt)
            )
        finally:
            loop.close()
    
    def _generate_mock_code_response(self, prompt: str) -> str:
        """Generate mock code response"""
        if "login" in prompt.lower():
            return """```python
async def test_login(page):
    # Navigate to login page
    await page.goto("https://example.com/login")
    
    # Fill login form
    await page.fill("#username", "testuser")
    await page.fill("#password", "password123")
    
    # Submit form
    await page.click("#loginBtn")
    
    # Wait for navigation
    await page.wait_for_load_state("networkidle")
    
    # Verify successful login
    assert await page.is_visible(".welcome-message"), "Login failed"
```"""
        elif "search" in prompt.lower():
            return """```python
async def test_search(page):
    # Navigate to search page
    await page.goto("https://example.com/search")
    
    # Enter search query
    await page.fill("#searchInput", "test query")
    
    # Submit search
    await page.click("#searchBtn")
    
    # Wait for results
    await page.wait_for_selector(".search-results")
    
    # Verify results are displayed
    results_count = await page.text_content(".results-count")
    assert "results found" in results_count, "No search results displayed"
```"""
        else:
            return """```python
async def test_example(page):
    # Navigate to page
    await page.goto("https://example.com")
    
    # Perform action
    await page.click(".action-button")
    
    # Wait for response
    await page.wait_for_selector(".response")
    
    # Verify result
    assert await page.is_visible(".success"), "Action failed"
```"""
    
    def _generate_mock_planning_response(self, prompt: str) -> str:
        """Generate mock planning response"""
        return """Test Plan:
1. Setup test environment
2. Navigate to application
3. Test login functionality
4. Test search functionality
5. Test checkout process
6. Verify results
7. Cleanup test environment"""

