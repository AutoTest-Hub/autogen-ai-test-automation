from playwright.async_api import async_playwright
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

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

from .base_agent import BaseTestAgent
from config.settings import AgentRole
from utils.locator_strategy import LocatorStrategy
from utils.step_generator import ThreeTierStepGenerator

# Setup logger
logger = logging.getLogger(__name__)

class EnhancedTestCreationAgent(BaseTestAgent):
    """Enhanced Test Creation Agent that generates real working code"""
    
    def __init__(self, local_ai_provider=None):
        agent_name = "EnhancedTestCreationAgent"
        super().__init__(
            role=AgentRole.TEST_CREATION,
            name=agent_name,
            system_message="You are an Enhanced Test Creation Agent that generates real, executable test code using discovered application data and best practices.",
            local_ai_provider=local_ai_provider
        )
        
        # Work directory for saving artifacts
        self.work_dir = Path(f"./work_dir/{agent_name}")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.step_generator = ThreeTierStepGenerator()
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.state = {}

    def update_state(self, status):
        self.state["status"] = status
        
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
    
    def _load_framework_options(self) -> Dict[str, Any]:
        """Load framework options from requirements.json"""
        try:
            requirements_path = Path("./requirements.json")
            if requirements_path.exists():
                with open(requirements_path, 'r') as f:
                    requirements = json.load(f)
                    framework_options = requirements.get("framework_options", {})
                    
                    # Set defaults if not specified
                    defaults = {
                        "use_page_objects": False,
                        "page_object_pattern": "standard",
                        "locator_strategy": "direct",
                        "test_generation_approach": "application_agnostic"
                    }
                    
                    for key, default_value in defaults.items():
                        if key not in framework_options:
                            framework_options[key] = default_value
                    
                    self.logger.info(f"Loaded framework options: {framework_options}")
                    return framework_options
            else:
                self.logger.warning("requirements.json not found, using default framework options")
                return {
                    "use_page_objects": False,
                    "page_object_pattern": "standard", 
                    "locator_strategy": "direct",
                    "test_generation_approach": "application_agnostic"
                }
        except Exception as e:
            self.logger.error(f"Error loading framework options: {str(e)}")
            return {
                "use_page_objects": False,
                "page_object_pattern": "standard",
                "locator_strategy": "direct", 
                "test_generation_approach": "application_agnostic"
            }
    
    async def _generate_real_test_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate real executable test code"""
        try:
            self.update_state("processing")
            
            test_plan = task_data.get("test_plan", {})
            application_data = task_data.get("application_data", {})
            
            # Load framework options from requirements.json
            framework_options = self._load_framework_options()
            
            # Extract real data from Discovery Agent
            discovered_pages = application_data.get("discovered_pages", [])
            discovered_elements = application_data.get("discovered_elements", {})
            user_workflows = application_data.get("user_workflows", [])
            base_url = application_data.get("base_url", "https://example.com")
            
            generated_files = []
            
            # Generate test cases from test plan scenarios
            test_scenarios = test_plan.get("test_scenarios", [])
            framework = test_plan.get("framework", "playwright")
            
            for test_scenario in test_scenarios:
                if framework == "playwright":
                    test_file = await self._create_playwright_test(
                        test_scenario, application_data, discovered_pages, discovered_elements, framework_options
                    )
                elif framework == "selenium":
                    test_file = await self._create_selenium_test(
                        test_scenario, application_data, discovered_pages, discovered_elements
                    )
                else:
                    test_file = await self._create_api_test(
                        test_scenario, application_data
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
                "total_tests": len(test_scenarios),
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
                                    pages: List, elements: Dict, framework_options: Dict = None) -> Dict:
        """Create real Playwright test with discovered elements - Enhanced with validations and test data"""
        
        test_name = test_case.get("name", "test_case")
        description = test_case.get("description", "Generated test case")
        steps = test_case.get("steps", [])
        
        # Enhanced: Extract validations, test_data, and environment from test case
        validations = test_case.get("validations", [])
        test_data = self._extract_test_data(test_case, app_data)
        environment = test_case.get("environment", {})
        expected_result = test_case.get("expected_result", "")
        
        # Clean test name for Python naming conventions
        clean_test_name = test_name.lower().replace(" ", "_").replace("-", "_")
        clean_class_name = "".join(word.capitalize() for word in clean_test_name.split("_"))
        
        # Find relevant page and elements for this test
        relevant_elements = self._find_relevant_elements(test_name, elements, pages)
        
        # Handle framework options for dual support
        if framework_options is None:
            framework_options = {"use_page_objects": False}
        
        use_page_objects = framework_options.get("use_page_objects", False)
        
        # Generate test code based on configuration
        if use_page_objects:
            test_code = await self._generate_page_object_test(
                test_name, description, steps, validations, test_data, 
                clean_test_name, clean_class_name, relevant_elements, pages
            )
        else:
            test_code = await self._generate_direct_locator_test(
                test_name, description, steps, validations, test_data,
                clean_test_name, clean_class_name, relevant_elements
            )
        
        # Save the test file to the correct tests directory
        tests_dir = Path("./tests")
        tests_dir.mkdir(exist_ok=True)
        
        # Clean test name to remove spaces and special characters
        clean_test_name = test_name.replace(" ", "_").replace("-", "_").lower()
        test_file_path = tests_dir / f"test_{clean_test_name}.py"
        
        with open(test_file_path, 'w') as f:
            f.write(test_code)
        
        self.logger.info(f"Generated Playwright test: {test_file_path} (Page Objects: {use_page_objects})")
        
        return {
            "type": "test",
            "framework": "playwright",
            "path": str(test_file_path),
            "name": f"test_{clean_test_name}.py",
            "test_count": 1,
            "elements_used": len(relevant_elements),
            "page_objects_used": use_page_objects
        }
    
    async def _generate_direct_locator_test(self, test_name: str, description: str, steps: List[str], 
                                    validations: List[str], test_data: Dict, clean_test_name: str, 
                                    clean_class_name: str, relevant_elements: Dict) -> str:
        """Generate test using direct LocatorStrategy approach (current working approach)"""
        
        test_code = f'''"""
Test {test_name}
Generated by Enhanced AutoGen Test Creation Agent
Application-Agnostic Test - Works with any web application
"""'''

        test_code += f'''
import pytest
import logging
from datetime import datetime
from utils.locator_strategy import LocatorStrategy
from utils.step_generator import ThreeTierStepGenerator

class Test{clean_class_name}:
    """Test class for {test_name}"""
    
    def test_{clean_test_name}(self, browser_setup):
        """
        Test: {test_name}
        Description: {description}
        """
        page, browser, context = browser_setup
        
        # Test data from requirements.json
        test_data = {test_data}
        
        # Always load additional data from requirements.json
        try:
            import json
            from pathlib import Path
            requirements_path = Path("./requirements.json")
            if requirements_path.exists():
                with open(requirements_path, 'r') as f:
                    requirements = json.load(f)
                    # Merge test_data with requirements data
                    base_data = {{
                        "base_url": requirements.get("application_url", requirements.get("base_url", "")),
                        **requirements.get("application_specific_config", {{}})
                    }}
                    test_data = {{**base_data, **test_data}}
        except Exception as e:
                logger.error(f"Failed to load requirements.json: {{e}}")
                test_data = {{}}
        
        # Initialize locator strategy for robust element finding
        locator_strategy = LocatorStrategy(page)
        
        try:
            # Get application URL - no hardcoded fallbacks
            app_url = test_data.get("base_url")
            if not app_url:
                raise ValueError("No application URL provided. Please specify base_url in test data.")
            
            # Navigate to application with robust loading
            try:
                page.goto(app_url, timeout=60000)  # Increase timeout to 60s
                page.wait_for_load_state("domcontentloaded", timeout=30000)  # Use domcontentloaded instead of networkidle
            except Exception as ex:
                # Retry once with different approach
                logging.warning(f"Initial page load failed, retrying: {{ex}}")
                page.goto(app_url, timeout=60000)
                page.wait_for_timeout(3000)  # Simple wait instead of networkidle
            
            # Execute test steps using LocatorStrategy (no hardcoded page objects)
'''
        
        # Add real test steps using the three-tier step generator
        for i, step in enumerate(steps, 1):
            step_code = await self.step_generator.generate_step(step, {{"framework_options": {{"use_page_objects": False}}}})
            test_code += f"            # Step {i}: {step}\n"
            test_code += f"            {step_code}\n\n"
        
        # Enhanced: Add specific validations from requirements.json
        validation_code = self._generate_assertions_from_validations(validations, test_name, relevant_elements)
        test_code += validation_code
        
        test_code += f'''
            # Final verification
            page.wait_for_timeout(1000)  # Allow UI to settle
            
            logging.info(f"Test {clean_test_name} completed successfully")
            
        except Exception as e:
            logging.error(f"Test {clean_test_name} failed: {{str(e)}}")
            raise
'''
        
        return test_code
    
    async def _generate_page_object_test(self, test_name: str, description: str, steps: List[str], 
                                 validations: List[str], test_data: Dict, clean_test_name: str, 
                                 clean_class_name: str, relevant_elements: Dict, pages: List) -> str:
        """Generate test using Page Object Model approach"""
        
        # Find the relevant page for this test
        page_name = self._find_page_for_test(test_name, pages)
        page_class_name = f"{page_name.capitalize()}Page"
        page_file_name = f"{page_name.lower()}_page"
        
        test_code = f'''"""
Test {test_name}
Generated by Enhanced AutoGen Test Creation Agent
Uses Page Object Model for maintainability
"""'''

        test_code += f'''
import pytest
import logging
from datetime import datetime
from pages.{page_file_name} import {page_class_name}
from utils.step_generator import ThreeTierStepGenerator

class Test{clean_class_name}:
    """Test class for {test_name}"""
    
    def test_{clean_test_name}(self, browser_setup):
        """
        Test: {test_name}
        Description: {description}
        """
        page, browser, context = browser_setup
        
        # Test data from requirements.json
        test_data = {test_data}
        
        # Always load additional data from requirements.json
        try:
            import json
            from pathlib import Path
            requirements_path = Path("./requirements.json")
            if requirements_path.exists():
                with open(requirements_path, 'r') as f:
                    requirements = json.load(f)
                    # Merge test_data with requirements data
                    base_data = {{
                        "base_url": requirements.get("application_url", requirements.get("base_url", "")),
                        **requirements.get("application_specific_config", {{}})
                    }}
                    test_data = {{**base_data, **test_data}}
        except Exception as e:
                logger.error(f"Failed to load requirements.json: {{e}}")
                test_data = {{}}
        
        # Initialize page object
        {page_name}_page = {page_class_name}(page)
        
        try:
            # Get application URL
            app_url = test_data.get("base_url")
            if not app_url:
                raise ValueError("No application URL provided. Please specify base_url in test data.")
            
            # Navigate to application
            page.goto(app_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            
            # Execute test steps using page objects
'''
        
        # Add real test steps using the three-tier step generator
        for i, step in enumerate(steps, 1):
            step_code = await self.step_generator.generate_step(step, {{"framework_options": {{"use_page_objects": True, "page_name": page_name}}}})
            test_code += f"            # Step {i}: {step}\n"
            test_code += f"            {step_code}\n\n"
        
        # Enhanced: Add specific validations from requirements.json
        validation_code = self._generate_assertions_from_validations(validations, test_name, relevant_elements, page_name)
        test_code += validation_code
        
        test_code += f'''
            # Final verification
            page.wait_for_timeout(1000)  # Allow UI to settle
            
            logging.info(f"Test {clean_test_name} completed successfully")
            
        except Exception as e:
            logging.error(f"Test {clean_test_name} failed: {{str(e)}}")
            raise
'''
        
        return test_code
    
    def _find_page_for_test(self, test_name: str, pages: List) -> str:
        """Find the most relevant page for a given test case"""
        test_name_lower = test_name.lower()
        
        for page in pages:
            page_name = page.get("name", "").lower()
            if page_name in test_name_lower:
                return page_name
        
        # Fallback to the first page if no match found
        return pages[0].get("name", "base") if pages else "base"
    
    def _find_relevant_elements(self, test_name: str, all_elements: Dict, pages: List) -> Dict:
        """Find elements relevant to a specific test case"""
        relevant_elements = {}
        test_name_lower = test_name.lower()
        
        # Find page associated with the test
        page_name = self._find_page_for_test(test_name, pages)
        
        if page_name in all_elements:
            page_elements = all_elements[page_name]
            
            for element_name, element_details in page_elements.items():
                # Check if element name is in test name or description
                if element_name.lower() in test_name_lower:
                    relevant_elements[element_name] = element_details
                else:
                    # Check for keywords in element details
                    element_str = str(element_details).lower()
                    if any(keyword in element_str for keyword in ["login", "submit", "username", "password"]):
                        if "login" in test_name_lower:
                            relevant_elements[element_name] = element_details
        
        return relevant_elements
    
    def _extract_test_data(self, test_case: Dict, app_data: Dict) -> Dict:
        """Extract and merge test data from test case and application data"""
        test_data = test_case.get("test_data", {})
        app_test_data = app_data.get("test_data", {})
        
        # Merge data, with test case data taking precedence
        merged_data = {**app_test_data, **test_data}
        
        # Add base_url if not present
        if "base_url" not in merged_data:
            merged_data["base_url"] = app_data.get("base_url", "")
        
        return merged_data
    
    def _generate_assertions_from_validations(self, validations: List[str], test_name: str, 
                                              relevant_elements: Dict, page_name: str = None) -> str:
        """Generate Playwright assertions from a list of validation strings"""
        
        assertion_code = "\n            # Add validations\n"
        
        for validation in validations:
            validation_lower = validation.lower()
            
            # Simple text visibility check
            if "should be visible" in validation_lower:
                text_to_check = validation.split("should be visible")[0].strip()
                assertion_code += f"            expect(page.get_by_text(\"{text_to_check}\")).to_be_visible()\n"
            
            # Element property check
            elif "element" in validation_lower and "should have" in validation_lower:
                parts = validation.split("should have")
                element_name = parts[0].replace("element", "").strip()
                property_value = parts[1].strip()
                
                # Find locator for the element
                locator = self._get_locator_for_element(element_name, relevant_elements, page_name)
                
                if locator:
                    if "text" in property_value:
                        expected_text = property_value.replace("text", "").strip()
                        assertion_code += f"            expect({locator}).to_have_text(\"{expected_text}\")\n"
                    elif "attribute" in property_value:
                        attr_parts = property_value.replace("attribute", "").strip().split("=")
                        attr_name = attr_parts[0].strip()
                        attr_value = attr_parts[1].strip()
                        assertion_code += f"            expect({locator}).to_have_attribute(\"{attr_name}\", \"{attr_value}\")\n"
            
            # URL check
            elif "url should be" in validation_lower:
                expected_url = validation.split("url should be")[1].strip()
                assertion_code += f"            expect(page).to_have_url(\"{expected_url}\")\n"
            
            # Title check
            elif "title should be" in validation_lower:
                expected_title = validation.split("title should be")[1].strip()
                assertion_code += f"            expect(page).to_have_title(\"{expected_title}\")\n"
        
        return assertion_code
    
    def _get_locator_for_element(self, element_name: str, relevant_elements: Dict, page_name: str = None) -> Optional[str]:
        """Get the Playwright locator for a given element name"""
        
        element_details = relevant_elements.get(element_name)
        if not element_details:
            return None
        
        if page_name:
            # Page Object Model approach
            return f"{page_name}_page.{element_name}"
        else:
            # Direct locator approach
            locator_strategy = element_details.get("preferred_strategy", "css")
            locator_value = element_details.get("locator")
            
            if locator_strategy == "css":
                return f"page.locator(\"{locator_value}\")"
            elif locator_strategy == "xpath":
                return f"page.locator(\"xpath={locator_value}\")"
            elif locator_strategy == "text":
                return f"page.get_by_text(\"{locator_value}\")"
            else:
                return f"page.locator(\"{locator_value}\")" # Default to CSS
    
    async def _create_page_objects_from_discovery(self, pages: List, elements: Dict, framework: str) -> List[Dict]:
        """Create page object files from discovered pages and elements"""
        
        generated_files = []
        pages_dir = Path("./pages")
        pages_dir.mkdir(exist_ok=True)
        
        for page_data in pages:
            page_name = page_data.get("name", "base")
            page_class_name = f"{page_name.capitalize()}Page"
            page_file_name = f"{page_name.lower()}_page.py"
            page_file_path = pages_dir / page_file_name
            
            page_elements = elements.get(page_name, {})
            
            # Generate page object code
            if framework == "playwright":
                page_code = self._generate_playwright_page_object(page_class_name, page_elements)
            elif framework == "selenium":
                page_code = self._generate_selenium_page_object(page_class_name, page_elements)
            else:
                continue # No page objects for API tests
            
            with open(page_file_path, 'w') as f:
                f.write(page_code)
            
            generated_files.append({
                "type": "page_object",
                "framework": framework,
                "path": str(page_file_path),
                "name": page_file_name
            })
            
            self.logger.info(f"Generated {framework.capitalize()} page object: {page_file_path}")
        
        return generated_files
    
    def _generate_playwright_page_object(self, class_name: str, elements: Dict) -> str:
        """Generate Playwright page object code"""
        
        code = f'''"""
Playwright Page Object for {class_name}
Generated by Enhanced AutoGen Test Creation Agent
"""'''

        code += f'''
from playwright.sync_api import Page, expect

class {class_name}:
    def __init__(self, page: Page):
        self.page = page
'''
        
        # Add locators for each element
        for element_name, details in elements.items():
            locator_strategy = details.get("preferred_strategy", "css")
            locator_value = details.get("locator")
            
            if locator_strategy == "css":
                code += f"        self.{element_name} = page.locator(\"{locator_value}\")\n"
            elif locator_strategy == "xpath":
                code += f"        self.{element_name} = page.locator(\"xpath={locator_value}\")\n"
            elif locator_strategy == "text":
                code += f"        self.{element_name} = page.get_by_text(\"{locator_value}\")\n"
            else:
                code += f"        self.{element_name} = page.locator(\"{locator_value}\")\n"
        
        # Add methods for common actions
        code += "\n    # --- Actions ---\n"
        for element_name, details in elements.items():
            element_type = details.get("type", "unknown")
            
            if element_type == "button" or element_type == "link":
                code += f"    def click_{element_name}(self):\n"
                code += f"        self.{element_name}.click()\n\n"
            elif element_type == "input" or element_type == "textarea":
                code += f"    def fill_{element_name}(self, text: str):\n"
                code += f"        self.{element_name}.fill(text)\n\n"
        
        return code
    
    async def _create_configuration_files(self, framework: str, base_url: str, app_data: Dict) -> List[Dict]:
        """Create configuration files for the test framework"""
        
        generated_files = []
        
        # Create pytest.ini
        pytest_ini_content = f'''[pytest]
addopts = -s -v --base-url={base_url}
'''
        pytest_ini_path = Path("./pytest.ini")
        with open(pytest_ini_path, 'w') as f:
            f.write(pytest_ini_content)
        
        generated_files.append({
            "type": "config",
            "path": str(pytest_ini_path),
            "name": "pytest.ini"
        })
        
        # Create conftest.py for browser setup
        conftest_content = self._generate_conftest_content(framework)
        conftest_path = Path("./tests/conftest.py")
        conftest_path.parent.mkdir(exist_ok=True)
        with open(conftest_path, 'w') as f:
            f.write(conftest_content)
        
        generated_files.append({
            "type": "config",
            "path": str(conftest_path),
            "name": "conftest.py"
        })
        
        return generated_files
    
    def _generate_conftest_content(self, framework: str) -> str:
        """Generate content for conftest.py based on framework"""
        
        if framework == "playwright":
            return f'''"""
Playwright conftest.py for browser setup
Generated by Enhanced AutoGen Test Creation Agent
"""'''

            return f'''
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_setup(request):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        yield page, browser, context
        
        browser.close()
'''
        elif framework == "selenium":
            return f'''"""
Selenium conftest.py for browser setup
Generated by Enhanced AutoGen Test Creation Agent
"""'''

            return f'''
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def browser_setup(request):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    yield driver
    
    driver.quit()
'''
        else:
            return "" # No conftest for API tests
    
    async def _generate_selenium_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Selenium tests - Placeholder for future implementation"""
        self.logger.warning("Selenium test generation is not fully implemented yet.")
        return {"status": "pending", "message": "Selenium test generation not implemented"}
    
    async def _generate_api_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API tests - Placeholder for future implementation"""
        self.logger.warning("API test generation is not fully implemented yet.")
        return {"status": "pending", "message": "API test generation not implemented"}
    
    async def _create_page_objects(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create page objects from discovered data"""
        application_data = task_data.get("application_data", {})
        discovered_pages = application_data.get("discovered_pages", [])
        discovered_elements = application_data.get("discovered_elements", {})
        framework = task_data.get("framework", "playwright")
        
        page_objects = await self._create_page_objects_from_discovery(
            discovered_pages, discovered_elements, framework
        )
        
        return {
            "status": "completed",
            "generated_files": page_objects
        }
    
    async def _generate_test_utilities(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test utilities and helpers - Placeholder"""
        self.logger.warning("Test utility generation is not implemented yet.")
        return {"status": "pending", "message": "Utility generation not implemented"}

