"""
Navigation Test (Fixed)
=================
Test navigation functionality for OrangeHRM with proper timeout handling.
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
                page.set_default_timeout(30000)  # 30 seconds timeout
                
                # Navigate to login page
                page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
                
                # Wait for the page to load
                page.wait_for_selector("input[name='username']", timeout=30000)
                
                # Fill username and password
                page.fill("input[name='username']", "Admin")
                page.fill("input[name='password']", "admin123")
                
                # Click login button
                page.click("button[type='submit']")
                
                # Wait for dashboard to appear instead of waiting for networkidle
                page.wait_for_selector(".oxd-topbar-header", timeout=30000)
                
                # Assert user is logged in
                assert page.is_visible(".oxd-topbar-header"), "User should be logged in"
                
                # Take screenshot of dashboard
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/dashboard_{timestamp}.png")
                
                # Navigate to different sections
                sections = [
                    ".oxd-main-menu-item:has-text('Admin')",
                    ".oxd-main-menu-item:has-text('PIM')",
                    ".oxd-main-menu-item:has-text('Leave')",
                    ".oxd-main-menu-item:has-text('Time')"
                ]
                
                for section in sections:
                    # Wait for section to be visible before clicking
                    page.wait_for_selector(section, timeout=30000)
                    page.click(section)
                    
                    # Wait for page to load after clicking
                    page.wait_for_selector(".oxd-topbar-header", timeout=30000)
                    
                    # Take screenshot of section
                    section_name = page.text_content(section)
                    section_name = section_name.strip().lower().replace(' ', '_')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    page.screenshot(path=f"screenshots/section_{section_name}_{timestamp}.png")
                    
                    # Assert section is loaded
                    assert page.is_visible(".oxd-topbar-header"), "Section should be loaded"
                
                # Logout
                page.wait_for_selector(".oxd-userdropdown-tab", timeout=30000)
                page.click(".oxd-userdropdown-tab")
                page.wait_for_timeout(1000)  # Wait for dropdown to appear
                
                # Wait for logout link to be visible
                page.wait_for_selector("a:has-text('Logout')", timeout=30000)
                page.click("a:has-text('Logout')")
                
                # Wait for login page to appear
                page.wait_for_selector("input[name='username']", timeout=30000)
                
                # Take screenshot after logout
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"screenshots/after_logout_{timestamp}.png")
                
                # Assert user is logged out
                assert page.is_visible("input[name='username']"), "User should be logged out"
                
            except Exception as e:
                # Take screenshot on failure
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    page.screenshot(path=f"screenshots/navigation_failure_{timestamp}.png")
                except:
                    pass
                
                logging.error(f"Test failed: {str(e)}")
                raise
            finally:
                # Clean up
                context.close()
                browser.close()

