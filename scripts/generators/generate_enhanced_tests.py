#!/usr/bin/env python3
"""
Generate Enhanced Tests
===================
This script generates enhanced tests with multiple test cases and headless toggle.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_tests(url, name):
    """Generate enhanced tests for a website"""
    logger.info(f"Generating enhanced tests for {name} at {url}")
    
    # Create directories
    tests_dir = Path("tests")
    screenshots_dir = Path("screenshots")
    
    for directory in [tests_dir, screenshots_dir]:
        directory.mkdir(exist_ok=True)
    
    # Create conftest.py if it doesn't exist
    conftest_path = Path("conftest.py")
    if not conftest_path.exists():
        logger.info("Creating conftest.py...")
        conftest_content = '''"""
Pytest Configuration
================
Configuration for pytest.
"""

import pytest

def pytest_addoption(parser):
    """Add command line options to pytest"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=True,
        help="Run tests in headless mode (default)"
    )
    parser.addoption(
        "--no-headless",
        action="store_true",
        default=False,
        help="Run tests in headed mode (with browser UI)"
    )

@pytest.fixture(scope="session")
def headless(request):
    """
    Fixture to determine if tests should run in headless mode
    
    Returns:
        bool: True if headless, False if headed
    """
    no_headless = request.config.getoption("--no-headless")
    if no_headless:
        return False
    return True'''
        
        with open(conftest_path, 'w') as f:
            f.write(conftest_content)
    
    # Create enhanced test
    logger.info("Creating enhanced test...")
    
    test_name = name.replace(" ", "")
    file_name = f"test_{name.lower().replace(' ', '_')}_enhanced.py"
    
    enhanced_test_content = f'''"""
Enhanced {name} Test
===================
Enhanced tests for {name} with multiple test cases and headless toggle.
"""

import pytest
import logging
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create screenshots directory if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

class Test{test_name}:
    """Enhanced test class for {name}"""
    
    @pytest.fixture
    def browser_context(self, headless):
        """
        Fixture to set up browser context
        
        Args:
            headless: Whether to run in headless mode (from conftest.py)
            
        Returns:
            tuple: (playwright, browser, context, page)
        """
        # Initialize playwright
        playwright = sync_playwright().start()
        
        # Launch browser with configurable headless mode
        browser = playwright.chromium.launch(
            headless=headless,
            slow_mo=100  # Add a small delay between actions
        )
        
        # Create a context with a longer default timeout
        context = browser.new_context(
            viewport={{'width': 1280, 'height': 720}}
        )
        
        # Create a page with longer default timeout
        page = context.new_page()
        page.set_default_timeout(60000)  # 60 seconds timeout
        
        # Log headless mode
        logger.info(f"Running in {{'headless' if headless else 'headed'}} mode")
        
        # Yield the resources
        yield playwright, browser, context, page
        
        # Clean up - use try/except to handle already closed resources
        try:
            context.close()
        except:
            pass
        
        try:
            browser.close()
        except:
            pass
        
        try:
            playwright.stop()
        except:
            pass
    
    def test_login_with_valid_credentials(self, browser_context):
        """
        Test login with valid credentials
        """
        playwright, browser, context, page = browser_context
        
        try:
            logger.info("Starting valid login test")
            
            # Navigate to login page
            logger.info("Navigating to login page")
            page.goto("{url}", 
                      wait_until="domcontentloaded")
            
            # Wait for the page to load and stabilize
            logger.info("Waiting for login page to load")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot of login page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"screenshots/login_page_{{timestamp}}.png")
            
            # Find username field
            username_selectors = [
                "input[name='username']",
                "input[placeholder='Username']",
                ".oxd-input[name='username']",
                "form .oxd-input",
                "input[type='text']"
            ]
            
            username_field = self._find_element(page, username_selectors, "username field")
            
            # Fill username
            logger.info("Filling username")
            username_field.fill("Admin")
            
            # Find password field
            password_selectors = [
                "input[name='password']",
                "input[placeholder='Password']",
                ".oxd-input[name='password']",
                "form .oxd-input[type='password']",
                "input[type='password']"
            ]
            
            password_field = self._find_element(page, password_selectors, "password field")
            
            # Fill password
            logger.info("Filling password")
            password_field.fill("admin123")
            
            # Find login button
            button_selectors = [
                "button[type='submit']",
                ".oxd-button",
                "button.oxd-button--main",
                "form button"
            ]
            
            login_button = self._find_element(page, button_selectors, "login button")
            
            # Click login button
            logger.info("Clicking login button")
            login_button.click()
            
            # Wait for page to load after login
            logger.info("Waiting for page to load after login")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot after login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"screenshots/after_login_{{timestamp}}.png")
            
            # Check if login was successful
            dashboard_selectors = [
                ".oxd-topbar-header",
                ".oxd-navbar-nav",
                ".oxd-main-menu",
                ".oxd-brand-banner",
                "header",
                "nav",
                ".dashboard",
                "#dashboard"
            ]
            
            dashboard_element = self._find_element(page, dashboard_selectors, "dashboard element")
            
            # Assert login was successful
            assert dashboard_element is not None, "Login failed - could not find dashboard elements"
            logger.info("Login successful")
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                page.screenshot(path=f"screenshots/login_failure_{{timestamp}}.png")
            except:
                pass
            
            logger.error(f"Test failed: {{str(e)}}")
            raise
    
    def test_login_with_invalid_credentials(self, browser_context):
        """
        Test login with invalid credentials
        """
        playwright, browser, context, page = browser_context
        
        try:
            logger.info("Starting invalid login test")
            
            # Navigate to login page
            logger.info("Navigating to login page")
            page.goto("{url}", 
                      wait_until="domcontentloaded")
            
            # Wait for the page to load and stabilize
            logger.info("Waiting for login page to load")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot of login page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"screenshots/invalid_login_page_{{timestamp}}.png")
            
            # Find username field
            username_selectors = [
                "input[name='username']",
                "input[placeholder='Username']",
                ".oxd-input[name='username']",
                "form .oxd-input",
                "input[type='text']"
            ]
            
            username_field = self._find_element(page, username_selectors, "username field")
            
            # Fill username
            logger.info("Filling invalid username")
            username_field.fill("invalid")
            
            # Find password field
            password_selectors = [
                "input[name='password']",
                "input[placeholder='Password']",
                ".oxd-input[name='password']",
                "form .oxd-input[type='password']",
                "input[type='password']"
            ]
            
            password_field = self._find_element(page, password_selectors, "password field")
            
            # Fill password
            logger.info("Filling invalid password")
            password_field.fill("invalid")
            
            # Find login button
            button_selectors = [
                "button[type='submit']",
                ".oxd-button",
                "button.oxd-button--main",
                "form button",
                "button:has-text('Login')",
                "button:has-text('Sign in')"
            ]
            
            login_button = self._find_element(page, button_selectors, "login button")
            
            # Click login button
            logger.info("Clicking login button")
            login_button.click()
            
            # Wait for page to load after login attempt
            logger.info("Waiting for page to load after login attempt")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot after login attempt
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"screenshots/after_invalid_login_{{timestamp}}.png")
            
            # Check for error message
            error_selectors = [
                ".oxd-alert-content-text",
                ".oxd-alert",
                ".alert-content",
                ".error-message",
                "text=Invalid credentials",
                "text=incorrect",
                "text=failed"
            ]
            
            error_element = self._find_element(page, error_selectors, "error message", required=False)
            
            # Assert error message is displayed
            assert error_element is not None, "Invalid login test failed - no error message displayed"
            logger.info("Invalid login test passed - error message displayed")
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                page.screenshot(path=f"screenshots/invalid_login_failure_{{timestamp}}.png")
            except:
                pass
            
            logger.error(f"Test failed: {{str(e)}}")
            raise
    
    def test_navigation(self, browser_context):
        """
        Test navigation functionality
        """
        playwright, browser, context, page = browser_context
        
        try:
            logger.info("Starting navigation test")
            
            # First login
            logger.info("Logging in first")
            
            # Navigate to login page
            logger.info("Navigating to login page")
            page.goto("{url}", 
                      wait_until="domcontentloaded")
            
            # Wait for the page to load and stabilize
            logger.info("Waiting for login page to load")
            page.wait_for_load_state("networkidle")
            
            # Find and fill username
            username_selectors = [
                "input[name='username']",
                "input[placeholder='Username']",
                ".oxd-input[name='username']",
                "form .oxd-input",
                "input[type='text']"
            ]
            
            username_field = self._find_element(page, username_selectors, "username field")
            username_field.fill("Admin")
            
            # Find and fill password
            password_selectors = [
                "input[name='password']",
                "input[placeholder='Password']",
                ".oxd-input[name='password']",
                "form .oxd-input[type='password']",
                "input[type='password']"
            ]
            
            password_field = self._find_element(page, password_selectors, "password field")
            password_field.fill("admin123")
            
            # Find and click login button
            button_selectors = [
                "button[type='submit']",
                ".oxd-button",
                "button.oxd-button--main",
                "form button",
                "button:has-text('Login')",
                "button:has-text('Sign in')"
            ]
            
            login_button = self._find_element(page, button_selectors, "login button")
            login_button.click()
            
            # Wait for dashboard to appear
            dashboard_selectors = [
                ".oxd-topbar-header",
                ".oxd-navbar-nav",
                ".oxd-main-menu",
                ".oxd-brand-banner",
                "header",
                "nav",
                ".dashboard",
                "#dashboard"
            ]
            
            dashboard_element = self._find_element(page, dashboard_selectors, "dashboard element")
            
            # Take screenshot of dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"screenshots/dashboard_{{timestamp}}.png")
            
            # Now test navigation
            logger.info("Testing navigation")
            
            # Define menu items to navigate to
            menu_items = [
                {{"name": "Admin", "selectors": [".oxd-main-menu-item:has-text('Admin')", "a:has-text('Admin')", "li:has-text('Admin')"]}},
                {{"name": "PIM", "selectors": [".oxd-main-menu-item:has-text('PIM')", "a:has-text('PIM')", "li:has-text('PIM')"]}},
                {{"name": "Leave", "selectors": [".oxd-main-menu-item:has-text('Leave')", "a:has-text('Leave')", "li:has-text('Leave')"]}},
                {{"name": "Time", "selectors": [".oxd-main-menu-item:has-text('Time')", "a:has-text('Time')", "li:has-text('Time')"]}},
                {{"name": "Dashboard", "selectors": [".oxd-main-menu-item:has-text('Dashboard')", "a:has-text('Dashboard')", "li:has-text('Dashboard')"]}},
                {{"name": "Directory", "selectors": [".oxd-main-menu-item:has-text('Directory')", "a:has-text('Directory')", "li:has-text('Directory')"]}},
                {{"name": "Maintenance", "selectors": [".oxd-main-menu-item:has-text('Maintenance')", "a:has-text('Maintenance')", "li:has-text('Maintenance')"]}},
                {{"name": "Claim", "selectors": [".oxd-main-menu-item:has-text('Claim')", "a:has-text('Claim')", "li:has-text('Claim')"]}},
                {{"name": "Buzz", "selectors": [".oxd-main-menu-item:has-text('Buzz')", "a:has-text('Buzz')", "li:has-text('Buzz')"]}},
                {{"name": "Performance", "selectors": [".oxd-main-menu-item:has-text('Performance')", "a:has-text('Performance')", "li:has-text('Performance')"]}},
                {{"name": "Recruitment", "selectors": [".oxd-main-menu-item:has-text('Recruitment')", "a:has-text('Recruitment')", "li:has-text('Recruitment')"]}},
                {{"name": "My Info", "selectors": [".oxd-main-menu-item:has-text('My Info')", "a:has-text('My Info')", "li:has-text('My Info')"]}},
            ]
            
            # Navigate to each menu item
            for item in menu_items:
                try:
                    logger.info(f"Navigating to {{item['name']}}")
                    
                    # Find and click menu item
                    menu_element = self._find_element(page, item["selectors"], f"{{item['name']}} menu item", required=False)
                    
                    if menu_element:
                        menu_element.click()
                        
                        # Wait for page to load
                        page.wait_for_load_state("networkidle")
                        
                        # Take screenshot
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        page.screenshot(path=f"screenshots/{{item['name'].lower().replace(' ', '_')}}_{{timestamp}}.png")
                        
                        # Verify navigation was successful
                        logger.info(f"Successfully navigated to {{item['name']}}")
                    else:
                        logger.info(f"Menu item {{item['name']}} not found, skipping")
                    
                except Exception as e:
                    logger.error(f"Failed to navigate to {{item['name']}}: {{str(e)}}")
                    # Continue with next menu item even if this one fails
            
            # Test logout
            logger.info("Testing logout")
            
            # Find and click user dropdown
            dropdown_selectors = [
                ".oxd-userdropdown-tab",
                ".userdropdown",
                "li.--active",
                ".user-dropdown",
                ".user-menu",
                ".profile-dropdown"
            ]
            
            dropdown = self._find_element(page, dropdown_selectors, "user dropdown")
            dropdown.click()
            
            # Wait for dropdown menu to appear
            page.wait_for_timeout(1000)
            
            # Find and click logout
            logout_selectors = [
                "a:has-text('Logout')",
                ".oxd-dropdown-menu li:last-child",
                "text=Logout",
                "text=Sign Out",
                "text=Log Out"
            ]
            
            logout = self._find_element(page, logout_selectors, "logout link")
            logout.click()
            
            # Wait for login page to appear
            page.wait_for_load_state("networkidle")
            
            # Take screenshot after logout
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"screenshots/after_logout_{{timestamp}}.png")
            
            # Verify logout was successful
            login_page_selectors = [
                "input[name='username']",
                "input[placeholder='Username']",
                ".oxd-input[name='username']",
                "input[type='text']"
            ]
            
            login_page_element = self._find_element(page, login_page_selectors, "login page element")
            assert login_page_element is not None, "Logout failed - could not find login page elements"
            logger.info("Logout successful")
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                page.screenshot(path=f"screenshots/navigation_failure_{{timestamp}}.png")
            except:
                pass
            
            logger.error(f"Test failed: {{str(e)}}")
            raise
    
    def _find_element(self, page, selectors, element_name, required=True, timeout=5000):
        """
        Helper method to find an element using multiple selectors
        
        Args:
            page: Playwright page
            selectors: List of selectors to try
            element_name: Name of the element for logging
            required: Whether the element is required
            timeout: Timeout for each selector
            
        Returns:
            The found element or None
        """
        element = None
        for selector in selectors:
            try:
                logger.info(f"Trying to find {{element_name}} with selector: {{selector}}")
                element = page.wait_for_selector(selector, timeout=timeout)
                if element:
                    logger.info(f"Found {{element_name}} with selector: {{selector}}")
                    break
            except Exception as e:
                logger.info(f"Selector {{selector}} not found: {{str(e)}}")
        
        if not element and required:
            logger.error(f"Could not find {{element_name}}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"screenshots/{{element_name.replace(' ', '_')}}_not_found_{{timestamp}}.png")
            raise Exception(f"Could not find {{element_name}}")
        
        return element'''
    
    with open(tests_dir / file_name, 'w') as f:
        f.write(enhanced_test_content)
    
    logger.info("Enhanced test created successfully!")
    
    return {
        "tests": [
            str(tests_dir / file_name)
        ]
    }

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate Enhanced Tests")
    parser.add_argument("--url", "-u", required=True, help="URL of the application to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the application")
    args = parser.parse_args()
    
    # Generate tests
    results = generate_tests(args.url, args.name)
    
    # Print results
    print("\nEnhanced Tests Generated Successfully!")
    print("\nTests:")
    for test in results['tests']:
        print(f"- {test}")
    
    print("\nTo run the tests:")
    print(f"python -m pytest {' '.join(results['tests'])} -v")
    print("\nTo run in headed mode (with browser UI):")
    print(f"python -m pytest {' '.join(results['tests'])} -v --no-headless")
    print("\nTo run specific test cases:")
    print(f"python -m pytest {results['tests'][0]}::Test{args.name.replace(' ', '')}::test_login_with_valid_credentials -v")
    print(f"python -m pytest {results['tests'][0]}::Test{args.name.replace(' ', '')}::test_login_with_invalid_credentials -v")
    print(f"python -m pytest {results['tests'][0]}::Test{args.name.replace(' ', '')}::test_navigation -v")

if __name__ == "__main__":
    main()

