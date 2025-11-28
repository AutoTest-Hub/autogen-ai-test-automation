#!/usr/bin/env python3
"""
Generate Universal Tests
===================
This script generates robust tests that work across different environments.
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
    """Generate universal tests for a website"""
    logger.info(f"Generating universal tests for {name} at {url}")
    
    # Create directories
    tests_dir = Path("tests")
    screenshots_dir = Path("screenshots")
    
    for directory in [tests_dir, screenshots_dir]:
        directory.mkdir(exist_ok=True)
    
    # Create universal test
    logger.info("Creating universal test...")
    
    universal_test_content = f'''"""
Universal {name} Test
===================
A robust test for {name} that works across different environments.
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

class Test{name.replace(" ", "")}:
    """Universal test class for {name}"""
    
    def test_login_and_navigation(self):
        """
        Test login and basic navigation
        """
        with sync_playwright() as playwright:
            # Launch browser with slower navigation to accommodate network issues
            browser = playwright.chromium.launch(
                headless=True,
                slow_mo=100  # Add a small delay between actions
            )
            
            # Create a context with a longer default timeout
            context = browser.new_context(
                viewport={{'width': 1280, 'height': 720}}
            )
            
            # Create a page with longer default timeout
            page = context.new_page()
            page.set_default_timeout(60000)  # 60 seconds timeout
            
            try:
                logger.info("Starting {name} test")
                
                # Navigate to login page
                logger.info("Navigating to login page")
                page.goto("{url}", 
                          wait_until="domcontentloaded")
                
                # Take screenshot of initial page
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/initial_page_{{timestamp}}.png")
                
                # Wait for the page to load and stabilize
                logger.info("Waiting for login page to load")
                page.wait_for_load_state("networkidle")
                
                # Check if we're on the login page by looking for multiple possible selectors
                login_selectors = [
                    "input[name='username']",
                    "input[placeholder='Username']",
                    ".oxd-input[name='username']",
                    "form .oxd-input",
                    "input[type='text']"
                ]
                
                username_field = None
                for selector in login_selectors:
                    try:
                        logger.info(f"Trying to find username field with selector: {{selector}}")
                        username_field = page.wait_for_selector(selector, timeout=5000)
                        if username_field:
                            logger.info(f"Found username field with selector: {{selector}}")
                            break
                    except Exception as e:
                        logger.info(f"Selector {{selector}} not found: {{str(e)}}")
                
                if not username_field:
                    logger.error("Could not find username field")
                    page.screenshot(path=f"screenshots/username_field_not_found_{{timestamp}}.png")
                    raise Exception("Could not find username field")
                
                # Take screenshot of login page
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/login_page_{{timestamp}}.png")
                
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
                
                password_field = None
                for selector in password_selectors:
                    try:
                        logger.info(f"Trying to find password field with selector: {{selector}}")
                        password_field = page.wait_for_selector(selector, timeout=5000)
                        if password_field:
                            logger.info(f"Found password field with selector: {{selector}}")
                            break
                    except Exception as e:
                        logger.info(f"Selector {{selector}} not found: {{str(e)}}")
                
                if not password_field:
                    logger.error("Could not find password field")
                    page.screenshot(path=f"screenshots/password_field_not_found_{{timestamp}}.png")
                    raise Exception("Could not find password field")
                
                # Fill password
                logger.info("Filling password")
                password_field.fill("admin123")
                
                # Find login button
                button_selectors = [
                    "button[type='submit']",
                    ".oxd-button",
                    "button.oxd-button--main",
                    "form button",
                    "button:has-text('Login')",
                    "button:has-text('Sign in')"
                ]
                
                login_button = None
                for selector in button_selectors:
                    try:
                        logger.info(f"Trying to find login button with selector: {{selector}}")
                        login_button = page.wait_for_selector(selector, timeout=5000)
                        if login_button:
                            logger.info(f"Found login button with selector: {{selector}}")
                            break
                    except Exception as e:
                        logger.info(f"Selector {{selector}} not found: {{str(e)}}")
                
                if not login_button:
                    logger.error("Could not find login button")
                    page.screenshot(path=f"screenshots/login_button_not_found_{{timestamp}}.png")
                    raise Exception("Could not find login button")
                
                # Click login button
                logger.info("Clicking login button")
                login_button.click()
                
                # Wait for page to load after login
                logger.info("Waiting for page to load after login")
                page.wait_for_load_state("networkidle")
                
                # Take screenshot after login attempt
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/after_login_{{timestamp}}.png")
                
                # Check if login was successful by looking for dashboard elements
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
                
                dashboard_element = None
                for selector in dashboard_selectors:
                    try:
                        logger.info(f"Trying to find dashboard element with selector: {{selector}}")
                        dashboard_element = page.wait_for_selector(selector, timeout=10000)
                        if dashboard_element:
                            logger.info(f"Found dashboard element with selector: {{selector}}")
                            break
                    except Exception as e:
                        logger.info(f"Selector {{selector}} not found: {{str(e)}}")
                
                if not dashboard_element:
                    logger.error("Login failed - could not find dashboard elements")
                    page.screenshot(path=f"screenshots/login_failed_{{timestamp}}.png")
                    raise Exception("Login failed - could not find dashboard elements")
                
                logger.info("Login successful")
                
                # Test passed
                logger.info("Test completed successfully")
                
            except Exception as e:
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    page.screenshot(path=f"screenshots/test_failure_{{timestamp}}.png")
                except:
                    pass
                
                logger.error(f"Test failed: {{str(e)}}")
                raise
            finally:
                # Clean up - use try/except to handle already closed resources
                try:
                    context.close()
                except:
                    pass
                
                try:
                    browser.close()
                except:
                    pass
'''
    
    with open(tests_dir / f"test_{name.lower().replace(' ', '_')}_universal.py", 'w') as f:
        f.write(universal_test_content)
    
    logger.info("Universal test created successfully!")
    
    return {
        "tests": [
            str(tests_dir / f"test_{name.lower().replace(' ', '_')}_universal.py")
        ]
    }

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate Universal Tests")
    parser.add_argument("--url", "-u", required=True, help="URL of the application to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the application")
    args = parser.parse_args()
    
    # Generate tests
    results = generate_tests(args.url, args.name)
    
    # Print results
    print("\nUniversal Tests Generated Successfully!")
    print("\nTests:")
    for test in results['tests']:
        print(f"- {test}")
    
    print("\nTo run the tests:")
    print(f"python -m pytest {' '.join(results['tests'])} -v")

if __name__ == "__main__":
    main()

