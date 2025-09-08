"""
Standalone test for real browser discovery
This test doesn't depend on the AutoGen framework
"""

import asyncio
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_the_internet_login():
    """Test login on The Internet Herokuapp"""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to login page
            login_url = "https://the-internet.herokuapp.com/login"
            await page.goto(login_url)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot before login
            await page.screenshot(path="screenshots/standalone_before_login.png")
            
            # Discover username input
            username_selector = "#username"
            password_selector = "#password"
            login_button_selector = "button[type='submit']"
            
            # Fill username and password
            await page.fill(username_selector, "tomsmith")
            await page.fill(password_selector, "SuperSecretPassword!")
            
            # Click login button
            await page.click(login_button_selector)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot after login
            await page.screenshot(path="screenshots/standalone_after_login.png")
            
            # Verify successful login
            success_message = await page.text_content(".flash.success")
            assert "You logged into a secure area" in success_message, "Login should be successful"
            
            print("Login successful!")
            
        finally:
            await context.close()
            await browser.close()

@pytest.mark.asyncio
async def test_saucedemo_login():
    """Test login on Sauce Demo"""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to login page
            login_url = "https://www.saucedemo.com/"
            await page.goto(login_url)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot before login
            await page.screenshot(path="screenshots/standalone_saucedemo_before_login.png")
            
            # Discover username input
            username_selector = "#user-name"
            password_selector = "#password"
            login_button_selector = "#login-button"
            
            # Fill username and password
            await page.fill(username_selector, "standard_user")
            await page.fill(password_selector, "secret_sauce")
            
            # Click login button
            await page.click(login_button_selector)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot after login
            await page.screenshot(path="screenshots/standalone_saucedemo_after_login.png")
            
            # Verify successful login by checking for inventory page
            inventory_title = await page.text_content(".title")
            assert "Products" in inventory_title, "Login should be successful"
            
            print("Login successful!")
            
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_the_internet_login())
    asyncio.run(test_saucedemo_login())

