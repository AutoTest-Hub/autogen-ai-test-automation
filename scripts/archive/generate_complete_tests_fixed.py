#!/usr/bin/env python3
"""
Generate Complete Tests (Fixed)
===================
This script generates complete tests for a website.
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

from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestGenerator:
    """
    Test Generator
    
    This class generates complete tests for a website.
    """
    
    def __init__(self):
        """Initialize the test generator"""
        # Create directories
        self.work_dir = Path("work_dir/TestGenerator")
        self.screenshots_dir = Path("screenshots")
        self.tests_dir = Path("tests")
        self.pages_dir = Path("pages")
        self.config_dir = Path("config")
        
        for directory in [self.work_dir, self.screenshots_dir, self.tests_dir, self.pages_dir, self.config_dir]:
            directory.mkdir(exist_ok=True, parents=True)
    
    async def generate_tests(self, url: str, name: str) -> Dict[str, Any]:
        """
        Generate tests for a website
        
        Args:
            url: URL of the website
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Generation results
        """
        logger.info(f"Generating tests for {name} at {url}")
        
        try:
            # Step 1: Discover elements
            discovery_results = await self._discover_elements(url)
            
            # Step 2: Generate page objects
            page_objects = self._generate_page_objects(name, discovery_results)
            
            # Step 3: Generate tests
            tests = self._generate_tests(name, discovery_results, page_objects)
            
            # Step 4: Generate configuration
            config = self._generate_config(name)
            
            # Return generation results
            generation_results = {
                "name": name,
                "url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "discovery_results": discovery_results,
                "page_objects": page_objects,
                "tests": tests,
                "config": config
            }
            
            logger.info(f"Tests generated successfully for {name}")
            return generation_results
            
        except Exception as e:
            logger.error(f"Test generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    async def _discover_elements(self, url: str) -> Dict[str, Any]:
        """
        Discover elements on a website
        
        Args:
            url: URL of the website
            
        Returns:
            Dict[str, Any]: Discovery results
        """
        logger.info(f"Discovering elements on {url}")
        
        try:
            # Launch browser and navigate to URL
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to URL
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.screenshots_dir / f"discovery_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                
                # Get page title
                title = await page.title()
                
                # Extract page information
                page_info = {
                    "url": url,
                    "title": title,
                    "timestamp": timestamp
                }
                
                # Discover elements
                elements = await self._discover_page_elements(page)
                
                # Close browser
                await context.close()
                await browser.close()
                
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
                
                logger.info(f"Discovery results saved to {results_path}")
                
                return discovery_results
                
        except Exception as e:
            logger.error(f"Discovery failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "elements": []
            }
    
    async def _discover_page_elements(self, page) -> List[Dict[str, Any]]:
        """
        Discover elements on a page
        
        Args:
            page: Playwright page
            
        Returns:
            List[Dict[str, Any]]: Discovered elements
        """
        logger.info("Discovering page elements")
        
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
                element_handles = await page.query_selector_all(selector)
                
                for handle in element_handles:
                    try:
                        # Get element properties
                        tag_name = await handle.evaluate("el => el.tagName ? el.tagName.toLowerCase() : ''")
                        element_id = await handle.evaluate("el => el.id || ''")
                        element_name = await handle.evaluate("el => el.name || ''")
                        element_type = await handle.evaluate("el => el.type || ''")
                        element_value = await handle.evaluate("el => el.value || ''")
                        element_text = await handle.evaluate("el => el.textContent || ''")
                        element_class = await handle.evaluate("el => el.className || ''")
                        element_placeholder = await handle.evaluate("el => el.placeholder || ''")
                        
                        # Generate selectors
                        selectors = await self._generate_selectors(handle, tag_name, element_id, element_name, element_class)
                        
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
                        logger.warning(f"Error processing element: {str(e)}")
                
            except Exception as e:
                logger.warning(f"Error finding elements with selector {selector}: {str(e)}")
        
        logger.info(f"Discovered {len(elements)} elements")
        return elements
    
    async def _generate_selectors(self, handle, tag_name, element_id, element_name, element_class) -> Dict[str, str]:
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
            xpath = await handle.evaluate("""el => {
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
            logger.warning(f"Error generating XPath: {str(e)}")
        
        # CSS selector
        try:
            css = await handle.evaluate("""el => {
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
            logger.warning(f"Error generating CSS selector: {str(e)}")
        
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
    
    def _generate_page_objects(self, name: str, discovery_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate page objects
        
        Args:
            name: Name of the website
            discovery_results: Discovery results
            
        Returns:
            List[Dict[str, Any]]: Generated page objects
        """
        logger.info(f"Generating page objects for {name}")
        
        page_objects = []
        
        try:
            # Create base page object
            base_page_path = self.pages_dir / "base_page.py"
            base_page_content = self._generate_base_page_content()
            
            with open(base_page_path, 'w') as f:
                f.write(base_page_content)
            
            logger.info(f"Base page object created: {base_page_path}")
            
            # Add base page to page objects
            page_objects.append({
                "name": "base_page.py",
                "path": str(base_page_path),
                "type": "base"
            })
            
            # Create page object for the website
            page_name = name.lower().replace(" ", "_")
            page_path = self.pages_dir / f"{page_name}_page.py"
            page_content = self._generate_page_object_content(name, discovery_results)
            
            with open(page_path, 'w') as f:
                f.write(page_content)
            
            logger.info(f"Page object created: {page_path}")
            
            # Add page object to page objects
            page_objects.append({
                "name": f"{page_name}_page.py",
                "path": str(page_path),
                "type": "page"
            })
            
            return page_objects
            
        except Exception as e:
            logger.error(f"Error generating page objects: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
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
    
    def _generate_tests(self, name: str, discovery_results: Dict[str, Any], page_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate tests
        
        Args:
            name: Name of the website
            discovery_results: Discovery results
            page_objects: Generated page objects
            
        Returns:
            List[Dict[str, Any]]: Generated tests
        """
        logger.info(f"Generating tests for {name}")
        
        tests = []
        
        try:
            # Create login test
            login_test_path = self.tests_dir / f"test_{name.lower().replace(' ', '_')}_login.py"
            login_test_content = self._generate_login_test_content(name, discovery_results)
            
            with open(login_test_path, 'w') as f:
                f.write(login_test_content)
            
            logger.info(f"Login test created: {login_test_path}")
            
            # Add login test to tests
            tests.append({
                "name": f"test_{name.lower().replace(' ', '_')}_login.py",
                "path": str(login_test_path),
                "type": "login"
            })
            
            # Create navigation test
            navigation_test_path = self.tests_dir / f"test_{name.lower().replace(' ', '_')}_navigation.py"
            navigation_test_content = self._generate_navigation_test_content(name, discovery_results)
            
            with open(navigation_test_path, 'w') as f:
                f.write(navigation_test_content)
            
            logger.info(f"Navigation test created: {navigation_test_path}")
            
            # Add navigation test to tests
            tests.append({
                "name": f"test_{name.lower().replace(' ', '_')}_navigation.py",
                "path": str(navigation_test_path),
                "type": "navigation"
            })
            
            return tests
            
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
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
        
        # Find username and password fields
        username_field = None
        password_field = None
        login_button = None
        
        for element in discovery_results.get("elements", []):
            # Username field
            if element.get("type") == "text" or element.get("placeholder", "").lower() in ["username", "email", "login"]:
                username_field = element
            # Password field
            elif element.get("type") == "password":
                password_field = element
            # Login button
            elif element.get("category") == "button" and element.get("text", "").lower() in ["login", "log in", "sign in"]:
                login_button = element
        
        # Create test content
        content = f"""#!/usr/bin/env python3
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
    
    def setup_method(self):
        \"\"\"
        Set up test
        \"\"\"
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.{page_name}_page = {class_name}(self.page)
    
    def teardown_method(self):
        \"\"\"
        Tear down test
        \"\"\"
        self.context.close()
        self.browser.close()
    
    def test_valid_login(self):
        \"\"\"
        Test login with valid credentials
        \"\"\"
        # Navigate to the page
        self.{page_name}_page.navigate()
        
        # Fill username and password
"""
        
        # Add username field
        if username_field:
            element_name = username_field.get("id") or username_field.get("name") or "username"
            element_name = element_name.lower().replace(" ", "_").replace("-", "_")
            element_name = ''.join(c for c in element_name if c.isalnum() or c == '_')
            content += f"        self.{page_name}_page.fill_{element_name}(\"Admin\")\n"
        else:
            content += "        # No username field found\n"
        
        # Add password field
        if password_field:
            element_name = password_field.get("id") or password_field.get("name") or "password"
            element_name = element_name.lower().replace(" ", "_").replace("-", "_")
            element_name = ''.join(c for c in element_name if c.isalnum() or c == '_')
            content += f"        self.{page_name}_page.fill_{element_name}(\"admin123\")\n"
        else:
            content += "        # No password field found\n"
        
        # Add login button
        if login_button:
            element_name = login_button.get("id") or login_button.get("name") or login_button.get("text", "").lower().replace(" ", "_")
            element_name = element_name.lower().replace(" ", "_").replace("-", "_")
            element_name = ''.join(c for c in element_name if c.isalnum() or c == '_')
            content += f"        self.{page_name}_page.click_{element_name}()\n"
        else:
            content += "        # No login button found\n"
        
        # Add verification
        content += """
        # Wait for navigation
        self.page.wait_for_load_state("networkidle")
        
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path="screenshots/login_success.png")
        
        # Verify login success
        assert "dashboard" in self.page.url.lower() or "home" in self.page.url.lower(), "Login failed"
    
    def test_invalid_login(self):
        \"\"\"
        Test login with invalid credentials
        \"\"\"
        # Navigate to the page
        self.{0}_page.navigate()
        
        # Fill username and password with invalid credentials
""".format(page_name)
        
        # Add username field
        if username_field:
            element_name = username_field.get("id") or username_field.get("name") or "username"
            element_name = element_name.lower().replace(" ", "_").replace("-", "_")
            element_name = ''.join(c for c in element_name if c.isalnum() or c == '_')
            content += f"        self.{page_name}_page.fill_{element_name}(\"invalid_user\")\n"
        else:
            content += "        # No username field found\n"
        
        # Add password field
        if password_field:
            element_name = password_field.get("id") or password_field.get("name") or "password"
            element_name = element_name.lower().replace(" ", "_").replace("-", "_")
            element_name = ''.join(c for c in element_name if c.isalnum() or c == '_')
            content += f"        self.{page_name}_page.fill_{element_name}(\"invalid_password\")\n"
        else:
            content += "        # No password field found\n"
        
        # Add login button
        if login_button:
            element_name = login_button.get("id") or login_button.get("name") or login_button.get("text", "").lower().replace(" ", "_")
            element_name = element_name.lower().replace(" ", "_").replace("-", "_")
            element_name = ''.join(c for c in element_name if c.isalnum() or c == '_')
            content += f"        self.{page_name}_page.click_{element_name}()\n"
        else:
            content += "        # No login button found\n"
        
        # Add verification
        content += """
        # Wait for error message
        self.page.wait_for_timeout(1000)
        
        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path="screenshots/login_failure.png")
        
        # Verify login failure
        assert "dashboard" not in self.page.url.lower() and "home" not in self.page.url.lower(), "Login should have failed"
"""
        
        return content
    
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
    
    def setup_method(self):
        \"\"\"
        Set up test
        \"\"\"
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.{page_name}_page = {class_name}(self.page)
    
    def teardown_method(self):
        \"\"\"
        Tear down test
        \"\"\"
        self.context.close()
        self.browser.close()
    
    def test_navigation(self):
        \"\"\"
        Test navigation functionality
        \"\"\"
        # Navigate to the page
        self.{page_name}_page.navigate()
        
        # Take screenshot of the home page
        os.makedirs("screenshots", exist_ok=True)
        self.page.screenshot(path="screenshots/navigation_home.png")
        
        # Verify page title
        title = "{discovery_results.get('title', '')}"
        if title:
            assert title in self.page.title(), "Page title does not match"
"""
        
        return content
    
    def _generate_config(self, name: str) -> Dict[str, Any]:
        """
        Generate configuration
        
        Args:
            name: Name of the website
            
        Returns:
            Dict[str, Any]: Generated configuration
        """
        logger.info(f"Generating configuration for {name}")
        
        config = {}
        
        try:
            # Create conftest.py
            conftest_path = self.tests_dir / "conftest.py"
            conftest_content = self._generate_conftest_content()
            
            with open(conftest_path, 'w') as f:
                f.write(conftest_content)
            
            logger.info(f"Conftest created: {conftest_path}")
            
            # Add conftest to config
            config["conftest"] = {
                "name": "conftest.py",
                "path": str(conftest_path)
            }
            
            # Create pytest.ini
            pytest_ini_path = Path("pytest.ini")
            pytest_ini_content = self._generate_pytest_ini_content()
            
            with open(pytest_ini_path, 'w') as f:
                f.write(pytest_ini_content)
            
            logger.info(f"Pytest.ini created: {pytest_ini_path}")
            
            # Add pytest.ini to config
            config["pytest_ini"] = {
                "name": "pytest.ini",
                "path": str(pytest_ini_path)
            }
            
            # Create requirements.txt
            requirements_path = Path("requirements.txt")
            requirements_content = self._generate_requirements_content()
            
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)
            
            logger.info(f"Requirements.txt created: {requirements_path}")
            
            # Add requirements.txt to config
            config["requirements"] = {
                "name": "requirements.txt",
                "path": str(requirements_path)
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Error generating configuration: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
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

def pytest_addoption(parser):
    \"\"\"
    Add command line options
    \"\"\"
    parser.addoption("--headless", action="store_true", default=True, help="Run browser in headless mode")

@pytest.fixture
def browser_setup(request):
    \"\"\"
    Set up browser
    
    Returns:
        tuple: (page, browser, context, playwright)
    \"\"\"
    # Get headless option
    headless = request.config.getoption("--headless")
    
    # Start playwright
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    
    # Return page, browser, context, and playwright
    yield page, browser, context, playwright
    
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
pytest-asyncio==0.21.1
playwright==1.51.0
"""

async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate Complete Tests")
    parser.add_argument("--url", "-u", required=True, help="URL of the website to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the website")
    args = parser.parse_args()
    
    # Create test generator
    generator = TestGenerator()
    
    # Generate tests
    generation_results = await generator.generate_tests(args.url, args.name)
    
    # Print generation results
    print("\nGeneration Results:")
    print(f"Website: {args.name} ({args.url})")
    
    print("\nDiscovery Results:")
    print(f"- Elements: {len(generation_results['discovery_results'].get('elements', []))}")
    
    print("\nPage Objects:")
    for page_object in generation_results.get("page_objects", []):
        print(f"- {page_object.get('name')}: {page_object.get('path')}")
    
    print("\nTests:")
    for test in generation_results.get("tests", []):
        print(f"- {test.get('name')}: {test.get('path')}")
    
    print("\nConfiguration:")
    for config_name, config in generation_results.get("config", {}).items():
        print(f"- {config.get('name')}: {config.get('path')}")
    
    print("\nTests generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())

