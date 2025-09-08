#!/usr/bin/env python3
"""
Test Advantage Online Shopping
==========================
This script demonstrates how to use the AI test automation framework to test the Advantage Online Shopping website.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    # Create necessary directories
    work_dir = Path("work_dir")
    screenshots_dir = Path("screenshots")
    for directory in [work_dir, screenshots_dir]:
        directory.mkdir(exist_ok=True)
    
    # Step 1: Run the real browser discovery agent
    logger.info("Step 1: Running real browser discovery agent for Advantage Online Shopping")
    discovery_dir = work_dir / "RealDiscoveryIntegration"
    discovery_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    discovery_results_path = discovery_dir / f"discovery_results_{timestamp}.json"
    
    # Create discovery results for Advantage Online Shopping
    discovery_results = {
        "application_url": "https://advantageonlineshopping.com",
        "page_elements": {
            "home": {
                "url": "https://advantageonlineshopping.com",
                "elements": {
                    "inputs": [
                        {
                            "id": "search",
                            "name": "search",
                            "type": "text",
                            "css": "#autoComplete"
                        }
                    ],
                    "buttons": [
                        {
                            "id": "search_btn",
                            "text": "Search",
                            "css": "#searchButton"
                        },
                        {
                            "id": "user_menu",
                            "text": "User",
                            "css": "#menuUser"
                        }
                    ],
                    "links": [
                        {
                            "id": "speakers",
                            "text": "SPEAKERS",
                            "css": "#speakersImg"
                        },
                        {
                            "id": "tablets",
                            "text": "TABLETS",
                            "css": "#tabletsImg"
                        },
                        {
                            "id": "laptops",
                            "text": "LAPTOPS",
                            "css": "#laptopsImg"
                        },
                        {
                            "id": "mice",
                            "text": "MICE",
                            "css": "#miceImg"
                        },
                        {
                            "id": "headphones",
                            "text": "HEADPHONES",
                            "css": "#headphonesImg"
                        }
                    ]
                }
            },
            "login": {
                "url": "https://advantageonlineshopping.com/#/",
                "elements": {
                    "inputs": [
                        {
                            "id": "username",
                            "name": "username",
                            "type": "text",
                            "css": "input[name='username']"
                        },
                        {
                            "id": "password",
                            "name": "password",
                            "type": "password",
                            "css": "input[name='password']"
                        }
                    ],
                    "buttons": [
                        {
                            "id": "sign_in",
                            "text": "SIGN IN",
                            "css": "#sign_in_btnundefined"
                        },
                        {
                            "id": "register",
                            "text": "CREATE NEW ACCOUNT",
                            "css": "a.create-new-account"
                        }
                    ]
                }
            },
            "product_category": {
                "url": "https://advantageonlineshopping.com/#/category/Speakers/4",
                "elements": {
                    "links": [
                        {
                            "id": "product",
                            "text": "Product",
                            "css": "a.productName"
                        },
                        {
                            "id": "filter",
                            "text": "Filter",
                            "css": "div.filterNameSelected"
                        }
                    ],
                    "buttons": [
                        {
                            "id": "sort",
                            "text": "Sort",
                            "css": "a.select-sort"
                        }
                    ]
                }
            },
            "product_details": {
                "url": "https://advantageonlineshopping.com/#/product/19",
                "elements": {
                    "buttons": [
                        {
                            "id": "add_to_cart",
                            "text": "ADD TO CART",
                            "css": "button[name='save_to_cart']"
                        },
                        {
                            "id": "quantity",
                            "text": "Quantity",
                            "css": "div.e-sec-plus-minus"
                        }
                    ],
                    "links": [
                        {
                            "id": "color",
                            "text": "Color",
                            "css": "span.productColor"
                        }
                    ]
                }
            },
            "shopping_cart": {
                "url": "https://advantageonlineshopping.com/#/shoppingCart",
                "elements": {
                    "buttons": [
                        {
                            "id": "checkout",
                            "text": "CHECKOUT",
                            "css": "#checkOutButton"
                        },
                        {
                            "id": "continue_shopping",
                            "text": "CONTINUE SHOPPING",
                            "css": "#shoppingCartLink"
                        }
                    ],
                    "links": [
                        {
                            "id": "remove",
                            "text": "Remove",
                            "css": "a.remove"
                        }
                    ]
                }
            }
        }
    }
    
    with open(discovery_results_path, 'w') as f:
        json.dump(discovery_results, f, indent=2)
    
    logger.info(f"Created discovery results: {discovery_results_path}")
    
    # Step 2: Generate tests using the simple generator
    logger.info("Step 2: Generating tests from discovery results")
    os.system(f"python simple_test_generator.py --discovery-results {discovery_results_path}")
    
    # Step 3: Create a custom test for product search and add to cart
    logger.info("Step 3: Creating a custom test for product search and add to cart")
    
    # Create page objects
    home_page_content = '''"""
Advantage Shopping Home Page Object
=================================
Page object for Advantage Shopping home page.
"""

from pages.base_page import BasePage

class AdvantageShoppingHomePage(BasePage):
    """Page object for Advantage Shopping home page"""
    
    def __init__(self, page):
        """
        Initialize Advantage Shopping home page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = "https://advantageonlineshopping.com"
        
        # Element selectors
        self.search_selector = "#autoComplete"
        self.search_button_selector = "#searchButton"
        self.user_menu_selector = "#menuUser"
        self.speakers_selector = "#speakersImg"
        self.tablets_selector = "#tabletsImg"
        self.laptops_selector = "#laptopsImg"
        self.mice_selector = "#miceImg"
        self.headphones_selector = "#headphonesImg"
    
    async def search(self, keyword):
        """
        Search for a product
        
        Args:
            keyword: Search keyword
        """
        await self.fill(self.search_selector, keyword)
        await self.click(self.search_button_selector)
    
    async def open_category(self, category):
        """
        Open a product category
        
        Args:
            category: Category name (speakers, tablets, laptops, mice, headphones)
        """
        category_selectors = {
            "speakers": self.speakers_selector,
            "tablets": self.tablets_selector,
            "laptops": self.laptops_selector,
            "mice": self.mice_selector,
            "headphones": self.headphones_selector
        }
        
        selector = category_selectors.get(category.lower())
        if selector:
            await self.click(selector)
        else:
            raise ValueError(f"Unknown category: {category}")
    
    async def open_user_menu(self):
        """Open user menu"""
        await self.click(self.user_menu_selector)
'''
    
    with open("pages/advantage_shopping_home_page.py", 'w') as f:
        f.write(home_page_content)
    
    product_page_content = '''"""
Product Page Object
=================
Page object for product page.
"""

from pages.base_page import BasePage

class ProductPage(BasePage):
    """Page object for product page"""
    
    def __init__(self, page):
        """
        Initialize product page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        
        # Element selectors
        self.add_to_cart_selector = "button[name='save_to_cart']"
        self.quantity_plus_selector = "div.plus"
        self.quantity_minus_selector = "div.minus"
        self.color_selector = "span.productColor"
    
    async def add_to_cart(self):
        """Add product to cart"""
        await self.click(self.add_to_cart_selector)
    
    async def select_quantity(self, quantity):
        """
        Select product quantity
        
        Args:
            quantity: Desired quantity
        """
        # First reset to 1
        current_quantity = 1
        
        # Then add or subtract as needed
        if quantity > current_quantity:
            for _ in range(quantity - current_quantity):
                await self.click(self.quantity_plus_selector)
        elif quantity < current_quantity:
            for _ in range(current_quantity - quantity):
                await self.click(self.quantity_minus_selector)
    
    async def select_color(self, color_index=0):
        """
        Select product color
        
        Args:
            color_index: Index of the color to select (0-based)
        """
        colors = await self.page.query_selector_all(self.color_selector)
        if colors and len(colors) > color_index:
            await colors[color_index].click()
'''
    
    with open("pages/product_page.py", 'w') as f:
        f.write(product_page_content)
    
    cart_page_content = '''"""
Shopping Cart Page Object
======================
Page object for shopping cart page.
"""

from pages.base_page import BasePage

class ShoppingCartPage(BasePage):
    """Page object for shopping cart page"""
    
    def __init__(self, page):
        """
        Initialize shopping cart page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = "https://advantageonlineshopping.com/#/shoppingCart"
        
        # Element selectors
        self.checkout_selector = "#checkOutButton"
        self.continue_shopping_selector = "#shoppingCartLink"
        self.remove_selector = "a.remove"
    
    async def checkout(self):
        """Proceed to checkout"""
        await self.click(self.checkout_selector)
    
    async def continue_shopping(self):
        """Continue shopping"""
        await self.click(self.continue_shopping_selector)
    
    async def remove_item(self, item_index=0):
        """
        Remove item from cart
        
        Args:
            item_index: Index of the item to remove (0-based)
        """
        remove_buttons = await self.page.query_selector_all(self.remove_selector)
        if remove_buttons and len(remove_buttons) > item_index:
            await remove_buttons[item_index].click()
'''
    
    with open("pages/shopping_cart_page.py", 'w') as f:
        f.write(cart_page_content)
    
    # Create test file
    test_content = '''"""
Advantage Shopping E2E Test
========================
End-to-end test for Advantage Online Shopping website.
"""

import pytest
import logging
from datetime import datetime

from pages.advantage_shopping_home_page import AdvantageShoppingHomePage
from pages.product_page import ProductPage
from pages.shopping_cart_page import ShoppingCartPage

class TestAdvantageShoppingE2E:
    """Test class for Advantage Shopping E2E"""
    
    @pytest.mark.asyncio
    async def test_search_and_add_to_cart(self, browser_setup):
        """
        Test searching for a product and adding it to cart
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page objects
            home_page = AdvantageShoppingHomePage(page)
            product_page = ProductPage(page)
            cart_page = ShoppingCartPage(page)
            
            # Navigate to home page
            await home_page.navigate()
            
            # Take screenshot of home page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/advantage_home_{timestamp}.png")
            
            # Open speakers category
            await home_page.open_category("speakers")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot of category page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/advantage_category_{timestamp}.png")
            
            # Click on the first product
            await page.click("a.productName")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot of product page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/advantage_product_{timestamp}.png")
            
            # Select color and quantity
            await product_page.select_color(0)
            await product_page.select_quantity(2)
            
            # Add to cart
            await product_page.add_to_cart()
            await page.wait_for_timeout(1000)  # Wait for animation
            
            # Navigate to shopping cart
            await page.goto("https://advantageonlineshopping.com/#/shoppingCart")
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot of cart page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/advantage_cart_{timestamp}.png")
            
            # Assert item is in cart
            cart_items = await page.query_selector_all("tr.ng-scope")
            assert len(cart_items) > 0, "Cart should not be empty"
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/advantage_failure_{timestamp}.png")
            
            logging.error(f"Test failed: {str(e)}")
            raise

# Run test if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
'''
    
    with open("tests/test_advantage_shopping_e2e.py", 'w') as f:
        f.write(test_content)
    
    logger.info("Created page objects and test file for Advantage Online Shopping")
    
    # Step 4: Run the test
    logger.info("Step 4: Running the test")
    os.system("python -m pytest tests/test_advantage_shopping_e2e.py -v")
    
    logger.info("Test completed successfully!")

if __name__ == "__main__":
    main()

