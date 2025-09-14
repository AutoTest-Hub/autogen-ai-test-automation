#!/usr/bin/env python3
"""
Generate Real Tests
================
This script generates real tests for a website using the multi-agent workflow.
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def generate_tests(url, name):
    """Generate tests for a website"""
    logger.info(f"Generating tests for {name} at {url}")
    
    # Create directories
    tests_dir = Path("tests")
    pages_dir = Path("pages")
    config_dir = Path("config")
    work_dir = Path("work_dir")
    
    for directory in [tests_dir, pages_dir, config_dir, work_dir]:
        directory.mkdir(exist_ok=True)
    
    # Create test plan
    logger.info("Creating test plan...")
    test_plan = {
        "application_name": name,
        "application_url": url,
        "test_scenarios": [
            {
                "name": "Login",
                "description": "Test login functionality",
                "priority": "high"
            },
            {
                "name": "Navigation",
                "description": "Test navigation functionality",
                "priority": "medium"
            },
            {
                "name": "Search",
                "description": "Test search functionality",
                "priority": "medium"
            }
        ]
    }
    
    # Save test plan
    test_plan_path = work_dir / f"{name.lower().replace(' ', '_')}_test_plan.json"
    with open(test_plan_path, 'w') as f:
        json.dump(test_plan, f, indent=2)
    
    logger.info(f"Test plan created: {test_plan_path}")
    
    # Create page objects
    logger.info("Creating page objects...")
    
    # Base page
    base_page_content = '''"""
Base Page Object
=============
Base page object for all pages.
"""

class BasePage:
    """Base page object for all pages"""
    
    def __init__(self, page):
        """
        Initialize base page object
        
        Args:
            page: Playwright page object
        """
        self.page = page
        self.url = None
    
    async def navigate(self):
        """Navigate to page URL"""
        if self.url:
            await self.page.goto(self.url)
        else:
            raise ValueError("Page URL not set")
    
    async def get_title(self):
        """Get page title"""
        return await self.page.title()
    
    async def fill(self, selector, value):
        """
        Fill input field
        
        Args:
            selector: Element selector
            value: Value to fill
        """
        await self.page.fill(selector, value)
    
    async def click(self, selector):
        """
        Click element
        
        Args:
            selector: Element selector
        """
        await self.page.click(selector)
    
    async def is_visible(self, selector):
        """
        Check if element is visible
        
        Args:
            selector: Element selector
            
        Returns:
            bool: True if element is visible, False otherwise
        """
        element = await self.page.query_selector(selector)
        return element is not None and await element.is_visible()
    
    async def get_text(self, selector):
        """
        Get element text
        
        Args:
            selector: Element selector
            
        Returns:
            str: Element text
        """
        return await self.page.text_content(selector)
'''
    
    with open(pages_dir / "base_page.py", 'w') as f:
        f.write(base_page_content)
    
    # Login page
    login_page_content = f'''"""
Login Page Object
=============
Page object for {name} login page.
"""

from pages.base_page import BasePage

class LoginPage(BasePage):
    """Page object for login page"""
    
    def __init__(self, page):
        """
        Initialize login page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = "{url}"
        
        # Element selectors
        self.username_selector = "input[name='username']"
        self.password_selector = "input[name='password']"
        self.login_button_selector = "button[type='submit']"
        self.error_message_selector = ".oxd-alert-content-text"
    
    async def login(self, username, password):
        """
        Login with username and password
        
        Args:
            username: Username
            password: Password
        """
        await self.fill(self.username_selector, username)
        await self.fill(self.password_selector, password)
        await self.click(self.login_button_selector)
    
    async def get_error_message(self):
        """
        Get error message
        
        Returns:
            str: Error message
        """
        return await self.get_text(self.error_message_selector)
    
    async def is_logged_in(self):
        """
        Check if user is logged in
        
        Returns:
            bool: True if user is logged in, False otherwise
        """
        # Check if dashboard is visible
        return await self.is_visible(".oxd-topbar-header")
'''
    
    with open(pages_dir / "login_page.py", 'w') as f:
        f.write(login_page_content)
    
    # Dashboard page
    dashboard_page_content = f'''"""
Dashboard Page Object
================
Page object for {name} dashboard page.
"""

from pages.base_page import BasePage

class DashboardPage(BasePage):
    """Page object for dashboard page"""
    
    def __init__(self, page):
        """
        Initialize dashboard page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = "{url}/dashboard"
        
        # Element selectors
        self.header_selector = ".oxd-topbar-header-title"
        self.user_dropdown_selector = ".oxd-userdropdown-tab"
        self.logout_selector = "a:has-text('Logout')"
    
    async def get_header_text(self):
        """
        Get header text
        
        Returns:
            str: Header text
        """
        return await self.get_text(self.header_selector)
    
    async def logout(self):
        """Logout"""
        await self.click(self.user_dropdown_selector)
        await self.page.wait_for_timeout(500)  # Wait for dropdown to appear
        await self.click(self.logout_selector)
'''
    
    with open(pages_dir / "dashboard_page.py", 'w') as f:
        f.write(dashboard_page_content)
    
    # Create tests
    logger.info("Creating tests...")
    
    # Login test
    login_test_content = f'''"""
Login Test
========
Test login functionality for {name}.
"""

import pytest
import logging
from datetime import datetime

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

class TestLogin:
    """Test class for login functionality"""
    
    @pytest.mark.asyncio
    async def test_valid_login(self, browser_setup):
        """
        Test login with valid credentials
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page objects
            login_page = LoginPage(page)
            dashboard_page = DashboardPage(page)
            
            # Navigate to login page
            await login_page.navigate()
            
            # Take screenshot of login page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/login_page_{{timestamp}}.png")
            
            # Login with valid credentials
            await login_page.login("Admin", "admin123")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot after login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/after_login_{{timestamp}}.png")
            
            # Assert user is logged in
            assert await login_page.is_logged_in(), "User should be logged in"
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/login_failure_{{timestamp}}.png")
            
            logging.error(f"Test failed: {{str(e)}}")
            raise
    
    @pytest.mark.asyncio
    async def test_invalid_login(self, browser_setup):
        """
        Test login with invalid credentials
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page objects
            login_page = LoginPage(page)
            
            # Navigate to login page
            await login_page.navigate()
            
            # Login with invalid credentials
            await login_page.login("invalid", "invalid")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot after invalid login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/invalid_login_{{timestamp}}.png")
            
            # Assert error message is displayed
            assert await login_page.is_visible(login_page.error_message_selector), "Error message should be displayed"
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/invalid_login_failure_{{timestamp}}.png")
            
            logging.error(f"Test failed: {{str(e)}}")
            raise
'''
    
    with open(tests_dir / f"test_{name.lower().replace(' ', '_')}_login.py", 'w') as f:
        f.write(login_test_content)
    
    # Navigation test
    navigation_test_content = f'''"""
Navigation Test
===========
Test navigation functionality for {name}.
"""

import pytest
import logging
from datetime import datetime

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

class TestNavigation:
    """Test class for navigation functionality"""
    
    @pytest.mark.asyncio
    async def test_navigation(self, browser_setup):
        """
        Test navigation functionality
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page objects
            login_page = LoginPage(page)
            dashboard_page = DashboardPage(page)
            
            # Navigate to login page
            await login_page.navigate()
            
            # Login with valid credentials
            await login_page.login("Admin", "admin123")
            await page.wait_for_load_state("networkidle")
            
            # Assert user is logged in
            assert await login_page.is_logged_in(), "User should be logged in"
            
            # Take screenshot of dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/dashboard_{{timestamp}}.png")
            
            # Navigate to different sections
            sections = [
                ".oxd-main-menu-item:has-text('Admin')",
                ".oxd-main-menu-item:has-text('PIM')",
                ".oxd-main-menu-item:has-text('Leave')",
                ".oxd-main-menu-item:has-text('Time')"
            ]
            
            for section in sections:
                await page.click(section)
                await page.wait_for_load_state("networkidle")
                
                # Take screenshot of section
                section_name = await page.text_content(section)
                section_name = section_name.strip().lower().replace(' ', '_')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                await page.screenshot(path=f"screenshots/section_{{section_name}}_{{timestamp}}.png")
                
                # Assert section is loaded
                assert await page.is_visible(".oxd-topbar-header"), "Section should be loaded"
            
            # Logout
            await dashboard_page.logout()
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot after logout
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/after_logout_{{timestamp}}.png")
            
            # Assert user is logged out
            assert await page.is_visible("input[name='username']"), "User should be logged out"
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/navigation_failure_{{timestamp}}.png")
            
            logging.error(f"Test failed: {{str(e)}}")
            raise
'''
    
    with open(tests_dir / f"test_{name.lower().replace(' ', '_')}_navigation.py", 'w') as f:
        f.write(navigation_test_content)
    
    # Create conftest.py if it doesn't exist
    conftest_path = tests_dir / "conftest.py"
    if not conftest_path.exists():
        conftest_content = '''"""
Pytest Configuration
================
Configuration for pytest.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright

@pytest.fixture
async def browser_setup():
    """
    Fixture for browser setup
    
    Returns:
        tuple: (page, browser, context, playwright)
    """
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        yield page, browser, context, playwright
        
        await context.close()
        await browser.close()
'''
        
        with open(conftest_path, 'w') as f:
            f.write(conftest_content)
    
    logger.info("Tests created successfully!")
    
    return {
        "test_plan": str(test_plan_path),
        "page_objects": [
            str(pages_dir / "base_page.py"),
            str(pages_dir / "login_page.py"),
            str(pages_dir / "dashboard_page.py")
        ],
        "tests": [
            str(tests_dir / f"test_{name.lower().replace(' ', '_')}_login.py"),
            str(tests_dir / f"test_{name.lower().replace(' ', '_')}_navigation.py")
        ]
    }

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate Real Tests")
    parser.add_argument("--url", "-u", required=True, help="URL of the application to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the application")
    args = parser.parse_args()
    
    # Generate tests
    results = asyncio.run(generate_tests(args.url, args.name))
    
    # Print results
    print("\nTests Generated Successfully!")
    print(f"Test Plan: {results['test_plan']}")
    print("\nPage Objects:")
    for page_object in results['page_objects']:
        print(f"- {page_object}")
    print("\nTests:")
    for test in results['tests']:
        print(f"- {test}")
    
    print("\nTo run the tests:")
    print(f"python -m pytest {' '.join(results['tests'])} -v")

if __name__ == "__main__":
    main()

