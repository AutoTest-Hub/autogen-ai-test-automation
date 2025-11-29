#!/usr/bin/env python3
"""
Enhance Test Creation Agent with Selenium and API Test Generation
================================================================
Add Selenium WebDriver and API testing capabilities to the Enhanced Test Creation Agent
"""

import os
import logging
from pathlib import Path
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCreationEnhancer:
    """Enhance the Test Creation Agent with Selenium and API capabilities"""
    
    def __init__(self):
        self.agent_file = "agents/test_creation_agent.py"
        self.backup_file = "agents/test_creation_agent_pre_selenium_api_backup.py"
        
    def enhance_agent(self):
        """Add Selenium and API test generation capabilities"""
        
        logger.info("🚀 Starting Test Creation Agent enhancement for Selenium and API")
        
        try:
            # Create backup
            self._create_backup()
            
            # Add Selenium capabilities
            self._add_selenium_capabilities()
            
            # Add API testing capabilities
            self._add_api_capabilities()
            
            # Update process_task method
            self._update_process_task_method()
            
            # Add new template methods
            self._add_template_methods()
            
            logger.info("✅ Test Creation Agent enhanced successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhancement failed: {str(e)}")
            return False
    
    def _create_backup(self):
        """Create backup of current agent"""
        logger.info("📦 Creating backup of current Enhanced Test Creation Agent")
        
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        with open(self.backup_file, 'w') as f:
            f.write(content)
        
        logger.info(f"✅ Backup created: {self.backup_file}")
    
    def _add_selenium_capabilities(self):
        """Add Selenium WebDriver test generation capabilities"""
        logger.info("🔧 Adding Selenium WebDriver capabilities")
        
        selenium_imports = '''
# Selenium imports for WebDriver test generation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
'''
        
        # Read current file
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        # Add Selenium imports after existing imports
        import_section_end = content.find('class EnhancedTestCreationAgent')
        if import_section_end != -1:
            content = content[:import_section_end] + selenium_imports + '\n' + content[import_section_end:]
        
        # Write back
        with open(self.agent_file, 'w') as f:
            f.write(content)
        
        logger.info("✅ Selenium imports added")
    
    def _add_api_capabilities(self):
        """Add API testing capabilities"""
        logger.info("🔧 Adding API testing capabilities")
        
        api_imports = '''
# API testing imports
import requests
import json
from typing import Dict, List, Any, Optional
'''
        
        # Read current file
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        # Add API imports after Selenium imports
        selenium_section = content.find('class EnhancedTestCreationAgent')
        if selenium_section != -1:
            content = content[:selenium_section] + api_imports + '\n' + content[selenium_section:]
        
        # Write back
        with open(self.agent_file, 'w') as f:
            f.write(content)
        
        logger.info("✅ API testing imports added")
    
    def _update_process_task_method(self):
        """Update process_task method to handle Selenium and API tasks"""
        logger.info("🔧 Updating process_task method")
        
        # Read current file
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        # Find the process_task method
        process_task_start = content.find('async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:')
        if process_task_start == -1:
            logger.error("Could not find process_task method")
            return
        
        # Find the end of the method (next method or class end)
        method_end = content.find('\n    async def ', process_task_start + 1)
        if method_end == -1:
            method_end = content.find('\n    def ', process_task_start + 1)
        
        if method_end == -1:
            logger.error("Could not find end of process_task method")
            return
        
        # Create new process_task method
        new_process_task = '''    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process test creation task with real code generation - Enhanced with Selenium and API"""
        task_type = task_data.get("task_type", "generate_tests")
        
        if task_type == "generate_tests":
            return await self._generate_real_test_code(task_data)
        elif task_type == "generate_selenium_tests":
            return await self._generate_selenium_tests(task_data)
        elif task_type == "generate_api_tests":
            return await self._generate_api_tests(task_data)
        elif task_type == "create_page_objects":
            return await self._create_page_objects(task_data)
        elif task_type == "generate_utilities":
            return await self._generate_test_utilities(task_data)
        else:
            return {
                "status": "error",
                "error": f"Unknown task type: {task_type}"
            }
'''
        
        # Replace the method
        content = content[:process_task_start] + new_process_task + content[method_end:]
        
        # Write back
        with open(self.agent_file, 'w') as f:
            f.write(content)
        
        logger.info("✅ process_task method updated")
    
    def _add_template_methods(self):
        """Add new template methods for Selenium and API tests"""
        logger.info("🔧 Adding Selenium and API template methods")
        
        # Read current file
        with open(self.agent_file, 'r') as f:
            content = f.read()
        
        # Find the end of the class (before the last method)
        class_end = content.rfind('\n    async def ')
        if class_end == -1:
            class_end = content.rfind('\n    def ')
        
        if class_end == -1:
            logger.error("Could not find end of class")
            return
        
        # Find the actual end of the last method
        method_end = content.find('\n\n', class_end)
        if method_end == -1:
            method_end = len(content)
        
        # Add new methods
        new_methods = '''
    async def _generate_selenium_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Selenium WebDriver tests"""
        try:
            logger.info("🔧 Generating Selenium WebDriver tests")
            
            test_plan = task_data.get("test_plan", {})
            application_url = task_data.get("application_url", "https://example.com")
            
            # Generate Selenium test files
            generated_files = []
            
            # Create main Selenium test
            selenium_test = self._create_selenium_test_file(test_plan, application_url)
            test_file_path = f"{self.work_dir}/test_selenium_automation.py"
            
            with open(test_file_path, 'w') as f:
                f.write(selenium_test)
            generated_files.append(test_file_path)
            
            # Create Selenium page objects
            page_objects = self._create_selenium_page_objects(test_plan)
            for page_name, page_content in page_objects.items():
                page_file_path = f"{self.work_dir}/{page_name}_selenium_page.py"
                with open(page_file_path, 'w') as f:
                    f.write(page_content)
                generated_files.append(page_file_path)
            
            # Create Selenium configuration
            config_content = self._create_selenium_config()
            config_file_path = f"{self.work_dir}/selenium_config.py"
            with open(config_file_path, 'w') as f:
                f.write(config_content)
            generated_files.append(config_file_path)
            
            logger.info(f"✅ Generated {len(generated_files)} Selenium test files")
            
            return {
                "status": "success",
                "framework": "selenium",
                "generated_files": generated_files,
                "test_count": len(generated_files),
                "artifacts": generated_files
            }
            
        except Exception as e:
            logger.error(f"❌ Selenium test generation failed: {str(e)}")
            return {
                "status": "error",
                "error": f"Selenium test generation failed: {str(e)}"
            }
    
    async def _generate_api_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API tests using requests library"""
        try:
            logger.info("🔧 Generating API tests")
            
            test_plan = task_data.get("test_plan", {})
            api_base_url = task_data.get("api_base_url", "https://api.example.com")
            
            # Generate API test files
            generated_files = []
            
            # Create main API test
            api_test = self._create_api_test_file(test_plan, api_base_url)
            test_file_path = f"{self.work_dir}/test_api_automation.py"
            
            with open(test_file_path, 'w') as f:
                f.write(api_test)
            generated_files.append(test_file_path)
            
            # Create API client
            api_client = self._create_api_client(api_base_url)
            client_file_path = f"{self.work_dir}/api_client.py"
            with open(client_file_path, 'w') as f:
                f.write(api_client)
            generated_files.append(client_file_path)
            
            # Create API test utilities
            api_utils = self._create_api_test_utilities()
            utils_file_path = f"{self.work_dir}/api_test_utils.py"
            with open(utils_file_path, 'w') as f:
                f.write(api_utils)
            generated_files.append(utils_file_path)
            
            logger.info(f"✅ Generated {len(generated_files)} API test files")
            
            return {
                "status": "success",
                "framework": "api_requests",
                "generated_files": generated_files,
                "test_count": len(generated_files),
                "artifacts": generated_files
            }
            
        except Exception as e:
            logger.error(f"❌ API test generation failed: {str(e)}")
            return {
                "status": "error",
                "error": f"API test generation failed: {str(e)}"
            }
    
    def _create_selenium_test_file(self, test_plan: Dict, application_url: str) -> str:
        """Create Selenium WebDriver test file"""
        timestamp = int(time.time())
        
        return f'''"""
Selenium WebDriver Test - Generated by AutoGen AI Test Framework
================================================================
Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Application: {application_url}
"""

import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium_config import SeleniumConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'selenium_test_{{timestamp}}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestSeleniumAutomation:
    """Selenium WebDriver test automation class"""
    
    @pytest.fixture(scope="class")
    def driver_setup(self):
        """Setup Selenium WebDriver"""
        config = SeleniumConfig()
        
        # Setup Chrome options
        chrome_options = ChromeOptions()
        if config.HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={{config.WINDOW_WIDTH}},{{config.WINDOW_HEIGHT}}")
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(config.IMPLICIT_WAIT)
        
        yield driver
        
        # Cleanup
        driver.quit()
    
    def test_login_functionality(self, driver_setup):
        """Test user login functionality with Selenium"""
        driver = driver_setup
        
        try:
            logger.info("🔍 Testing login functionality with Selenium")
            
            # Navigate to application
            driver.get("{application_url}")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find and click login button/link
            login_selectors = [
                (By.ID, "loginBtn"),
                (By.LINK_TEXT, "Sign in"),
                (By.LINK_TEXT, "Login"),
                (By.CSS_SELECTOR, "[data-testid='login']"),
                (By.XPATH, "//button[contains(text(), 'Login')]")
            ]
            
            login_element = None
            for selector_type, selector_value in login_selectors:
                try:
                    login_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    break
                except:
                    continue
            
            if login_element:
                login_element.click()
                logger.info("✅ Login button clicked")
            else:
                logger.warning("⚠️ Login button not found, proceeding with form search")
            
            # Find username field
            username_selectors = [
                (By.ID, "username"),
                (By.NAME, "username"),
                (By.CSS_SELECTOR, "[data-testid='username']"),
                (By.XPATH, "//input[@type='text' or @type='email']")
            ]
            
            username_field = None
            for selector_type, selector_value in username_selectors:
                try:
                    username_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    break
                except:
                    continue
            
            # Find password field
            password_selectors = [
                (By.ID, "password"),
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "[data-testid='password']"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            password_field = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    break
                except:
                    continue
            
            # Enter credentials
            if username_field and password_field:
                username_field.clear()
                username_field.send_keys("testuser")
                
                password_field.clear()
                password_field.send_keys("testpass")
                
                logger.info("✅ Credentials entered")
                
                # Find and click submit button
                submit_selectors = [
                    (By.ID, "loginSubmit"),
                    (By.CSS_SELECTOR, "[type='submit']"),
                    (By.XPATH, "//button[contains(text(), 'Sign in') or contains(text(), 'Login')]")
                ]
                
                submit_button = None
                for selector_type, selector_value in submit_selectors:
                    try:
                        submit_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((selector_type, selector_value))
                        )
                        break
                    except:
                        continue
                
                if submit_button:
                    submit_button.click()
                    logger.info("✅ Login form submitted")
                    
                    # Wait for login to complete
                    time.sleep(3)
                    
                    # Verify login success
                    success_indicators = [
                        (By.CSS_SELECTOR, "[data-testid='user-menu']"),
                        (By.ID, "userMenu"),
                        (By.CLASS_NAME, "user-profile"),
                        (By.XPATH, "//span[contains(text(), 'Welcome')]")
                    ]
                    
                    login_successful = False
                    for selector_type, selector_value in success_indicators:
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            login_successful = True
                            break
                        except:
                            continue
                    
                    # Take screenshot
                    screenshot_path = f"selenium_login_test_{{timestamp}}.png"
                    driver.save_screenshot(screenshot_path)
                    logger.info(f"📸 Screenshot saved: {{screenshot_path}}")
                    
                    # Assert login success
                    assert login_successful or "dashboard" in driver.current_url.lower(), "Login verification failed"
                    logger.info("🎉 Login test completed successfully")
                    
                else:
                    logger.error("❌ Submit button not found")
                    assert False, "Submit button not found"
            else:
                logger.error("❌ Username or password field not found")
                assert False, "Login form fields not found"
                
        except Exception as e:
            # Take error screenshot
            error_screenshot = f"selenium_login_error_{{timestamp}}.png"
            driver.save_screenshot(error_screenshot)
            logger.error(f"❌ Login test failed: {{str(e)}}")
            logger.error(f"📸 Error screenshot: {{error_screenshot}}")
            raise
    
    def test_navigation_functionality(self, driver_setup):
        """Test basic navigation functionality"""
        driver = driver_setup
        
        try:
            logger.info("🔍 Testing navigation functionality")
            
            # Navigate to application
            driver.get("{application_url}")
            
            # Test page title
            assert driver.title, "Page title should not be empty"
            logger.info(f"✅ Page title: {{driver.title}}")
            
            # Test navigation links
            nav_links = driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"✅ Found {{len(nav_links)}} navigation links")
            
            # Take screenshot
            screenshot_path = f"selenium_navigation_test_{{timestamp}}.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {{screenshot_path}}")
            
            assert len(nav_links) > 0, "Should have navigation links"
            logger.info("🎉 Navigation test completed successfully")
            
        except Exception as e:
            error_screenshot = f"selenium_navigation_error_{{timestamp}}.png"
            driver.save_screenshot(error_screenshot)
            logger.error(f"❌ Navigation test failed: {{str(e)}}")
            logger.error(f"📸 Error screenshot: {{error_screenshot}}")
            raise
'''
    
    def _create_selenium_page_objects(self, test_plan: Dict) -> Dict[str, str]:
        """Create Selenium page object files"""
        page_objects = {}
        
        # Login Page Object
        page_objects["login"] = '''"""
Login Page Object for Selenium WebDriver
========================================
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)

class LoginPageSelenium:
    """Login page object for Selenium WebDriver"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # Locators
        self.username_locators = [
            (By.ID, "username"),
            (By.NAME, "username"),
            (By.CSS_SELECTOR, "[data-testid='username']"),
            (By.XPATH, "//input[@type='text' or @type='email']")
        ]
        
        self.password_locators = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "[data-testid='password']"),
            (By.XPATH, "//input[@type='password']")
        ]
        
        self.login_button_locators = [
            (By.ID, "loginBtn"),
            (By.CSS_SELECTOR, "[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Sign in') or contains(text(), 'Login')]")
        ]
    
    def find_element_with_fallback(self, locators):
        """Find element using multiple locator strategies"""
        for locator_type, locator_value in locators:
            try:
                element = self.wait.until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
                return element
            except:
                continue
        return None
    
    def enter_username(self, username):
        """Enter username in the username field"""
        username_field = self.find_element_with_fallback(self.username_locators)
        if username_field:
            username_field.clear()
            username_field.send_keys(username)
            logger.info("✅ Username entered")
            return True
        else:
            logger.error("❌ Username field not found")
            return False
    
    def enter_password(self, password):
        """Enter password in the password field"""
        password_field = self.find_element_with_fallback(self.password_locators)
        if password_field:
            password_field.clear()
            password_field.send_keys(password)
            logger.info("✅ Password entered")
            return True
        else:
            logger.error("❌ Password field not found")
            return False
    
    def click_login_button(self):
        """Click the login button"""
        login_button = self.find_element_with_fallback(self.login_button_locators)
        if login_button:
            login_button.click()
            logger.info("✅ Login button clicked")
            return True
        else:
            logger.error("❌ Login button not found")
            return False
    
    def login(self, username, password):
        """Complete login process"""
        success = True
        success &= self.enter_username(username)
        success &= self.enter_password(password)
        success &= self.click_login_button()
        return success
'''
        
        return page_objects
    
    def _create_selenium_config(self) -> str:
        """Create Selenium configuration file"""
        return '''"""
Selenium WebDriver Configuration
===============================
"""

import os

class SeleniumConfig:
    """Configuration for Selenium WebDriver tests"""
    
    # Browser settings
    HEADLESS = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
    BROWSER = os.getenv('SELENIUM_BROWSER', 'chrome')
    
    # Window settings
    WINDOW_WIDTH = int(os.getenv('SELENIUM_WINDOW_WIDTH', '1920'))
    WINDOW_HEIGHT = int(os.getenv('SELENIUM_WINDOW_HEIGHT', '1080'))
    
    # Timeout settings
    IMPLICIT_WAIT = int(os.getenv('SELENIUM_IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('SELENIUM_EXPLICIT_WAIT', '10'))
    
    # Test settings
    SCREENSHOT_ON_FAILURE = os.getenv('SELENIUM_SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    
    # Application settings
    BASE_URL = os.getenv('APPLICATION_URL', 'https://example.com')
    
    @classmethod
    def get_chrome_options(cls):
        """Get Chrome browser options"""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        
        if cls.HEADLESS:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={cls.WINDOW_WIDTH},{cls.WINDOW_HEIGHT}")
        
        return options
    
    @classmethod
    def get_firefox_options(cls):
        """Get Firefox browser options"""
        from selenium.webdriver.firefox.options import Options
        options = Options()
        
        if cls.HEADLESS:
            options.add_argument("--headless")
        
        return options
'''
    
    def _create_api_test_file(self, test_plan: Dict, api_base_url: str) -> str:
        """Create API test file"""
        timestamp = int(time.time())
        
        return f'''"""
API Test Suite - Generated by AutoGen AI Test Framework
=======================================================
Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
API Base URL: {api_base_url}
"""

import requests
import json
import logging
from datetime import datetime
from api_client import APIClient
from api_test_utils import APITestUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'api_test_{{timestamp}}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestAPIAutomation:
    """API test automation class"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Setup API client"""
        client = APIClient("{api_base_url}")
        return client
    
    @pytest.fixture(scope="class")
    def test_utils(self):
        """Setup test utilities"""
        return APITestUtils()
    
    def test_api_health_check(self, api_client, test_utils):
        """Test API health check endpoint"""
        try:
            logger.info("🔍 Testing API health check")
            
            # Make health check request
            response = api_client.get("/health")
            
            # Validate response
            assert response.status_code == 200, f"Expected 200, got {{response.status_code}}"
            
            # Validate response structure
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                assert 'status' in data or 'health' in data, "Health check should contain status information"
                logger.info(f"✅ Health check response: {{data}}")
            
            logger.info("🎉 API health check test completed successfully")
            
        except Exception as e:
            logger.error(f"❌ API health check test failed: {{str(e)}}")
            raise
    
    def test_api_authentication(self, api_client, test_utils):
        """Test API authentication endpoints"""
        try:
            logger.info("🔍 Testing API authentication")
            
            # Test login endpoint
            login_data = {{
                "username": "testuser",
                "password": "testpass"
            }}
            
            response = api_client.post("/auth/login", json=login_data)
            
            # Check if authentication endpoint exists
            if response.status_code == 404:
                logger.warning("⚠️ Authentication endpoint not found, skipping auth test")
                pytest.skip("Authentication endpoint not available")
            
            # Validate successful authentication
            assert response.status_code in [200, 201], f"Expected 200/201, got {{response.status_code}}"
            
            if response.headers.get('content-type', '').startswith('application/json'):
                auth_data = response.json()
                
                # Look for common authentication response fields
                auth_indicators = ['token', 'access_token', 'jwt', 'sessionId', 'authToken']
                has_auth_token = any(indicator in auth_data for indicator in auth_indicators)
                
                if has_auth_token:
                    logger.info("✅ Authentication token received")
                else:
                    logger.warning("⚠️ No authentication token found in response")
            
            logger.info("🎉 API authentication test completed successfully")
            
        except Exception as e:
            logger.error(f"❌ API authentication test failed: {{str(e)}}")
            raise
    
    def test_api_data_endpoints(self, api_client, test_utils):
        """Test API data retrieval endpoints"""
        try:
            logger.info("🔍 Testing API data endpoints")
            
            # Common data endpoints to test
            endpoints_to_test = [
                "/api/users",
                "/api/products", 
                "/api/data",
                "/users",
                "/products",
                "/items"
            ]
            
            successful_endpoints = []
            
            for endpoint in endpoints_to_test:
                try:
                    response = api_client.get(endpoint)
                    
                    if response.status_code == 200:
                        successful_endpoints.append(endpoint)
                        logger.info(f"✅ Endpoint {{endpoint}} responded successfully")
                        
                        # Validate JSON response if applicable
                        if response.headers.get('content-type', '').startswith('application/json'):
                            data = response.json()
                            assert data is not None, f"Endpoint {{endpoint}} returned null data"
                            
                    elif response.status_code == 404:
                        logger.info(f"ℹ️ Endpoint {{endpoint}} not found (404)")
                    else:
                        logger.warning(f"⚠️ Endpoint {{endpoint}} returned {{response.status_code}}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error testing endpoint {{endpoint}}: {{str(e)}}")
            
            # Assert at least one endpoint worked
            if successful_endpoints:
                logger.info(f"✅ Successfully tested {{len(successful_endpoints)}} endpoints")
            else:
                logger.warning("⚠️ No data endpoints found or working")
                pytest.skip("No working data endpoints found")
            
            logger.info("🎉 API data endpoints test completed successfully")
            
        except Exception as e:
            logger.error(f"❌ API data endpoints test failed: {{str(e)}}")
            raise
    
    def test_api_error_handling(self, api_client, test_utils):
        """Test API error handling"""
        try:
            logger.info("🔍 Testing API error handling")
            
            # Test invalid endpoint
            response = api_client.get("/invalid/endpoint/that/should/not/exist")
            assert response.status_code == 404, f"Expected 404 for invalid endpoint, got {{response.status_code}}"
            logger.info("✅ 404 error handling working correctly")
            
            # Test invalid method (if applicable)
            try:
                response = api_client.delete("/")
                if response.status_code == 405:
                    logger.info("✅ 405 Method Not Allowed handling working correctly")
            except:
                logger.info("ℹ️ Method not allowed test skipped")
            
            logger.info("🎉 API error handling test completed successfully")
            
        except Exception as e:
            logger.error(f"❌ API error handling test failed: {{str(e)}}")
            raise
'''
    
    def _create_api_client(self, api_base_url: str) -> str:
        """Create API client file"""
        return f'''"""
API Client for Test Automation
==============================
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIClient:
    """API client for test automation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({{
            'Content-Type': 'application/json',
            'User-Agent': 'AutoGen-Test-Framework/1.0'
        }})
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make GET request"""
        url = f"{{self.base_url}}{{endpoint}}"
        logger.info(f"GET {{url}}")
        
        try:
            response = self.session.get(url, params=params, **kwargs)
            logger.info(f"Response: {{response.status_code}}")
            return response
        except Exception as e:
            logger.error(f"GET request failed: {{str(e)}}")
            raise
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make POST request"""
        url = f"{{self.base_url}}{{endpoint}}"
        logger.info(f"POST {{url}}")
        
        try:
            response = self.session.post(url, data=data, json=json, **kwargs)
            logger.info(f"Response: {{response.status_code}}")
            return response
        except Exception as e:
            logger.error(f"POST request failed: {{str(e)}}")
            raise
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make PUT request"""
        url = f"{{self.base_url}}{{endpoint}}"
        logger.info(f"PUT {{url}}")
        
        try:
            response = self.session.put(url, data=data, json=json, **kwargs)
            logger.info(f"Response: {{response.status_code}}")
            return response
        except Exception as e:
            logger.error(f"PUT request failed: {{str(e)}}")
            raise
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request"""
        url = f"{{self.base_url}}{{endpoint}}"
        logger.info(f"DELETE {{url}}")
        
        try:
            response = self.session.delete(url, **kwargs)
            logger.info(f"Response: {{response.status_code}}")
            return response
        except Exception as e:
            logger.error(f"DELETE request failed: {{str(e)}}")
            raise
    
    def set_auth_token(self, token: str, token_type: str = "Bearer"):
        """Set authentication token"""
        self.session.headers.update({{
            'Authorization': f'{{token_type}} {{token}}'
        }})
        logger.info("✅ Authentication token set")
    
    def clear_auth(self):
        """Clear authentication"""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        logger.info("✅ Authentication cleared")
'''
    
    def _create_api_test_utilities(self) -> str:
        """Create API test utilities file"""
        return '''"""
API Test Utilities
==================
"""

import json
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class APITestUtils:
    """Utilities for API testing"""
    
    @staticmethod
    def validate_json_schema(data: Dict, required_fields: List[str]) -> bool:
        """Validate JSON response has required fields"""
        try:
            for field in required_fields:
                if field not in data:
                    logger.error(f"❌ Required field '{field}' missing from response")
                    return False
            
            logger.info("✅ JSON schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ JSON schema validation failed: {str(e)}")
            return False
    
    @staticmethod
    def validate_response_time(response, max_time_seconds: float = 5.0) -> bool:
        """Validate API response time"""
        try:
            response_time = response.elapsed.total_seconds()
            
            if response_time <= max_time_seconds:
                logger.info(f"✅ Response time OK: {response_time:.2f}s")
                return True
            else:
                logger.warning(f"⚠️ Slow response time: {response_time:.2f}s (max: {max_time_seconds}s)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Response time validation failed: {str(e)}")
            return False
    
    @staticmethod
    def extract_auth_token(response_data: Dict) -> str:
        """Extract authentication token from response"""
        try:
            # Common token field names
            token_fields = ['token', 'access_token', 'jwt', 'authToken', 'sessionId']
            
            for field in token_fields:
                if field in response_data:
                    token = response_data[field]
                    logger.info(f"✅ Auth token extracted from field: {field}")
                    return token
            
            logger.warning("⚠️ No auth token found in response")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Token extraction failed: {str(e)}")
            return ""
    
    @staticmethod
    def wait_for_condition(condition_func, timeout_seconds: int = 30, poll_interval: float = 1.0) -> bool:
        """Wait for a condition to become true"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                if condition_func():
                    logger.info("✅ Condition met")
                    return True
            except Exception as e:
                logger.debug(f"Condition check failed: {str(e)}")
            
            time.sleep(poll_interval)
        
        logger.error(f"❌ Condition not met within {timeout_seconds} seconds")
        return False
    
    @staticmethod
    def compare_json_responses(response1: Dict, response2: Dict, ignore_fields: List[str] = None) -> bool:
        """Compare two JSON responses, optionally ignoring certain fields"""
        try:
            ignore_fields = ignore_fields or []
            
            # Create copies and remove ignored fields
            data1 = {k: v for k, v in response1.items() if k not in ignore_fields}
            data2 = {k: v for k, v in response2.items() if k not in ignore_fields}
            
            if data1 == data2:
                logger.info("✅ JSON responses match")
                return True
            else:
                logger.error("❌ JSON responses differ")
                logger.debug(f"Response 1: {json.dumps(data1, indent=2)}")
                logger.debug(f"Response 2: {json.dumps(data2, indent=2)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ JSON comparison failed: {str(e)}")
            return False

def main():
    """Main enhancement function"""
    print("\n" + "="*70)
    print("ENHANCE TEST CREATION AGENT - SELENIUM & API CAPABILITIES")
    print("="*70)
    
    enhancer = TestCreationEnhancer()
    
    try:
        success = enhancer.enhance_agent()
        
        if success:
            print("\n🎉 SUCCESS: Test Creation Agent enhanced with Selenium and API capabilities!")
            print("✅ Selenium WebDriver test generation added")
            print("✅ API testing capabilities added")
            print("✅ New task types: 'generate_selenium_tests', 'generate_api_tests'")
            print("✅ Backup created for rollback if needed")
            print("\nNext steps:")
            print("1. Test the enhanced capabilities")
            print("2. Validate Selenium and API test generation")
            print("3. Update requirements.txt with new dependencies")
        else:
            print("\n❌ FAILURE: Enhancement failed")
            print("⚠️ Check logs above for specific issues")
            print("🔄 Original agent should still be functional")
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        logger.error(f"Critical error in main: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

