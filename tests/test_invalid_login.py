import pytest
from playwright.sync_api import sync_playwright

@pytest.mark.asyncio
async def test_invalid_login(page):
    async with page as browser:
        await browser.goto("https://the-internet.herokuapp.com/login")  # Navigate to login page
        
        logging.info("Navigated to the Login Page.")
        
        invalid_username = "wronguser"
        invalid_password = "wrongpass"
        
        await page.fill('input[type="text"]', invalid_username)  # Enter invalid username
        await page.fill('input[type="password"]', invalid_password)  # Enter invalid password
        
        logging.info("Entered the Invalid Credentials.")
        
        try:
            await browser.click("#login-button")  # Click login button with id selector
            
            logging.info("Clicked on Login Button, expecting error message to appear...")
            
            await page.wait_for_selector(".error", timeout=10_000)  # Wait for the error element (assumed class ".error" is used by application)
            
        except Exception as e:
            logging.error("Error occurred while clicking login button.")
        
        try:
            await page.wait_for_url(f"/login?invalid=credentials")  # Wait for URL change indicating failed authentication (assuming this is the redirect)
            
        except Exception as e:
            logging.error("Error occurred while waiting for invalid credentials error in URL.")
        
        try:
            await page.wait_for_selector(".alert-danger", timeout=10_000)  # Wait for specific error message element (assuming class ".alert-danger" is used by application)
            
        except Exception as e:
            logging.error("Error occurred while waiting for the expected error message.")
        
        assert "Invalid username or password." in await page.inner_html(".alert-danger")  # Verify that an appropriate error message appears on screen