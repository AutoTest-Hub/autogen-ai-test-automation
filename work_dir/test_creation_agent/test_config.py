"""
Test Configuration for AutoGen Generated Tests
"""

import os
from typing import Dict, Any


class TestConfig:
    """Configuration settings for test execution"""
    
    # Application settings
    BASE_URL = os.getenv("BASE_URL", "https://www.advantageonlineshopping.com/#/")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
    
    # Browser settings
    BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    # Test data
    TEST_CREDENTIALS = {
        "username": os.getenv("TEST_USERNAME", "helios"),
        "password": os.getenv("TEST_PASSWORD", "Password123")
    }
    
    # Execution settings
    PARALLEL_EXECUTION = os.getenv("PARALLEL_EXECUTION", "false").lower() == "true"
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))
    
    # Reporting settings
    SCREENSHOT_ON_FAILURE = True
    GENERATE_HTML_REPORT = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_browser_config(cls) -> Dict[str, Any]:
        """Get browser configuration"""
        return {
            "browser_type": cls.BROWSER_TYPE,
            "headless": cls.HEADLESS,
            "timeout": cls.BROWSER_TIMEOUT
        }
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data configuration"""
        return {
            "credentials": cls.TEST_CREDENTIALS,
            "base_url": cls.BASE_URL,
            "api_base_url": cls.API_BASE_URL
        }


# Global config instance
config = TestConfig()
