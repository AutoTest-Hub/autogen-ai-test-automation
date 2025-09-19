"""
Priority-Based Locator Strategy
==============================
This module provides a robust locator strategy with automatic fallback mechanism
for web element location using semantic types and priority-ordered selectors.
"""

import logging
import re
from typing import List, Dict, Optional
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
            
            "user_dropdown": [
                # High priority - specific dropdown indicators
                "[data-testid*='user-dropdown']",
                "[data-testid*='user-menu']",
                "[data-testid*='profile-dropdown']",
                ".user-dropdown",
                ".profile-dropdown",
                ".user-menu",
                # Medium priority - user elements with dropdown indicators
                "[class*='user'][class*='dropdown']",
                "[class*='user'] .dropdown-toggle",
                ".user-name[data-toggle='dropdown']",
                ".username[data-toggle='dropdown']",
                # Low priority - generic user elements (clickable)
                "[class*='user']:not(input):not(label)",
                "[class*='profile']:not(input):not(label)",
                ".user-info",
                ".profile-info",
                "[aria-haspopup='true'][class*='user']"
            ],
            
            "menu_item": [
                # High priority - specific menu items
                "[data-testid*='menu-item']",
                "[data-testid*='nav-item']",
                "[role='menuitem']",
                ".menu-item",
                ".nav-item",
                ".navigation-item",
                # Medium priority - navigation links
                "nav a",
                ".nav-link",
                ".menu-link",
                ".sidebar-nav a",
                ".main-nav a",
                # Low priority - generic menu patterns
                ".nav li a",
                ".menu li a",
                "ul.nav a",
                "ul.menu a"
            ],
            
            "button": [
                # High priority - semantic buttons
                "button",
                "[type='button']",
                "[type='submit']",
                "[role='button']",
                # Medium priority - button-like elements
                ".btn",
                ".button",
                ".submit",
                ".action-btn",
                # Low priority - clickable elements
                "[onclick]",
                ".clickable",
                "input[type='button']",
                "input[type='submit']"
            ],
            
            "link": [
                # High priority - semantic links
                "a[href]",
                "[role='link']",
                # Medium priority - link-like elements
                ".link",
                ".nav-link",
                ".menu-link",
                # Low priority - clickable text elements
                "a:not([href])",
                "[class*='link']",
                "span[onclick]"
            ],
            
              "dashboard_content": [
                # High priority
                "[data-testid*='dashboard']",
                "#dashboard",
                ".dashboard",
                # Medium priority
                ".main-content",
                ".content-area",
                "[role='main']",
                # Low priority
                ".page-content",
                "main"
            ],
            
            # Dashboard Widget Elements
            "dashboard_widget": [
                # High priority - generic dashboard widgets
                "[data-testid*='widget']",
                "[data-testid*='dashboard-widget']",
                ".widget",
                ".dashboard-widget",
                ".card",
                # Medium priority - widget containers
                ".widget-container",
                ".dashboard-card",
                ".panel",
                # Low priority - generic containers
                "[class*='widget']",
                "[class*='card']",
                ".content-box"
            ],
            
            "time_widget": [
                # High priority - time/work related widgets
                "[data-testid*='time']",
                "[data-testid*='work']",
                "[data-testid*='attendance']",
                # Medium priority - text-based matching
                ":has-text('Time at Work')",
                ":has-text('Time')",
                ":has-text('Work')",
                ":has-text('Attendance')",
                # Low priority - class-based matching
                "[class*='time']",
                "[class*='work']",
                "[class*='attendance']"
            ],
            
            "actions_widget": [
                # High priority - actions related widgets
                "[data-testid*='action']",
                "[data-testid*='my-action']",
                # Medium priority - text-based matching
                ":has-text('My Actions')",
                ":has-text('Actions')",
                ":has-text('Tasks')",
                # Low priority - class-based matching
                "[class*='action']",
                "[class*='task']"
            ],
            
            "quick_launch_widget": [
                # High priority - quick launch related widgets
                "[data-testid*='quick']",
                "[data-testid*='launch']",
                "[data-testid*='quick-launch']",
                # Medium priority - text-based matching
                ":has-text('Quick Launch')",
                ":has-text('Quick Access')",
                ":has-text('Shortcuts')",
                # Low priority - class-based matching
                "[class*='quick']",
                "[class*='launch']",
                "[class*='shortcut']"
            ],
            
            "buzz_widget": [
                # High priority - buzz/social related widgets
                "[data-testid*='buzz']",
                "[data-testid*='social']",
                "[data-testid*='posts']",
                # Medium priority - text-based matching
                ":has-text('Buzz Latest Posts')",
                ":has-text('Buzz')",
                ":has-text('Latest Posts')",
                ":has-text('Social')",
                # Low priority - class-based matching
                "[class*='buzz']",
                "[class*='social']",
                "[class*='post']"
            ],
            
            # Generic Text Elements - Application Agnostic
            "heading_generic": [
                # High priority - semantic headings
                "h1", "h2", "h3", "h4", "h5", "h6",
                "[role='heading']",
                ".heading", ".title", ".header-text",
                # Medium priority
                ".page-title", ".section-title", ".card-title",
                # Low priority
                "[class*='heading']", "[class*='title']"
            ],
            
            "text_generic": [
                # High priority - text content
                "p", "span", "div[class*='text']",
                ".text", ".content", ".description",
                # Medium priority
                "[role='text']", ".message", ".info",
                # Low priority
                "div:not([class]):not([id])", "span:not([class]):not([id])"
            ],
            
            "label_generic": [
                # High priority - labels and captions
                "label", "[role='label']",
                ".label", ".caption", ".field-label",
                # Medium priority
                ".form-label", ".input-label",
                # Low priority
                "[class*='label']", "[for]"
            ],
            
            # Generic Navigation Patterns - Application Agnostic
            "navigation_item": [
                # High priority - semantic navigation
                "[role='menuitem']",
                "nav a",
                ".nav-item",
                ".menu-item",
                ".navigation-item",
                # Medium priority - common patterns
                ".nav-link",
                ".menu-link",
                ".sidebar-nav a",
                ".main-nav a",
                ".navbar-nav a",
                # Low priority - generic patterns
                ".nav li a",
                ".menu li a",
                "ul.nav a",
                "ul.menu a"
            ],
            
            "navigation_menu": [
                # High priority
                "[role='navigation']",
                "nav",
                ".navigation",
                ".main-menu",
                ".primary-nav",
                # Medium priority
                ".navbar",
                ".nav-container",
                ".menu-container",
                # Low priority
                ".nav",
                ".menu"
            ],
            
            "primary_navigation": [
                # High priority
                "[role='navigation'][aria-label*='main' i]",
                ".main-navigation",
                ".primary-navigation",
                ".main-nav",
                # Medium priority
                "nav.primary",
                ".navbar-main",
                ".header-nav",
                # Low priority
                "nav:first-of-type",
                ".nav:first-of-type"
            ],
            
            "secondary_navigation": [
                # High priority
                "[role='navigation'][aria-label*='secondary' i]",
                ".secondary-navigation",
                ".sub-navigation",
                ".sidebar-nav",
                # Medium priority
                ".side-nav",
                ".left-nav",
                ".right-nav",
                # Low priority
                "nav:not(.primary):not(.main)",
                ".nav:not(.primary):not(.main)"
            ],
            
            "breadcrumb_item": [
                # High priority
                "[role='breadcrumb'] a",
                ".breadcrumb a",
                ".breadcrumbs a",
                # Medium priority
                ".breadcrumb-item",
                ".crumb",
                # Low priority
                ".path a",
                ".trail a"
            ],
            
            "tab_item": [
                # High priority
                "[role='tab']",
                ".tab",
                ".tab-item",
                ".nav-tab",
                # Medium priority
                ".tabs a",
                ".tab-link",
                ".tab-button",
                # Low priority
                ".tabbed-nav a",
                "ul.tabs a"
            ],
            
            "dropdown_item": [
                # High priority
                "[role='menuitem']",
                ".dropdown-item",
                ".menu-item",
                # Medium priority
                ".dropdown a",
                ".menu a",
                ".submenu a",
                # Low priority
                ".dropdown li a",
                ".menu li a"
            ],
            
            "button_generic": [
                # High priority
                "button",
                "[role='button']",
                "input[type='button']",
                # Medium priority
                ".btn",
                ".button",
                ".action-button",
                # Low priority
                "a.btn",
                ".clickable"
            ],
            
            "link_generic": [
                # High priority
                "a[href]",
                "[role='link']",
                # Medium priority
                ".link",
                ".action-link",
                # Low priority
                "a"
            ],
            
            "content_area": [
                # High priority
                "[role='main']",
                "main",
                ".main-content",
                # Medium priority
                ".content",
                ".page-content",
                ".content-area",
                # Low priority
                "#content",
                ".main"
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
            ],
            
            # E-commerce Specific Elements
            "product_card": [
                # High priority - specific product containers
                "[data-testid*='product']",
                "[data-product-id]",
                ".product-item",
                ".product-card",
                # Medium priority - generic product containers
                ".product",
                "[class*='product']",
                ".item",
                # Low priority - generic containers with product content
                "div:has(.add-to-cart)",
                "div:has([class*='price'])",
                ".card:has(button)"
            ],
            
            "add_to_cart": [
                # High priority - specific add to cart buttons
                "[data-action='add-to-cart']",
                "[data-testid*='add-cart']",
                "button:has-text('Add to cart')",
                "a:has-text('Add to cart')",
                # Medium priority - class-based selectors
                ".add-to-cart",
                ".btn-add-cart",
                ".add-cart-btn",
                # Low priority - generic buttons near products
                "button[class*='add']",
                ".product button",
                ".item button"
            ],
            
            "cart_icon": [
                # High priority - specific cart elements
                "[data-testid*='cart']",
                "a[href*='cart']",
                ".cart-link",
                ".shopping-cart",
                # Medium priority - cart navigation
                "nav a:has-text('Cart')",
                ".header a:has-text('Cart')",
                # Low priority - generic cart indicators
                "[class*='cart']",
                ".fa-shopping-cart",
                ".cart-icon"
            ],
            
            "search_product": [
                # High priority - specific product search
                "[data-testid*='search']",
                "input[placeholder*='Search Product' i]",
                "input[placeholder*='Search' i]",
                "#search-product",
                # Medium priority - search inputs
                ".search-input",
                ".product-search",
                "input[name*='search']",
                # Low priority - generic search
                "input[type='search']",
                ".search input",
                "form input[type='text']"
            ],
            
            "category_filter": [
                # High priority - specific category elements
                "[data-testid*='category']",
                ".category-link",
                "a[href*='category']",
                ".filter-category",
                # Medium priority - navigation categories
                ".category",
                ".cat-link",
                "nav a[class*='category']",
                # Low priority - generic category elements
                "[class*='category']",
                ".sidebar a",
                ".filter a"
            ],
            
            "brand_filter": [
                # High priority - specific brand elements
                "[data-testid*='brand']",
                ".brand-link",
                "a[href*='brand']",
                ".filter-brand",
                # Medium priority - brand navigation
                ".brand",
                ".brand-item",
                # Low priority - generic brand elements
                "[class*='brand']",
                ".sidebar .brand",
                ".filter .brand"
            ],
            
            "quantity_input": [
                # High priority - specific quantity controls
                "[data-testid*='quantity']",
                "input[name*='quantity']",
                ".quantity-input",
                "input[type='number']",
                # Medium priority - quantity controls
                ".qty-input",
                ".quantity",
                "[class*='quantity'] input",
                # Low priority - generic number inputs
                "input[min='1']",
                ".cart input[type='number']",
                "table input[type='number']"
            ],
            
            "checkout_button": [
                # High priority - specific checkout buttons
                "[data-testid*='checkout']",
                "button:has-text('Checkout')",
                "a:has-text('Checkout')",
                "button:has-text('Proceed To Checkout')",
                # Medium priority - checkout links/buttons
                ".checkout-btn",
                ".btn-checkout",
                "a[href*='checkout']",
                # Low priority - generic checkout elements
                "[class*='checkout']",
                ".cart button",
                ".proceed-btn"
            ],
            
            "price_display": [
                # High priority - specific price elements
                "[data-testid*='price']",
                ".price",
                ".product-price",
                "[class*='price']",
                # Medium priority - currency indicators
                ":has-text('Rs.')",
                ":has-text('$')",
                ":has-text('€')",
                # Low priority - generic price patterns
                ".cost",
                ".amount",
                "[class*='cost']"
            ],
            
            "product_name": [
                # High priority - specific product name elements
                "[data-testid*='product-name']",
                ".product-name",
                ".product-title",
                ".item-name",
                # Medium priority - heading elements in products
                ".product h1",
                ".product h2",
                ".product h3",
                # Low priority - generic name elements
                "[class*='name']",
                "[class*='title']",
                ".product a"
            ],
            
            "product_image": [
                # High priority - specific product images
                "[data-testid*='product-image']",
                ".product-image",
                ".product img",
                ".item-image",
                # Medium priority - product container images
                "[class*='product'] img",
                ".card img",
                # Low priority - generic images
                "img[alt*='product' i]",
                "img[src*='product']",
                ".image img"
            ],
            
            "search_field": [
                # High priority - specific search inputs
                "[data-testid*='search']",
                "input[name*='search']",
                "input[placeholder*='search' i]",
                "#search",
                ".search-input",
                # Medium priority - search form elements
                "form[class*='search'] input",
                ".search input",
                "[class*='search'] input[type='text']",
                # Low priority - generic search patterns
                "input[type='search']",
                "input[aria-label*='search' i]",
                "[role='searchbox']"
            ]
        }
    
    def find_element(self, semantic_type: str, timeout: int = 5000) -> Optional[Locator]:
        """
        Find element using priority-based fallback strategy with enhanced debugging.
        
        Args:
            semantic_type: Semantic type of element (e.g., 'username_field')
            timeout: Timeout in milliseconds for each selector attempt
            
        Returns:
            Playwright Locator if found, None otherwise
        """
        selectors = self.locator_map.get(semantic_type, [])
        
        if not selectors:
            logger.warning(f"❌ No selectors defined for semantic type: {semantic_type}")
            logger.info(f"📋 Available semantic types: {list(self.locator_map.keys())}")
            return None
        
        logger.info(f"🔍 Searching for element: {semantic_type} (trying {len(selectors)} selectors)")
        logger.debug(f"📍 Current URL: {self.page.url}")
        logger.debug(f"📄 Page title: {self.page.title()}")
        
        for i, selector in enumerate(selectors):
            try:
                logger.debug(f"🎯 Trying selector {i+1}/{len(selectors)} for {semantic_type}: {selector}")
                locator = self.page.locator(selector)
                
                # Check if element exists
                element_count = locator.count()
                logger.debug(f"📊 Found {element_count} elements matching selector: {selector}")
                
                if element_count > 0:
                    # Use first() to get the first matching element
                    first_locator = locator.first
                    
                    # Check visibility with detailed logging
                    try:
                        is_visible = first_locator.is_visible(timeout=timeout)
                        if is_visible:
                            logger.info(f"✅ Found visible {semantic_type} using selector: {selector}")
                            return first_locator
                        else:
                            logger.debug(f"👁️ Element found but not visible: {selector}")
                    except PlaywrightTimeoutError:
                        logger.debug(f"⏰ Visibility check timeout for: {selector}")
                else:
                    logger.debug(f"🚫 No elements found for selector: {selector}")
                
            except PlaywrightTimeoutError:
                logger.debug(f"⏰ Timeout for selector: {selector}")
                continue
            except Exception as e:
                logger.debug(f"💥 Error with selector {selector}: {str(e)}")
                continue
        
        # Enhanced error reporting when element not found
        logger.warning(f"❌ Could not find element for semantic type: {semantic_type}")
        logger.info(f"🔧 Debugging info:")
        logger.info(f"   - Tried {len(selectors)} selectors")
        logger.info(f"   - Current URL: {self.page.url}")
        logger.info(f"   - Page loaded: {self.page.url != 'about:blank'}")
        
        # Take debug screenshot if element not found
        try:
            from datetime import datetime
            debug_filename = f"debug_element_not_found_{semantic_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.page.screenshot(path=debug_filename)
            logger.info(f"📸 Debug screenshot saved: {debug_filename}")
        except Exception as e:
            logger.debug(f"Failed to save debug screenshot: {e}")
        
        return None
    
    def find_element_by_text(self, semantic_type: str, text: str, timeout: int = 5000):
        """
        Find element by semantic type and text content using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            text: Text content to match
            timeout: Timeout in milliseconds
            
        Returns:
            Playwright locator if found, None otherwise
        """
        selectors = self.locator_map.get(semantic_type, [])
        
        if not selectors:
            logger.warning(f"No selectors defined for semantic type: {semantic_type}")
            return None
        
        for i, selector in enumerate(selectors):
            try:
                logger.debug(f"Trying text-based selector {i+1}/{len(selectors)} for {semantic_type} with text '{text}': {selector}")
                
                # Try case-insensitive text match first (most reliable)
                locator = self.page.locator(selector).filter(has_text=re.compile(re.escape(text), re.IGNORECASE))
                if locator.count() > 0 and locator.first.is_visible(timeout=timeout):
                    logger.info(f"Found {semantic_type} with case-insensitive text '{text}' using selector: {selector}")
                    return locator.first
                
                # Try exact text match (case-sensitive fallback)
                locator = self.page.locator(f"{selector}:has-text('{text}')")
                if locator.count() > 0 and locator.first.is_visible(timeout=timeout):
                    logger.info(f"Found {semantic_type} with exact text '{text}' using selector: {selector}")
                    return locator.first
                
                # Try partial text match
                locator = self.page.locator(selector).filter(has_text=text)
                if locator.count() > 0 and locator.first.is_visible(timeout=timeout):
                    logger.info(f"Found {semantic_type} with partial text '{text}' using selector: {selector}")
                    return locator.first
                    
            except PlaywrightTimeoutError:
                logger.debug(f"Timeout for text-based selector: {selector}")
                continue
            except Exception as e:
                logger.debug(f"Error finding {semantic_type} with text '{text}' using {selector}: {str(e)}")
                continue
        
        logger.warning(f"Element {semantic_type} with text '{text}' not found using any selector")
        return None
    
    def click_by_text(self, semantic_type: str, text: str, timeout: int = 5000) -> bool:
        """
        Click element by semantic type and text content using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            text: Text content to match
            timeout: Timeout in milliseconds
            
        Returns:
            True if click succeeded, False otherwise
        """
        element = self.find_element_by_text(semantic_type, text, timeout)
        if element:
            try:
                element.click(timeout=timeout)
                logger.info(f"Successfully clicked {semantic_type} with text '{text}'")
                return True
            except Exception as e:
                logger.error(f"Failed to click {semantic_type} with text '{text}': {str(e)}")
                return False
        return False
    
    def is_visible_by_text(self, semantic_type: str, text: str, timeout: int = 5000) -> bool:
        """
        Check if element with specific text is visible using priority-based fallback.
        
        Args:
            semantic_type: Semantic type of element
            text: Text content to match
            timeout: Timeout in milliseconds
            
        Returns:
            True if element is visible, False otherwise
        """
        element = self.find_element_by_text(semantic_type, text, timeout)
        return element is not None
    
    def get_text_by_text(self, semantic_type: str, text: str, timeout: int = 5000) -> Optional[str]:
        """
        Get text content of element found by semantic type and partial text match.
        
        Args:
            semantic_type: Semantic type of element
            text: Text content to match
            timeout: Timeout in milliseconds
            
        Returns:
            Text content if found, None otherwise
        """
        element = self.find_element_by_text(semantic_type, text, timeout)
        if element:
            try:
                text_content = element.text_content(timeout=timeout)
                logger.info(f"Successfully got text from {semantic_type} with text '{text}'")
                return text_content
            except Exception as e:
                logger.error(f"Failed to get text from {semantic_type} with text '{text}': {str(e)}")
                return None
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
        Click element using priority-based fallback with enhanced debugging.
        
        Args:
            semantic_type: Semantic type of element
            timeout: Timeout in milliseconds
            
        Returns:
            True if click succeeded, False otherwise
        """
        logger.info(f"🖱️ Attempting to click: {semantic_type}")
        element = self.find_element(semantic_type, timeout)
        if element:
            try:
                # Additional checks before clicking
                logger.debug(f"🔍 Pre-click checks for {semantic_type}")
                logger.debug(f"   - Element visible: {element.is_visible()}")
                logger.debug(f"   - Element enabled: {element.is_enabled()}")
                
                element.click(timeout=timeout)
                logger.info(f"✅ Successfully clicked {semantic_type}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to click {semantic_type}: {str(e)}")
                
                # Take debug screenshot on click failure
                try:
                    from datetime import datetime
                    debug_filename = f"debug_click_failure_{semantic_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.page.screenshot(path=debug_filename)
                    logger.info(f"📸 Click failure screenshot saved: {debug_filename}")
                except Exception as screenshot_e:
                    logger.debug(f"Failed to save click failure screenshot: {screenshot_e}")
                
                return False
        
        logger.error(f"❌ Could not find element to click: {semantic_type}")
        return False
    
    def fill(self, semantic_type: str, value: str, timeout: int = 5000) -> bool:
        """
        Fill element using priority-based fallback with enhanced debugging.
        
        Args:
            semantic_type: Semantic type of element
            value: Value to fill
            timeout: Timeout in milliseconds
            
        Returns:
            True if fill succeeded, False otherwise
        """
        logger.info(f"✏️ Attempting to fill: {semantic_type} with value: {'*' * len(value) if 'password' in semantic_type.lower() else value}")
        element = self.find_element(semantic_type, timeout)
        if element:
            try:
                # Additional checks before filling
                logger.debug(f"🔍 Pre-fill checks for {semantic_type}")
                logger.debug(f"   - Element visible: {element.is_visible()}")
                logger.debug(f"   - Element enabled: {element.is_enabled()}")
                
                # Clear field first, then fill
                element.clear(timeout=timeout)
                element.fill(value, timeout=timeout)
                
                # Verify the value was filled correctly
                filled_value = element.input_value()
                if filled_value == value:
                    logger.info(f"✅ Successfully filled {semantic_type}")
                else:
                    logger.warning(f"⚠️ Fill verification failed for {semantic_type}: expected '{value}', got '{filled_value}'")
                
                return True
            except Exception as e:
                logger.error(f"❌ Failed to fill {semantic_type}: {str(e)}")
                
                # Take debug screenshot on fill failure
                try:
                    from datetime import datetime
                    debug_filename = f"debug_fill_failure_{semantic_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.page.screenshot(path=debug_filename)
                    logger.info(f"📸 Fill failure screenshot saved: {debug_filename}")
                except Exception as screenshot_e:
                    logger.debug(f"Failed to save fill failure screenshot: {screenshot_e}")
                
                return False
        
        logger.error(f"❌ Could not find element to fill: {semantic_type}")
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


    
    def click_by_text(self, semantic_type: str, text: str, timeout: int = 5000) -> bool:
        """
        Click element by text content using application-agnostic approach.
        
        Args:
            semantic_type: Semantic type of element
            text: Text content to search for
            timeout: Timeout in milliseconds
            
        Returns:
            True if click succeeded, False otherwise
        """
        logger.info(f"🖱️ Attempting to click by text: '{text}' in {semantic_type}")
        
        # Try to find element by text first
        element = self.find_element_by_text(semantic_type, text, timeout)
        if element:
            try:
                element.click(timeout=timeout)
                logger.info(f"✅ Successfully clicked '{text}' in {semantic_type}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to click '{text}' in {semantic_type}: {str(e)}")
                return False
        
        # Fallback: try generic text-based selectors that work with any application
        generic_text_selectors = [
            f"text='{text}'",
            f"text={text}",
            f"[aria-label*='{text}' i]",
            f"[title*='{text}' i]",
            f"*:has-text('{text}')",
            f"button:has-text('{text}')",
            f"a:has-text('{text}')",
            f"span:has-text('{text}')",
            f"div:has-text('{text}')"
        ]
        
        for selector in generic_text_selectors:
            try:
                logger.debug(f"🎯 Trying generic text selector: {selector}")
                locator = self.page.locator(selector)
                
                if locator.count() > 0:
                    first_locator = locator.first
                    if first_locator.is_visible(timeout=1000):
                        first_locator.click(timeout=timeout)
                        logger.info(f"✅ Successfully clicked '{text}' using generic selector: {selector}")
                        return True
                        
            except Exception as e:
                logger.debug(f"Generic text selector failed {selector}: {e}")
                continue
        
        logger.warning(f"❌ Could not click '{text}' in {semantic_type} using any method")
        return False
    
    def is_visible_by_text(self, semantic_type: str, text: str, timeout: int = 5000) -> bool:
        """
        Check if element with specific text is visible using application-agnostic approach.
        
        Args:
            semantic_type: Semantic type of element
            text: Text content to search for
            timeout: Timeout in milliseconds
            
        Returns:
            True if element is visible, False otherwise
        """
        logger.debug(f"👁️ Checking visibility by text: '{text}' in {semantic_type}")
        
        # Try semantic type first
        element = self.find_element_by_text(semantic_type, text, timeout)
        if element:
            return True
        
        # Fallback: try generic text-based visibility check
        generic_text_selectors = [
            f"text='{text}'",
            f"text={text}",
            f"*:has-text('{text}')"
        ]
        
        for selector in generic_text_selectors:
            try:
                locator = self.page.locator(selector)
                if locator.count() > 0 and locator.first.is_visible(timeout=1000):
                    logger.debug(f"✅ Found visible text '{text}' using: {selector}")
                    return True
            except Exception as e:
                logger.debug(f"Text visibility check failed {selector}: {e}")
                continue
        
        logger.debug(f"❌ Text '{text}' not visible in {semantic_type}")
        return False

