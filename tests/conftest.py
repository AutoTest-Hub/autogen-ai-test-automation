"""
Pytest Configuration
================
Configuration for pytest.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright

@pytest.fixture
def browser_setup(event_loop):
    """
    Fixture for browser setup that works with pytest-asyncio
    
    Returns:
        tuple: (page, browser, context, playwright)
    """
    # Create a new event loop
    async def setup():
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        return page, browser, context, playwright
    
    # Run the setup in the event loop
    return event_loop.run_until_complete(setup())

