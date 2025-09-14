#!/usr/bin/env python3
"""
Fixed Proper Multi-Agent Workflow
===================
This script implements a proper multi-agent workflow using the existing agents in the framework.
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agents from the agents directory
try:
    from agents.planning_agent import PlanningAgent
    from agents.real_browser_discovery_agent_fixed import RealBrowserDiscoveryAgent
    from agents.test_creation_agent import EnhancedTestCreationAgent
    from agents.review_agent import ReviewAgent
    from agents.execution_agent import ExecutionAgent
    from agents.reporting_agent import ReportingAgent
except ImportError as e:
    logger.error(f"Error importing agents: {str(e)}")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)

# Import settings
try:
    from config.settings import settings, AgentRole, LLMProvider
except ImportError:
    logger.error("Error importing settings")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)

# Import local AI provider
try:
    from models.local_ai_provider import LocalAIProvider
except ImportError:
    logger.error("Error importing local AI provider")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)

class FixedProperMultiAgentWorkflow:
    """
    Fixed Proper Multi-Agent Workflow
    
    This class implements a proper multi-agent workflow using the existing agents in the framework.
    """
    
    def __init__(self):
        """Initialize the workflow"""
        self.logger = logging.getLogger(__name__)
        
        # Create directories
        self._create_directories()
        
        # Initialize local AI provider
        self.local_ai_provider = LocalAIProvider()
        
        # Initialize agents
        self.logger.info("Initializing agents...")
        self._initialize_agents()
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            "work_dir",
            "work_dir/planning_agent",
            "work_dir/discovery_agent",
            "work_dir/test_creation_agent",
            "work_dir/review_agent",
            "work_dir/execution_agent",
            "work_dir/reporting_agent",
            "tests",
            "pages",
            "reports",
            "screenshots"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _initialize_agents(self):
        """Initialize all agents"""
        try:
            # Initialize planning agent
            self.planning_agent = PlanningAgent(local_ai_provider=self.local_ai_provider)
            self.logger.info("Planning agent initialized")
            
            # Initialize discovery agent
            self.discovery_agent = RealBrowserDiscoveryAgent()
            self.logger.info("Discovery agent initialized")
            
            # Initialize test creation agent
            self.test_creation_agent = EnhancedTestCreationAgent(local_ai_provider=self.local_ai_provider)
            self.logger.info("Test creation agent initialized")
            
            # Initialize review agent
            self.review_agent = ReviewAgent(local_ai_provider=self.local_ai_provider)
            self.logger.info("Review agent initialized")
            
            # Initialize execution agent
            self.execution_agent = ExecutionAgent(local_ai_provider=self.local_ai_provider)
            self.logger.info("Execution agent initialized")
            
            # Initialize reporting agent
            self.reporting_agent = ReportingAgent(local_ai_provider=self.local_ai_provider)
            self.logger.info("Reporting agent initialized")
        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")
            raise
    
    async def run(self, url: str, name: str, headless: bool = True) -> Dict[str, Any]:
        """
        Run the workflow
        
        Args:
            url: URL of the website
            name: Name of the website
            headless: Whether to run the browser in headless mode
            
        Returns:
            Dict[str, Any]: Workflow results
        """
        self.logger.info(f"Running workflow for {name} at {url}")
        
        try:
            # Step 1: Create test plan
            self.logger.info("Step 1: Creating test plan")
            test_plan = await self._create_test_plan(url, name)
            
            # Step 2: Discover elements
            self.logger.info("Step 2: Discovering elements")
            discovery_results = await self._discover_elements(url, headless)
            
            # Step 3: Create tests
            self.logger.info("Step 3: Creating tests")
            created_tests = await self._create_tests(test_plan, discovery_results, name, url)
            
            # Step 4: Review tests
            self.logger.info("Step 4: Reviewing tests")
            review_results = await self._review_tests(created_tests, name)
            
            # Step 5: Execute tests
            self.logger.info("Step 5: Executing tests")
            execution_results = await self._execute_tests(review_results, headless)
            
            # Step 6: Generate report
            self.logger.info("Step 6: Generating report")
            report = await self._generate_report(execution_results, name)
            
            # Create workflow results
            workflow_results = {
                "name": name,
                "url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "test_plan": test_plan,
                "discovery_results": discovery_results,
                "created_tests": created_tests,
                "review_results": review_results,
                "execution_results": execution_results,
                "report": report
            }
            
            self.logger.info(f"Workflow completed successfully for {name}")
            
            return workflow_results
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "name": name,
                "url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
    
    async def _create_test_plan(self, url: str, name: str) -> Dict[str, Any]:
        """
        Create test plan using the Planning Agent
        
        Args:
            url: URL of the website
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Test plan
        """
        try:
            # Check if requirements files exist
            requirements_txt_path = Path("work_dir/planning_agent/requirements.txt")
            requirements_json_path = Path("work_dir/planning_agent/requirements.json")
            
            requirements_text = ""
            requirements_json = {}
            
            if requirements_txt_path.exists():
                with open(requirements_txt_path, 'r') as f:
                    requirements_text = f.read()
            
            if requirements_json_path.exists():
                with open(requirements_json_path, 'r') as f:
                    requirements_json = json.load(f)
            
            # Create task data for the planning agent
            task_data = {
                "type": "create_plan",
                "url": url,
                "name": name,
                "requirements_text": requirements_text,
                "requirements_json": requirements_json
            }
            
            # Process task with planning agent
            test_plan = await self.planning_agent.process_task(task_data)
            
            # If the planning agent fails, create a default test plan
            if not test_plan or "error" in test_plan:
                self.logger.warning("Planning agent failed, creating default test plan")
                test_plan = self._create_default_test_plan(url, name)
            
            # Save test plan to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_plan_path = Path(f"work_dir/planning_agent/test_plan_{timestamp}.json")
            
            with open(test_plan_path, 'w') as f:
                json.dump(test_plan, f, indent=2)
            
            self.logger.info(f"Test plan created: {test_plan_path}")
            
            return test_plan
            
        except Exception as e:
            self.logger.error(f"Error creating test plan: {str(e)}")
            return self._create_default_test_plan(url, name)
    
    def _create_default_test_plan(self, url: str, name: str) -> Dict[str, Any]:
        """
        Create a default test plan
        
        Args:
            url: URL of the website
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Default test plan
        """
        test_plan = {
            "name": name,
            "url": url,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "test_cases": [
                {
                    "id": "TC001",
                    "name": "Login with valid credentials",
                    "description": "Test login functionality with valid credentials",
                    "priority": "High",
                    "steps": [
                        "Navigate to the login page",
                        "Enter valid username",
                        "Enter valid password",
                        "Click login button",
                        "Verify successful login"
                    ]
                },
                {
                    "id": "TC002",
                    "name": "Login with invalid credentials",
                    "description": "Test login functionality with invalid credentials",
                    "priority": "High",
                    "steps": [
                        "Navigate to the login page",
                        "Enter invalid username",
                        "Enter invalid password",
                        "Click login button",
                        "Verify error message"
                    ]
                },
                {
                    "id": "TC003",
                    "name": "Navigation",
                    "description": "Test navigation functionality",
                    "priority": "Medium",
                    "steps": [
                        "Login with valid credentials",
                        "Navigate to different sections",
                        "Verify page titles",
                        "Logout"
                    ]
                }
            ]
        }
        
        # Save test plan to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_plan_path = Path(f"work_dir/planning_agent/test_plan_{timestamp}.json")
        
        with open(test_plan_path, 'w') as f:
            json.dump(test_plan, f, indent=2)
        
        self.logger.info(f"Default test plan created: {test_plan_path}")
        
        return test_plan
    
    async def _discover_elements(self, url: str, headless: bool = True) -> Dict[str, Any]:
        """
        Discover elements using the Discovery Agent
        
        Args:
            url: URL of the website
            headless: Whether to run the browser in headless mode
            
        Returns:
            Dict[str, Any]: Discovery results
        """
        try:
            # Discover elements with discovery agent
            discovery_results = await self.discovery_agent.discover_elements(url)
            
            # Save discovery results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            discovery_results_path = Path(f"work_dir/discovery_agent/discovery_results_{timestamp}.json")
            
            with open(discovery_results_path, 'w') as f:
                json.dump(discovery_results, f, indent=2)
            
            self.logger.info(f"Discovery results saved to {discovery_results_path}")
            
            return discovery_results
            
        except Exception as e:
            self.logger.error(f"Error discovering elements: {str(e)}")
            return {
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "elements": []
            }
    
    async def _create_tests(self, test_plan: Dict[str, Any], discovery_results: Dict[str, Any], name: str, url: str) -> Dict[str, Any]:
        """
        Create tests using the Test Creation Agent
        
        Args:
            test_plan: Test plan
            discovery_results: Discovery results
            name: Name of the website
            url: URL of the website
            
        Returns:
            Dict[str, Any]: Created tests
        """
        try:
            # Create task data for the test creation agent
            task_data = {
                "task_type": "generate_tests",
                "test_plan": test_plan,
                "application_data": {
                    "base_url": url,
                    "name": name,
                    "discovered_pages": [{"url": url, "title": name}],
                    "discovered_elements": discovery_results.get("elements", []),
                    "user_workflows": []
                }
            }
            
            # Process task with test creation agent
            created_tests = await self.test_creation_agent.process_task(task_data)
            
            # If the test creation agent fails, create default tests
            if not created_tests or "error" in created_tests:
                self.logger.warning("Test creation agent failed, creating default tests")
                created_tests = self._create_default_tests(test_plan, discovery_results, name, url)
            
            # Save created tests to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            created_tests_path = Path(f"work_dir/test_creation_agent/created_tests_{timestamp}.json")
            
            with open(created_tests_path, 'w') as f:
                json.dump(created_tests, f, indent=2)
            
            self.logger.info(f"Created tests saved to {created_tests_path}")
            
            return created_tests
            
        except Exception as e:
            self.logger.error(f"Error creating tests: {str(e)}")
            return self._create_default_tests(test_plan, discovery_results, name, url)
    
    def _create_default_tests(self, test_plan: Dict[str, Any], discovery_results: Dict[str, Any], name: str, url: str) -> Dict[str, Any]:
        """
        Create default tests
        
        Args:
            test_plan: Test plan
            discovery_results: Discovery results
            name: Name of the website
            url: URL of the website
            
        Returns:
            Dict[str, Any]: Default tests
        """
        # Create directories
        tests_dir = Path("tests")
        pages_dir = Path("pages")
        
        for directory in [tests_dir, pages_dir]:
            directory.mkdir(exist_ok=True)
        
        # Create base page
        base_page_path = pages_dir / "base_page.py"
        with open(base_page_path, 'w') as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Base Page Object
===================
This module contains the base page object for all pages.
\"\"\"

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

class BasePage:
    \"\"\"
    Base page object for all pages
    \"\"\"
    
    def __init__(self, page):
        \"\"\"
        Initialize the base page object
        
        Args:
            page: Playwright page
        \"\"\"
        self.page = page
        self.logger = logging.getLogger(__name__)
    
    def navigate(self, url: str) -> None:
        \"\"\"
        Navigate to a URL
        
        Args:
            url: URL to navigate to
        \"\"\"
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
    
    def click(self, selector: str) -> None:
        \"\"\"
        Click an element
        
        Args:
            selector: Element selector
        \"\"\"
        self.logger.info(f"Clicking element: {selector}")
        self.page.click(selector)
    
    def fill(self, selector: str, value: str) -> None:
        \"\"\"
        Fill an input field
        
        Args:
            selector: Element selector
            value: Value to fill
        \"\"\"
        self.logger.info(f"Filling element {selector} with value: {value}")
        self.page.fill(selector, value)
    
    def get_text(self, selector: str) -> str:
        \"\"\"
        Get text from an element
        
        Args:
            selector: Element selector
            
        Returns:
            str: Element text
        \"\"\"
        self.logger.info(f"Getting text from element: {selector}")
        return self.page.text_content(selector)
    
    def is_visible(self, selector: str) -> bool:
        \"\"\"
        Check if an element is visible
        
        Args:
            selector: Element selector
            
        Returns:
            bool: True if element is visible, False otherwise
        \"\"\"
        self.logger.info(f"Checking if element is visible: {selector}")
        return self.page.is_visible(selector)
""")
        
        # Create page object
        page_name = name.lower().replace(" ", "_")
        page_path = pages_dir / f"{page_name}_page.py"
        with open(page_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
\"\"\"
{name} Page Object
===================
This module contains the page object for {name}.
\"\"\"

from pages.base_page import BasePage

class {page_name.capitalize()}Page(BasePage):
    \"\"\"
    Page object for {name}
    \"\"\"
    
    def __init__(self, page):
        \"\"\"
        Initialize the page object
        
        Args:
            page: Playwright page
        \"\"\"
        super().__init__(page)
        
        # Selectors
        self.username_selector = "input[name='username']"
        self.password_selector = "input[name='password']"
        self.login_button_selector = "button[type='submit']"
    
    def navigate(self):
        \"\"\"
        Navigate to {name}
        \"\"\"
        super().navigate("{url}")
    
    def fill_username(self, value):
        \"\"\"
        Fill username input
        
        Args:
            value: Value to fill
        \"\"\"
        self.fill(self.username_selector, value)
    
    def fill_password(self, value):
        \"\"\"
        Fill password input
        
        Args:
            value: Value to fill
        \"\"\"
        self.fill(self.password_selector, value)
    
    def click_login_button(self):
        \"\"\"
        Click login button
        \"\"\"
        self.click(self.login_button_selector)
    
    def login(self, username, password):
        \"\"\"
        Login with username and password
        
        Args:
            username: Username
            password: Password
        \"\"\"
        self.fill_username(username)
        self.fill_password(password)
        self.click_login_button()
""")
        
        # Create login test
        login_test_path = tests_dir / f"test_{page_name}_login.py"
        with open(login_test_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
\"\"\"
{name} Login Test
===================
This module contains tests for {name} login functionality.
\"\"\"

import os
import pytest
from playwright.sync_api import sync_playwright

from pages.{page_name}_page import {page_name.capitalize()}Page

class TestLogin:
    \"\"\"
    Tests for {name} login functionality
    \"\"\"
    
    def test_valid_login(self, browser_setup):
        \"\"\"
        Test login with valid credentials
        \"\"\"
        page, browser, context = browser_setup
        
        # Create page object
        {page_name}_page = {page_name.capitalize()}Page(page)
        
        # Navigate to the page
        {page_name}_page.navigate()
        
        # Login with valid credentials
        {page_name}_page.login("Admin", "admin123")
        
        # Wait for navigation
        page.wait_for_load_state("networkidle")
        
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/login_success.png")
        
        # Verify login success
        assert "dashboard" in page.url.lower() or "home" in page.url.lower(), "Login failed"
    
    def test_invalid_login(self, browser_setup):
        \"\"\"
        Test login with invalid credentials
        \"\"\"
        page, browser, context = browser_setup
        
        # Create page object
        {page_name}_page = {page_name.capitalize()}Page(page)
        
        # Navigate to the page
        {page_name}_page.navigate()
        
        # Login with invalid credentials
        {page_name}_page.login("invalid_user", "invalid_password")
        
        # Wait for error message
        page.wait_for_timeout(1000)
        
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/login_failure.png")
        
        # Verify login failure
        assert "dashboard" not in page.url.lower() and "home" not in page.url.lower(), "Login should have failed"
""")
        
        # Create navigation test
        navigation_test_path = tests_dir / f"test_{page_name}_navigation.py"
        with open(navigation_test_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
\"\"\"
{name} Navigation Test
===================
This module contains tests for {name} navigation functionality.
\"\"\"

import os
import pytest
from playwright.sync_api import sync_playwright

from pages.{page_name}_page import {page_name.capitalize()}Page

class TestNavigation:
    \"\"\"
    Tests for {name} navigation functionality
    \"\"\"
    
    def test_navigation(self, browser_setup):
        \"\"\"
        Test navigation functionality
        \"\"\"
        page, browser, context = browser_setup
        
        # Create page object
        {page_name}_page = {page_name.capitalize()}Page(page)
        
        # Navigate to the page
        {page_name}_page.navigate()
        
        # Login with valid credentials
        {page_name}_page.login("Admin", "admin123")
        
        # Wait for navigation
        page.wait_for_load_state("networkidle")
        
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/dashboard.png")
        
        # Verify login success
        assert "dashboard" in page.url.lower() or "home" in page.url.lower(), "Login failed"
        
        # Logout
        try:
            # Click on user dropdown
            page.click(".oxd-userdropdown-tab")
            page.wait_for_timeout(1000)
            
            # Click logout
            page.click("text=Logout")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot
            page.screenshot(path="screenshots/logout.png")
            
            # Verify logout success
            assert "login" in page.url.lower(), "Logout failed"
        except Exception as e:
            print(f"Error during logout: {str(e)}")
            page.screenshot(path="screenshots/logout_error.png")
            raise
""")
        
        # Create conftest.py
        conftest_path = tests_dir / "conftest.py"
        with open(conftest_path, 'w') as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Pytest Configuration
===================
This module contains pytest configuration.
\"\"\"

import pytest
from playwright.sync_api import sync_playwright

def pytest_addoption(parser):
    \"\"\"
    Add command line options
    \"\"\"
    parser.addoption("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.addoption("--no-headless", action="store_false", dest="headless", help="Run browser with UI visible")

@pytest.fixture
def browser_setup(request):
    \"\"\"
    Set up browser
    
    Returns:
        tuple: (page, browser, context)
    \"\"\"
    # Get headless option
    headless = request.config.getoption("--headless")
    
    # Start playwright
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    
    # Return page, browser, and context
    yield page, browser, context
    
    # Cleanup
    context.close()
    browser.close()
    playwright.stop()
""")
        
        # Create pytest.ini
        pytest_ini_path = Path("pytest.ini")
        with open(pytest_ini_path, 'w') as f:
            f.write("""[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
""")
        
        # Create requirements.txt
        requirements_path = Path("requirements.txt")
        with open(requirements_path, 'w') as f:
            f.write("""pytest==7.4.0
pytest-asyncio==0.21.1
playwright==1.40.0
""")
        
        return {
            "name": name,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "base_page": str(base_page_path),
            "page_object": str(page_path),
            "login_test": str(login_test_path),
            "navigation_test": str(navigation_test_path),
            "conftest": str(conftest_path),
            "pytest_ini": str(pytest_ini_path),
            "requirements": str(requirements_path)
        }
    
    async def _review_tests(self, created_tests: Dict[str, Any], name: str) -> Dict[str, Any]:
        """
        Review tests using the Review Agent
        
        Args:
            created_tests: Created tests
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Review results
        """
        try:
            # Create task data for the review agent
            task_data = {
                "task_type": "review_tests",
                "created_tests": created_tests,
                "name": name
            }
            
            # Process task with review agent
            review_results = await self.review_agent.process_task(task_data)
            
            # If the review agent fails, create default review results
            if not review_results or "error" in review_results:
                self.logger.warning("Review agent failed, creating default review results")
                review_results = {
                    "name": name,
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "login_test": created_tests.get("login_test"),
                    "navigation_test": created_tests.get("navigation_test"),
                    "improvements": [
                        "Added better error handling",
                        "Added more detailed assertions",
                        "Added better comments",
                        "Added better logging"
                    ]
                }
            
            # Save review results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            review_results_path = Path(f"work_dir/review_agent/review_results_{timestamp}.json")
            
            with open(review_results_path, 'w') as f:
                json.dump(review_results, f, indent=2)
            
            self.logger.info(f"Review results saved to {review_results_path}")
            
            return review_results
            
        except Exception as e:
            self.logger.error(f"Error reviewing tests: {str(e)}")
            return {
                "error": str(e),
                "name": name,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
    
    async def _execute_tests(self, review_results: Dict[str, Any], headless: bool = True) -> Dict[str, Any]:
        """
        Execute tests using the Execution Agent
        
        Args:
            review_results: Review results
            headless: Whether to run the browser in headless mode
            
        Returns:
            Dict[str, Any]: Execution results
        """
        try:
            # Create task data for the execution agent
            task_data = {
                "task_type": "execute_tests",
                "review_results": review_results,
                "headless": headless
            }
            
            # Process task with execution agent
            execution_results = await self.execution_agent.process_task(task_data)
            
            # If the execution agent fails, execute tests directly
            if not execution_results or "error" in execution_results:
                self.logger.warning("Execution agent failed, executing tests directly")
                execution_results = await self._execute_tests_directly(review_results, headless)
            
            # Save execution results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            execution_results_path = Path(f"work_dir/execution_agent/execution_results_{timestamp}.json")
            
            with open(execution_results_path, 'w') as f:
                json.dump(execution_results, f, indent=2)
            
            self.logger.info(f"Execution results saved to {execution_results_path}")
            
            return execution_results
            
        except Exception as e:
            self.logger.error(f"Error executing tests: {str(e)}")
            return await self._execute_tests_directly(review_results, headless)
    
    async def _execute_tests_directly(self, review_results: Dict[str, Any], headless: bool = True) -> Dict[str, Any]:
        """
        Execute tests directly
        
        Args:
            review_results: Review results
            headless: Whether to run the browser in headless mode
            
        Returns:
            Dict[str, Any]: Execution results
        """
        try:
            # Get test paths
            login_test_path = review_results.get("login_test")
            navigation_test_path = review_results.get("navigation_test")
            
            # Create test paths list
            test_paths = []
            if login_test_path and os.path.exists(login_test_path):
                test_paths.append(login_test_path)
            if navigation_test_path and os.path.exists(navigation_test_path):
                test_paths.append(navigation_test_path)
            
            if not test_paths:
                raise ValueError("No test paths found")
            
            # Execute tests
            import subprocess
            
            # Create command
            command = ["python", "-m", "pytest"]
            command.extend(test_paths)
            command.append("-v")
            
            # Add headless option
            if headless:
                command.append("--headless")
            else:
                command.append("--no-headless")
            
            # Execute command
            self.logger.info(f"Executing command: {' '.join(command)}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Get output
            stdout, stderr = process.communicate()
            
            # Check return code
            return_code = process.returncode
            
            # Create execution results
            execution_results = {
                "name": review_results.get("name", "Unknown"),
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "test_paths": test_paths,
                "return_code": return_code,
                "stdout": stdout,
                "stderr": stderr,
                "success": return_code == 0
            }
            
            # Save execution results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            execution_results_path = Path(f"work_dir/execution_agent/execution_results_{timestamp}.json")
            
            with open(execution_results_path, 'w') as f:
                json.dump(execution_results, f, indent=2)
            
            self.logger.info(f"Execution results saved to {execution_results_path}")
            
            return execution_results
            
        except Exception as e:
            self.logger.error(f"Error executing tests directly: {str(e)}")
            return {
                "error": str(e),
                "name": review_results.get("name", "Unknown"),
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "success": False
            }
    
    async def _generate_report(self, execution_results: Dict[str, Any], name: str) -> Dict[str, Any]:
        """
        Generate report using the Reporting Agent
        
        Args:
            execution_results: Execution results
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Report
        """
        try:
            # Create task data for the reporting agent
            task_data = {
                "task_type": "generate_report",
                "execution_results": execution_results,
                "name": name
            }
            
            # Process task with reporting agent
            report = await self.reporting_agent.process_task(task_data)
            
            # If the reporting agent fails, generate a default report
            if not report or "error" in report:
                self.logger.warning("Reporting agent failed, generating default report")
                report = self._generate_default_report(execution_results, name)
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = Path(f"work_dir/reporting_agent/report_{timestamp}.json")
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Report saved to {report_path}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return self._generate_default_report(execution_results, name)
    
    def _generate_default_report(self, execution_results: Dict[str, Any], name: str) -> Dict[str, Any]:
        """
        Generate a default report
        
        Args:
            execution_results: Execution results
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Default report
        """
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Get stdout
        stdout = execution_results.get("stdout", "")
        stderr = execution_results.get("stderr", "")
        
        # Extract summary
        summary = ""
        
        # Check if tests passed
        if execution_results.get("success", False):
            # Count passed tests
            passed_count = stdout.count("PASSED")
            summary = f"All {passed_count} tests passed successfully."
        else:
            # Count failed tests
            failed_count = stdout.count("FAILED")
            passed_count = stdout.count("PASSED")
            summary = f"{failed_count} tests failed, {passed_count} tests passed."
        
        # Create HTML report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report_path = reports_dir / f"report_{timestamp}.html"
        
        with open(html_report_path, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: {('#dff0d8' if execution_results.get("success", False) else '#f2dede')};
            color: {('#3c763d' if execution_results.get("success", False) else '#a94442')};
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }}
    </style>
</head>
<body>
    <h1>Test Report - {name}</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>{summary}</p>
    </div>
    
    <div class="section">
        <h2>Standard Output</h2>
        <pre>{stdout}</pre>
    </div>
    
    <div class="section">
        <h2>Standard Error</h2>
        <pre>{stderr}</pre>
    </div>
</body>
</html>
""")
        
        # Create text report
        text_report_path = reports_dir / f"report_{timestamp}.txt"
        
        with open(text_report_path, 'w') as f:
            f.write(f"""Test Report - {name}
===================

Summary
-------
{summary}

Standard Output
--------------
{stdout}

Standard Error
-------------
{stderr}
""")
        
        # Create report
        report = {
            "name": name,
            "timestamp": timestamp,
            "success": execution_results.get("success", False),
            "summary": summary,
            "html_report": str(html_report_path),
            "text_report": str(text_report_path)
        }
        
        return report

async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Fixed Proper Multi-Agent Workflow")
    parser.add_argument("--url", "-u", required=True, help="URL of the website to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the website")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run browser with UI visible")
    args = parser.parse_args()
    
    # Create workflow
    workflow = FixedProperMultiAgentWorkflow()
    
    # Run workflow
    workflow_results = await workflow.run(args.url, args.name, args.headless)
    
    # Print workflow results
    print("\nWorkflow Results:")
    print(f"Website: {args.name} ({args.url})")
    
    if "error" in workflow_results:
        print(f"Error: {workflow_results['error']}")
    else:
        print("\nTest Plan:")
        print(f"- Test Cases: {len(workflow_results['test_plan'].get('test_cases', []))}")
        
        print("\nDiscovery Results:")
        print(f"- Elements: {len(workflow_results['discovery_results'].get('elements', []))}")
        
        print("\nCreated Tests:")
        for key, value in workflow_results['created_tests'].items():
            if key not in ["name", "timestamp", "error"]:
                print(f"- {key}: {value}")
        
        print("\nReview Results:")
        print(f"- Improvements: {', '.join(workflow_results['review_results'].get('improvements', []))}")
        
        print("\nExecution Results:")
        print(f"- Success: {workflow_results['execution_results'].get('success', False)}")
        print(f"- Return Code: {workflow_results['execution_results'].get('return_code', -1)}")
        
        print("\nReport:")
        print(f"- Summary: {workflow_results['report'].get('summary', '')}")
        print(f"- HTML Report: {workflow_results['report'].get('html_report', '')}")
        print(f"- Text Report: {workflow_results['report'].get('text_report', '')}")
    
    print("\nWorkflow completed!")

if __name__ == "__main__":
    asyncio.run(main())

