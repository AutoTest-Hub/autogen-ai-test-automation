import logging
from pages import LoginPage, DashboardPage
import pytest
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(url="https://the-internet.herokuapp.com/login")
        page = browser.new_page()
        yield page
        page.close()
        browser.close()

def test_logout(page):
    # Navigate to the login page and perform actions as per scenario steps
    
    logger.info("Starting logout functionality tests")
    
    try:
        with open('test-data/credentials.json', 'r') as file:
            credentials = json.load(file)  # Assuming JSON formatted credentials are stored in this test data directory
        
        page.goto("https://the-internet.herokuapp.com/login")
        logger.info("Navigated to login page.")
        
        login_page = LoginPage(page, "user123", "password@123")  # Assuming we have a generic constructor for our custom Page Objects that accepts credentials as parameters
        assert not login_page.is_logged_in(), "User should be logged out initially."
        
        logger.info("Attempting to log in.")
        page = login_page.login(credentials['username'], credentials['password'])  # Assuming a generic `login` method that returns the current Page instance for chainable actions
        assert page.is_logged_in(), "User should be logged in after successful login."
        
        logger.info("Selecting user dropdown.")
        page.click("#user-dropdown")
        expect(page).to_have_selector('#user-dropdown')  # Assuming the element has an id of 'user-dropdown' for simplicity, otherwise use more specific selectors as needed
        
        logger.info("Clicking on logout.")
        page.click("#logout")  # Using a generic selector assuming it is unique enough in this context or replace with appropriate locator strategy if necessary
        expect(page).to_be_visible("#login-error", False)  # Assuming the error message appears after clicking logout when not logged out, otherwise adjust assertion accordingly.
        
        logger.info("Verifying redirect to login page.")
        assert page.url == "https://the-internet.herokuapp.com/login" or expect(page).to_have_url("https://the-internet.herokuapp.com/login"), \
               f"Expected URL after logout should be the login page, but got {page.url}."
        
        logger.info("Logout functionality test passed.")
    
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")