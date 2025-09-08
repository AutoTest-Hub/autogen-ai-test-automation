"""
Login Page Object
==============
Page object for the login page.
"""

from pages.base_page import BasePage

class LoginPage(BasePage):
    """Page object for the login page"""
    
    def __init__(self, page, base_url: str = "https://example.com"):
        """
        Initialize the login page object
        
        Args:
            page: The browser page object (Playwright Page or Selenium WebDriver)
            base_url: Base URL of the application
        """
        super().__init__(page, base_url)
        self.url = "/login"  # URL path for the login page
        
        # Element selectors - these should be discovered by the RealBrowserDiscoveryAgent
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "button[type='submit']"
        self.error_message = ".error-message"
        self.forgot_password_link = "a:has-text('Forgot Password')"
        self.register_link = "a:has-text('Register')"
    
    async def is_loaded(self) -> bool:
        """
        Check if the login page is loaded
        
        Returns:
            bool: True if the page is loaded, False otherwise
        """
        try:
            # Wait for login form elements
            await self.page.wait_for_selector(self.username_input, timeout=5000)
            await self.page.wait_for_selector(self.password_input, timeout=5000)
            await self.page.wait_for_selector(self.login_button, timeout=5000)
            return True
        except Exception as e:
            self.logger.error(f"Error checking if login page is loaded: {str(e)}")
            return False
    
    async def login(self, username: str, password: str):
        """
        Login with the provided credentials
        
        Args:
            username: Username or email
            password: Password
        """
        self.logger.info(f"Logging in with username: {username}")
        
        # Fill username and password
        await self.fill(self.username_input, username)
        await self.fill(self.password_input, password)
        
        # Click login button
        await self.click(self.login_button)
        
        # Wait for navigation to complete
        await self.page.wait_for_load_state("networkidle")
    
    async def get_error_message(self) -> str:
        """
        Get the error message if login failed
        
        Returns:
            str: The error message text
        """
        try:
            await self.page.wait_for_selector(self.error_message, timeout=2000)
            return await self.get_text(self.error_message)
        except Exception:
            return ""
    
    async def click_forgot_password(self):
        """Click the forgot password link"""
        await self.click(self.forgot_password_link)
        await self.page.wait_for_load_state("networkidle")
    
    async def click_register(self):
        """Click the register link"""
        await self.click(self.register_link)
        await self.page.wait_for_load_state("networkidle")

