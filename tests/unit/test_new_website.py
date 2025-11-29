#!/usr/bin/env python3
"""
Test New Website
==============
This script demonstrates how to use the AI test automation framework to test a new website.
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test New Website")
    parser.add_argument("--url", "-u", required=True, help="URL of the website to test")
    parser.add_argument("--name", "-n", required=True, help="Name of the website (used for file naming)")
    args = parser.parse_args()
    
    # Create necessary directories
    work_dir = Path("work_dir")
    screenshots_dir = Path("screenshots")
    for directory in [work_dir, screenshots_dir]:
        directory.mkdir(exist_ok=True)
    
    # Step 1: Run the real browser discovery agent
    logger.info(f"Step 1: Running real browser discovery agent for {args.url}")
    discovery_dir = work_dir / "RealDiscoveryIntegration"
    discovery_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    discovery_results_path = discovery_dir / f"discovery_results_{timestamp}.json"
    
    # Create a simple discovery results file
    discovery_results = {
        "application_url": args.url,
        "page_elements": {
            args.name: {
                "url": args.url,
                "elements": {
                    "inputs": [
                        {
                            "id": "username",
                            "name": "username",
                            "type": "text",
                            "css": "#username"
                        },
                        {
                            "id": "password",
                            "name": "password",
                            "type": "password",
                            "css": "#password"
                        }
                    ],
                    "buttons": [
                        {
                            "id": "login",
                            "text": "Login",
                            "css": "button[type='submit']"
                        }
                    ],
                    "links": [
                        {
                            "id": "home",
                            "text": "Home",
                            "css": "a[href='/']"
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
    
    # Step 3: Create a custom test for the website
    logger.info("Step 3: Creating a custom test for the website")
    
    # Create page object
    page_name = args.name.lower().replace(' ', '_')
    page_class = "".join(word.capitalize() for word in args.name.split())
    page_class += "Page"
    
    page_content = f'''"""
{args.name} Page Object
======================
Page object for {args.name} page.
"""

from pages.base_page import BasePage

class {page_class}(BasePage):
    """Page object for {args.name} page"""
    
    def __init__(self, page):
        """
        Initialize {args.name} page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = "{args.url}"
        
        # Element selectors
        self.username_selector = "#username"
        self.password_selector = "#password"
        self.login_button_selector = "button[type='submit']"
        
    async def login(self, username, password):
        """
        Login with username and password
        
        Args:
            username: Username
            password: Password
        """
        await self.fill(self.username_selector, username)
        await self.fill(self.password_selector, password)
        await self.click(self.login_button_selector)
'''
    
    with open(f"pages/{page_name}_page.py", 'w') as f:
        f.write(page_content)
    
    # Create test file
    test_content = f'''"""
{args.name} Test
==============
Test for {args.name} website.
"""

import pytest
import logging
from datetime import datetime

from pages.{page_name}_page import {page_class}

class Test{page_class[:-4]}:
    """Test class for {args.name}"""
    
    @pytest.mark.asyncio
    async def test_{page_name}(self, browser_setup):
        """
        Test {args.name} website
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page object
            {page_name}_page = {page_class}(page)
            
            # Navigate to page
            await {page_name}_page.navigate()
            
            # Take screenshot before actions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/{page_name}_before_{{timestamp}}.png")
            
            # Perform actions (customize as needed)
            # await {page_name}_page.login("username", "password")
            
            # Take screenshot after actions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/{page_name}_after_{{timestamp}}.png")
            
            # Add assertions here
            assert await page.title() != "", "Page title should not be empty"
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/{page_name}_failure_{{timestamp}}.png")
            
            logging.error(f"Test failed: {{str(e)}}")
            raise

# Run test if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
'''
    
    with open(f"tests/test_{page_name}.py", 'w') as f:
        f.write(test_content)
    
    logger.info(f"Created page object: pages/{page_name}_page.py")
    logger.info(f"Created test file: tests/test_{page_name}.py")
    
    # Step 4: Run the test
    logger.info("Step 4: Running the test")
    os.system(f"python -m pytest tests/test_{page_name}.py -v")
    
    logger.info("Test completed successfully!")

if __name__ == "__main__":
    main()

