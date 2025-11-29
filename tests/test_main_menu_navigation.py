import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture
def page():
    browser = sync_playwright().start()
    yield browser.page
    browser.close()

class TestMainMenuNavigation:
    def test_main_menu_navigation(self, page):
        target_url = "https://the-internet.herokuapp.com/login"
        
        # Navigate to the login page and log in with valid credentials
        logging.info("Navigating to Login Page")
        page.goto(target_url)
        expect(page).to_have_url(f"{target_url}/login")
        
        logging.info("Performing User Authentication")
        # Assuming there are direct actions or selectors for username and password input fields, buttons etc.
        page.locator('button[aria-label="Log in"]').click()  # Example locator based on common patterns
        
        expect(page).to_have_url("/dashboard")
        
        logging.info("Verifying Dashboard Page Load and Title")
        dashboard = page.locator('h1')  # Assuming the title is in an h1 tag for this example
        assert "Dashboard" == expect(dashboard).to_have_text()
        
        logging.info("Verifying Dashboard Page Content")
        content = page.locator('p').inner_text()  # Assuming paragraphs contain relevant dashboard information
        expected_content = 'Welcome to the Dashboard'  # Example of what we expect on a successful login and navigation
        assert "Dashboard" in content
        
        logging.info("Navigating through Main Menu Items")
        main_menu_items = ['Home', 'Profile', 'Settings']  # Listing the expected menu items to navigate through
        for item in main_menu_items:
            page.locator(f'a[title="{item}"]').click()
            
            logging.info(f"Verifying {item} Page Load and Title")
            expect(page).to_have_url(target_url + f"/main-menu/{item}")  # Assuming the URL structure includes main menu items as paths
            page_title = await page.locator('h1').inner_text()
            
            logging.info(f"Verifying {item} Page Title and Content")
            assert item in page_title
            content = await page.locator('p').inner_text()  # Assuming paragraphs contain relevant information for each menu section
            expected_content = f'Welcome to the {item}' if item != 'Settings' else 'Manage Account Settings'  # Example of what we expect on a successful navigation and loading
            
            assert content == expected_content