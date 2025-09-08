"""
Selector Helpers
=============
Utility functions for working with selectors.
"""

import re
from typing import List, Dict, Any, Optional, Union, Tuple

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
    try:
        from selenium.webdriver.common.by import By
        
        if is_xpath_selector(selector):
            # Remove 'xpath=' prefix if present
            if selector.startswith('xpath='):
                selector = selector[6:]
            return (By.XPATH, selector)
        elif selector.startswith('#'):
            return (By.ID, selector[1:])
        elif selector.startswith('.'):
            return (By.CLASS_NAME, selector[1:])
        elif selector.startswith('[name='):
            # Extract name from [name='value']
            match = re.match(r"\[name=['\"]([^'\"]+)['\"]\]", selector)
            if match:
                return (By.NAME, match.group(1))
        return (By.CSS_SELECTOR, selector)
    except ImportError:
        # Return a tuple of strings if Selenium is not installed
        if is_xpath_selector(selector):
            return ("xpath", selector)
        elif selector.startswith('#'):
            return ("id", selector[1:])
        elif selector.startswith('.'):
            return ("class name", selector[1:])
        elif selector.startswith('[name='):
            match = re.match(r"\[name=['\"]([^'\"]+)['\"]\]", selector)
            if match:
                return ("name", match.group(1))
        return ("css selector", selector)

class SelectorStrategy:
    """
    Selector strategy for finding the most robust selectors
    
    This class provides methods for generating and ranking selectors
    based on reliability and robustness.
    """
    
    @staticmethod
    def get_optimal_selector(element_data: Dict[str, Any]) -> str:
        """
        Get the optimal selector for an element
        
        Args:
            element_data: Element data including id, name, class, etc.
            
        Returns:
            str: The optimal selector
        """
        # Try ID selector (most reliable)
        if element_data.get("id"):
            return f"#{element_data['id']}"
        
        # Try name selector
        if element_data.get("name"):
            return f"[name='{element_data['name']}']"
        
        # Try data-testid or other data attributes
        for key in element_data:
            if key.startswith("data-"):
                return f"[{key}='{element_data[key]}']"
        
        # Try class selector if it's not too generic
        if element_data.get("class"):
            classes = element_data["class"].split()
            if len(classes) > 0:
                # Filter out common utility classes
                specific_classes = [c for c in classes if not SelectorStrategy._is_utility_class(c)]
                if specific_classes:
                    return f".{specific_classes[0]}"
        
        # Try tag with attribute
        tag = element_data.get("tag", "div")
        if element_data.get("type"):
            return f"{tag}[type='{element_data['type']}']"
        
        # Last resort: XPath
        if element_data.get("xpath"):
            return element_data["xpath"]
        
        # Fallback
        return f"{tag}"
    
    @staticmethod
    def _is_utility_class(class_name: str) -> bool:
        """
        Check if a class is a utility class
        
        Args:
            class_name: Class name to check
            
        Returns:
            bool: True if it's a utility class
        """
        utility_patterns = [
            r'^(mt|mb|ml|mr|pt|pb|pl|pr|m|p)-\d+$',  # Margin/padding utilities
            r'^(flex|grid|block|inline|hidden)$',     # Display utilities
            r'^(text|bg|border)-',                    # Text, background, border utilities
            r'^(w|h)-',                               # Width/height utilities
            r'^(rounded|shadow)',                     # Border radius and shadow utilities
            r'^(hover|focus|active)',                 # State utilities
            r'^(sm|md|lg|xl):',                       # Responsive utilities
            r'^(ng-|v-)',                             # Framework-specific classes
        ]
        
        return any(re.match(pattern, class_name) for pattern in utility_patterns)
    
    @staticmethod
    def generate_selector_alternatives(element_data: Dict[str, Any]) -> List[str]:
        """
        Generate alternative selectors for an element
        
        Args:
            element_data: Element data
            
        Returns:
            List[str]: List of alternative selectors
        """
        alternatives = []
        
        # ID selector
        if element_data.get("id"):
            alternatives.append(f"#{element_data['id']}")
        
        # Name selector
        if element_data.get("name"):
            alternatives.append(f"[name='{element_data['name']}']")
        
        # Tag and type
        if element_data.get("tag") and element_data.get("type"):
            alternatives.append(f"{element_data['tag']}[type='{element_data['type']}']")
        
        # Class selector
        if element_data.get("class"):
            classes = element_data["class"].split()
            if classes:
                alternatives.append(f".{classes[0]}")
        
        # Text content for buttons and links
        if element_data.get("text") and element_data.get("tag") in ["button", "a"]:
            text = element_data["text"].strip()
            if text:
                alternatives.append(f"{element_data['tag']}:has-text('{text}')")
        
        # XPath
        if element_data.get("xpath"):
            alternatives.append(element_data["xpath"])
        
        return alternatives
    
    @staticmethod
    def rank_selectors(selectors: List[str]) -> List[str]:
        """
        Rank selectors by reliability
        
        Args:
            selectors: List of selectors
            
        Returns:
            List[str]: Ranked selectors
        """
        def get_selector_score(selector: str) -> int:
            """Get a score for a selector based on reliability"""
            if selector.startswith('#'):
                return 100  # ID selectors are most reliable
            elif selector.startswith('[data-testid'):
                return 90   # data-testid selectors are very reliable
            elif selector.startswith('[name'):
                return 80   # name selectors are reliable
            elif ':has-text(' in selector:
                return 70   # text selectors are good but can change
            elif selector.startswith('.'):
                return 60   # class selectors can change
            elif selector.startswith('['):
                return 50   # attribute selectors
            elif selector.startswith('//'):
                return 40   # XPath selectors are less reliable
            else:
                return 30   # Tag selectors are least reliable
        
        return sorted(selectors, key=get_selector_score, reverse=True)

def get_robust_selector(element_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Get robust selectors for an element with fallbacks
    
    Args:
        element_data: Element data
        
    Returns:
        Dict[str, str]: Dictionary with primary and fallback selectors
    """
    alternatives = SelectorStrategy.generate_selector_alternatives(element_data)
    ranked = SelectorStrategy.rank_selectors(alternatives)
    
    result = {
        "primary": ranked[0] if ranked else "",
    }
    
    # Add fallbacks
    for i, selector in enumerate(ranked[1:3], 1):
        result[f"fallback{i}"] = selector
    
    return result

