"""
Test Real Application
==================
This test file demonstrates end-to-end testing with real applications
using the RealBrowserDiscoveryAgent for element discovery.
"""

import pytest
import logging
import asyncio
import json
from datetime import datetime
from pathlib import Path

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents
from agents.real_browser_discovery_agent import RealBrowserDiscoveryAgent
from models.mock_ai_provider import MockAIProvider

class TestRealApplication:
    """Test class for real application testing"""
    
    @pytest.fixture(scope="class")
    def discovery_agent(self):
        """
        Fixture for RealBrowserDiscoveryAgent
        
        Returns:
            RealBrowserDiscoveryAgent: The discovery agent
        """
        ai_provider = MockAIProvider()
        return RealBrowserDiscoveryAgent(local_ai_provider=ai_provider)
    
    @pytest.mark.asyncio
    async def test_the_internet_login(self, browser_setup, discovery_agent):
        """
        Test login on The Internet Herokuapp
        
        Args:
            browser_setup: Browser setup fixture
            discovery_agent: Discovery agent fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Step 1: Discover login page elements
            login_url = "https://the-internet.herokuapp.com/login"
            
            logging.info(f"Discovering elements on {login_url}")
            
            discovery_result = await discovery_agent._discover_page_elements({
                "page_url": login_url,
                "element_types": ["inputs", "buttons", "forms"]
            })
            
            assert discovery_result["status"] == "completed", "Element discovery should complete successfully"
            
            # Save discovery results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"the_internet_login_discovery_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(discovery_result, f, indent=2)
            
            logging.info(f"Discovery results saved to {results_file}")
            
            # Step 2: Extract selectors for username, password, and login button
            elements = discovery_result.get("elements", {})
            
            # Find username input
            username_selector = None
            for input_el in elements.get("inputs", []):
                input_type = input_el.get("type", "")
                input_id = input_el.get("id", "")
                
                if input_type == "text" and input_id == "username":
                    username_selector = input_el.get("css")
                    break
            
            # Find password input
            password_selector = None
            for input_el in elements.get("inputs", []):
                input_type = input_el.get("type", "")
                input_id = input_el.get("id", "")
                
                if input_type == "password" and input_id == "password":
                    password_selector = input_el.get("css")
                    break
            
            # Find login button
            login_button_selector = None
            for button in elements.get("buttons", []):
                button_type = button.get("type", "")
                button_text = button.get("text", "")
                
                if button_type == "submit" and "Login" in button_text:
                    login_button_selector = button.get("css")
                    break
            
            # Verify selectors were found
            assert username_selector, "Username selector should be found"
            assert password_selector, "Password selector should be found"
            assert login_button_selector, "Login button selector should be found"
            
            logging.info(f"Found selectors:")
            logging.info(f"  Username: {username_selector}")
            logging.info(f"  Password: {password_selector}")
            logging.info(f"  Login button: {login_button_selector}")
            
            # Step 3: Use the discovered selectors to perform login
            await page.goto(login_url)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot before login
            await page.screenshot(path=f"screenshots/before_login_{timestamp}.png")
            
            # Fill username and password
            await page.fill(username_selector, "tomsmith")
            await page.fill(password_selector, "SuperSecretPassword!")
            
            # Click login button
            await page.click(login_button_selector)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot after login
            await page.screenshot(path=f"screenshots/after_login_{timestamp}.png")
            
            # Verify successful login
            success_message = await page.text_content(".flash.success")
            assert "You logged into a secure area" in success_message, "Login should be successful"
            
            logging.info("Login successful!")
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/login_failure_{timestamp}.png")
            
            logging.error(f"Test failed: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_saucedemo_login(self, browser_setup, discovery_agent):
        """
        Test login on Sauce Demo
        
        Args:
            browser_setup: Browser setup fixture
            discovery_agent: Discovery agent fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Step 1: Discover login page elements
            login_url = "https://www.saucedemo.com/"
            
            logging.info(f"Discovering elements on {login_url}")
            
            discovery_result = await discovery_agent._discover_page_elements({
                "page_url": login_url,
                "element_types": ["inputs", "buttons", "forms"]
            })
            
            assert discovery_result["status"] == "completed", "Element discovery should complete successfully"
            
            # Save discovery results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"saucedemo_login_discovery_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(discovery_result, f, indent=2)
            
            logging.info(f"Discovery results saved to {results_file}")
            
            # Step 2: Extract selectors for username, password, and login button
            elements = discovery_result.get("elements", {})
            
            # Find username input
            username_selector = None
            for input_el in elements.get("inputs", []):
                input_type = input_el.get("type", "")
                input_id = input_el.get("id", "")
                input_name = input_el.get("name", "")
                
                if input_type == "text" and (input_id == "user-name" or input_name == "user-name"):
                    username_selector = input_el.get("css")
                    break
            
            # Find password input
            password_selector = None
            for input_el in elements.get("inputs", []):
                input_type = input_el.get("type", "")
                input_id = input_el.get("id", "")
                input_name = input_el.get("name", "")
                
                if input_type == "password" and (input_id == "password" or input_name == "password"):
                    password_selector = input_el.get("css")
                    break
            
            # Find login button
            login_button_selector = None
            for button in elements.get("buttons", []):
                button_type = button.get("type", "")
                button_id = button.get("id", "")
                button_name = button.get("name", "")
                
                if button_type == "submit" or button_id == "login-button" or button_name == "login-button":
                    login_button_selector = button.get("css")
                    break
            
            # Verify selectors were found
            assert username_selector, "Username selector should be found"
            assert password_selector, "Password selector should be found"
            assert login_button_selector, "Login button selector should be found"
            
            logging.info(f"Found selectors:")
            logging.info(f"  Username: {username_selector}")
            logging.info(f"  Password: {password_selector}")
            logging.info(f"  Login button: {login_button_selector}")
            
            # Step 3: Use the discovered selectors to perform login
            await page.goto(login_url)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot before login
            await page.screenshot(path=f"screenshots/saucedemo_before_login_{timestamp}.png")
            
            # Fill username and password
            await page.fill(username_selector, "standard_user")
            await page.fill(password_selector, "secret_sauce")
            
            # Click login button
            await page.click(login_button_selector)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot after login
            await page.screenshot(path=f"screenshots/saucedemo_after_login_{timestamp}.png")
            
            # Verify successful login by checking for inventory page
            inventory_title = await page.text_content(".title")
            assert "Products" in inventory_title, "Login should be successful"
            
            logging.info("Login successful!")
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/saucedemo_login_failure_{timestamp}.png")
            
            logging.error(f"Test failed: {str(e)}")
            raise

# Run tests if executed directly
if __name__ == "__main__":
    # Install Playwright browsers if needed
    try:
        import subprocess
        from playwright.async_api import async_playwright
        
        # Check if browsers are installed
        async def check_browsers():
            async with async_playwright() as p:
                try:
                    browser = await p.chromium.launch(headless=True)
                    await browser.close()
                    return True
                except Exception:
                    return False
        
        if not asyncio.run(check_browsers()):
            print("Installing Playwright browsers...")
            subprocess.run(["playwright", "install", "chromium"])
    except ImportError:
        print("Installing Playwright...")
        subprocess.run(["pip", "install", "playwright"])
        subprocess.run(["playwright", "install", "chromium"])
    
    # Run pytest
    pytest.main(["-xvs", __file__])

