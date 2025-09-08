"""
Login Test (Fixed)
==============
Test login functionality for OrangeHRM with proper timeout handling.
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
                page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
                
                # Wait for the page to load
                page.wait_for_selector("input[name='username']", timeout=10000)
                
                # Take screenshot of login page
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/login_page_{timestamp}.png")
                
                # Fill username and password
                page.fill("input[name='username']", "Admin")
                page.fill("input[name='password']", "admin123")
                
                # Click login button
                page.click("button[type='submit']")
                
                # Wait for navigation to complete
                page.wait_for_load_state("networkidle", timeout=10000)
                
                # Take screenshot after login
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/after_login_{timestamp}.png")
                
                # Assert user is logged in
                assert page.is_visible(".oxd-topbar-header"), "User should be logged in"
                
            except Exception as e:
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    page.screenshot(path=f"screenshots/login_failure_{timestamp}.png")
                except:
                    pass
                
                logging.error(f"Test failed: {str(e)}")
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
                page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
                
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
                page.screenshot(path=f"screenshots/invalid_login_{timestamp}.png")
                
                # Assert error message is displayed
                assert page.is_visible(".oxd-alert-content-text"), "Error message should be displayed"
                
            except Exception as e:
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    page.screenshot(path=f"screenshots/invalid_login_failure_{timestamp}.png")
                except:
                    pass
                
                logging.error(f"Test failed: {str(e)}")
                raise
            finally:
                # Clean up
                context.close()
                browser.close()

