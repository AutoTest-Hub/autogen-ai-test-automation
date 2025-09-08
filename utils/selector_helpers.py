"""
Selector Helpers
=============
Utility functions for working with selectors.
"""

from typing import List, Dict, Any, Optional

def get_best_selector(selectors: List[Dict[str, Any]]) -> Optional[str]:
    """
    Get the best selector from a list of selectors
    
    Args:
        selectors: List of selector objects
        
    Returns:
        str: The best selector value, or None if no selectors are provided
    """
    if not selectors:
        return None
    
    # Sort selectors by priority
    priority_order = {"highest": 0, "high": 1, "medium": 2, "low": 3}
    sorted_selectors = sorted(
        selectors, 
        key=lambda s: priority_order.get(s.get("priority", "low"), 99)
    )
    
    # Return the highest priority selector
    return sorted_selectors[0].get("value")

def get_selector_by_type(selectors: List[Dict[str, Any]], selector_type: str) -> Optional[str]:
    """
    Get a selector of a specific type from a list of selectors
    
    Args:
        selectors: List of selector objects
        selector_type: Type of selector to get (css, xpath, id)
        
    Returns:
        str: The selector value, or None if no matching selector is found
    """
    if not selectors:
        return None
    
    # Find selector of the specified type
    for selector in selectors:
        if selector.get("type") == selector_type:
            return selector.get("value")
    
    return None

def is_xpath_selector(selector: str) -> bool:
    """
    Check if a selector is an XPath selector
    
    Args:
        selector: Selector to check
        
    Returns:
        bool: True if the selector is an XPath selector, False otherwise
    """
    return selector.startswith('//') or selector.startswith('(//') or selector.startswith('xpath=')

def is_css_selector(selector: str) -> bool:
    """
    Check if a selector is a CSS selector
    
    Args:
        selector: Selector to check
        
    Returns:
        bool: True if the selector is a CSS selector, False otherwise
    """
    return not is_xpath_selector(selector)

def convert_to_playwright_selector(selector: str) -> str:
    """
    Convert a selector to a format compatible with Playwright
    
    Args:
        selector: Selector to convert
        
    Returns:
        str: Playwright-compatible selector
    """
    if is_xpath_selector(selector):
        # Remove 'xpath=' prefix if present
        if selector.startswith('xpath='):
            selector = selector[6:]
        return f"xpath={selector}"
    return selector

def convert_to_selenium_selector(selector: str) -> tuple:
    """
    Convert a selector to a format compatible with Selenium
    
    Args:
        selector: Selector to convert
        
    Returns:
        tuple: (By type, selector value)
    """
    from selenium.webdriver.common.by import By
    
    if is_xpath_selector(selector):
        # Remove 'xpath=' prefix if present
        if selector.startswith('xpath='):
            selector = selector[6:]
        return (By.XPATH, selector)
    return (By.CSS_SELECTOR, selector)

