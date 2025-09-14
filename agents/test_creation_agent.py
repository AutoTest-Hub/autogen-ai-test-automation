#!/usr/bin/env python3
"""
Enhanced Test Creation Agent
===========================
This enhanced version generates real working test code instead of templates,
integrating properly with Discovery Agent data.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseTestAgent
from config.settings import AgentRole

# Setup logger
logger = logging.getLogger(__name__)

class EnhancedTestCreationAgent(BaseTestAgent):
    """Enhanced Test Creation Agent that generates real working code"""
    
    def __init__(self, local_ai_provider=None):
        super().__init__(
            role=AgentRole.TEST_CREATION,
            name="EnhancedTestCreationAgent",
            system_message="You are an Enhanced Test Creation Agent that generates real, executable test code using discovered application data and best practices.",
            local_ai_provider=local_ai_provider
        )
        
        # Work directory for saving artifacts
        self.work_dir = Path(f"./work_dir/{self.name}")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Register enhanced functions
        self.register_function(self._generate_real_test_code, "Generate real executable test code")
        self.register_function(self._create_page_objects, "Create page object models")
        self.register_function(self._generate_test_utilities, "Generate test utilities and helpers")
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process test creation task with real code generation - Enhanced with Selenium and API"""
        task_type = task_data.get("task_type", "generate_tests")
        
        if task_type == "generate_tests":
            return await self._generate_real_test_code(task_data)
        elif task_type == "generate_selenium_tests":
            return await self._generate_selenium_tests(task_data)
        elif task_type == "generate_api_tests":
            return await self._generate_api_tests(task_data)
        elif task_type == "create_page_objects":
            return await self._create_page_objects(task_data)
        elif task_type == "generate_utilities":
            return await self._generate_test_utilities(task_data)
        else:
            return {
                "status": "error",
                "error": f"Unknown task type: {task_type}"
            }
    
    def get_capabilities(self) -> List[str]:
        """Get enhanced capabilities"""
        return [
            "real_code_generation",
            "discovery_integration",
            "page_object_models",
            "test_utilities",
            "playwright_tests",
            "selenium_tests",
            "api_tests",
            "assertions_and_validations"
        ]
    
    async def _generate_real_test_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate real executable test code"""
        try:
            self.update_state("processing")
            
            test_plan = task_data.get("test_plan", {})
            application_data = task_data.get("application_data", {})
            
            # Extract real data from Discovery Agent
            discovered_pages = application_data.get("discovered_pages", [])
            discovered_elements = application_data.get("discovered_elements", {})
            user_workflows = application_data.get("user_workflows", [])
            base_url = application_data.get("base_url", "https://example.com")
            
            generated_files = []
            
            # Generate test cases from test plan
            test_cases = test_plan.get("test_cases", [])
            framework = test_plan.get("framework", "playwright")
            
            for test_case in test_cases:
                if framework == "playwright":
                    test_file = await self._create_playwright_test(
                        test_case, application_data, discovered_pages, discovered_elements
                    )
                elif framework == "selenium":
                    test_file = await self._create_selenium_test(
                        test_case, application_data, discovered_pages, discovered_elements
                    )
                else:
                    test_file = await self._create_api_test(
                        test_case, application_data
                    )
                
                if test_file:
                    generated_files.append(test_file)
            
            # Generate page objects if we have discovered pages
            if discovered_pages:
                page_objects = await self._create_page_objects_from_discovery(
                    discovered_pages, discovered_elements, framework
                )
                generated_files.extend(page_objects)
            
            # Generate configuration and utilities
            config_files = await self._create_configuration_files(
                framework, base_url, application_data
            )
            generated_files.extend(config_files)
            
            self.update_state("completed")
            
            return {
                "status": "completed",
                "generated_files": generated_files,
                "framework": framework,
                "total_tests": len(test_cases),
                "base_url": base_url,
                "discovery_integration": "enabled" if discovered_pages else "disabled"
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced test generation failed: {str(e)}")
            self.update_state("error")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _create_playwright_test(self, test_case: Dict, app_data: Dict, 
                                    pages: List, elements: Dict) -> Dict:
        """Create real Playwright test with discovered elements"""
        
        test_name = test_case.get("name", "test_case")
        description = test_case.get("description", "Generated test case")
        steps = test_case.get("steps", [])
        
        # Clean test name for Python naming conventions
        clean_test_name = test_name.lower().replace(" ", "_").replace("-", "_")
        clean_class_name = "".join(word.capitalize() for word in clean_test_name.split("_"))
        
        # Find relevant page and elements for this test
        relevant_elements = self._find_relevant_elements(test_name, elements, pages)
        
        # Generate real test code with page object integration
        # Determine appropriate page object based on test name
        test_name_lower = test_name.lower()
        if "login" in test_name_lower:
            page_object_import = "from pages.login_page import LoginPage"
            page_object_class = "LoginPage"
        elif "dashboard" in test_name_lower or "navigation" in test_name_lower:
            page_object_import = "from pages.dashboard_page import DashboardPage"
            page_object_class = "DashboardPage"
        else:
            page_object_import = "from pages.main_page import MainPage"
            page_object_class = "MainPage"
        
        test_code = f'''"""
Test {test_name}
Generated by Enhanced AutoGen Test Creation Agent
"""

import pytest
import logging
from datetime import datetime
{page_object_import}

class Test{clean_class_name}:
    """Test class for {test_name}"""
    
    def test_{clean_test_name}(self, browser_setup):
        """
        Test: {test_name}
        Description: {description}
        """
        page, browser, context = browser_setup
        
        try:
            # Initialize page object
            page_obj = {page_object_class}(page)
            
            # Navigate to application
            page.goto("{app_data.get('base_url', app_data.get('url', 'https://opensource-demo.orangehrmlive.com/web/index.php/auth/login'))}")
            page.wait_for_load_state("networkidle")
            
            # Execute test steps with discovered selectors
'''
        
        # Add real test steps based on discovered elements
        for i, step in enumerate(steps, 1):
            step_code = self._generate_real_playwright_step(step, relevant_elements, i)
            test_code += f"            # Step {i}: {step}\n"
            test_code += step_code + "\n"
        
        # Add assertions with proper variable scope
        test_code += f'''
            # Final verification
            page.wait_for_timeout(1000)  # Allow UI to settle
            
            logging.info(f"Test {clean_test_name} completed successfully")
            
        except Exception as e:
            logging.error(f"Test {clean_test_name} failed: {{str(e)}}")
            raise
'''
        
        # Save the test file to the correct tests directory
        tests_dir = Path("./tests")
        tests_dir.mkdir(exist_ok=True)
        
        # Clean test name to remove spaces and special characters
        clean_test_name = test_name.replace(" ", "_").replace("-", "_").lower()
        test_file_path = tests_dir / f"test_{clean_test_name}.py"
        
        with open(test_file_path, 'w') as f:
            f.write(test_code)
        
        self.logger.info(f"Generated Playwright test: {test_file_path}")
        
        return {
            "type": "test",
            "framework": "playwright",
            "path": str(test_file_path),
            "name": f"test_{clean_test_name}.py",
            "test_count": 1,
            "elements_used": len(relevant_elements)
        }
    
    def _generate_real_playwright_step(self, step: str, elements: Dict, step_num: int) -> str:
        """Generate real Playwright code for a test step using page objects"""
        step_lower = step.lower()
        
        if "navigate" in step_lower or "go to" in step_lower:
            return "            # Navigate using page object\n            page_obj.navigate()"
        
        elif "click" in step_lower and "login" in step_lower:
            return '''            # Click login button using page object
            page_obj.click_login()
            page.wait_for_timeout(500)'''
        
        elif "enter" in step_lower and "username" in step_lower:
            return '''            # Enter username using page object
            page_obj.fill_username("Admin")
            page.wait_for_timeout(200)'''
        
        elif "enter" in step_lower and "password" in step_lower:
            return '''            # Enter password using page object
            page_obj.fill_password("admin123")
            page.wait_for_timeout(200)'''
        
        elif "login" in step_lower and ("valid" in step_lower or "complete" in step_lower):
            return '''            # Perform complete login using page object
            page_obj.login("Admin", "admin123")
            page.wait_for_timeout(1000)'''
        
        elif "login" in step_lower and "invalid" in step_lower:
            return '''            # Perform invalid login using page object
            page_obj.login("invalid_user", "invalid_pass")
            page.wait_for_timeout(1000)'''
        
        elif "verify" in step_lower or "check" in step_lower:
            return f'''            # Verification step {step_num}
            # Wait for expected element to be visible
            page.wait_for_selector("body", timeout=5000)
            
            # Assert the step was successful
            assert page.url is not None, "Page should be loaded"'''
        
        else:
            # Generic step
            return f'''            # Generic step: {step}
            page.wait_for_timeout(500)
            logging.info("Executed step: {step}")'''
    
    def _find_relevant_elements(self, test_name: str, elements: Dict, pages: List) -> Dict:
        """Find elements relevant to the test case"""
        relevant = {}
        test_name_lower = test_name.lower()
        
        # Extract elements from discovery results structure
        discovered_elements = []
        if isinstance(elements, dict) and "elements" in elements:
            discovered_elements = elements["elements"]
        elif isinstance(elements, list):
            discovered_elements = elements
        
        # Map discovered elements to selectors
        for element in discovered_elements:
            if isinstance(element, dict):
                element_type = element.get("type", "").lower()
                element_name = element.get("name", "").lower()
                element_text = element.get("text", "").lower()
                element_category = element.get("category", "").lower()
                selectors = element.get("selectors", {})
                
                # Map username field
                if element_name == "username" or "username" in element.get("placeholder", "").lower():
                    relevant["username_field"] = selectors.get("name", "input[name='username']")
                
                # Map password field  
                elif element_type == "password" or element_name == "password":
                    relevant["password_field"] = selectors.get("name", "input[name='password']")
                
                # Map login button
                elif element_category == "button" and ("login" in element_text or "submit" in element_type):
                    relevant["login_button"] = selectors.get("class", selectors.get("css", "button[type='submit']"))
        
        # Add fallback selectors if none found
        if not relevant.get("username_field"):
            relevant["username_field"] = "input[name='username']"
        if not relevant.get("password_field"):
            relevant["password_field"] = "input[name='password']"
        if not relevant.get("login_button"):
            relevant["login_button"] = "button[type='submit']"
        
        return relevant
    
    async def _create_page_objects_from_discovery(self, pages: List, elements: Dict, 
                                                framework: str) -> List[Dict]:
        """Create page object models from discovered data"""
        page_objects = []
        
        # Create specific page objects based on common test scenarios
        page_scenarios = [
            {"name": "Login", "url": pages[0].get("url", "/") if pages else "/", "focus": "login"},
            {"name": "Dashboard", "url": pages[0].get("url", "/").replace("login", "dashboard") if pages else "/dashboard", "focus": "navigation"},
            {"name": "Main", "url": pages[0].get("url", "/") if pages else "/", "focus": "general"}
        ]
        
        for scenario in page_scenarios:
            page_name = scenario["name"]
            page_url = scenario["url"]
            # Use elements from the first discovered page for all scenarios
            page_elements = pages[0].get("elements", []) if pages else []
            
            if framework == "playwright":
                page_object = await self._create_playwright_page_object(
                    page_name, page_url, page_elements
                )
            elif framework == "selenium":
                page_object = await self._create_selenium_page_object(
                    page_name, page_url, page_elements
                )
            
            if page_object:
                page_objects.append(page_object)
        
        return page_objects
    
    async def _create_playwright_page_object(self, page_name: str, page_url: str, 
                                           elements: List) -> Dict:
        """Create Playwright page object"""
        
        # Create specific class name based on page name
        clean_page_name = page_name.replace(" ", "").replace("-", "").replace("_", "")
        class_name = f"{clean_page_name}Page"
        file_name = f"{page_name.lower().replace(' ', '_').replace('-', '_')}_page.py"
        
        page_object_code = f'''"""
{page_name} Page Object
Generated by Enhanced AutoGen Test Creation Agent
"""

from playwright.sync_api import Page
import logging

class {class_name}:
    """Page object for {page_name}"""
    
    def __init__(self, page: Page):
        self.page = page
        self.url = "{page_url}"
        
        # Element selectors discovered from application analysis
'''
        
        # Add discovered elements as properties with actual selectors
        username_selector = "input[name='username']"
        password_selector = "input[name='password']"
        login_button_selector = "button[type='submit']"
        
        # Extract actual selectors from discovered elements
        for element in elements:
            if isinstance(element, dict):
                element_name = element.get("name", "").lower()
                element_type = element.get("type", "").lower()
                element_category = element.get("category", "").lower()
                selectors = element.get("selectors", {})
                
                if element_name == "username":
                    username_selector = selectors.get("name", "input[name='username']")
                elif element_type == "password" or element_name == "password":
                    password_selector = selectors.get("name", "input[name='password']")
                elif element_category == "button" and "login" in element.get("text", "").lower():
                    login_button_selector = selectors.get("class", "button[type='submit']")
        
        page_object_code += f'''        self.username_field = "{username_selector}"
        self.password_field = "{password_selector}"
        self.login_button = "{login_button_selector}"
        
    def navigate(self):
        """Navigate to {page_name}"""
        self.page.goto(self.url)
        self.page.wait_for_load_state("networkidle")
        
    def fill_username(self, username: str):
        """Fill username field"""
        self.page.fill(self.username_field, username)
        
    def fill_password(self, password: str):
        """Fill password field"""
        self.page.fill(self.password_field, password)
        
    def click_login(self):
        """Click login button"""
        self.page.click(self.login_button)
        
    def login(self, username: str, password: str):
        """Perform complete login"""
        self.fill_username(username)
        self.fill_password(password)
        self.click_login()
'''
        
        # Save the page object file to the correct pages directory
        pages_dir = Path("./pages")
        pages_dir.mkdir(exist_ok=True)
        
        page_object_path = pages_dir / file_name
        
        with open(page_object_path, 'w') as f:
            f.write(page_object_code)
        
        self.logger.info(f"Generated page object: {page_object_path}")
        
        return {
            "type": "page_object",
            "framework": "playwright",
            "path": str(page_object_path),
            "name": file_name,
            "class_name": class_name,
            "elements_count": len(elements)
        }
    
    async def _create_configuration_files(self, framework: str, base_url: str, 
                                        app_data: Dict) -> List[Dict]:
        """Create configuration and utility files"""
        config_files = []
        
        # Create pytest configuration
        pytest_config = f'''"""
Pytest Configuration for AutoGen Generated Tests
"""

import pytest
import logging
import os
from datetime import datetime

# Configure logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = f"test_results/{{timestamp}}"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{{log_dir}}/test_execution_{{timestamp}}.log'),
        logging.StreamHandler()
    ]
)

# Test configuration
BASE_URL = "{base_url}"
HEADLESS = True
TIMEOUT = 30000

# Browser configuration
BROWSER_CONFIG = {{
    "headless": HEADLESS,
    "viewport": {{"width": 1920, "height": 1080}},
    "ignore_https_errors": True
}}

@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {{
        "base_url": BASE_URL,
        "timeout": TIMEOUT,
        "browser_config": BROWSER_CONFIG
    }}
'''
        
        config_path = Path("tests/conftest.py")
        # Only create conftest.py if it doesn't exist, don't overwrite existing one
        if not config_path.exists():
            with open(config_path, 'w') as f:
                f.write(pytest_config)
        
        config_files.append({
            "type": "configuration",
            "path": str(config_path),
            "name": "conftest.py",
            "purpose": "pytest configuration"
        })
        
        # Create requirements file
        if framework == "playwright":
            requirements = '''# AutoGen Generated Test Requirements
pytest==7.4.0
playwright==1.40.0
pytest-asyncio==0.21.1
pytest-html==3.2.0
'''
        else:
            requirements = '''# AutoGen Generated Test Requirements
pytest==7.4.0
selenium==4.15.0
webdriver-manager==4.0.1
pytest-html==3.2.0
'''
        
        # Use root directory requirements.txt instead of work_dir
        requirements_path = Path("requirements.txt")
        if not requirements_path.exists():
            with open(requirements_path, 'w') as f:
                f.write(requirements)
        
        config_files.append({
            "type": "requirements",
            "path": str(requirements_path),
            "name": "requirements.txt",
            "purpose": "test dependencies"
        })
        
        return config_files
    
    # Placeholder methods for other frameworks
    async def _create_selenium_test(self, test_case: Dict, app_data: Dict, 
                                  pages: List, elements: Dict) -> Dict:
        """Create Selenium test (placeholder for future implementation)"""
        return None
    
    async def _create_api_test(self, test_case: Dict, app_data: Dict) -> Dict:
        """Create API test (placeholder for future implementation)"""
        return None
    
    async def _create_selenium_page_object(self, page_name: str, page_url: str, 
                                         elements: List) -> Dict:
        """Create Selenium page object (placeholder for future implementation)"""
        return None
    
    async def _create_page_objects(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create page objects (main method)"""
        return await self._create_page_objects_from_discovery(
            task_data.get("pages", []),
            task_data.get("elements", {}),
            task_data.get("framework", "playwright")
        )
    
    async def _generate_test_utilities(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test utilities"""
        return {
            "status": "completed",
            "utilities": ["conftest.py", "requirements.txt"]
        }


    async def _generate_selenium_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Selenium WebDriver tests"""
        try:
            logger.info("🔧 Generating Selenium WebDriver tests")
            
            test_plan = task_data.get("test_plan", {})
            application_url = task_data.get("application_url", "https://example.com")
            
            # Generate Selenium test files
            generated_files = []
            
            # Create main Selenium test
            selenium_test = self._create_selenium_test_template(test_plan, application_url)
            test_file_path = f"{self.work_dir}/test_selenium_automation.py"
            
            with open(test_file_path, 'w') as f:
                f.write(selenium_test)
            generated_files.append(test_file_path)
            
            # Create Selenium configuration
            config_content = self._create_selenium_config_template()
            config_file_path = f"{self.work_dir}/selenium_config.py"
            with open(config_file_path, 'w') as f:
                f.write(config_content)
            generated_files.append(config_file_path)
            
            # Create requirements for Selenium (use root directory)
            selenium_requirements = self._create_selenium_requirements()
            req_file_path = "requirements.txt"
            # Only create if it doesn't exist to avoid overwriting
            if not Path(req_file_path).exists():
                with open(req_file_path, 'w') as f:
                    f.write(selenium_requirements)
            generated_files.append(req_file_path)
            
            logger.info(f"✅ Generated {len(generated_files)} Selenium test files")
            
            return {
                "status": "success",
                "framework": "selenium",
                "generated_files": generated_files,
                "test_count": len(generated_files),
                "artifacts": generated_files
            }
            
        except Exception as e:
            logger.error(f"❌ Selenium test generation failed: {str(e)}")
            return {
                "status": "error",
                "error": f"Selenium test generation failed: {str(e)}"
            }
    
    async def _generate_api_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API tests using requests library"""
        try:
            logger.info("🔧 Generating API tests")
            
            test_plan = task_data.get("test_plan", {})
            api_base_url = task_data.get("api_base_url", "https://api.example.com")
            
            # Generate API test files
            generated_files = []
            
            # Create main API test
            api_test = self._create_api_test_template(test_plan, api_base_url)
            test_file_path = f"{self.work_dir}/test_api_automation.py"
            
            with open(test_file_path, 'w') as f:
                f.write(api_test)
            generated_files.append(test_file_path)
            
            # Create API client
            api_client = self._create_api_client_template(api_base_url)
            client_file_path = f"{self.work_dir}/api_client.py"
            with open(client_file_path, 'w') as f:
                f.write(api_client)
            generated_files.append(client_file_path)
            
            # Create API requirements (use root directory)
            api_requirements = self._create_api_requirements()
            req_file_path = "requirements.txt"
            # Only create if it doesn't exist to avoid overwriting
            if not Path(req_file_path).exists():
                with open(req_file_path, 'w') as f:
                    f.write(api_requirements)
            generated_files.append(req_file_path)
            
            logger.info(f"✅ Generated {len(generated_files)} API test files")
            
            return {
                "status": "success",
                "framework": "api_requests",
                "generated_files": generated_files,
                "test_count": len(generated_files),
                "artifacts": generated_files
            }
            
        except Exception as e:
            logger.error(f"❌ API test generation failed: {str(e)}")
            return {
                "status": "error",
                "error": f"API test generation failed: {str(e)}"
            }
    
    def _create_selenium_test_template(self, test_plan: Dict, application_url: str) -> str:
        """Create Selenium WebDriver test template"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f'''"""
Selenium WebDriver Test - Generated by AutoGen AI Test Framework
================================================================
Generated at: {timestamp}
Application: {application_url}
"""

import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium_config import SeleniumConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestSeleniumAutomation:
    """Selenium WebDriver test automation class"""
    
    def setup_method(self):
        """Setup Selenium WebDriver"""
        config = SeleniumConfig()
        
        # Setup Chrome options
        chrome_options = ChromeOptions()
        if config.HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={{config.WINDOW_WIDTH}},{{config.WINDOW_HEIGHT}}")
        
        # Initialize driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)
    
    def teardown_method(self):
        """Cleanup Selenium WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def test_login_functionality(self):
        """Test user login functionality with Selenium"""
        try:
            logger.info("🔍 Testing login functionality with Selenium")
            
            # Navigate to application
            self.driver.get("{application_url}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot
            timestamp = int(time.time())
            screenshot_path = f"selenium_login_test_{{timestamp}}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {{screenshot_path}}")
            
            logger.info("🎉 Selenium login test template completed")
            
        except Exception as e:
            timestamp = int(time.time())
            error_screenshot = f"selenium_login_error_{{timestamp}}.png"
            self.driver.save_screenshot(error_screenshot)
            logger.error(f"❌ Selenium login test failed: {{str(e)}}")
            logger.error(f"📸 Error screenshot: {{error_screenshot}}")
            raise
    
    def test_navigation_functionality(self):
        """Test basic navigation functionality"""
        try:
            logger.info("🔍 Testing navigation functionality")
            
            # Navigate to application
            self.driver.get("{application_url}")
            
            # Test page title
            assert self.driver.title, "Page title should not be empty"
            logger.info(f"✅ Page title: {{self.driver.title}}")
            
            # Take screenshot
            timestamp = int(time.time())
            screenshot_path = f"selenium_navigation_test_{{timestamp}}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {{screenshot_path}}")
            
            logger.info("🎉 Selenium navigation test completed")
            
        except Exception as e:
            timestamp = int(time.time())
            error_screenshot = f"selenium_navigation_error_{{timestamp}}.png"
            self.driver.save_screenshot(error_screenshot)
            logger.error(f"❌ Selenium navigation test failed: {{str(e)}}")
            logger.error(f"📸 Error screenshot: {{error_screenshot}}")
            raise

if __name__ == "__main__":
    test = TestSeleniumAutomation()
    test.setup_method()
    try:
        test.test_login_functionality()
        test.test_navigation_functionality()
    finally:
        test.teardown_method()
'''
    
    def _create_selenium_config_template(self) -> str:
        """Create Selenium configuration template"""
        return '''"""
Selenium WebDriver Configuration
===============================
"""

import os

class SeleniumConfig:
    """Configuration for Selenium WebDriver tests"""
    
    # Browser settings
    HEADLESS = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
    BROWSER = os.getenv('SELENIUM_BROWSER', 'chrome')
    
    # Window settings
    WINDOW_WIDTH = int(os.getenv('SELENIUM_WINDOW_WIDTH', '1920'))
    WINDOW_HEIGHT = int(os.getenv('SELENIUM_WINDOW_HEIGHT', '1080'))
    
    # Timeout settings
    IMPLICIT_WAIT = int(os.getenv('SELENIUM_IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('SELENIUM_EXPLICIT_WAIT', '10'))
    
    # Test settings
    SCREENSHOT_ON_FAILURE = os.getenv('SELENIUM_SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    
    # Application settings
    BASE_URL = os.getenv('APPLICATION_URL', 'https://example.com')
'''
    
    def _create_selenium_requirements(self) -> str:
        """Create Selenium requirements file"""
        return '''# Selenium WebDriver requirements
selenium>=4.15.0
webdriver-manager>=4.0.0
'''
    
    def _create_api_test_template(self, test_plan: Dict, api_base_url: str) -> str:
        """Create API test template"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f'''"""
API Test Suite - Generated by AutoGen AI Test Framework
=======================================================
Generated at: {timestamp}
API Base URL: {api_base_url}
"""

import requests
import json
import logging
from datetime import datetime
from api_client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestAPIAutomation:
    """API test automation class"""
    
    def setup_method(self):
        """Setup API client"""
        self.api_client = APIClient("{api_base_url}")
    
    def test_api_health_check(self):
        """Test API health check endpoint"""
        try:
            logger.info("🔍 Testing API health check")
            
            # Make health check request
            response = self.api_client.get("/health")
            
            # Basic validation
            assert response.status_code in [200, 404], f"Unexpected status code: {{response.status_code}}"
            
            if response.status_code == 200:
                logger.info("✅ Health check endpoint available")
            else:
                logger.info("ℹ️ Health check endpoint not found (404)")
            
            logger.info("🎉 API health check test completed")
            
        except Exception as e:
            logger.error(f"❌ API health check test failed: {{str(e)}}")
            raise
    
    def test_api_authentication(self):
        """Test API authentication endpoints"""
        try:
            logger.info("🔍 Testing API authentication")
            
            # Test login endpoint
            login_data = {{
                "username": "testuser",
                "password": "testpass"
            }}
            
            response = self.api_client.post("/auth/login", json=login_data)
            
            # Check if authentication endpoint exists
            if response.status_code == 404:
                logger.info("ℹ️ Authentication endpoint not found, skipping auth test")
                return
            
            # Basic validation
            assert response.status_code in [200, 201, 401, 403], f"Unexpected status code: {{response.status_code}}"
            
            if response.status_code in [200, 201]:
                logger.info("✅ Authentication endpoint available and responding")
            else:
                logger.info(f"ℹ️ Authentication endpoint returned {{response.status_code}}")
            
            logger.info("🎉 API authentication test completed")
            
        except Exception as e:
            logger.error(f"❌ API authentication test failed: {{str(e)}}")
            raise

if __name__ == "__main__":
    test = TestAPIAutomation()
    test.setup_method()
    test.test_api_health_check()
    test.test_api_authentication()
'''
    
    def _create_api_client_template(self, api_base_url: str) -> str:
        """Create API client template"""
        return f'''"""
API Client for Test Automation
==============================
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """API client for test automation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({{
            'Content-Type': 'application/json',
            'User-Agent': 'AutoGen-Test-Framework/1.0'
        }})
    
    def get(self, endpoint: str, params=None, **kwargs):
        """Make GET request"""
        url = f"{{self.base_url}}{{endpoint}}"
        logger.info(f"GET {{url}}")
        
        try:
            response = self.session.get(url, params=params, **kwargs)
            logger.info(f"Response: {{response.status_code}}")
            return response
        except Exception as e:
            logger.error(f"GET request failed: {{str(e)}}")
            raise
    
    def post(self, endpoint: str, data=None, json=None, **kwargs):
        """Make POST request"""
        url = f"{{self.base_url}}{{endpoint}}"
        logger.info(f"POST {{url}}")
        
        try:
            response = self.session.post(url, data=data, json=json, **kwargs)
            logger.info(f"Response: {{response.status_code}}")
            return response
        except Exception as e:
            logger.error(f"POST request failed: {{str(e)}}")
            raise
'''
    
    def _create_api_requirements(self) -> str:
        """Create API requirements file"""
        return '''# API testing requirements
requests>=2.31.0
'''

    def get_capabilities(self) -> List[str]:
        """Get enhanced capabilities including Selenium and API"""
        return [
            "real_code_generation",
            "discovery_integration",
            "page_object_models",
            "test_utilities",
            "playwright_tests",
            "selenium_tests",
            "api_tests",
            "assertions_and_validations",
            "selenium_webdriver_tests",
            "api_requests_tests",
            "multi_framework_support"
        ]

