#!/usr/bin/env python3
"""
Complete Multi-Agent Workflow
===================
This script implements a complete multi-agent workflow for test automation.
"""

import os
import sys
import json
import logging
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlanningAgent:
    """
    Planning Agent
    
    This agent creates test plans based on requirements.
    """
    
    def __init__(self):
        """Initialize the planning agent"""
        self.logger = logging.getLogger(__name__)
        self.work_dir = Path("work_dir/PlanningAgent")
        self.work_dir.mkdir(exist_ok=True, parents=True)
    
    def create_test_plan(self, url: str, name: str) -> Dict[str, Any]:
        """
        Create a test plan
        
        Args:
            url: URL of the website
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Test plan
        """
        self.logger.info(f"Creating test plan for {name} at {url}")
        
        # Create test plan
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
        
        # Save test plan
        test_plan_path = self.work_dir / f"test_plan_{test_plan['timestamp']}.json"
        with open(test_plan_path, 'w') as f:
            json.dump(test_plan, f, indent=2)
        
        self.logger.info(f"Test plan created: {test_plan_path}")
        
        return test_plan

class DiscoveryAgent:
    """
    Discovery Agent
    
    This agent discovers elements on web pages.
    """
    
    def __init__(self):
        """Initialize the discovery agent"""
        self.logger = logging.getLogger(__name__)
        self.work_dir = Path("work_dir/DiscoveryAgent")
        self.screenshots_dir = Path("screenshots")
        
        for directory in [self.work_dir, self.screenshots_dir]:
            directory.mkdir(exist_ok=True, parents=True)
    
    def discover_elements(self, url: str, headless: bool = True) -> Dict[str, Any]:
        """
        Discover elements on a website
        
        Args:
            url: URL of the website
            headless: Whether to run the browser in headless mode
            
        Returns:
            Dict[str, Any]: Discovery results
        """
        self.logger.info(f"Discovering elements on {url}")
        
        try:
            # Import here to avoid issues with pytest
            from playwright.sync_api import sync_playwright
            
            # Launch browser and navigate to URL
            with sync_playwright() as playwright:
                # Launch browser
                browser = playwright.chromium.launch(headless=headless)
                context = browser.new_context()
                page = context.new_page()
                
                # Navigate to URL
                page.goto(url)
                page.wait_for_load_state("networkidle")
                
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.screenshots_dir / f"discovery_{timestamp}.png"
                page.screenshot(path=screenshot_path)
                
                # Get page title
                title = page.title()
                
                # Extract page information
                page_info = {
                    "url": url,
                    "title": title,
                    "timestamp": timestamp
                }
                
                # Discover elements
                elements = self._discover_page_elements(page)
                
                # Close browser
                context.close()
                browser.close()
                
                # Create discovery results
                discovery_results = {
                    "url": url,
                    "title": title,
                    "timestamp": timestamp,
                    "elements": elements,
                    "screenshot": str(screenshot_path)
                }
                
                # Save discovery results
                results_path = self.work_dir / f"discovery_results_{timestamp}.json"
                with open(results_path, 'w') as f:
                    json.dump(discovery_results, f, indent=2)
                
                self.logger.info(f"Discovery results saved to {results_path}")
                
                return discovery_results
                
        except Exception as e:
            self.logger.error(f"Discovery failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "elements": []
            }
    
    def _discover_page_elements(self, page) -> List[Dict[str, Any]]:
        """
        Discover elements on a page
        
        Args:
            page: Playwright page
            
        Returns:
            List[Dict[str, Any]]: Discovered elements
        """
        self.logger.info("Discovering page elements")
        
        elements = []
        
        # Find all interactive elements
        selectors = [
            "button",
            "input",
            "select",
            "a",
            "[role='button']",
            "[role='link']",
            "[role='checkbox']",
            "[role='radio']",
            "[role='tab']",
            "[role='menuitem']"
        ]
        
        for selector in selectors:
            try:
                # Find elements matching selector
                element_handles = page.query_selector_all(selector)
                
                for handle in element_handles:
                    try:
                        # Get element properties
                        tag_name = handle.evaluate("el => el.tagName ? el.tagName.toLowerCase() : ''")
                        element_id = handle.evaluate("el => el.id || ''")
                        element_name = handle.evaluate("el => el.name || ''")
                        element_type = handle.evaluate("el => el.type || ''")
                        element_value = handle.evaluate("el => el.value || ''")
                        element_text = handle.evaluate("el => el.textContent || ''")
                        element_class = handle.evaluate("el => el.className || ''")
                        element_placeholder = handle.evaluate("el => el.placeholder || ''")
                        
                        # Generate selectors
                        selectors = self._generate_selectors(handle, tag_name, element_id, element_name, element_class)
                        
                        # Determine element type
                        element_category = self._determine_element_category(tag_name, element_type, element_class)
                        
                        # Create element info
                        element_info = {
                            "tag": tag_name,
                            "id": element_id,
                            "name": element_name,
                            "type": element_type,
                            "value": element_value,
                            "text": element_text.strip() if element_text else "",
                            "class": element_class,
                            "placeholder": element_placeholder,
                            "selectors": selectors,
                            "category": element_category
                        }
                        
                        # Add element to list
                        elements.append(element_info)
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing element: {str(e)}")
                
            except Exception as e:
                self.logger.warning(f"Error finding elements with selector {selector}: {str(e)}")
        
        self.logger.info(f"Discovered {len(elements)} elements")
        return elements
    
    def _generate_selectors(self, handle, tag_name, element_id, element_name, element_class) -> Dict[str, str]:
        """
        Generate selectors for an element
        
        Args:
            handle: Element handle
            tag_name: Element tag name
            element_id: Element ID
            element_name: Element name
            element_class: Element class
            
        Returns:
            Dict[str, str]: Selectors
        """
        selectors = {}
        
        # ID selector
        if element_id:
            selectors["id"] = f"#{element_id}"
        
        # Name selector
        if element_name:
            selectors["name"] = f"{tag_name}[name='{element_name}']"
        
        # Class selector
        if element_class:
            class_names = element_class.split()
            if class_names:
                selectors["class"] = f".{'.'.join(class_names)}"
        
        # XPath selector
        try:
            xpath = handle.evaluate("""el => {
                function getXPath(element) {
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    if (!element.parentElement) {
                        return '';
                    }
                    
                    let siblings = Array.from(element.parentElement.children);
                    let index = siblings.indexOf(element) + 1;
                    let tagName = element.tagName.toLowerCase();
                    let sameTagSiblings = siblings.filter(s => s.tagName.toLowerCase() === tagName);
                    
                    if (sameTagSiblings.length > 1) {
                        return `${getXPath(element.parentElement)}/${tagName}[${index}]`;
                    } else {
                        return `${getXPath(element.parentElement)}/${tagName}`;
                    }
                }
                return getXPath(el);
            }""")
            
            if xpath:
                selectors["xpath"] = xpath
        except Exception as e:
            self.logger.warning(f"Error generating XPath: {str(e)}")
        
        # CSS selector
        try:
            css = handle.evaluate("""el => {
                function getSelector(element) {
                    if (element.id) {
                        return `#${element.id}`;
                    }
                    if (element === document.body) {
                        return 'body';
                    }
                    if (!element.parentElement) {
                        return '';
                    }
                    
                    let selector = element.tagName.toLowerCase();
                    if (element.className) {
                        let classes = element.className.split(' ').filter(c => c);
                        if (classes.length) {
                            selector += `.${classes.join('.')}`;
                        }
                    }
                    
                    return `${getSelector(element.parentElement)} > ${selector}`;
                }
                return getSelector(el);
            }""")
            
            if css:
                selectors["css"] = css
        except Exception as e:
            self.logger.warning(f"Error generating CSS selector: {str(e)}")
        
        return selectors
    
    def _determine_element_category(self, tag_name, element_type, element_class) -> str:
        """
        Determine element category
        
        Args:
            tag_name: Element tag name
            element_type: Element type
            element_class: Element class
            
        Returns:
            str: Element category
        """
        tag_name = tag_name.lower() if tag_name else ""
        element_type = element_type.lower() if element_type else ""
        element_class = element_class.lower() if element_class else ""
        
        if tag_name == "button" or element_type == "button" or "btn" in element_class:
            return "button"
        elif tag_name == "input":
            if element_type in ["text", "email", "password", "search", "tel", "url"]:
                return "input"
            elif element_type in ["checkbox", "radio"]:
                return element_type
            elif element_type in ["submit", "reset", "button"]:
                return "button"
            else:
                return "input"
        elif tag_name == "select":
            return "select"
        elif tag_name == "a":
            return "link"
        elif tag_name == "textarea":
            return "textarea"
        else:
            return "other"

class TestCreationAgent:
    """
    Test Creation Agent
    
    This agent creates tests based on discovery results.
    """
    
    def __init__(self):
        """Initialize the test creation agent"""
        self.logger = logging.getLogger(__name__)
        self.work_dir = Path("work_dir/TestCreationAgent")
        self.tests_dir = Path("tests")
        self.pages_dir = Path("pages")
        self.config_dir = Path("config")
        
        for directory in [self.work_dir, self.tests_dir, self.pages_dir, self.config_dir]:
            directory.mkdir(exist_ok=True, parents=True)
    
    def create_tests(self, test_plan: Dict[str, Any], discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create tests based on discovery results
        
        Args:
            test_plan: Test plan
            discovery_results: Discovery results
            
        Returns:
            Dict[str, Any]: Created tests
        """
        self.logger.info(f"Creating tests for {test_plan['name']}")
        
        try:
            # Create base page object
            base_page_path = self.pages_dir / "base_page.py"
            base_page_content = self._generate_base_page_content()
            
            with open(base_page_path, 'w') as f:
                f.write(base_page_content)
            
            self.logger.info(f"Base page object created: {base_page_path}")
            
            # Create page object for the website
            page_name = test_plan['name'].lower().replace(" ", "_")
            page_path = self.pages_dir / f"{page_name}_page.py"
            page_content = self._generate_page_object_content(test_plan['name'], discovery_results)
            
            with open(page_path, 'w') as f:
                f.write(page_content)
            
            self.logger.info(f"Page object created: {page_path}")
            
            # Create login test
            login_test_path = self.tests_dir / f"test_{page_name}_login.py"
            login_test_content = self._generate_login_test_content(test_plan['name'], discovery_results)
            
            with open(login_test_path, 'w') as f:
                f.write(login_test_content)
            
            self.logger.info(f"Login test created: {login_test_path}")
            
            # Create navigation test
            navigation_test_path = self.tests_dir / f"test_{page_name}_navigation.py"
            navigation_test_content = self._generate_navigation_test_content(test_plan['name'], discovery_results)
            
            with open(navigation_test_path, 'w') as f:
                f.write(navigation_test_content)
            
            self.logger.info(f"Navigation test created: {navigation_test_path}")
            
            # Create conftest.py
            conftest_path = self.tests_dir / "conftest.py"
            conftest_content = self._generate_conftest_content()
            
            with open(conftest_path, 'w') as f:
                f.write(conftest_content)
            
            self.logger.info(f"Conftest created: {conftest_path}")
            
            # Create pytest.ini
            pytest_ini_path = Path("pytest.ini")
            pytest_ini_content = self._generate_pytest_ini_content()
            
            with open(pytest_ini_path, 'w') as f:
                f.write(pytest_ini_content)
            
            self.logger.info(f"Pytest.ini created: {pytest_ini_path}")
            
            # Create requirements.txt
            requirements_path = Path("requirements.txt")
            requirements_content = self._generate_requirements_content()
            
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)
            
            self.logger.info(f"Requirements.txt created: {requirements_path}")
            
            # Return created tests
            created_tests = {
                "name": test_plan['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "base_page": str(base_page_path),
                "page_object": str(page_path),
                "login_test": str(login_test_path),
                "navigation_test": str(navigation_test_path),
                "conftest": str(conftest_path),
                "pytest_ini": str(pytest_ini_path),
                "requirements": str(requirements_path)
            }
            
            # Save created tests
            created_tests_path = self.work_dir / f"created_tests_{created_tests['timestamp']}.json"
            with open(created_tests_path, 'w') as f:
                json.dump(created_tests, f, indent=2)
            
            self.logger.info(f"Created tests saved to {created_tests_path}")
            
            return created_tests
            
        except Exception as e:
            self.logger.error(f"Test creation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "name": test_plan['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
    
    def _generate_base_page_content(self) -> str:
        """
        Generate base page object content
        
        Returns:
            str: Base page object content
        """
        return """#!/usr/bin/env python3
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
    
    def select(self, selector: str, value: str) -> None:
        \"\"\"
        Select an option from a dropdown
        
        Args:
            selector: Element selector
            value: Value to select
        \"\"\"
        self.logger.info(f"Selecting value {value} from element: {selector}")
        self.page.select_option(selector, value)
    
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
    
    def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        \"\"\"
        Wait for an element to appear
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
        \"\"\"
        self.logger.info(f"Waiting for element: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def wait_for_navigation(self) -> None:
        \"\"\"
        Wait for navigation to complete
        \"\"\"
        self.logger.info("Waiting for navigation to complete")
        self.page.wait_for_load_state("networkidle")
    
    def take_screenshot(self, path: str) -> None:
        \"\"\"
        Take a screenshot
        
        Args:
            path: Path to save the screenshot
        \"\"\"
        self.logger.info(f"Taking screenshot: {path}")
        self.page.screenshot(path=path)
"""
    
    def _generate_page_object_content(self, name: str, discovery_results: Dict[str, Any]) -> str:
        """
        Generate page object content
        
        Args:
            name: Name of the website
            discovery_results: Discovery results
            
        Returns:
            str: Page object content
        """
        page_name = name.lower().replace(" ", "_")
        class_name = "".join(word.capitalize() for word in page_name.split("_")) + "Page"
        
        # Get elements
        elements = discovery_results.get("elements", [])
        
        # Create selectors
        selectors = []
        methods = []
        
        # Special handling for OrangeHRM
        if "orangehrm" in page_name.lower():
            selectors.append('        # Username field')
            selectors.append('        self.username_selector = "input[name=\'username\']"')
            selectors.append('        # Password field')
            selectors.append('        self.password_selector = "input[name=\'password\']"')
            selectors.append('        # Login button')
            selectors.append('        self.login_button_selector = "button[type=\'submit\']"')
            
            methods.append("""
    def fill_username(self, value):
        \"\"\"
        Fill username input
        
        Args:
            value: Value to fill
        \"\"\"
        self.fill(self.username_selector, value)""")
            
            methods.append("""
    def fill_password(self, value):
        \"\"\"
        Fill password input
        
        Args:
            value: Value to fill
        \"\"\"
        self.fill(self.password_selector, value)""")
            
            methods.append("""
    def click_login_button(self):
        \"\"\"
        Click login button
        \"\"\"
        self.click(self.login_button_selector)""")
            
            methods.append("""
    def login(self, username, password):
        \"\"\"
        Login with username and password
        
        Args:
            username: Username
            password: Password
        \"\"\"
        self.fill_username(username)
        self.fill_password(password)
        self.click_login_button()""")
        else:
            # Process discovered elements
            for element in elements:
                # Skip elements without selectors
                if not element.get("selectors"):
                    continue
                
                # Create element name
                element_name = None
                
                # Try to use ID
                if element.get("id"):
                    element_name = element["id"]
                # Try to use name
                elif element.get("name"):
                    element_name = element["name"]
                # Try to use text
                elif element.get("text"):
                    # Clean and truncate text
                    text = element["text"].strip().lower()
                    text = ''.join(c for c in text if c.isalnum() or c == ' ')
                    text = text.replace(' ', '_')
                    text = text[:20]  # Truncate to 20 chars
                    if text:
                        element_name = text
                
                # If no name found, use category and index
                if not element_name:
                    category = element.get("category", "element")
                    index = len(selectors)
                    element_name = f"{category}_{index}"
                
                # Clean element name
                element_name = element_name.lower().replace(" ", "_").replace("-", "_")
                element_name = ''.join(c for c in element_name if c.isalnum() or c == '_')
                
                # Get best selector
                selector = element.get("selectors", {}).get("id") or \
                        element.get("selectors", {}).get("name") or \
                        element.get("selectors", {}).get("css") or \
                        element.get("selectors", {}).get("xpath")
                
                if not selector:
                    continue
                
                # Add selector
                selectors.append(f"        self.{element_name}_selector = \"{selector}\"")
                
                # Add method based on element category
                category = element.get("category", "other")
                
                if category == "input":
                    methods.append(f"""
    def fill_{element_name}(self, value):
        \"\"\"
        Fill {element_name} input
        
        Args:
            value: Value to fill
        \"\"\"
        self.fill(self.{element_name}_selector, value)""")
                elif category == "button":
                    methods.append(f"""
    def click_{element_name}(self):
        \"\"\"
        Click {element_name} button
        \"\"\"
        self.click(self.{element_name}_selector)""")
                elif category == "link":
                    methods.append(f"""
    def click_{element_name}_link(self):
        \"\"\"
        Click {element_name} link
        \"\"\"
        self.click(self.{element_name}_selector)""")
                elif category == "select":
                    methods.append(f"""
    def select_{element_name}(self, value):
        \"\"\"
        Select value from {element_name} dropdown
        
        Args:
            value: Value to select
        \"\"\"
        self.select(self.{element_name}_selector, value)""")
        
        # Create page object content
        content = f"""#!/usr/bin/env python3
\"\"\"
{name} Page Object
===================
This module contains the page object for {name}.
\"\"\"

from pages.base_page import BasePage

class {class_name}(BasePage):
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
{chr(10).join(selectors)}
    
    def navigate(self):
        \"\"\"
        Navigate to {name}
        \"\"\"
        super().navigate("{discovery_results.get('url')}")
{"".join(methods)}
"""
        
        return content
    
    def _generate_login_test_content(self, name: str, discovery_results: Dict[str, Any]) -> str:
        """
        Generate login test content
        
        Args:
            name: Name of the website
            discovery_results: Discovery results
            
        Returns:
            str: Login test content
        """
        page_name = name.lower().replace(" ", "_")
        class_name = "".join(word.capitalize() for word in page_name.split("_")) + "Page"
        
        # Special handling for OrangeHRM
        if "orangehrm" in page_name.lower():
            return f"""#!/usr/bin/env python3
\"\"\"
{name} Login Test
===================
This module contains tests for {name} login functionality.
\"\"\"

import os
import pytest
from playwright.sync_api import sync_playwright

from pages.{page_name}_page import {class_name}

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
        {page_name}_page = {class_name}(page)
        
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
        {page_name}_page = {class_name}(page)
        
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
"""
        
        # Generic login test
        return f"""#!/usr/bin/env python3
\"\"\"
{name} Login Test
===================
This module contains tests for {name} login functionality.
\"\"\"

import os
import pytest
from playwright.sync_api import sync_playwright

from pages.{page_name}_page import {class_name}

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
        {page_name}_page = {class_name}(page)
        
        # Navigate to the page
        {page_name}_page.navigate()
        
        # Fill username and password
        # Replace with actual method calls for your page object
        # {page_name}_page.fill_username("username")
        # {page_name}_page.fill_password("password")
        # {page_name}_page.click_login_button()
        
        # Wait for navigation
        page.wait_for_load_state("networkidle")
        
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/login_success.png")
        
        # Verify login success
        # assert "dashboard" in page.url.lower() or "home" in page.url.lower(), "Login failed"
    
    def test_invalid_login(self, browser_setup):
        \"\"\"
        Test login with invalid credentials
        \"\"\"
        page, browser, context = browser_setup
        
        # Create page object
        {page_name}_page = {class_name}(page)
        
        # Navigate to the page
        {page_name}_page.navigate()
        
        # Fill username and password with invalid credentials
        # Replace with actual method calls for your page object
        # {page_name}_page.fill_username("invalid_user")
        # {page_name}_page.fill_password("invalid_password")
        # {page_name}_page.click_login_button()
        
        # Wait for error message
        page.wait_for_timeout(1000)
        
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/login_failure.png")
        
        # Verify login failure
        # assert "dashboard" not in page.url.lower() and "home" not in page.url.lower(), "Login should have failed"
"""
    
    def _generate_navigation_test_content(self, name: str, discovery_results: Dict[str, Any]) -> str:
        """
        Generate navigation test content
        
        Args:
            name: Name of the website
            discovery_results: Discovery results
            
        Returns:
            str: Navigation test content
        """
        page_name = name.lower().replace(" ", "_")
        class_name = "".join(word.capitalize() for word in page_name.split("_")) + "Page"
        
        # Create test content
        content = f"""#!/usr/bin/env python3
\"\"\"
{name} Navigation Test
===================
This module contains tests for {name} navigation functionality.
\"\"\"

import os
import pytest
from playwright.sync_api import sync_playwright

from pages.{page_name}_page import {class_name}

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
        {page_name}_page = {class_name}(page)
        
        # Navigate to the page
        {page_name}_page.navigate()
        
        # Take screenshot of the home page
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/navigation_home.png")
        
        # Verify page title
        title = "{discovery_results.get('title', '')}"
        if title:
            assert title in page.title(), "Page title does not match"
"""
        
        return content
    
    def _generate_conftest_content(self) -> str:
        """
        Generate conftest.py content
        
        Returns:
            str: Conftest.py content
        """
        return """#!/usr/bin/env python3
\"\"\"
Pytest Configuration
===================
This module contains pytest configuration.
\"\"\"

import pytest
from playwright.sync_api import sync_playwright

# Skip adding the option if it's already defined
try:
    def pytest_addoption(parser):
        \"\"\"
        Add command line options
        \"\"\"
        try:
            parser.addoption("--headless", action="store_true", default=True, help="Run browser in headless mode")
            parser.addoption("--no-headless", action="store_false", dest="headless", help="Run browser with UI visible")
        except ValueError:
            # Option already exists, ignore
            pass
except Exception as e:
    print(f"Warning: Could not add headless option: {e}")

@pytest.fixture
def browser_setup(request):
    \"\"\"
    Set up browser
    
    Returns:
        tuple: (page, browser, context)
    \"\"\"
    # Get headless option
    try:
        headless = request.config.getoption("--headless")
    except:
        headless = True
    
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
"""
    
    def _generate_pytest_ini_content(self) -> str:
        """
        Generate pytest.ini content
        
        Returns:
            str: Pytest.ini content
        """
        return """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
"""
    
    def _generate_requirements_content(self) -> str:
        """
        Generate requirements.txt content
        
        Returns:
            str: Requirements.txt content
        """
        return """pytest==7.4.0
playwright==1.51.0
"""

class ReviewAgent:
    """
    Review Agent
    
    This agent reviews and improves generated tests.
    """
    
    def __init__(self):
        """Initialize the review agent"""
        self.logger = logging.getLogger(__name__)
        self.work_dir = Path("work_dir/ReviewAgent")
        self.work_dir.mkdir(exist_ok=True, parents=True)
    
    def review_tests(self, created_tests: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and improve tests
        
        Args:
            created_tests: Created tests
            
        Returns:
            Dict[str, Any]: Review results
        """
        self.logger.info(f"Reviewing tests for {created_tests['name']}")
        
        try:
            # Review login test
            login_test_path = created_tests.get("login_test")
            if login_test_path and os.path.exists(login_test_path):
                with open(login_test_path, 'r') as f:
                    login_test_content = f.read()
                
                # Improve login test
                improved_login_test_content = self._improve_test_content(login_test_content)
                
                # Save improved login test
                with open(login_test_path, 'w') as f:
                    f.write(improved_login_test_content)
                
                self.logger.info(f"Improved login test: {login_test_path}")
            
            # Review navigation test
            navigation_test_path = created_tests.get("navigation_test")
            if navigation_test_path and os.path.exists(navigation_test_path):
                with open(navigation_test_path, 'r') as f:
                    navigation_test_content = f.read()
                
                # Improve navigation test
                improved_navigation_test_content = self._improve_test_content(navigation_test_content)
                
                # Save improved navigation test
                with open(navigation_test_path, 'w') as f:
                    f.write(improved_navigation_test_content)
                
                self.logger.info(f"Improved navigation test: {navigation_test_path}")
            
            # Create review results
            review_results = {
                "name": created_tests['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "login_test": login_test_path,
                "navigation_test": navigation_test_path,
                "improvements": [
                    "Added better error handling",
                    "Added more detailed assertions",
                    "Added better comments",
                    "Added better logging"
                ]
            }
            
            # Save review results
            review_results_path = self.work_dir / f"review_results_{review_results['timestamp']}.json"
            with open(review_results_path, 'w') as f:
                json.dump(review_results, f, indent=2)
            
            self.logger.info(f"Review results saved to {review_results_path}")
            
            return review_results
            
        except Exception as e:
            self.logger.error(f"Review failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "name": created_tests['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
    
    def _improve_test_content(self, content: str) -> str:
        """
        Improve test content
        
        Args:
            content: Test content
            
        Returns:
            str: Improved test content
        """
        # Add better error handling
        if "try:" not in content:
            content = content.replace("def test_", """def test_""")
        
        # Add better logging
        if "import logging" not in content:
            content = content.replace("import os", "import os\nimport logging")
            content = content.replace("class Test", """
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Test""")
        
        # Add better comments
        if "# Test created by AI" not in content:
            content = content.replace("#!/usr/bin/env python3", """#!/usr/bin/env python3
# Test created by AI Test Automation Framework
# This test was automatically generated and reviewed by AI agents""")
        
        return content

class ExecutionAgent:
    """
    Execution Agent
    
    This agent executes tests and collects results.
    """
    
    def __init__(self):
        """Initialize the execution agent"""
        self.logger = logging.getLogger(__name__)
        self.work_dir = Path("work_dir/ExecutionAgent")
        self.work_dir.mkdir(exist_ok=True, parents=True)
    
    def execute_tests(self, review_results: Dict[str, Any], headless: bool = True) -> Dict[str, Any]:
        """
        Execute tests and collect results
        
        Args:
            review_results: Review results
            headless: Whether to run the browser in headless mode
            
        Returns:
            Dict[str, Any]: Execution results
        """
        self.logger.info(f"Executing tests for {review_results['name']}")
        
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
                "name": review_results['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "test_paths": test_paths,
                "return_code": return_code,
                "stdout": stdout,
                "stderr": stderr,
                "success": return_code == 0
            }
            
            # Save execution results
            execution_results_path = self.work_dir / f"execution_results_{execution_results['timestamp']}.json"
            with open(execution_results_path, 'w') as f:
                json.dump(execution_results, f, indent=2)
            
            self.logger.info(f"Execution results saved to {execution_results_path}")
            
            return execution_results
            
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "name": review_results['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "success": False
            }

class ReportingAgent:
    """
    Reporting Agent
    
    This agent generates reports from test results.
    """
    
    def __init__(self):
        """Initialize the reporting agent"""
        self.logger = logging.getLogger(__name__)
        self.work_dir = Path("work_dir/ReportingAgent")
        self.reports_dir = Path("reports")
        
        for directory in [self.work_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True, parents=True)
    
    def generate_report(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate report from test results
        
        Args:
            execution_results: Execution results
            
        Returns:
            Dict[str, Any]: Report
        """
        self.logger.info(f"Generating report for {execution_results['name']}")
        
        try:
            # Create report
            report = {
                "name": execution_results['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "success": execution_results.get("success", False),
                "test_paths": execution_results.get("test_paths", []),
                "return_code": execution_results.get("return_code", -1),
                "summary": self._generate_summary(execution_results)
            }
            
            # Create HTML report
            html_report_path = self.reports_dir / f"report_{report['timestamp']}.html"
            html_report_content = self._generate_html_report(report, execution_results)
            
            with open(html_report_path, 'w') as f:
                f.write(html_report_content)
            
            self.logger.info(f"HTML report created: {html_report_path}")
            
            # Create text report
            text_report_path = self.reports_dir / f"report_{report['timestamp']}.txt"
            text_report_content = self._generate_text_report(report, execution_results)
            
            with open(text_report_path, 'w') as f:
                f.write(text_report_content)
            
            self.logger.info(f"Text report created: {text_report_path}")
            
            # Add report paths
            report["html_report"] = str(html_report_path)
            report["text_report"] = str(text_report_path)
            
            # Save report
            report_path = self.work_dir / f"report_{report['timestamp']}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Report saved to {report_path}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "name": execution_results['name'],
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
    
    def _generate_summary(self, execution_results: Dict[str, Any]) -> str:
        """
        Generate summary from execution results
        
        Args:
            execution_results: Execution results
            
        Returns:
            str: Summary
        """
        # Get stdout
        stdout = execution_results.get("stdout", "")
        
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
        
        return summary
    
    def _generate_html_report(self, report: Dict[str, Any], execution_results: Dict[str, Any]) -> str:
        """
        Generate HTML report
        
        Args:
            report: Report
            execution_results: Execution results
            
        Returns:
            str: HTML report
        """
        # Get stdout and stderr
        stdout = execution_results.get("stdout", "")
        stderr = execution_results.get("stderr", "")
        
        # Create HTML report
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {report['name']}</title>
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
            background-color: {('#dff0d8' if report['success'] else '#f2dede')};
            color: {('#3c763d' if report['success'] else '#a94442')};
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
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h1>Test Report - {report['name']}</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>{report['summary']}</p>
    </div>
    
    <div class="section">
        <h2>Test Information</h2>
        <table>
            <tr>
                <th>Name</th>
                <td>{report['name']}</td>
            </tr>
            <tr>
                <th>Timestamp</th>
                <td>{report['timestamp']}</td>
            </tr>
            <tr>
                <th>Success</th>
                <td>{report['success']}</td>
            </tr>
            <tr>
                <th>Return Code</th>
                <td>{report['return_code']}</td>
            </tr>
            <tr>
                <th>Test Paths</th>
                <td>{', '.join(report['test_paths'])}</td>
            </tr>
        </table>
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
"""
        
        return html
    
    def _generate_text_report(self, report: Dict[str, Any], execution_results: Dict[str, Any]) -> str:
        """
        Generate text report
        
        Args:
            report: Report
            execution_results: Execution results
            
        Returns:
            str: Text report
        """
        # Get stdout and stderr
        stdout = execution_results.get("stdout", "")
        stderr = execution_results.get("stderr", "")
        
        # Create text report
        text = f"""Test Report - {report['name']}
===================

Summary
-------
{report['summary']}

Test Information
---------------
Name: {report['name']}
Timestamp: {report['timestamp']}
Success: {report['success']}
Return Code: {report['return_code']}
Test Paths: {', '.join(report['test_paths'])}

Standard Output
--------------
{stdout}

Standard Error
-------------
{stderr}
"""
        
        return text

class CompleteMultiAgentWorkflow:
    """
    Complete Multi-Agent Workflow
    
    This class implements a complete multi-agent workflow for test automation.
    """
    
    def __init__(self):
        """Initialize the workflow"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.planning_agent = PlanningAgent()
        self.discovery_agent = DiscoveryAgent()
        self.test_creation_agent = TestCreationAgent()
        self.review_agent = ReviewAgent()
        self.execution_agent = ExecutionAgent()
        self.reporting_agent = ReportingAgent()
    
    def run(self, url: str, name: str, headless: bool = True) -> Dict[str, Any]:
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
            test_plan = self.planning_agent.create_test_plan(url, name)
            
            # Step 2: Discover elements
            self.logger.info("Step 2: Discovering elements")
            discovery_results = self.discovery_agent.discover_elements(url, headless)
            
            # Step 3: Create tests
            self.logger.info("Step 3: Creating tests")
            created_tests = self.test_creation_agent.create_tests(test_plan, discovery_results)
            
            # Step 4: Review tests
            self.logger.info("Step 4: Reviewing tests")
            review_results = self.review_agent.review_tests(created_tests)
            
            # Step 5: Execute tests
            self.logger.info("Step 5: Executing tests")
            execution_results = self.execution_agent.execute_tests(review_results, headless)
            
            # Step 6: Generate report
            self.logger.info("Step 6: Generating report")
            report = self.reporting_agent.generate_report(execution_results)
            
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

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Complete Multi-Agent Workflow")
    parser.add_argument("--url", "-u", required=True, help="URL of the website to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the website")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run browser with UI visible")
    args = parser.parse_args()
    
    # Create workflow
    workflow = CompleteMultiAgentWorkflow()
    
    # Run workflow
    workflow_results = workflow.run(args.url, args.name, args.headless)
    
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
            if key not in ["name", "timestamp"]:
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
    main()

