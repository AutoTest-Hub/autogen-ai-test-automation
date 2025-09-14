"""
Test user authentication workflow
"""

import pytest
import logging
from datetime import datetime
from pages.login_page import LoginPage

class TestUserLogin:
    """Test class for user login functionality"""
    
    @pytest.mark.asyncio
    async def test_valid_login(self, browser_setup, test_config):
        """
        Test login with valid credentials
        
        Args:
            browser_setup: Browser setup fixture
            test_config: Test configuration fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page objects
            login_page = LoginPage(page, test_config["base_url"])
            
            # Navigate to login page
            await login_page.navigate()
            
            # Verify login page is loaded
            assert await login_page.is_loaded(), "Login page should be loaded"
            
            # Login with valid credentials
            await login_page.login("testuser", "password123")
            
            # Verify successful login (this would typically check for elements on the next page)
            # For this example, we'll just check that we're no longer on the login page
            assert not await login_page.is_loaded(), "Should navigate away from login page after successful login"
            
            # Take screenshot for evidence
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/test_valid_login_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            
            logging.info(f"Test test_valid_login completed successfully")
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/test_valid_login_failure_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            
            logging.error(f"Test test_valid_login failed: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_invalid_login(self, browser_setup, test_config):
        """
        Test login with invalid credentials
        
        Args:
            browser_setup: Browser setup fixture
            test_config: Test configuration fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page objects
            login_page = LoginPage(page, test_config["base_url"])
            
            # Navigate to login page
            await login_page.navigate()
            
            # Verify login page is loaded
            assert await login_page.is_loaded(), "Login page should be loaded"
            
            # Login with invalid credentials
            await login_page.login("invalid_user", "invalid_password")
            
            # Verify error message
            error_message = await login_page.get_error_message()
            assert error_message, "Error message should be displayed for invalid login"
            
            # Verify still on login page
            assert await login_page.is_loaded(), "Should remain on login page after failed login"
            
            # Take screenshot for evidence
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/test_invalid_login_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            
            logging.info(f"Test test_invalid_login completed successfully")
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/test_invalid_login_failure_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            
            logging.error(f"Test test_invalid_login failed: {str(e)}")
            raise

