"""
Priority-Based Locator Strategy
==============================
This module provides a robust locator strategy with automatic fallback mechanisms
for web automation testing using Playwright.
"""

import logging
from typing import Dict, List, Optional, Union
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class LocatorStrategy:
    """
    Priority-based locator strategy with automatic fallback mechanism.
    
    This class provides a robust way to locate elements on web pages by trying
    multiple selectors in order of priority until one succeeds.
    """
    
    def __init__(self, page: Page):
        """
        Initialize the locator strategy.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.locator_map = self._build_locator_map()
    
    def _build_locator_map(self) -> Dict[str, List[str]]:
        """
        Build the comprehensive locator map with priority-ordered selectors.
        
        Returns:
            Dict mapping semantic element types to priority-ordered selector lists
        """
        return {
            # Authentication Elements
            "username_field": [
                # High priority - specific attributes
                "[data-testid*='username']",
                "[data-testid*='email']", 
                "#username",
                "#email",
                "input[name='username']",
                "input[name='email']",
                # Medium priority - type and placeholder based
                "input[type='text'][placeholder*='username' i]",
                "input[type='text'][placeholder*='email' i]",
                "input[type='email']",
                ".username-input",
                ".email-input",
                # Low priority - generic patterns
                "input[type='text']:first-of-type",
                ".form-control:first-of-type",
                "input:first-of-type"
            ],
            
            "password_field": [
                # High priority
                "[data-testid*='password']",
                "#password",
                "input[name='password']",
                # Medium priority
                "input[type='password']",
                ".password-input",
                ".form-password",
                # Low priority
                "input[placeholder*='password' i]"
            ],
            
            "login_button": [
                # High priority
                "[data-testid*='login']",
                "[data-testid*='signin']",
                "#login-button",
                "#signin-button",
                "button[name='login']",
                "input[name='login']",
                # Medium priority
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Login')",
                "button:has-text('Sign in')",
                "button:has-text('Log in')",
                # Low priority
                ".login-btn",
                ".btn-login",
                ".signin-btn",
                ".submit-btn"
            ],
            
            "logout_button": [
                # High priority
                "[data-testid*='logout']",
                "[data-testid*='signout']",
                "#logout",
                "button[name='logout']",
                # Medium priority
                "button:has-text('Logout')",
                "button:has-text('Log out')",
                "button:has-text('Sign out')",
                "a:has-text('Logout')",
                "a:has-text('Log out')",
                # Low priority
                "[aria-label*='logout' i]",
                ".logout",
                ".signout"
            ],
            
            # Navigation Elements
            "user_display": [
                # High priority
                "[data-testid*='user']",
                "[data-testid*='profile']",
                "[data-testid*='account']",
                # Medium priority
                ".user-name",
                ".username",
                ".profile-name",
                ".account-name",
                # Low priority
                "[class*='user']",
                "[class*='profile']",
                "[class*='account']",
                "[aria-label*='user' i]",
                "[title*='user' i]"
            ],
            
            "dashboard_content": [
                # High priority
                "[data-testid*='dashboard']",
                "#dashboard",
                ".dashboard",
                # Medium priority
                ".main-content",
                ".content",
                "main",
                # Low priority
                ".dashboard-widget",
                "[class*='dashboard']",
                ".home-content"
            ],
            
            # Validation Elements
            "error_message": [
                # High priority
                "[role='alert']",
                "[data-testid*='error']",
                ".error",
                ".alert-danger",
                ".alert-error",
                # Medium priority
                ".error-message",
                ".invalid-feedback",
                ".field-error",
                ".validation-error",
                # Low priority
                "[class*='error']",
                ".alert"
            ],
            
            "success_message": [
                # High priority
                "[data-testid*='success']",
                ".success",
                ".alert-success",
                # Medium priority
                ".success-message",
                ".confirmation",
                # Low priority
                "[class*='success']"
            ],
            
            "validation_message": [
                # High priority
                ".invalid-feedback",
                ".field-error",
                ".validation-error",
                # Medium priority
                "[role='alert']",
                ".error",
                # Low priority
                "[class*='error']",
                "[class*='invalid']"
            ]
        }
    
    def find_element(self, semantic_type: str, timeout: int = 5000) -> Optional[Locator]:
        """
        Find element using priority-based fallback strategy.
        
        Args:
            semantic_type: Semantic type of element (e.g., 'username_field')
            timeout: Timeout in milliseconds for each selector attempt
            
        Returns:
            Playwright Locator if found, None otherwise
        """
        selectors = self.locator_map.get(semantic_type, [])
        
        if not selectors:
            logger.warning(f"No selectors defined for semantic type: {semantic_type}")
            return None
        
        for i, selector in enumerate(selectors):
            try:
                logger.debug(f"Trying selector {i+1}/{len(selectors)} for {semantic_type}: {selector}")
                locator = self.page.locator(selector)
                
                # Check if element exists and is visible
                if locator.count() > 0:
                    # Use first() to get the first matching element
                    first_locator = locator.first
                    if first_locator.is_visible(timeout=timeout):
                        logger.info(f"Found {semantic_type} using selector: {selector}")
                        return first_locator
                
            except PlaywrightTimeoutError:
                logger.debug(f"Timeout for selector: {selector}")
                continue
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {str(e)}")
                continue
        
        logger.warning(f"Could not find element for semantic type: {semantic_type}")
        return None
    
    def is_visible(self, semantic_type: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            timeout: Timeout in milliseconds
            
        Returns:
            True if element is visible, False otherwise
        """
        element = self.find_element(semantic_type, timeout)
        return element is not None
    
    def click(self, semantic_type: str, timeout: int = 5000) -> bool:
        """
        Click element using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            timeout: Timeout in milliseconds
            
        Returns:
            True if click succeeded, False otherwise
        """
        element = self.find_element(semantic_type, timeout)
        if element:
            try:
                element.click(timeout=timeout)
                logger.info(f"Successfully clicked {semantic_type}")
                return True
            except Exception as e:
                logger.error(f"Failed to click {semantic_type}: {str(e)}")
                return False
        return False
    
    def fill(self, semantic_type: str, value: str, timeout: int = 5000) -> bool:
        """
        Fill element using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            value: Value to fill
            timeout: Timeout in milliseconds
            
        Returns:
            True if fill succeeded, False otherwise
        """
        element = self.find_element(semantic_type, timeout)
        if element:
            try:
                element.fill(value, timeout=timeout)
                logger.info(f"Successfully filled {semantic_type} with value")
                return True
            except Exception as e:
                logger.error(f"Failed to fill {semantic_type}: {str(e)}")
                return False
        return False
    
    def get_text(self, semantic_type: str, timeout: int = 5000) -> Optional[str]:
        """
        Get text content of element using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            timeout: Timeout in milliseconds
            
        Returns:
            Text content if found, None otherwise
        """
        element = self.find_element(semantic_type, timeout)
        if element:
            try:
                text = element.text_content(timeout=timeout)
                logger.info(f"Successfully got text from {semantic_type}")
                return text
            except Exception as e:
                logger.error(f"Failed to get text from {semantic_type}: {str(e)}")
                return None
        return None
    
    def wait_for_element(self, semantic_type: str, timeout: int = 10000) -> bool:
        """
        Wait for element to appear using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            timeout: Timeout in milliseconds
            
        Returns:
            True if element appeared, False otherwise
        """
        selectors = self.locator_map.get(semantic_type, [])
        
        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                locator.first.wait_for(state="visible", timeout=timeout)
                logger.info(f"Element {semantic_type} appeared using selector: {selector}")
                return True
            except PlaywrightTimeoutError:
                continue
            except Exception as e:
                logger.debug(f"Error waiting for {selector}: {str(e)}")
                continue
        
        logger.warning(f"Element {semantic_type} did not appear within timeout")
        return False
    
    def add_custom_selectors(self, semantic_type: str, selectors: List[str], priority: str = "medium"):
        """
        Add custom selectors for a semantic type.
        
        Args:
            semantic_type: Semantic type of element
            selectors: List of selectors to add
            priority: Priority level ('high', 'medium', 'low')
        """
        if semantic_type not in self.locator_map:
            self.locator_map[semantic_type] = []
        
        existing_selectors = self.locator_map[semantic_type]
        
        if priority == "high":
            # Insert at the beginning
            self.locator_map[semantic_type] = selectors + existing_selectors
        elif priority == "low":
            # Append at the end
            self.locator_map[semantic_type].extend(selectors)
        else:  # medium priority
            # Insert in the middle
            mid_point = len(existing_selectors) // 2
            self.locator_map[semantic_type] = (
                existing_selectors[:mid_point] + 
                selectors + 
                existing_selectors[mid_point:]
            )
        
        logger.info(f"Added {len(selectors)} custom selectors for {semantic_type} with {priority} priority")

