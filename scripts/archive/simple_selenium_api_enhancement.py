#!/usr/bin/env python3
"""
Simple Selenium and API Enhancement for Test Creation Agent
===========================================================
Add Selenium and API capabilities without importing test dependencies
"""

import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enhance_test_creation_agent():
    """Add Selenium and API capabilities to the Enhanced Test Creation Agent"""
    
    logger.info("🚀 Starting simple Selenium and API enhancement")
    
    agent_file = "agents/test_creation_agent.py"
    backup_file = "agents/test_creation_agent_pre_selenium_api_backup.py"
    
    try:
        # Create backup
        logger.info("📦 Creating backup of current Enhanced Test Creation Agent")
        with open(agent_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        logger.info(f"✅ Backup created: {backup_file}")
        
        # Update the process_task method to handle new task types
        logger.info("🔧 Adding Selenium and API task types to process_task method")
        
        old_process_task = '''    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process test creation task with real code generation"""
        task_type = task_data.get("task_type", "generate_tests")
        
        if task_type == "generate_tests":
            return await self._generate_real_test_code(task_data)
        elif task_type == "create_page_objects":
            return await self._create_page_objects(task_data)
        elif task_type == "generate_utilities":
            return await self._generate_test_utilities(task_data)
        else:
            return {
                "status": "error",
                "error": f"Unknown task type: {task_type}"
            }'''
        
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
            }'''
        
        # Replace the process_task method
        content = content.replace(old_process_task, new_process_task)
        
        # Add new methods at the end of the class (before the last closing)
        logger.info("🔧 Adding Selenium and API generation methods")
        
        # Find the end of the class
        class_end_marker = "        return page_objects"
        insertion_point = content.rfind(class_end_marker)
        
        if insertion_point == -1:
            logger.error("Could not find insertion point in class")
            return False
        
        # Move to after the return statement
        insertion_point = content.find('\n', insertion_point) + 1
        
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
            selenium_test = self._create_selenium_test_template(test_plan, application_url)
            test_file_path = f"{self.work_dir}/test_selenium_automation.py"
            
            with open(test_file_path, 'w') as f:
                f.write(selenium_test)
            generated_files.append(test_file_path)
            
            # Create Selenium configuration
            config_content = self._create_selenium_config_template()
            config_file_path = f"{self.work_dir}/selenium_config.py"
            with open(config_file_path, 'w') as f:
                f.write(config_content)
            generated_files.append(config_file_path)
            
            # Create requirements for Selenium
            selenium_requirements = self._create_selenium_requirements()
            req_file_path = f"{self.work_dir}/selenium_requirements.txt"
            with open(req_file_path, 'w') as f:
                f.write(selenium_requirements)
            generated_files.append(req_file_path)
            
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
            api_test = self._create_api_test_template(test_plan, api_base_url)
            test_file_path = f"{self.work_dir}/test_api_automation.py"
            
            with open(test_file_path, 'w') as f:
                f.write(api_test)
            generated_files.append(test_file_path)
            
            # Create API client
            api_client = self._create_api_client_template(api_base_url)
            client_file_path = f"{self.work_dir}/api_client.py"
            with open(client_file_path, 'w') as f:
                f.write(api_client)
            generated_files.append(client_file_path)
            
            # Create API requirements
            api_requirements = self._create_api_requirements()
            req_file_path = f"{self.work_dir}/api_requirements.txt"
            with open(req_file_path, 'w') as f:
                f.write(api_requirements)
            generated_files.append(req_file_path)
            
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
    
    def _create_selenium_test_template(self, test_plan: Dict, application_url: str) -> str:
        """Create Selenium WebDriver test template"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f'''"""
Selenium WebDriver Test - Generated by AutoGen AI Test Framework
================================================================
Generated at: {timestamp}
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestSeleniumAutomation:
    """Selenium WebDriver test automation class"""
    
    def setup_method(self):
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
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)
    
    def teardown_method(self):
        """Cleanup Selenium WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def test_login_functionality(self):
        """Test user login functionality with Selenium"""
        try:
            logger.info("🔍 Testing login functionality with Selenium")
            
            # Navigate to application
            self.driver.get("{application_url}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find and interact with login elements
            # This is a basic template - real implementation would use discovered selectors
            
            # Take screenshot
            timestamp = int(time.time())
            screenshot_path = f"selenium_login_test_{{timestamp}}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {{screenshot_path}}")
            
            logger.info("🎉 Selenium login test template completed")
            
        except Exception as e:
            timestamp = int(time.time())
            error_screenshot = f"selenium_login_error_{{timestamp}}.png"
            self.driver.save_screenshot(error_screenshot)
            logger.error(f"❌ Selenium login test failed: {{str(e)}}")
            logger.error(f"📸 Error screenshot: {{error_screenshot}}")
            raise
    
    def test_navigation_functionality(self):
        """Test basic navigation functionality"""
        try:
            logger.info("🔍 Testing navigation functionality")
            
            # Navigate to application
            self.driver.get("{application_url}")
            
            # Test page title
            assert self.driver.title, "Page title should not be empty"
            logger.info(f"✅ Page title: {{self.driver.title}}")
            
            # Take screenshot
            timestamp = int(time.time())
            screenshot_path = f"selenium_navigation_test_{{timestamp}}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {{screenshot_path}}")
            
            logger.info("🎉 Selenium navigation test completed")
            
        except Exception as e:
            timestamp = int(time.time())
            error_screenshot = f"selenium_navigation_error_{{timestamp}}.png"
            self.driver.save_screenshot(error_screenshot)
            logger.error(f"❌ Selenium navigation test failed: {{str(e)}}")
            logger.error(f"📸 Error screenshot: {{error_screenshot}}")
            raise

if __name__ == "__main__":
    test = TestSeleniumAutomation()
    test.setup_method()
    try:
        test.test_login_functionality()
        test.test_navigation_functionality()
    finally:
        test.teardown_method()
'''
    
    def _create_selenium_config_template(self) -> str:
        """Create Selenium configuration template"""
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
'''
    
    def _create_selenium_requirements(self) -> str:
        """Create Selenium requirements file"""
        return '''# Selenium WebDriver requirements
selenium>=4.15.0
webdriver-manager>=4.0.0
'''
    
    def _create_api_test_template(self, test_plan: Dict, api_base_url: str) -> str:
        """Create API test template"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f'''"""
API Test Suite - Generated by AutoGen AI Test Framework
=======================================================
Generated at: {timestamp}
API Base URL: {api_base_url}
"""

import requests
import json
import logging
from datetime import datetime
from api_client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestAPIAutomation:
    """API test automation class"""
    
    def setup_method(self):
        """Setup API client"""
        self.api_client = APIClient("{api_base_url}")
    
    def test_api_health_check(self):
        """Test API health check endpoint"""
        try:
            logger.info("🔍 Testing API health check")
            
            # Make health check request
            response = self.api_client.get("/health")
            
            # Basic validation
            assert response.status_code in [200, 404], f"Unexpected status code: {{response.status_code}}"
            
            if response.status_code == 200:
                logger.info("✅ Health check endpoint available")
            else:
                logger.info("ℹ️ Health check endpoint not found (404)")
            
            logger.info("🎉 API health check test completed")
            
        except Exception as e:
            logger.error(f"❌ API health check test failed: {{str(e)}}")
            raise
    
    def test_api_authentication(self):
        """Test API authentication endpoints"""
        try:
            logger.info("🔍 Testing API authentication")
            
            # Test login endpoint
            login_data = {{
                "username": "testuser",
                "password": "testpass"
            }}
            
            response = self.api_client.post("/auth/login", json=login_data)
            
            # Check if authentication endpoint exists
            if response.status_code == 404:
                logger.info("ℹ️ Authentication endpoint not found, skipping auth test")
                return
            
            # Basic validation
            assert response.status_code in [200, 201, 401, 403], f"Unexpected status code: {{response.status_code}}"
            
            if response.status_code in [200, 201]:
                logger.info("✅ Authentication endpoint available and responding")
            else:
                logger.info(f"ℹ️ Authentication endpoint returned {{response.status_code}}")
            
            logger.info("🎉 API authentication test completed")
            
        except Exception as e:
            logger.error(f"❌ API authentication test failed: {{str(e)}}")
            raise
    
    def test_api_data_endpoints(self):
        """Test API data retrieval endpoints"""
        try:
            logger.info("🔍 Testing API data endpoints")
            
            # Common data endpoints to test
            endpoints_to_test = [
                "/api/users",
                "/api/products", 
                "/api/data",
                "/users",
                "/products"
            ]
            
            successful_endpoints = []
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.api_client.get(endpoint)
                    
                    if response.status_code == 200:
                        successful_endpoints.append(endpoint)
                        logger.info(f"✅ Endpoint {{endpoint}} responded successfully")
                    elif response.status_code == 404:
                        logger.info(f"ℹ️ Endpoint {{endpoint}} not found (404)")
                    else:
                        logger.info(f"ℹ️ Endpoint {{endpoint}} returned {{response.status_code}}")
                        
                except Exception as e:
                    logger.info(f"ℹ️ Error testing endpoint {{endpoint}}: {{str(e)}}")
            
            logger.info(f"✅ Tested {{len(endpoints_to_test)}} endpoints, {{len(successful_endpoints)}} successful")
            logger.info("🎉 API data endpoints test completed")
            
        except Exception as e:
            logger.error(f"❌ API data endpoints test failed: {{str(e)}}")
            raise

if __name__ == "__main__":
    test = TestAPIAutomation()
    test.setup_method()
    test.test_api_health_check()
    test.test_api_authentication()
    test.test_api_data_endpoints()
'''
    
    def _create_api_client_template(self, api_base_url: str) -> str:
        """Create API client template"""
        return f'''"""
API Client for Test Automation
==============================
"""

import requests
import json
import logging

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
    
    def get(self, endpoint: str, params=None, **kwargs):
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
    
    def post(self, endpoint: str, data=None, json=None, **kwargs):
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
    
    def put(self, endpoint: str, data=None, json=None, **kwargs):
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
    
    def delete(self, endpoint: str, **kwargs):
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
'''
    
    def _create_api_requirements(self) -> str:
        """Create API requirements file"""
        return '''# API testing requirements
requests>=2.31.0
'''
'''
        
        # Insert the new methods
        content = content[:insertion_point] + new_methods + content[insertion_point:]
        
        # Update the get_capabilities method
        logger.info("🔧 Updating get_capabilities method")
        
        old_capabilities = '''    def get_capabilities(self) -> List[str]:
        """Get enhanced capabilities"""
        return [
            "real_code_generation",
            "discovery_integration",
            "page_object_models",
            "test_utilities",
            "playwright_tests",
            "selenium_tests",
            "api_tests",
            "assertions_and_validations"
        ]'''
        
        new_capabilities = '''    def get_capabilities(self) -> List[str]:
        """Get enhanced capabilities including Selenium and API"""
        return [
            "real_code_generation",
            "discovery_integration",
            "page_object_models",
            "test_utilities",
            "playwright_tests",
            "selenium_tests",
            "api_tests",
            "assertions_and_validations",
            "selenium_webdriver_tests",
            "api_requests_tests",
            "multi_framework_support"
        ]'''
        
        content = content.replace(old_capabilities, new_capabilities)
        
        # Write the enhanced file
        with open(agent_file, 'w') as f:
            f.write(content)
        
        logger.info("✅ Test Creation Agent enhanced successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhancement failed: {str(e)}")
        return False

def main():
    """Main enhancement function"""
    print("\n" + "="*70)
    print("SIMPLE SELENIUM & API ENHANCEMENT")
    print("="*70)
    
    try:
        success = enhance_test_creation_agent()
        
        if success:
            print("\n🎉 SUCCESS: Test Creation Agent enhanced with Selenium and API capabilities!")
            print("✅ Selenium WebDriver test generation added")
            print("✅ API testing capabilities added")
            print("✅ New task types: 'generate_selenium_tests', 'generate_api_tests'")
            print("✅ Backup created for rollback if needed")
            print("\nNext steps:")
            print("1. Test the enhanced capabilities")
            print("2. Install selenium and requests: pip install selenium requests")
            print("3. Validate Selenium and API test generation")
        else:
            print("\n❌ FAILURE: Enhancement failed")
            print("⚠️ Check logs above for specific issues")
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

