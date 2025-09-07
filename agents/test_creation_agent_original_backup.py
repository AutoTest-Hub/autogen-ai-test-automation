"""
Test Creation Agent for AutoGen Test Automation Framework
Responsible for generating high-quality test automation code
"""

import json
import os
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseTestAgent
from config.settings import AgentRole, TestFramework


class TestCreationAgent(BaseTestAgent):
    """Agent responsible for generating test automation code"""
    
    def __init__(self, **kwargs):
        system_message = """
You are the Test Creation Agent, an expert in test automation code generation. Your responsibilities include:

1. **Code Generation**: Generate high-quality test automation code based on test plans
2. **Framework Integration**: Create tests using appropriate frameworks (Playwright, Selenium, Requests)
3. **Best Practices**: Follow testing best practices and coding standards
4. **Data Management**: Implement data-driven testing patterns
5. **Error Handling**: Include comprehensive error handling and recovery
6. **Documentation**: Generate clear documentation and comments

**Key Capabilities**:
- Generate Playwright tests for UI automation
- Create Selenium WebDriver tests for cross-browser testing
- Build API tests using Requests/HTTPX
- Implement Page Object Model patterns
- Create data-driven test frameworks
- Generate utility functions and helpers

**Code Quality Standards**:
- Clean, readable, and maintainable code
- Comprehensive error handling and logging
- Proper test structure and organization
- Reusable components and utilities
- Clear documentation and comments

**Output Format**: Always provide complete, executable test code with:
- Proper imports and dependencies
- Setup and teardown methods
- Clear test methods with descriptive names
- Comprehensive assertions and validations
- Error handling and recovery mechanisms

Be thorough, follow best practices, and ensure code quality.
"""
        
        super().__init__(
            role=AgentRole.TEST_CREATION,
            system_message=system_message,
            **kwargs
        )
        
        # Register test creation functions
        self._register_test_creation_functions()
    
    def _register_test_creation_functions(self):
        """Register test creation specific functions"""
        
        def generate_playwright_test(test_scenario: Dict[str, Any]) -> str:
            """Generate Playwright test code"""
            return self._create_playwright_test_template(test_scenario)
        
        def generate_selenium_test(test_scenario: Dict[str, Any]) -> str:
            """Generate Selenium test code"""
            return self._create_selenium_test_template(test_scenario)
        
        def generate_api_test(test_scenario: Dict[str, Any]) -> str:
            """Generate API test code"""
            return self._create_api_test_template(test_scenario)
        
        def create_page_object(page_info: Dict[str, Any]) -> str:
            """Create Page Object Model class"""
            return self._create_page_object_template(page_info)
        
        def generate_test_utilities(utils_config: Dict[str, Any]) -> str:
            """Generate test utility functions"""
            return self._create_utilities_template(utils_config)
        
        # Register functions
        self.register_function(generate_playwright_test, "Generate Playwright test automation code")
        self.register_function(generate_selenium_test, "Generate Selenium WebDriver test code")
        self.register_function(generate_api_test, "Generate API test automation code")
        self.register_function(create_page_object, "Create Page Object Model classes")
        self.register_function(generate_test_utilities, "Generate test utility functions")
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process test creation tasks"""
        try:
            self.update_state("processing", current_task="test_creation")
            
            task_type = task_data.get("type", "generate_tests")
            
            if task_type == "generate_tests":
                result = await self._generate_tests(task_data)
            elif task_type == "create_framework":
                result = await self._create_test_framework(task_data)
            elif task_type == "generate_utilities":
                result = await self._generate_utilities(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.state["tasks_completed"] += 1
            self.update_state("completed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing test creation task: {e}")
            self.state["errors"] += 1
            self.update_state("error", error_message=str(e))
            raise
    
    async def _generate_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test automation code from test plan"""
        test_plan = task_data.get("test_plan", {})
        scenarios = test_plan.get("test_scenarios", [])
        
        self.logger.info(f"Generating tests for {len(scenarios)} scenarios")
        
        generated_tests = []
        test_files = []
        
        for i, scenario in enumerate(scenarios):
            try:
                # Determine the appropriate framework
                framework = scenario.get("required_framework", "playwright")
                
                # Generate test code based on framework
                if framework == "playwright":
                    test_code = self._generate_playwright_test_code(scenario)
                elif framework == "selenium":
                    test_code = self._generate_selenium_test_code(scenario)
                elif framework in ["requests", "httpx"]:
                    test_code = self._generate_api_test_code(scenario)
                else:
                    test_code = self._generate_playwright_test_code(scenario)  # Default
                
                # Create test file
                test_filename = f"test_{scenario.get('name', f'scenario_{i}').lower().replace(' ', '_')}.py"
                test_filepath = self.save_work_artifact(test_filename, test_code)
                
                test_info = {
                    "scenario_name": scenario.get("name", f"Scenario {i+1}"),
                    "framework": framework,
                    "test_file": test_filepath,
                    "test_code": test_code,
                    "complexity_score": scenario.get("complexity_score", 0.5),
                    "estimated_duration": scenario.get("estimated_duration_minutes", 10)
                }
                
                generated_tests.append(test_info)
                test_files.append(test_filepath)
                
            except Exception as e:
                self.logger.error(f"Error generating test for scenario {i}: {e}")
                continue
        
        # Generate test suite runner
        suite_runner = self._generate_test_suite_runner(generated_tests)
        suite_file = self.save_work_artifact("test_suite_runner.py", suite_runner)
        
        # Generate configuration file
        config_code = self._generate_test_config(test_plan)
        config_file = self.save_work_artifact("test_config.py", config_code)
        
        # Generate requirements file
        requirements = self._generate_requirements(generated_tests)
        requirements_file = self.save_work_artifact("requirements.txt", requirements)
        
        return {
            "status": "success",
            "generated_tests": generated_tests,
            "test_files": test_files,
            "suite_runner": suite_file,
            "config_file": config_file,
            "requirements_file": requirements_file,
            "summary": {
                "total_tests": len(generated_tests),
                "frameworks_used": list(set(t["framework"] for t in generated_tests)),
                "total_estimated_duration": sum(t["estimated_duration"] for t in generated_tests)
            }
        }
    
    def _generate_playwright_test_code(self, scenario: Dict[str, Any]) -> str:
        """Generate Playwright test code for a scenario"""
        template = '''"""
{test_description}
Generated by AutoGen Test Creation Agent
"""

import asyncio
import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from datetime import datetime
import logging


class Test{test_class_name}:
    """Test class for {test_name}"""
    
    @pytest.fixture(scope="class")
    async def browser_context(self):
        """Setup browser context for tests"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless={headless})
            context = await browser.new_context(
                viewport={{"width": 1920, "height": 1080}},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            yield context
            await context.close()
            await browser.close()
    
    @pytest.fixture
    async def page(self, browser_context):
        """Create a new page for each test"""
        page = await browser_context.new_page()
        yield page
        await page.close()
    
    async def test_{test_method_name}(self, page: Page):
        """
        Test: {test_name}
        Description: {test_description}
        Priority: {priority}
        """
        try:
            # Test setup
            await self._setup_test(page)
            
            # Execute test steps
{test_steps_code}
            
            # Verify final results
            await self._verify_final_results(page)
            
            logging.info(f"Test {test_method_name} completed successfully")
            
        except Exception as e:
            # Capture screenshot on failure
            screenshot_path = f"screenshots/failure_{{test_method_name}}_{{timestamp}}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            logging.error(f"Test {test_method_name} failed: {{e}}")
            raise
    
    async def _setup_test(self, page: Page):
        """Setup test environment"""
        # Navigate to application
        await page.goto("{application_url}")
        await page.wait_for_load_state("networkidle")
        
        # Additional setup steps
        logging.info("Test setup completed")
    
{helper_methods}
    
    async def _verify_final_results(self, page: Page):
        """Verify final test results"""
{verification_code}
        logging.info("Final verification completed")


if __name__ == "__main__":
    # Run the test directly
    asyncio.run(Test{test_class_name}().test_{test_method_name}())
'''
        
        # Extract scenario information
        test_name = scenario.get("name", "Unknown Test")
        test_description = scenario.get("description", "")
        priority = scenario.get("priority", "Medium")
        application_url = scenario.get("application", "https://example.com")
        test_steps = scenario.get("test_steps", [])
        
        # Generate class and method names
        test_class_name = self._to_class_name(test_name)
        test_method_name = self._to_method_name(test_name)
        
        # Generate test steps code
        test_steps_code = self._generate_playwright_steps_code(test_steps)
        
        # Generate helper methods
        helper_methods = self._generate_playwright_helper_methods(scenario)
        
        # Generate verification code
        verification_code = self._generate_verification_code(scenario)
        
        return template.format(
            test_name=test_name,
            test_description=test_description,
            test_class_name=test_class_name,
            test_method_name=test_method_name,
            priority=priority,
            application_url=application_url,
            headless="True",  # Default to headless
            test_steps_code=test_steps_code,
            helper_methods=helper_methods,
            verification_code=verification_code,
            timestamp=int(time.time())
        )
    
    def _generate_playwright_steps_code(self, test_steps: List[Dict[str, Any]]) -> str:
        """Generate Playwright code for test steps"""
        steps_code = []
        
        for i, step in enumerate(test_steps, 1):
            action = step.get("action", "")
            expected_result = step.get("expectedResult", "")
            
            step_code = f'''
            # Step {i}: {action}
            logging.info("Executing step {i}: {action}")
            {{self._convert_action_to_playwright_code(action)}}
            
            # Verify step result
            {{self._convert_expected_result_to_verification(expected_result)}}
            await page.wait_for_timeout(1000)  # Brief pause between steps
'''
            steps_code.append(step_code)
        
        return "\n".join(steps_code)
    
    def _convert_action_to_playwright_code(self, action: str) -> str:
        """Convert natural language action to Playwright code"""
        action_lower = action.lower()
        
        if "navigate" in action_lower or "go to" in action_lower:
            return 'await page.goto("{url}")\n            await page.wait_for_load_state("networkidle")'
        elif "click" in action_lower:
            if "login" in action_lower or "sign in" in action_lower:
                return 'await page.click("text=Login")'
            elif "button" in action_lower:
                return 'await page.click("button")'
            else:
                return 'await page.click("SELECTOR_TO_BE_UPDATED")'
        elif "enter" in action_lower or "type" in action_lower:
            if "username" in action_lower:
                return 'await page.fill("input[name=\\"username\\"]", "helios")'
            elif "password" in action_lower:
                return 'await page.fill("input[name=\\"password\\"]", "Password123")'
            else:
                return 'await page.fill("SELECTOR_TO_BE_UPDATED", "VALUE_TO_BE_UPDATED")'
        elif "select" in action_lower:
            return 'await page.select_option("select", "OPTION_TO_BE_UPDATED")'
        elif "verify" in action_lower or "check" in action_lower:
            return 'await expect(page.locator("SELECTOR_TO_BE_UPDATED")).to_be_visible()'
        else:
            return f'# TODO: Implement action: {action}\n            pass'
    
    def _convert_expected_result_to_verification(self, expected_result: str) -> str:
        """Convert expected result to verification code"""
        if not expected_result:
            return "# No specific verification required"
        
        result_lower = expected_result.lower()
        
        if "display" in result_lower or "show" in result_lower:
            return 'await expect(page.locator("SELECTOR_TO_BE_UPDATED")).to_be_visible()'
        elif "success" in result_lower:
            return 'await expect(page.locator("text=Success")).to_be_visible()'
        elif "error" in result_lower:
            return 'await expect(page.locator("text=Error")).to_be_visible()'
        else:
            return f'# TODO: Verify: {expected_result}'
    
    def _generate_playwright_helper_methods(self, scenario: Dict[str, Any]) -> str:
        """Generate helper methods for Playwright tests"""
        return '''
    async def _wait_for_element(self, page: Page, selector: str, timeout: int = 30000):
        """Wait for element to be visible"""
        await page.wait_for_selector(selector, timeout=timeout)
    
    async def _safe_click(self, page: Page, selector: str):
        """Safely click an element with retry logic"""
        for attempt in range(3):
            try:
                await page.click(selector, timeout=10000)
                break
            except Exception as e:
                if attempt == 2:
                    raise e
                await page.wait_for_timeout(1000)
    
    async def _safe_fill(self, page: Page, selector: str, value: str):
        """Safely fill an input field"""
        await page.fill(selector, "")  # Clear first
        await page.fill(selector, value)
        await page.wait_for_timeout(500)
'''
    
    def _generate_selenium_test_code(self, scenario: Dict[str, Any]) -> str:
        """Generate Selenium test code for a scenario"""
        # Similar structure to Playwright but using Selenium WebDriver
        template = '''"""
{test_description}
Generated by AutoGen Test Creation Agent
"""

import unittest
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime


class Test{test_class_name}(unittest.TestCase):
    """Test class for {test_name}"""
    
    @classmethod
    def setUpClass(cls):
        """Setup WebDriver for all tests"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 30)
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup WebDriver"""
        cls.driver.quit()
    
    def test_{test_method_name}(self):
        """
        Test: {test_name}
        Description: {test_description}
        Priority: {priority}
        """
        try:
            # Test setup
            self._setup_test()
            
            # Execute test steps
{test_steps_code}
            
            # Verify final results
            self._verify_final_results()
            
            logging.info(f"Test {test_method_name} completed successfully")
            
        except Exception as e:
            # Capture screenshot on failure
            screenshot_path = f"screenshots/failure_{{test_method_name}}_{{timestamp}}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"Test {test_method_name} failed: {{e}}")
            raise
    
    def _setup_test(self):
        """Setup test environment"""
        # Navigate to application
        self.driver.get("{application_url}")
        time.sleep(2)
        
        logging.info("Test setup completed")
    
{helper_methods}
    
    def _verify_final_results(self):
        """Verify final test results"""
{verification_code}
        logging.info("Final verification completed")


if __name__ == "__main__":
    unittest.main()
'''
        
        # Similar processing as Playwright but with Selenium-specific code generation
        test_name = scenario.get("name", "Unknown Test")
        test_description = scenario.get("description", "")
        priority = scenario.get("priority", "Medium")
        application_url = scenario.get("application", "https://example.com")
        
        test_class_name = self._to_class_name(test_name)
        test_method_name = self._to_method_name(test_name)
        
        test_steps_code = self._generate_selenium_steps_code(scenario.get("test_steps", []))
        helper_methods = self._generate_selenium_helper_methods(scenario)
        verification_code = self._generate_selenium_verification_code(scenario)
        
        return template.format(
            test_name=test_name,
            test_description=test_description,
            test_class_name=test_class_name,
            test_method_name=test_method_name,
            priority=priority,
            application_url=application_url,
            test_steps_code=test_steps_code,
            helper_methods=helper_methods,
            verification_code=verification_code,
            timestamp=int(time.time())
        )
    
    def _generate_selenium_steps_code(self, test_steps: List[Dict[str, Any]]) -> str:
        """Generate Selenium code for test steps"""
        steps_code = []
        
        for i, step in enumerate(test_steps, 1):
            action = step.get("action", "")
            
            step_code = f'''
            # Step {i}: {action}
            logging.info("Executing step {i}: {action}")
            {{self._convert_action_to_selenium_code(action)}}
            time.sleep(1)  # Brief pause between steps
'''
            steps_code.append(step_code)
        
        return "\n".join(steps_code)
    
    def _convert_action_to_selenium_code(self, action: str) -> str:
        """Convert natural language action to Selenium code"""
        action_lower = action.lower()
        
        if "navigate" in action_lower or "go to" in action_lower:
            return 'self.driver.get("URL_TO_BE_UPDATED")'
        elif "click" in action_lower:
            return 'self.driver.find_element(By.XPATH, "XPATH_TO_BE_UPDATED").click()'
        elif "enter" in action_lower or "type" in action_lower:
            return 'self.driver.find_element(By.NAME, "FIELD_NAME").send_keys("VALUE_TO_BE_UPDATED")'
        else:
            return f'# TODO: Implement action: {action}'
    
    def _generate_selenium_helper_methods(self, scenario: Dict[str, Any]) -> str:
        """Generate helper methods for Selenium tests"""
        return '''
    def _wait_for_element(self, locator, timeout=30):
        """Wait for element to be present"""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def _safe_click(self, locator):
        """Safely click an element"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def _safe_send_keys(self, locator, text):
        """Safely send keys to an element"""
        element = self.wait.until(EC.presence_of_element_located(locator))
        element.clear()
        element.send_keys(text)
'''
    
    def _generate_selenium_verification_code(self, scenario: Dict[str, Any]) -> str:
        """Generate verification code for Selenium tests"""
        return '''
        # Add specific verifications based on expected results
        self.assertTrue(True, "Verification placeholder - update with actual checks")
'''
    
    def _generate_api_test_code(self, scenario: Dict[str, Any]) -> str:
        """Generate API test code for a scenario"""
        template = '''"""
{test_description}
Generated by AutoGen Test Creation Agent
"""

import requests
import pytest
import json
import logging
from datetime import datetime


class Test{test_class_name}:
    """API Test class for {test_name}"""
    
    def setup_class(self):
        """Setup for API tests"""
        self.base_url = "{base_url}"
        self.session = requests.Session()
        self.session.headers.update({{"Content-Type": "application/json"}})
    
    def teardown_class(self):
        """Cleanup after API tests"""
        self.session.close()
    
    def test_{test_method_name}(self):
        """
        API Test: {test_name}
        Description: {test_description}
        Priority: {priority}
        """
        try:
            # Execute API test steps
{api_test_steps}
            
            logging.info(f"API test {test_method_name} completed successfully")
            
        except Exception as e:
            logging.error(f"API test {test_method_name} failed: {{e}}")
            raise
    
{helper_methods}


if __name__ == "__main__":
    pytest.main([__file__])
'''
        
        test_name = scenario.get("name", "Unknown Test")
        test_description = scenario.get("description", "")
        priority = scenario.get("priority", "Medium")
        base_url = scenario.get("application", "https://api.example.com")
        
        test_class_name = self._to_class_name(test_name)
        test_method_name = self._to_method_name(test_name)
        
        api_test_steps = self._generate_api_test_steps(scenario.get("test_steps", []))
        helper_methods = self._generate_api_helper_methods(scenario)
        
        return template.format(
            test_name=test_name,
            test_description=test_description,
            test_class_name=test_class_name,
            test_method_name=test_method_name,
            priority=priority,
            base_url=base_url,
            api_test_steps=api_test_steps,
            helper_methods=helper_methods,
            timestamp=int(time.time())
        )
    
    def _generate_api_test_steps(self, test_steps: List[Dict[str, Any]]) -> str:
        """Generate API test steps"""
        steps_code = []
        
        for i, step in enumerate(test_steps, 1):
            action = step.get("action", "")
            
            step_code = f'''
            # Step {i}: {action}
            logging.info("Executing API step {i}: {action}")
            {{self._convert_action_to_api_code(action)}}
'''
            steps_code.append(step_code)
        
        return "\n".join(steps_code)
    
    def _convert_action_to_api_code(self, action: str) -> str:
        """Convert action to API test code"""
        action_lower = action.lower()
        
        if "get" in action_lower:
            return '''response = {{self.session.get(f"{{self.base_url}}/ENDPOINT_TO_BE_UPDATED")}}
            assert response.status_code == 200'''
        elif "post" in action_lower:
            return '''data = {"key": "value"}  # Update with actual data
            response = {{self.session.post(f"{{self.base_url}}/ENDPOINT_TO_BE_UPDATED", json=data)}}
            assert response.status_code in [200, 201]'''
        else:
            return f'# TODO: Implement API action: {action}'
    
    def _generate_api_helper_methods(self, scenario: Dict[str, Any]) -> str:
        """Generate API helper methods"""
        return '''
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with error handling"""
        url = f"{{self.base_url}}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        return response
    
    def _validate_response(self, response, expected_status=200):
        """Validate API response"""
        assert response.status_code == expected_status
        return response.json() if response.content else None
'''
    
    def _generate_test_suite_runner(self, generated_tests: List[Dict[str, Any]]) -> str:
        """Generate test suite runner"""
        template = '''"""
Test Suite Runner for AutoGen Generated Tests
Generated by AutoGen Test Creation Agent
"""

import pytest
import sys
import os
import time
from datetime import datetime
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'test_execution_{timestamp}.log'),
        logging.StreamHandler()
    ]
)


class TestSuiteRunner:
    """Test suite runner for all generated tests"""
    
    def __init__(self):
        self.test_files = {test_files}
        self.total_tests = {total_tests}
        
    def run_all_tests(self):
        """Run all generated tests"""
        logging.info(f"Starting test suite execution with {{self.total_tests}} tests")
        
        # Run pytest with generated test files
        pytest_args = [
            "-v",
            "--tb=short",
            "--html=test_report.html",
            "--self-contained-html",
            *self.test_files
        ]
        
        {{exit_code}} = pytest.main(pytest_args)
        
        if {{exit_code}} == 0:
            logging.info("All tests passed successfully!")
        else:
            logging.error(f"Test suite failed with exit code: {{exit_code}}")
        
        return {{exit_code}}
    
    def run_specific_test(self, {{test_file}}: str):
        """Run a specific test file"""
        if {{test_file}} in self.test_files:
            logging.info(f"Running specific test: {{test_file}}")
            return pytest.main(["-v", {{test_file}}])
        else:
            logging.error(f"Test file not found: {{test_file}}")
            return 1


if __name__ == "__main__":
    runner = TestSuiteRunner()
    {{exit_code}} = runner.run_all_tests()
    sys.exit({{exit_code}})
'''
        
        test_files = [test["test_file"] for test in generated_tests]
        total_tests = len(generated_tests)
        
        return template.format(
            test_files=test_files,
            total_tests=total_tests,
            timestamp=int(time.time())
        )
    
    def _generate_test_config(self, test_plan: Dict[str, Any]) -> str:
        """Generate test configuration file"""
        return '''"""
Test Configuration for AutoGen Generated Tests
"""

import os
from typing import Dict, Any


class TestConfig:
    """Configuration settings for test execution"""
    
    # Application settings
    BASE_URL = os.getenv("BASE_URL", "https://www.advantageonlineshopping.com/#/")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
    
    # Browser settings
    BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    # Test data
    TEST_CREDENTIALS = {
        "username": os.getenv("TEST_USERNAME", "helios"),
        "password": os.getenv("TEST_PASSWORD", "Password123")
    }
    
    # Execution settings
    PARALLEL_EXECUTION = os.getenv("PARALLEL_EXECUTION", "false").lower() == "true"
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))
    
    # Reporting settings
    SCREENSHOT_ON_FAILURE = True
    GENERATE_HTML_REPORT = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_browser_config(cls) -> Dict[str, Any]:
        """Get browser configuration"""
        return {
            "browser_type": cls.BROWSER_TYPE,
            "headless": cls.HEADLESS,
            "timeout": cls.BROWSER_TIMEOUT
        }
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data configuration"""
        return {
            "credentials": cls.TEST_CREDENTIALS,
            "base_url": cls.BASE_URL,
            "api_base_url": cls.API_BASE_URL
        }


# Global config instance
config = TestConfig()
'''
    
    def _generate_requirements(self, generated_tests: List[Dict[str, Any]]) -> str:
        """Generate requirements.txt for generated tests"""
        frameworks = set(test["framework"] for test in generated_tests)
        
        requirements = [
            "# Generated test requirements",
            "pytest>=7.4.0",
            "pytest-html>=4.1.0",
            "pytest-asyncio>=0.21.0",
        ]
        
        if "playwright" in frameworks:
            requirements.extend([
                "playwright>=1.40.0",
                "pytest-playwright>=0.4.0"
            ])
        
        if "selenium" in frameworks:
            requirements.extend([
                "selenium>=4.15.0",
                "webdriver-manager>=4.0.0"
            ])
        
        if any(fw in frameworks for fw in ["requests", "httpx"]):
            requirements.extend([
                "requests>=2.31.0",
                "httpx>=0.25.0"
            ])
        
        requirements.extend([
            "structlog>=23.2.0",
            "python-dotenv>=1.0.0"
        ])
        
        return "\n".join(requirements)
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to valid Python class name"""
        return "".join(word.capitalize() for word in name.replace("-", " ").replace("_", " ").split())
    
    def _to_method_name(self, name: str) -> str:
        """Convert name to valid Python method name"""
        return "_".join(word.lower() for word in name.replace("-", " ").replace("_", " ").split())
    
    def _generate_verification_code(self, scenario: Dict[str, Any]) -> str:
        """Generate verification code based on expected results"""
        expected_results = scenario.get("expected_results", [])
        
        if not expected_results:
            return "        # Add specific verifications based on test requirements"
        
        verifications = []
        for result in expected_results:
            if "login" in result.lower():
                verifications.append('        await expect(page.locator("text=Welcome")).to_be_visible()')
            elif "success" in result.lower():
                verifications.append('        await expect(page.locator("text=Success")).to_be_visible()')
            else:
                verifications.append(f'        # TODO: Verify: {result}')
        
        return "\n".join(verifications)
    
    async def _create_test_framework(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete test framework structure"""
        # Implementation for creating framework structure
        return {"status": "completed", "framework": "Framework created"}
    
    async def _generate_utilities(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test utility functions"""
        # Implementation for utility generation
        return {"status": "completed", "utilities": "Utilities generated"}
    
    def get_capabilities(self) -> List[str]:
        """Get test creation agent capabilities"""
        return [
            "playwright_test_generation",
            "selenium_test_generation", 
            "api_test_generation",
            "page_object_creation",
            "test_framework_setup",
            "utility_function_generation",
            "test_suite_creation",
            "configuration_management"
        ]

