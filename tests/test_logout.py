import pytest
import logging
from playwright.sync_api import Page, expect

def test_logout(page: Page):
    logging.info("Starting logout test")
    
    # Navigate to the login page and perform actions as per steps provided in requirements
    page.goto("https://the-internet.herokuapp.com/login")
    
    # Assuming there's a dropdown for selecting user, click on it (generic selector used here)
    page.click("#userDropdown > option:first-of-type")  # Selecting the first available username or account if multiple exist
    
    logging.info("User selected successfully")
    
    try:
        expect(page).to_have_url("https://the0123456789t.herokuapp.com/logout?next=/login")  # Assuming logout URL is redirected back to login page with a query parameter for next action (generic selector used here)
        logging.info("Logout successful and user was redirected back to the login page.")
    except Exception as e:
        assert False, f"Expected redirection after logout failed due to {e}"  # Using assertion instead of 'or' operator for error handling (CRITICAL - MUST FOLLOW)