"""
Pytest Configuration for AutoGen Generated Tests
"""

import pytest
import logging
from datetime import datetime

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
BASE_URL = "https://example.com"
HEADLESS = True
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
