"""
Configuration Manager for MVP File Storage
Handles storage backend configuration and environment variables
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for file storage and other settings"""
    
    def __init__(self):
        self.storage_config = self._load_storage_config()
        self.app_config = self._load_app_config()
        logger.info(f"📋 Configuration loaded - Storage: {self.storage_config['type']}")
    
    def _load_storage_config(self) -> Dict[str, Any]:
        """Load storage configuration from environment variables"""
        storage_type = os.getenv('STORAGE_TYPE', 'local').lower()
        
        config = {
            'type': storage_type,
            'base_path': os.getenv('STORAGE_BASE_PATH', '/opt/test-automation-platform/data'),
            'cache_ttl': int(os.getenv('FILE_CACHE_TTL', '300')),  # 5 minutes default
        }
        
        if storage_type == 's3':
            config.update({
                'bucket': os.getenv('S3_BUCKET', 'test-automation-platform'),
                'region': os.getenv('AWS_REGION', 'us-east-1'),
                'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            })
        elif storage_type == 'azure':
            config.update({
                'account_name': os.getenv('AZURE_STORAGE_ACCOUNT'),
                'account_key': os.getenv('AZURE_STORAGE_KEY'),
                'container': os.getenv('AZURE_CONTAINER', 'test-files'),
            })
        elif storage_type == 'gcs':
            config.update({
                'bucket': os.getenv('GCS_BUCKET', 'test-automation-files'),
                'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
                'project_id': os.getenv('GCP_PROJECT_ID'),
            })
        
        return config
    
    def _load_app_config(self) -> Dict[str, Any]:
        """Load general application configuration"""
        return {
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', '10')),
            'max_files_per_suite': int(os.getenv('MAX_FILES_PER_SUITE', '100')),
            'enable_file_compression': os.getenv('ENABLE_FILE_COMPRESSION', 'false').lower() == 'true',
            'backup_enabled': os.getenv('BACKUP_ENABLED', 'true').lower() == 'true',
            'backup_retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
        }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration"""
        return self.storage_config.copy()
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.app_config.copy()
    
    def validate_storage_config(self) -> bool:
        """Validate storage configuration"""
        storage_type = self.storage_config['type']
        
        if storage_type == 'local':
            base_path = self.storage_config['base_path']
            try:
                Path(base_path).mkdir(parents=True, exist_ok=True)
                return True
            except Exception as e:
                logger.error(f"Failed to create local storage directory {base_path}: {e}")
                return False
        
        elif storage_type == 's3':
            required_keys = ['bucket', 'access_key', 'secret_key']
            missing_keys = [key for key in required_keys if not self.storage_config.get(key)]
            if missing_keys:
                logger.error(f"Missing S3 configuration: {missing_keys}")
                return False
            return True
        
        elif storage_type == 'azure':
            required_keys = ['account_name', 'account_key', 'container']
            missing_keys = [key for key in required_keys if not self.storage_config.get(key)]
            if missing_keys:
                logger.error(f"Missing Azure configuration: {missing_keys}")
                return False
            return True
        
        elif storage_type == 'gcs':
            required_keys = ['bucket', 'project_id']
            missing_keys = [key for key in required_keys if not self.storage_config.get(key)]
            if missing_keys:
                logger.error(f"Missing GCS configuration: {missing_keys}")
                return False
            return True
        
        else:
            logger.error(f"Unsupported storage type: {storage_type}")
            return False
    
    def get_file_path_template(self, customer_id: str, suite_id: str, file_name: str) -> str:
        """Generate file path template based on storage type"""
        storage_type = self.storage_config['type']
        
        relative_path = f"customers/customer_{customer_id}/test_suites/suite_{suite_id}/tests/{file_name}"
        
        if storage_type == 'local':
            return os.path.join(self.storage_config['base_path'], relative_path)
        elif storage_type == 's3':
            return f"s3://{self.storage_config['bucket']}/{relative_path}"
        elif storage_type == 'azure':
            return f"azure://{self.storage_config['container']}/{relative_path}"
        elif storage_type == 'gcs':
            return f"gcs://{self.storage_config['bucket']}/{relative_path}"
        else:
            return relative_path
    
    def setup_logging(self):
        """Setup logging based on configuration"""
        log_level = getattr(logging, self.app_config['log_level'].upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('test_automation.log') if self.app_config['debug'] else logging.NullHandler()
            ]
        )
        
        # Set specific logger levels
        logging.getLogger('file_storage_manager').setLevel(log_level)
        logging.getLogger('real_agent_processor').setLevel(log_level)
        logging.getLogger('database_postgres_full').setLevel(log_level)
    
    def create_environment_file(self, file_path: str = '.env.example'):
        """Create example environment file with all configuration options"""
        env_content = f"""# Test Automation Platform Configuration

# Storage Configuration
STORAGE_TYPE=local  # Options: local, s3, azure, gcs
STORAGE_BASE_PATH=/opt/test-automation-platform/data

# S3 Configuration (if STORAGE_TYPE=s3)
S3_BUCKET=test-automation-platform
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Azure Configuration (if STORAGE_TYPE=azure)
AZURE_STORAGE_ACCOUNT=your_account
AZURE_STORAGE_KEY=your_key
AZURE_CONTAINER=test-files

# Google Cloud Configuration (if STORAGE_TYPE=gcs)
GCS_BUCKET=test-automation-files
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=your_project_id

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
MAX_FILES_PER_SUITE=100
ENABLE_FILE_COMPRESSION=false
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30

# File Cache Configuration
FILE_CACHE_TTL=300  # 5 minutes

# Database Configuration
DATABASE_URL=postgresql://app_user:password@localhost/test_automation_platform
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Security Configuration
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Test Execution Configuration
TEST_TIMEOUT=30000
BROWSER_TYPE=chromium  # Options: chromium, firefox, webkit
HEADLESS=true
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720

# Monitoring Configuration
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
"""
        
        try:
            with open(file_path, 'w') as f:
                f.write(env_content)
            logger.info(f"📝 Created environment file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to create environment file: {e}")

# Global configuration instance
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get global configuration instance"""
    return config

def validate_environment() -> bool:
    """Validate environment configuration"""
    config = get_config()
    
    # Validate storage configuration
    if not config.validate_storage_config():
        logger.error("❌ Storage configuration validation failed")
        return False
    
    # Check required environment variables
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ Environment configuration validated successfully")
    return True

def setup_directories():
    """Setup required directories for local storage"""
    config = get_config()
    
    if config.storage_config['type'] == 'local':
        base_path = config.storage_config['base_path']
        
        # Create directory structure
        directories = [
            base_path,
            os.path.join(base_path, 'customers'),
            os.path.join(base_path, 'templates'),
            os.path.join(base_path, 'backup'),
            os.path.join(base_path, 'logs'),
            os.path.join(base_path, 'cache'),
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                return False
    
    return True

if __name__ == "__main__":
    # Create example environment file
    config = ConfigManager()
    config.create_environment_file()
    config.setup_logging()
    
    # Validate configuration
    if validate_environment():
        print("✅ Configuration is valid")
        setup_directories()
    else:
        print("❌ Configuration validation failed")
