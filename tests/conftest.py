#!/usr/bin/env python3
"""
Pytest Configuration
===================
This module contains pytest configuration.
"""

import pytest
from playwright.sync_api import sync_playwright

# Skip adding the option if it's already defined
try:
    def pytest_addoption(parser):
        """
        Add command line options
        """
        try:
            parser.addoption("--headless", action="store_true", default=True, help="Run browser in headless mode")
        except ValueError:
            # Option already exists, ignore
            pass
except Exception as e:
    print(f"Warning: Could not add headless option: {e}")

@pytest.fixture
def browser_setup(request):
    """
    Set up browser
    
    Returns:
        tuple: (page, browser, context)
    """
    # Get headless option
    try:
        headless = request.config.getoption("--headless")
    except:
        headless = True
    
    # Start playwright
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    
    # Return page, browser, and context
    yield page, browser, context
    
    # Cleanup
    context.close()
    browser.close()
    playwright.stop()

