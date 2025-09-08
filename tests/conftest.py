"""
Pytest Configuration
================
Configuration for pytest.
"""

import pytest
import logging
from pathlib import Path

# Create screenshots directory if it doesn't exist
screenshots_dir = Path("./screenshots")
screenshots_dir.mkdir(exist_ok=True)

@pytest.fixture
async def browser_setup():
    """
    Fixture for browser setup
    
    Returns:
        tuple: (page, browser, context, playwright)
    """
    from playwright.async_api import async_playwright
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Return the page, browser, context, and playwright
        yield page, browser, context, playwright
        
        # Cleanup
        await context.close()
        await browser.close()

