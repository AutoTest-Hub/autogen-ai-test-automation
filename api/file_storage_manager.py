"""
Universal File Storage Manager for MVP
Supports multiple storage backends: Local, S3, Azure Blob, Google Cloud Storage
"""

import os
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class FileStorageManager(ABC):
    """Abstract base class for file storage backends"""
    
    @abstractmethod
    def save_test_file(self, customer_id: str, suite_id: str, test_case: Dict[str, Any]) -> str:
        """Save test file and return file path"""
        pass
    
    @abstractmethod
    def load_test_file(self, file_path: str) -> str:
        """Load test file content"""
        pass
    
    @abstractmethod
    def delete_test_file(self, file_path: str) -> bool:
        """Delete test file"""
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata (size, checksum, etc.)"""
        pass

class LocalFileManager(FileStorageManager):
    """Local file system storage for On-Premise deployments"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.getenv('STORAGE_BASE_PATH', '/opt/test-automation-platform/data')
        self.ensure_base_directory()
    
    def ensure_base_directory(self):
        """Ensure base directory exists"""
        os.makedirs(self.base_path, exist_ok=True)
        logger.info(f"📁 Local file storage initialized at: {self.base_path}")
    
    def save_test_file(self, customer_id: str, suite_id: str, test_case: Dict[str, Any]) -> str:
        """Save test file to local file system"""
        try:
            # Generate file structure
            file_name = f"test_{self._sanitize_filename(test_case['name'])}.py"
            suite_dir = os.path.join(
                self.base_path,
                "customers",
                f"customer_{customer_id}",
                "test_suites",
                f"suite_{suite_id}",
                "tests"
            )
            
            # Create directory structure
            os.makedirs(suite_dir, exist_ok=True)
            
            file_path = os.path.join(suite_dir, file_name)
            
            # Generate Playwright test code
            test_code = self._generate_playwright_code(test_case)
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(test_code)
            
            # Create conftest.py if it doesn't exist
            self._ensure_conftest_file(suite_dir, customer_id, suite_id)
            
            logger.info(f"💾 Saved test file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save test file: {e}")
            raise
    
    def load_test_file(self, file_path: str) -> str:
        """Load test file from local file system"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load test file {file_path}: {e}")
            raise
    
    def delete_test_file(self, file_path: str) -> bool:
        """Delete test file from local file system"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Deleted test file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete test file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local file system"""
        return os.path.exists(file_path)
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata from local file system"""
        try:
            if not os.path.exists(file_path):
                return {}
            
            stat = os.stat(file_path)
            
            # Calculate checksum
            with open(file_path, 'rb') as f:
                content = f.read()
                checksum = hashlib.sha256(content).hexdigest()
            
            return {
                'size_bytes': stat.st_size,
                'checksum': checksum,
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime)
            }
        except Exception as e:
            logger.error(f"Failed to get file metadata for {file_path}: {e}")
            return {}
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename for file system"""
        # Replace spaces and special characters
        sanitized = name.lower().replace(' ', '_').replace('-', '_')
        # Remove non-alphanumeric characters except underscores
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized[:50]  # Limit length
    
    def _generate_playwright_code(self, test_case: Dict[str, Any]) -> str:
        """Generate Playwright test code from test case"""
        test_name = self._sanitize_filename(test_case['name'])
        
        # Generate test steps code
        steps_code = self._generate_steps_code(test_case.get('steps', []))
        
        # Generate assertions code
        assertions_code = self._generate_assertions_code(test_case.get('expected_result', ''))
        
        return f'''"""
{test_case.get('description', 'Generated test case')}

Generated from intent: {test_case.get('intent', 'AI Agent')}
Test type: {test_case.get('type', 'functional')}
Priority: {test_case.get('priority', 'medium')}
Generated at: {datetime.now().isoformat()}
"""

import pytest
from playwright.sync_api import Page, expect
import json
import os

def test_{test_name}(page: Page):
    """
    {test_case.get('description', 'Generated test case')}
    """
    try:
        # Test configuration
        base_url = os.getenv('TEST_BASE_URL', 'https://example.com')
        timeout = int(os.getenv('TEST_TIMEOUT', '30000'))
        
        # Set page timeout
        page.set_default_timeout(timeout)
        
        # Navigate to application
        page.goto(base_url)
        
        # Test steps
{steps_code}
        
        # Assertions
{assertions_code}
        
        print(f"✅ Test '{test_case['name']}' completed successfully")
        
    except Exception as e:
        print(f"❌ Test '{test_case['name']}' failed: {{str(e)}}")
        # Take screenshot on failure
        page.screenshot(path=f"test_failure_{test_name}_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.png")
        raise

if __name__ == "__main__":
    # Allow running test directly
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    sys.exit(result.returncode)
'''
    
    def _generate_steps_code(self, steps: List[Dict]) -> str:
        """Generate code for test steps"""
        if not steps:
            return "        # No specific steps defined\n        pass"
        
        code_lines = []
        for i, step in enumerate(steps, 1):
            action = step.get('action', 'unknown')
            target = step.get('target', '')
            value = step.get('value', '')
            
            code_lines.append(f"        # Step {i}: {step.get('description', action)}")
            
            if action == 'navigate':
                code_lines.append(f"        page.goto('{target}')")
            elif action == 'click':
                code_lines.append(f"        page.click('{target}')")
            elif action == 'fill' or action == 'type':
                code_lines.append(f"        page.fill('{target}', '{value}')")
            elif action == 'wait':
                code_lines.append(f"        page.wait_for_timeout({value or 1000})")
            elif action == 'wait_for_element':
                code_lines.append(f"        page.wait_for_selector('{target}')")
            else:
                code_lines.append(f"        # TODO: Implement action '{action}' for target '{target}'")
            
            code_lines.append("")  # Empty line between steps
        
        return "\n".join(code_lines)
    
    def _generate_assertions_code(self, expected_result: str) -> str:
        """Generate code for assertions"""
        if not expected_result:
            return "        # No specific assertions defined\n        assert True  # Test completed without errors"
        
        # Simple assertion based on expected result
        if 'login' in expected_result.lower():
            return """        # Verify successful login
        expect(page).to_have_url(re.compile(r".*(dashboard|home|profile).*"))
        expect(page.locator('body')).not_to_contain_text('error')"""
        elif 'error' in expected_result.lower():
            return """        # Verify error handling
        expect(page.locator('body')).to_contain_text('error')"""
        else:
            return f"""        # Verify expected result
        # Expected: {expected_result}
        expect(page.locator('body')).to_be_visible()
        assert True  # Test completed - manual verification needed"""
    
    def _ensure_conftest_file(self, suite_dir: str, customer_id: str, suite_id: str):
        """Create conftest.py file for Playwright configuration"""
        conftest_path = os.path.join(suite_dir, 'conftest.py')
        
        if not os.path.exists(conftest_path):
            conftest_content = f'''"""
Pytest configuration for test suite {suite_id}
Customer: {customer_id}
Generated at: {datetime.now().isoformat()}
"""

import pytest
import os
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """Browser fixture for all tests"""
    with sync_playwright() as p:
        browser_type = os.getenv('BROWSER_TYPE', 'chromium')
        headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        
        if browser_type == 'firefox':
            browser = p.firefox.launch(headless=headless)
        elif browser_type == 'webkit':
            browser = p.webkit.launch(headless=headless)
        else:
            browser = p.chromium.launch(headless=headless)
        
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    """Page fixture for each test"""
    context = browser.new_context(
        viewport={{"width": 1280, "height": 720}},
        ignore_https_errors=True
    )
    page = context.new_page()
    yield page
    context.close()

# Test configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add integration marker to all tests
        item.add_marker(pytest.mark.integration)
'''
            
            with open(conftest_path, 'w', encoding='utf-8') as f:
                f.write(conftest_content)
            
            logger.info(f"📝 Created conftest.py: {conftest_path}")

class S3FileManager(FileStorageManager):
    """S3-based file storage for SaaS deployments"""
    
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET', 'test-automation-platform')
        self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize S3 client"""
        try:
            import boto3
            self.s3_client = boto3.client('s3')
            logger.info(f"☁️ S3 file storage initialized for bucket: {self.bucket_name}")
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def save_test_file(self, customer_id: str, suite_id: str, test_case: Dict[str, Any]) -> str:
        """Save test file to S3"""
        try:
            # Generate S3 key
            file_name = f"test_{self._sanitize_filename(test_case['name'])}.py"
            s3_key = f"customers/customer_{customer_id}/test_suites/suite_{suite_id}/tests/{file_name}"
            
            # Generate test code
            test_code = LocalFileManager._generate_playwright_code(self, test_case)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=test_code.encode('utf-8'),
                ContentType='text/x-python',
                Metadata={
                    'customer_id': customer_id,
                    'suite_id': suite_id,
                    'test_case_id': test_case.get('id', ''),
                    'generated_at': datetime.now().isoformat(),
                    'test_type': test_case.get('type', 'functional'),
                    'priority': test_case.get('priority', 'medium')
                }
            )
            
            file_path = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"☁️ Saved test file to S3: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save test file to S3: {e}")
            raise
    
    def load_test_file(self, file_path: str) -> str:
        """Load test file from S3"""
        try:
            # Parse S3 path
            bucket, key = self._parse_s3_path(file_path)
            
            # Download from S3
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read().decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to load test file from S3 {file_path}: {e}")
            raise
    
    def delete_test_file(self, file_path: str) -> bool:
        """Delete test file from S3"""
        try:
            bucket, key = self._parse_s3_path(file_path)
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"🗑️ Deleted test file from S3: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete test file from S3 {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            bucket, key = self._parse_s3_path(file_path)
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except:
            return False
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata from S3"""
        try:
            bucket, key = self._parse_s3_path(file_path)
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            
            return {
                'size_bytes': response['ContentLength'],
                'checksum': response.get('ETag', '').strip('"'),
                'last_modified': response['LastModified'],
                'metadata': response.get('Metadata', {})
            }
        except Exception as e:
            logger.error(f"Failed to get S3 file metadata for {file_path}: {e}")
            return {}
    
    def _parse_s3_path(self, s3_path: str) -> tuple:
        """Parse S3 path into bucket and key"""
        if not s3_path.startswith('s3://'):
            raise ValueError(f"Invalid S3 path: {s3_path}")
        
        path_parts = s3_path[5:].split('/', 1)
        if len(path_parts) != 2:
            raise ValueError(f"Invalid S3 path format: {s3_path}")
        
        return path_parts[0], path_parts[1]
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename for S3"""
        return LocalFileManager._sanitize_filename(self, name)

def get_file_storage_manager() -> FileStorageManager:
    """Factory function to get appropriate file storage manager"""
    storage_type = os.getenv('STORAGE_TYPE', 'local').lower()
    
    if storage_type == 's3':
        return S3FileManager()
    elif storage_type == 'azure':
        # TODO: Implement AzureBlobManager
        logger.warning("Azure Blob Storage not implemented yet, falling back to local storage")
        return LocalFileManager()
    elif storage_type == 'gcs':
        # TODO: Implement GCSFileManager
        logger.warning("Google Cloud Storage not implemented yet, falling back to local storage")
        return LocalFileManager()
    else:
        return LocalFileManager()

# Simple in-memory cache for file content
class FileCache:
    """Simple in-memory cache for file content"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, file_path: str) -> Optional[str]:
        """Get cached file content"""
        if file_path in self.cache:
            content, timestamp = self.cache[file_path]
            if (datetime.now().timestamp() - timestamp) < self.ttl:
                return content
            else:
                del self.cache[file_path]
        return None
    
    def set(self, file_path: str, content: str):
        """Cache file content"""
        self.cache[file_path] = (content, datetime.now().timestamp())
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
    
    def cleanup(self):
        """Remove expired entries"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if (current_time - timestamp) >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

# Global file cache instance
file_cache = FileCache()
