#!/usr/bin/env python3
"""
Create Simple Test
================
This script creates a simple working test for demonstration purposes.
"""

import os
from pathlib import Path

# Create necessary directories
tests_dir = Path("tests")
pages_dir = Path("pages")
screenshots_dir = Path("screenshots")

for directory in [tests_dir, pages_dir, screenshots_dir]:
    directory.mkdir(exist_ok=True)

# Create base page
base_page_content = """
import logging
from typing import Any, Optional

class BasePage:
    \"\"\"Base class for all page objects\"\"\"
    
    def __init__(self, page):
        \"\"\"
        Initialize base page object
        
        Args:
            page: Playwright page object
        \"\"\"
        self.page = page
        self.url = ""  # URL path relative to base URL
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def navigate(self):
        \"\"\"Navigate to the page\"\"\"
        self.logger.info(f"Navigating to {self.url}")
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("networkidle")
    
    async def click(self, selector: str, timeout: int = 30000):
        \"\"\"
        Click an element
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
        \"\"\"
        self.logger.debug(f"Clicking element: {selector}")
        await self.page.wait_for_selector(selector, timeout=timeout)
        await self.page.click(selector)
    
    async def fill(self, selector: str, value: str, timeout: int = 30000):
        \"\"\"
        Fill an input field
        
        Args:
            selector: Element selector
            value: Value to fill
            timeout: Timeout in milliseconds
        \"\"\"
        self.logger.debug(f"Filling element {selector} with value: {value}")
        await self.page.wait_for_selector(selector, timeout=timeout)
        await self.page.fill(selector, value)
    
    async def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        \"\"\"
        Check if element is visible
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element is visible, False otherwise
        \"\"\"
        try:
            await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
            return True
        except Exception:
            return False
"""

with open(pages_dir / "base_page.py", "w") as f:
    f.write(base_page_content)

# Create login page
login_page_content = """
from pages.base_page import BasePage

class LoginPage(BasePage):
    \"\"\"Page object for login page\"\"\"
    
    def __init__(self, page):
        \"\"\"
        Initialize login page object
        
        Args:
            page: Playwright page object
        \"\"\"
        super().__init__(page)
        self.url = "https://the-internet.herokuapp.com/login"
        
        # Element selectors
        self.username_selector = "#username"
        self.password_selector = "#password"
        self.login_button_selector = "button[type='submit']"
        self.flash_message_selector = "#flash"
    
    async def login(self, username: str, password: str):
        \"\"\"
        Login with username and password
        
        Args:
            username: Username
            password: Password
        \"\"\"
        await self.fill(self.username_selector, username)
        await self.fill(self.password_selector, password)
        await self.click(self.login_button_selector)
    
    async def get_flash_message(self) -> str:
        \"\"\"
        Get flash message text
        
        Returns:
            Flash message text
        \"\"\"
        element = await self.page.wait_for_selector(self.flash_message_selector)
        return await element.text_content()
"""

with open(pages_dir / "login_page.py", "w") as f:
    f.write(login_page_content)

# Create conftest.py
conftest_content = """
import pytest
import logging
from pathlib import Path

# Create screenshots directory if it doesn't exist
screenshots_dir = Path("./screenshots")
screenshots_dir.mkdir(exist_ok=True)

@pytest.fixture
async def browser_setup():
    \"\"\"
    Fixture for browser setup
    
    Returns:
        tuple: (page, browser, context, playwright)
    \"\"\"
    from playwright.async_api import async_playwright
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    
    # Return the page, browser, context, and playwright
    yield page, browser, context, playwright
    
    # Cleanup
    await context.close()
    await browser.close()
    await playwright.stop()
"""

with open(tests_dir / "conftest.py", "w") as f:
    f.write(conftest_content)

# Create test file
test_content = """
import pytest
import logging
from datetime import datetime

from pages.login_page import LoginPage

class TestLogin:
    \"\"\"Test class for login\"\"\"
    
    @pytest.mark.asyncio
    async def test_login(self, browser_setup):
        \"\"\"
        Test login functionality
        
        Args:
            browser_setup: Browser setup fixture
        \"\"\"
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page object
            login_page = LoginPage(page)
            
            # Navigate to page
            await login_page.navigate()
            
            # Take screenshot before login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/login_before_{timestamp}.png")
            
            # Login
            await login_page.login("tomsmith", "SuperSecretPassword!")
            
            # Take screenshot after login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/login_after_{timestamp}.png")
            
            # Assert successful login
            flash_message = await login_page.get_flash_message()
            assert "You logged into a secure area" in flash_message
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/login_failure_{timestamp}.png")
            
            logging.error(f"Test failed: {str(e)}")
            raise

# Run test if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
"""

with open(tests_dir / "test_login.py", "w") as f:
    f.write(test_content)

print("Created simple test files:")
print(f"  - {pages_dir}/base_page.py")
print(f"  - {pages_dir}/login_page.py")
print(f"  - {tests_dir}/conftest.py")
print(f"  - {tests_dir}/test_login.py")
print("\nTo run the test:")
print("  pytest tests/test_login.py -v")

