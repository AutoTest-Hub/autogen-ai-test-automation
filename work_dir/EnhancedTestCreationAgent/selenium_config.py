"""
Selenium WebDriver Configuration
===============================
"""

import os

class SeleniumConfig:
    """Configuration for Selenium WebDriver tests"""
    
    # Browser settings
    HEADLESS = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
    BROWSER = os.getenv('SELENIUM_BROWSER', 'chrome')
    
    # Window settings
    WINDOW_WIDTH = int(os.getenv('SELENIUM_WINDOW_WIDTH', '1920'))
    WINDOW_HEIGHT = int(os.getenv('SELENIUM_WINDOW_HEIGHT', '1080'))
    
    # Timeout settings
    IMPLICIT_WAIT = int(os.getenv('SELENIUM_IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('SELENIUM_EXPLICIT_WAIT', '10'))
    
    # Test settings
    SCREENSHOT_ON_FAILURE = os.getenv('SELENIUM_SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    
    # Application settings
    BASE_URL = os.getenv('APPLICATION_URL', 'https://example.com')
