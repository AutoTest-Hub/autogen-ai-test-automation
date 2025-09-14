"""
Pytest Configuration for AutoGen Generated Tests
"""

import pytest
import logging
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configure logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = f"test_results/{timestamp}"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/test_execution_{timestamp}.log'),
        logging.StreamHandler()
    ]
)

# Test configuration
BASE_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
# Read headless mode from environment variable, default to True
HEADLESS = os.getenv("PYTEST_HEADLESS", "true").lower() == "true"
TIMEOUT = 30000

# Browser configuration
BROWSER_CONFIG = {
    "headless": HEADLESS,
    "viewport": {"width": 1920, "height": 1080},
    "ignore_https_errors": True
}

@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "base_url": BASE_URL,
        "timeout": TIMEOUT,
        "browser_config": BROWSER_CONFIG
    }

@pytest.fixture(scope="function")
def browser_setup():
    """Browser setup fixture for Playwright tests"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=BROWSER_CONFIG["headless"],
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            viewport=BROWSER_CONFIG["viewport"],
            ignore_https_errors=BROWSER_CONFIG["ignore_https_errors"]
        )
        page = context.new_page()
        page.set_default_timeout(TIMEOUT)
        
        yield page, browser, context
        
        # Cleanup
        context.close()
        browser.close()

