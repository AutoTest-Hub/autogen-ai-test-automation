"""
Base Page Object
==============
Base class for all page objects in the framework.
"""

import logging
from typing import Optional, Dict, Any

class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, page, base_url: str = "https://example.com"):
        """
        Initialize the base page object
        
        Args:
            page: The browser page object (Playwright Page or Selenium WebDriver)
            base_url: Base URL of the application
        """
        self.page = page
        self.base_url = base_url
        self.url = "/"  # Default URL path, to be overridden by subclasses
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def navigate(self):
        """Navigate to the page"""
        full_url = self.base_url + self.url
        self.logger.info(f"Navigating to {full_url}")
        
        # Handle different browser automation frameworks
        if hasattr(self.page, 'goto'):  # Playwright
            await self.page.goto(full_url)
            await self.page.wait_for_load_state("networkidle")
        elif hasattr(self.page, 'get'):  # Selenium
            self.page.get(full_url)
            # Wait for page to load would be implemented here
        else:
            raise ValueError("Unsupported browser automation framework")
    
    async def is_loaded(self) -> bool:
        """
        Check if the page is loaded
        
        Returns:
            bool: True if the page is loaded, False otherwise
        """
        try:
            # Default implementation, should be overridden by subclasses
            await self.page.wait_for_selector("body", timeout=5000)
            return True
        except Exception as e:
            self.logger.error(f"Error checking if page is loaded: {str(e)}")
            return False
    
    async def get_title(self) -> str:
        """
        Get the page title
        
        Returns:
            str: The page title
        """
        if hasattr(self.page, 'title'):  # Playwright
            return await self.page.title()
        elif hasattr(self.page, 'title'):  # Selenium
            return self.page.title
        else:
            raise ValueError("Unsupported browser automation framework")
    
    async def wait_for_element(self, selector: str, timeout: int = 5000) -> bool:
        """
        Wait for an element to be visible
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            
        Returns:
            bool: True if the element is visible, False otherwise
        """
        try:
            if hasattr(self.page, 'wait_for_selector'):  # Playwright
                await self.page.wait_for_selector(selector, timeout=timeout)
            elif hasattr(self.page, 'find_element'):  # Selenium
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                # Determine selector type
                by_type = By.CSS_SELECTOR
                if selector.startswith('//'):
                    by_type = By.XPATH
                
                WebDriverWait(self.page, timeout / 1000).until(
                    EC.visibility_of_element_located((by_type, selector))
                )
            else:
                raise ValueError("Unsupported browser automation framework")
            
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for element {selector}: {str(e)}")
            return False
    
    async def click(self, selector: str):
        """
        Click an element
        
        Args:
            selector: Element selector
        """
        try:
            if hasattr(self.page, 'click'):  # Playwright
                await self.page.click(selector)
            elif hasattr(self.page, 'find_element'):  # Selenium
                from selenium.webdriver.common.by import By
                
                # Determine selector type
                by_type = By.CSS_SELECTOR
                if selector.startswith('//'):
                    by_type = By.XPATH
                
                element = self.page.find_element(by_type, selector)
                element.click()
            else:
                raise ValueError("Unsupported browser automation framework")
        except Exception as e:
            self.logger.error(f"Error clicking element {selector}: {str(e)}")
            raise
    
    async def fill(self, selector: str, value: str):
        """
        Fill a form field
        
        Args:
            selector: Element selector
            value: Value to fill
        """
        try:
            if hasattr(self.page, 'fill'):  # Playwright
                await self.page.fill(selector, value)
            elif hasattr(self.page, 'find_element'):  # Selenium
                from selenium.webdriver.common.by import By
                
                # Determine selector type
                by_type = By.CSS_SELECTOR
                if selector.startswith('//'):
                    by_type = By.XPATH
                
                element = self.page.find_element(by_type, selector)
                element.clear()
                element.send_keys(value)
            else:
                raise ValueError("Unsupported browser automation framework")
        except Exception as e:
            self.logger.error(f"Error filling element {selector}: {str(e)}")
            raise
    
    async def get_text(self, selector: str) -> str:
        """
        Get text from an element
        
        Args:
            selector: Element selector
            
        Returns:
            str: The element text
        """
        try:
            if hasattr(self.page, 'text_content'):  # Playwright
                element = await self.page.query_selector(selector)
                if element:
                    return await element.text_content() or ""
                return ""
            elif hasattr(self.page, 'find_element'):  # Selenium
                from selenium.webdriver.common.by import By
                
                # Determine selector type
                by_type = By.CSS_SELECTOR
                if selector.startswith('//'):
                    by_type = By.XPATH
                
                element = self.page.find_element(by_type, selector)
                return element.text
            else:
                raise ValueError("Unsupported browser automation framework")
        except Exception as e:
            self.logger.error(f"Error getting text from element {selector}: {str(e)}")
            return ""

