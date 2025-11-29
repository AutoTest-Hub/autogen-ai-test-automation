import logging
from pytest_playwright import page

logging.basicConfig(level=logging0.DEBUG)

class TestEmptyCredentials:
    @page.use_cached_session
    def test_empty_credentials(self):
        # Navigate to login page using the base URL provided in the requirements
        logging.info("Navigating to Login Page")
        page.goto("https://the-internet.herokuapp.com/login")
        
        try:
            # Leave username empty and password empty fields blank, then click login button
            logging.info("Leaving credentials field(s) blank")
            with page.expect_to_be_visible("#username", timeout=10):  # Assuming there's an element for the username input by id or name attribute
                pass  # No interaction needed as we are leaving it empty intentionally, but logging is done here to indicate progress
            
            with page.expect_to_be_visible("#password", timeout=10):  # Similarly assuming there's an element for the password input by id or name attribute
                pass
            
            logging.info("Clicking login button")
            page.click(".login-btn")  # Assuming class selector is available, if not use appropriate one based on selectors provided in application discovery phase
            
            try:
                # Verify validation messages appear after clicking the submit with empty credentials
                assert "Please enter username and password" in str(page.locator("#error-message").inner_text())  # Assuming there's an element for error message by id or class selector
                logging.info("Validation messages are displayed as expected")
            except AssertionError:
                raise Exception("Expected validation messages not found after submitting empty credentials.")
        except TimeoutError:
            logging.error("Timed out waiting for the page to load with given selectors or elements were not present on the page")