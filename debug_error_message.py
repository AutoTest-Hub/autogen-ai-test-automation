#!/usr/bin/env python3
"""
Debug script to understand error message behavior in OrangeHRM
"""

from playwright.sync_api import sync_playwright
from utils.locator_strategy import LocatorStrategy
import time

def debug_error_message():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        locator_strategy = LocatorStrategy(page)
        
        try:
            # Navigate to login page
            page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
            page.wait_for_load_state("networkidle")
            print("✓ Navigated to login page")
            
            # Fill invalid credentials
            success = locator_strategy.fill("username_field", "InvalidUser")
            print(f"✓ Username filled: {success}")
            
            success = locator_strategy.fill("password_field", "WrongPassword123")
            print(f"✓ Password filled: {success}")
            
            # Click login button
            success = locator_strategy.click("login_button")
            print(f"✓ Login button clicked: {success}")
            
            # Wait for response
            page.wait_for_timeout(2000)
            print("✓ Waited for response")
            
            # Check current URL
            print(f"Current URL: {page.url}")
            
            # Try to find error message
            error_visible = locator_strategy.is_visible("error_message")
            print(f"Error message visible: {error_visible}")
            
            # Get page content to see what's actually there
            content = page.content()
            
            # Look for common error patterns
            error_patterns = [
                "invalid", "error", "wrong", "incorrect", "failed", 
                "alert", "danger", "warning", "message"
            ]
            
            found_patterns = []
            for pattern in error_patterns:
                if pattern.lower() in content.lower():
                    found_patterns.append(pattern)
            
            print(f"Found error patterns in page: {found_patterns}")
            
            # Try to find any alert elements
            alerts = page.query_selector_all("[role='alert']")
            print(f"Found {len(alerts)} alert elements")
            
            # Try to find any error-related elements
            error_elements = page.query_selector_all("[class*='error'], [class*='alert'], [class*='invalid']")
            print(f"Found {len(error_elements)} error-related elements")
            
            for i, element in enumerate(error_elements[:3]):  # Show first 3
                try:
                    text = element.text_content()
                    if text and text.strip():
                        print(f"Error element {i+1}: {text.strip()}")
                except:
                    pass
            
            # Take a screenshot for debugging
            page.screenshot(path="debug_error_message.png")
            print("✓ Screenshot saved as debug_error_message.png")
            
        except Exception as e:
            print(f"Error during debug: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_error_message()

