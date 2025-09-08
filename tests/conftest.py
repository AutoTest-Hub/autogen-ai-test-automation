"""
Pytest Configuration for AutoGen Generated Tests
"""

import pytest
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'test_execution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

# Test configuration
BASE_URL = os.environ.get("TEST_BASE_URL", "https://example.com")
HEADLESS = os.environ.get("TEST_HEADLESS", "true").lower() == "true"
TIMEOUT = int(os.environ.get("TEST_TIMEOUT", "30000"))
BROWSER = os.environ.get("TEST_BROWSER", "chromium")  # chromium, firefox, webkit

# Browser configuration
BROWSER_CONFIG = {
    "headless": HEADLESS,
    "viewport": {"width": 1920, "height": 1080},
    "ignore_https_errors": True,
    "timeout": TIMEOUT
}

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """
    Test configuration fixture
    
    Returns:
        Dict[str, Any]: Test configuration
    """
    return {
        "base_url": BASE_URL,
        "timeout": TIMEOUT,
        "browser": BROWSER,
        "browser_config": BROWSER_CONFIG
    }

@pytest.fixture
async def browser_setup(test_config):
    """
    Setup browser for tests
    
    Args:
        test_config: Test configuration
        
    Returns:
        Tuple: (page, browser, context, playwright)
    """
    from playwright.async_api import async_playwright
    
    # Start Playwright
    playwright = await async_playwright().start()
    
    # Select browser based on configuration
    browser_type = test_config.get("browser", "chromium")
    if browser_type == "firefox":
        browser_instance = playwright.firefox
    elif browser_type == "webkit":
        browser_instance = playwright.webkit
    else:
        browser_instance = playwright.chromium
    
    # Launch browser
    browser = await browser_instance.launch(
        headless=test_config.get("browser_config", {}).get("headless", True)
    )
    
    # Create context
    context = await browser.new_context(
        viewport=test_config.get("browser_config", {}).get("viewport", {"width": 1280, "height": 720}),
        ignore_https_errors=test_config.get("browser_config", {}).get("ignore_https_errors", True)
    )
    
    # Create page
    page = await context.new_page()
    
    # Set base URL
    page.base_url = test_config.get("base_url", "https://example.com")
    
    # Set default timeout
    page.default_timeout = test_config.get("timeout", 30000)
    
    try:
        # Return browser setup
        return page, browser, context, playwright
    finally:
        # Cleanup will be handled by the test
        pass

@pytest.fixture
async def browser_with_cleanup(browser_setup):
    """
    Browser setup with automatic cleanup
    
    Args:
        browser_setup: Browser setup fixture
        
    Yields:
        Tuple: (page, browser, context, playwright)
    """
    page, browser, context, playwright = browser_setup
    
    try:
        yield page, browser, context, playwright
    finally:
        # Cleanup
        await context.close()
        await browser.close()
        await playwright.stop()

@pytest.fixture(scope="function")
def selenium_setup(test_config):
    """
    Setup Selenium WebDriver for tests
    
    Args:
        test_config: Test configuration
        
    Yields:
        WebDriver: Selenium WebDriver instance
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Setup Chrome options
        chrome_options = Options()
        if test_config.get("browser_config", {}).get("headless", True):
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={test_config.get('browser_config', {}).get('viewport', {}).get('width', 1280)},{test_config.get('browser_config', {}).get('viewport', {}).get('height', 720)}")
        
        # Initialize WebDriver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Set implicit wait
        driver.implicitly_wait(test_config.get("timeout", 30000) / 1000)
        
        # Yield WebDriver
        yield driver
        
        # Cleanup
        driver.quit()
    except ImportError:
        pytest.skip("Selenium not installed. Skipping Selenium tests.")

