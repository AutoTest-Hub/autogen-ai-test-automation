#!/usr/bin/env python3
"""
Generate Real Tests (Fixed)
======================
This script generates real tests for a website using synchronous Playwright.
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
    """Generate tests for a website"""
    logger.info(f"Generating tests for {name} at {url}")
    
    # Create directories
    tests_dir = Path("tests")
    pages_dir = Path("pages")
    config_dir = Path("config")
    work_dir = Path("work_dir")
    screenshots_dir = Path("screenshots")
    
    for directory in [tests_dir, pages_dir, config_dir, work_dir, screenshots_dir]:
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
    
    # Create login test
    logger.info("Creating tests...")
    
    login_test_content = f'''"""
Login Test
========
Test login functionality for {name}.
"""

import pytest
from playwright.sync_api import sync_playwright
import logging
from datetime import datetime
import os

# Create screenshots directory if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

class TestLogin:
    """Test class for login functionality"""
    
    def test_valid_login(self):
        """
        Test login with valid credentials
        """
        with sync_playwright() as playwright:
            # Launch browser
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # Set default timeout to prevent hanging
                page.set_default_timeout(10000)  # 10 seconds timeout
                
                # Navigate to login page
                page.goto("{url}")
                
                # Wait for the page to load
                page.wait_for_selector("input[name='username']", timeout=10000)
                
                # Take screenshot of login page
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/login_page_{{timestamp}}.png")
                
                # Fill username and password
                page.fill("input[name='username']", "Admin")
                page.fill("input[name='password']", "admin123")
                
                # Click login button
                page.click("button[type='submit']")
                
                # Wait for navigation to complete
                page.wait_for_load_state("networkidle", timeout=10000)
                
                # Take screenshot after login
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/after_login_{{timestamp}}.png")
                
                # Assert user is logged in
                assert page.is_visible(".oxd-topbar-header"), "User should be logged in"
                
            except Exception as e:
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    page.screenshot(path=f"screenshots/login_failure_{{timestamp}}.png")
                except:
                    pass
                
                logging.error(f"Test failed: {{str(e)}}")
                raise
            finally:
                # Clean up
                context.close()
                browser.close()
    
    def test_invalid_login(self):
        """
        Test login with invalid credentials
        """
        with sync_playwright() as playwright:
            # Launch browser
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # Set default timeout to prevent hanging
                page.set_default_timeout(10000)  # 10 seconds timeout
                
                # Navigate to login page
                page.goto("{url}")
                
                # Wait for the page to load
                page.wait_for_selector("input[name='username']", timeout=10000)
                
                # Fill username and password
                page.fill("input[name='username']", "invalid")
                page.fill("input[name='password']", "invalid")
                
                # Click login button
                page.click("button[type='submit']")
                
                # Wait for navigation to complete
                page.wait_for_load_state("networkidle", timeout=10000)
                
                # Take screenshot after invalid login
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/invalid_login_{{timestamp}}.png")
                
                # Assert error message is displayed
                assert page.is_visible(".oxd-alert-content-text"), "Error message should be displayed"
                
            except Exception as e:
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    page.screenshot(path=f"screenshots/invalid_login_failure_{{timestamp}}.png")
                except:
                    pass
                
                logging.error(f"Test failed: {{str(e)}}")
                raise
            finally:
                # Clean up
                context.close()
                browser.close()
'''
    
    with open(tests_dir / f"test_{name.lower().replace(' ', '_')}_login.py", 'w') as f:
        f.write(login_test_content)
    
    # Create navigation test
    navigation_test_content = f'''"""
Navigation Test
===========
Test navigation functionality for {name}.
"""

import pytest
from playwright.sync_api import sync_playwright
import logging
from datetime import datetime
import os

# Create screenshots directory if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

class TestNavigation:
    """Test class for navigation functionality"""
    
    def test_navigation(self):
        """
        Test navigation functionality
        """
        with sync_playwright() as playwright:
            # Launch browser
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # Set default timeout to prevent hanging
                page.set_default_timeout(10000)  # 10 seconds timeout
                
                # Navigate to login page
                page.goto("{url}")
                
                # Wait for the page to load
                page.wait_for_selector("input[name='username']", timeout=10000)
                
                # Fill username and password
                page.fill("input[name='username']", "Admin")
                page.fill("input[name='password']", "admin123")
                
                # Click login button
                page.click("button[type='submit']")
                
                # Wait for navigation to complete
                page.wait_for_load_state("networkidle", timeout=10000)
                
                # Assert user is logged in
                assert page.is_visible(".oxd-topbar-header"), "User should be logged in"
                
                # Take screenshot of dashboard
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/dashboard_{{timestamp}}.png")
                
                # Navigate to different sections
                sections = [
                    ".oxd-main-menu-item:has-text('Admin')",
                    ".oxd-main-menu-item:has-text('PIM')",
                    ".oxd-main-menu-item:has-text('Leave')",
                    ".oxd-main-menu-item:has-text('Time')"
                ]
                
                for section in sections:
                    page.click(section)
                    page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Take screenshot of section
                    section_name = page.text_content(section)
                    section_name = section_name.strip().lower().replace(' ', '_')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    page.screenshot(path=f"screenshots/section_{{section_name}}_{{timestamp}}.png")
                    
                    # Assert section is loaded
                    assert page.is_visible(".oxd-topbar-header"), "Section should be loaded"
                
                # Logout
                page.click(".oxd-userdropdown-tab")
                page.wait_for_timeout(500)  # Wait for dropdown to appear
                page.click("a:has-text('Logout')")
                page.wait_for_load_state("networkidle", timeout=10000)
                
                # Take screenshot after logout
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/after_logout_{{timestamp}}.png")
                
                # Assert user is logged out
                assert page.is_visible("input[name='username']"), "User should be logged out"
                
            except Exception as e:
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    page.screenshot(path=f"screenshots/navigation_failure_{{timestamp}}.png")
                except:
                    pass
                
                logging.error(f"Test failed: {{str(e)}}")
                raise
            finally:
                # Clean up
                context.close()
                browser.close()
'''
    
    with open(tests_dir / f"test_{name.lower().replace(' ', '_')}_navigation.py", 'w') as f:
        f.write(navigation_test_content)
    
    logger.info("Tests created successfully!")
    
    return {
        "test_plan": str(test_plan_path),
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
    results = generate_tests(args.url, args.name)
    
    # Print results
    print("\nTests Generated Successfully!")
    print(f"Test Plan: {results['test_plan']}")
    print("\nTests:")
    for test in results['tests']:
        print(f"- {test}")
    
    print("\nTo run the tests:")
    print(f"python -m pytest {' '.join(results['tests'])} -v")

if __name__ == "__main__":
    main()

