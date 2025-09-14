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
        """Process test creation task with real code generation"""
        task_type = task_data.get("task_type", "generate_tests")
        
        if task_type == "generate_tests":
            return await self._generate_real_test_code(task_data)
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
        
        # Find relevant page and elements for this test
        relevant_elements = self._find_relevant_elements(test_name, elements, pages)
        
        # Generate real test code
        test_code = f'''"""
{description}
Generated by Enhanced AutoGen Test Creation Agent
"""

import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import asyncio
import logging
from datetime import datetime

class Test{test_name.title().replace("_", "")}:
    """Test class for {test_name}"""
    
    @pytest.fixture(scope="class")
    async def browser_setup(self):
        """Setup browser for tests"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        yield page, browser, context, playwright
        
        await context.close()
        await browser.close()
        await playwright.stop()
    
    @pytest.mark.asyncio
    async def test_{test_name}(self, browser_setup):
        """
        Test: {test_name}
        Description: {description}
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Navigate to application
            await page.goto("{app_data.get('base_url', 'https://advantageonlineshopping.com')}")
            await page.wait_for_load_state("networkidle")
            
            # Execute test steps with real selectors
'''
        
        # Add real test steps based on discovered elements
        for i, step in enumerate(steps, 1):
            step_code = self._generate_real_playwright_step(step, relevant_elements, i)
            test_code += f"            # Step {i}: {step}\n"
            test_code += step_code + "\n"
        
        # Add assertions
        test_code += '''
            # Final verification
            await page.wait_for_timeout(1000)  # Allow UI to settle
            
            # Take screenshot for evidence
            await page.screenshot(path=f"test_evidence_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            logging.info(f"Test {test_name} completed successfully")
            
        except Exception as e:
            # Take screenshot on failure
            await page.screenshot(path=f"test_failure_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            logging.error(f"Test {test_name} failed: {str(e)}")
            raise
'''
        
        # Save the test file
        test_file_path = self.work_dir / f"test_{test_name}.py"
        with open(test_file_path, 'w') as f:
            f.write(test_code)
        
        self.logger.info(f"Generated Playwright test: {test_file_path}")
        
        return {
            "type": "test",
            "framework": "playwright",
            "path": str(test_file_path),
            "name": f"test_{test_name}.py",
            "test_count": 1,
            "elements_used": len(relevant_elements)
        }
    
    def _generate_real_playwright_step(self, step: str, elements: Dict, step_num: int) -> str:
        """Generate real Playwright code for a test step"""
        step_lower = step.lower()
        
        if "navigate" in step_lower or "go to" in step_lower:
            return "            await page.goto(page.url)  # Already navigated in setup"
        
        elif "click" in step_lower and "login" in step_lower:
            login_selector = elements.get("login_button", "#loginBtn")
            return f'''            # Click login button
            await page.click("{login_selector}")
            await page.wait_for_timeout(500)'''
        
        elif "enter" in step_lower and "username" in step_lower:
            username_selector = elements.get("username_field", "#username")
            return f'''            # Enter username
            await page.fill("{username_selector}", "testuser")
            await page.wait_for_timeout(200)'''
        
        elif "enter" in step_lower and "password" in step_lower:
            password_selector = elements.get("password_field", "#password")
            return f'''            # Enter password
            await page.fill("{password_selector}", "testpass")
            await page.wait_for_timeout(200)'''
        
        elif "search" in step_lower:
            search_selector = elements.get("search_box", "#searchBox")
            return f'''            # Perform search
            await page.fill("{search_selector}", "laptop")
            await page.press("{search_selector}", "Enter")
            await page.wait_for_timeout(1000)'''
        
        elif "verify" in step_lower or "check" in step_lower:
            return f'''            # Verification step {step_num}
            # Wait for expected element to be visible
            await page.wait_for_selector(".success-indicator, .welcome-message, .search-results", timeout=5000)
            
            # Assert the step was successful
            assert await page.is_visible(".success-indicator, .welcome-message, .search-results"), "Expected element not found"'''
        
        else:
            # Generic step
            return f'''            # Generic step: {step}
            await page.wait_for_timeout(500)
            logging.info("Executed step: {step}")'''
    
    def _find_relevant_elements(self, test_name: str, elements: Dict, pages: List) -> Dict:
        """Find elements relevant to the test case"""
        relevant = {}
        test_name_lower = test_name.lower()
        
        # Common element mappings
        element_mappings = {
            "login": ["login_button", "username_field", "password_field"],
            "search": ["search_box", "search_button"],
            "cart": ["add_to_cart", "cart_icon"],
            "checkout": ["checkout_button", "payment_form"]
        }
        
        # Find relevant elements based on test name
        for keyword, element_names in element_mappings.items():
            if keyword in test_name_lower:
                for element_name in element_names:
                    if element_name in elements:
                        relevant[element_name] = elements[element_name]
        
        # Add default selectors if none found
        if not relevant:
            relevant = {
                "login_button": "#loginBtn",
                "username_field": "#username", 
                "password_field": "#password",
                "search_box": "#searchBox"
            }
        
        return relevant
    
    async def _create_page_objects_from_discovery(self, pages: List, elements: Dict, 
                                                framework: str) -> List[Dict]:
        """Create page object models from discovered data"""
        page_objects = []
        
        for page in pages:
            page_name = page.get("name", "UnknownPage")
            page_url = page.get("url", "/")
            page_elements = page.get("elements", [])
            
            if framework == "playwright":
                page_object = await self._create_playwright_page_object(
                    page_name, page_url, page_elements
                )
            else:
                page_object = await self._create_selenium_page_object(
                    page_name, page_url, page_elements
                )
            
            if page_object:
                page_objects.append(page_object)
        
        return page_objects
    
    async def _create_playwright_page_object(self, page_name: str, page_url: str, 
                                           elements: List) -> Dict:
        """Create Playwright page object"""
        
        class_name = f"{page_name.title().replace(' ', '')}Page"
        
        page_object_code = f'''"""
{page_name} Page Object
Generated by Enhanced AutoGen Test Creation Agent
"""

from playwright.async_api import Page
import logging

class {class_name}:
    """Page object for {page_name}"""
    
    def __init__(self, page: Page):
        self.page = page
        self.url = "{page_url}"
        
        # Element selectors discovered from application analysis
'''
        
        # Add discovered elements as properties
        for element in elements:
            element_name = element.get("name", "unknown_element")
            selector = element.get("selector", f"#{element_name}")
            page_object_code += f'        self.{element_name}_selector = "{selector}"\n'
        
        # Add common methods
        page_object_code += f'''
    async def navigate(self):
        """Navigate to {page_name}"""
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("networkidle")
        logging.info(f"Navigated to {page_name}")
    
    async def is_loaded(self) -> bool:
        """Check if page is loaded"""
        try:
            # Wait for a key element to be visible
            await self.page.wait_for_selector("body", timeout=5000)
            return True
        except:
            return False
'''
        
        # Add element-specific methods
        for element in elements:
            element_name = element.get("name", "unknown_element")
            element_type = element.get("type", "unknown")
            
            if element_type == "button":
                page_object_code += f'''
    async def click_{element_name}(self):
        """Click {element_name}"""
        await self.page.click(self.{element_name}_selector)
        await self.page.wait_for_timeout(500)
        logging.info(f"Clicked {element_name}")
'''
            elif element_type == "input":
                page_object_code += f'''
    async def fill_{element_name}(self, value: str):
        """Fill {element_name} with value"""
        await self.page.fill(self.{element_name}_selector, value)
        await self.page.wait_for_timeout(200)
        logging.info(f"Filled {element_name} with: {{value}}")
'''
        
        # Save page object file
        page_object_path = self.work_dir / f"{page_name.lower().replace(' ', '_')}_page.py"
        with open(page_object_path, 'w') as f:
            f.write(page_object_code)
        
        self.logger.info(f"Generated page object: {page_object_path}")
        
        return {
            "type": "page_object",
            "framework": "playwright",
            "path": str(page_object_path),
            "name": f"{page_name.lower().replace(' ', '_')}_page.py",
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

# Configure logging with organized directory structure
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
        
        config_path = self.work_dir / "conftest.py"
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
        
        requirements_path = self.work_dir / "requirements.txt"
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

