"""
Pytest configuration and fixtures for test automation
"""

import os
import pytest
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Skip adding the option if it's already defined
try:
    def pytest_addoption(parser):
        """
        Add command line options
        """
        try:
            parser.addoption("--headless", action="store_true", default=True, help="Run browser in headless mode")
            parser.addoption("--no-headless", action="store_false", dest="headless", help="Run browser with UI visible")
        except ValueError:
            # Option already exists, ignore
            pass
except Exception as e:
    pass

# Global variables for test session
test_session_timestamp = None
test_results_dir = None

def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    global test_session_timestamp, test_results_dir
    test_session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_results_dir = Path(f"test_results/{test_session_timestamp}")
    test_results_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging for this test session
    log_file = test_results_dir / f"test_execution_{test_session_timestamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results and handle screenshots"""
    outcome = yield
    rep = outcome.get_result()
    
    # Only process during the call phase (actual test execution)
    if call.when == "call":
        global test_results_dir
        if test_results_dir and hasattr(item, 'funcargs') and 'browser_setup' in item.funcargs:
            page, browser, context = item.funcargs['browser_setup']
            test_name = item.name
            
            try:
                if rep.passed:
                    # Take screenshot on success
                    screenshot_path = test_results_dir / f"test_success_{test_name}_{test_session_timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    logging.info(f"✅ Test {test_name} PASSED - Screenshot: {screenshot_path}")
                    
                elif rep.failed:
                    # Take screenshot on failure
                    screenshot_path = test_results_dir / f"test_failure_{test_name}_{test_session_timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    logging.error(f"❌ Test {test_name} FAILED - Screenshot: {screenshot_path}")
                    logging.error(f"Failure reason: {rep.longrepr}")
                    
            except Exception as e:
                logging.warning(f"Could not capture screenshot for {test_name}: {e}")

@pytest.fixture(scope="function")
def browser_setup(request):
    """
    Browser setup fixture with automatic cleanup
    """
    # Get headless setting from environment variable (set by execution agent) or command line
    headless = os.environ.get('PYTEST_HEADLESS', 'true').lower() == 'true'
    if hasattr(request.config.option, 'headless'):
        headless = request.config.option.headless
    
    playwright = sync_playwright().start()
    
    # Launch browser with appropriate settings
    browser = playwright.chromium.launch(
        headless=headless,
        args=['--no-sandbox', '--disable-dev-shm-usage'] if headless else []
    )
    
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        ignore_https_errors=True
    )
    
    page = context.new_page()
    
    # Log test start
    test_name = request.node.name
    logging.info(f"🚀 Starting test: {test_name}")
    
    yield page, browser, context
    
    # Cleanup
    logging.info(f"🏁 Completed test: {test_name}")
    context.close()
    browser.close()
    playwright.stop()

