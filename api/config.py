"""
API Configuration and Settings
==============================

Configuration management for the AI Test Automation SaaS Platform API.
"""

import os
from typing import List

class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        # API Configuration
        self.app_name = "AI Test Automation SaaS Platform"
        self.app_version = "1.0.0"
        self.debug = False
        
        # Security
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # CORS
        self.allowed_origins = ["*"]  # Configure for production
        
        # Database (for future implementation)
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./test_automation.db")
        
        # Redis (for caching and queues)
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # File Storage
        self.upload_dir = "uploads"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # API Limits
        self.default_api_quota = 100
        self.max_concurrent_executions = 5
        
        # Workflow Configuration
        self.default_timeout = 300  # 5 minutes
        self.max_timeout = 1800     # 30 minutes
        
        # Logging
        self.log_level = "INFO"
        self.log_file = "api.log"

# Global settings instance
settings = Settings()

# API Response Templates
API_RESPONSES = {
    "success": {
        "status": "success",
        "message": "Operation completed successfully"
    },
    "error": {
        "status": "error",
        "message": "An error occurred"
    },
    "validation_error": {
        "status": "error",
        "message": "Validation failed"
    },
    "not_found": {
        "status": "error",
        "message": "Resource not found"
    },
    "unauthorized": {
        "status": "error",
        "message": "Authentication required"
    },
    "forbidden": {
        "status": "error",
        "message": "Access denied"
    },
    "quota_exceeded": {
        "status": "error",
        "message": "API quota exceeded"
    }
}

# Application Type Configurations
APPLICATION_TYPES = {
    "ecommerce": {
        "name": "E-commerce",
        "description": "Online shopping and retail applications",
        "default_scenarios": ["user_registration", "product_browsing", "checkout"],
        "priority_areas": ["authentication", "payment", "inventory"],
        "estimated_duration": 300
    },
    "enterprise_hrms": {
        "name": "Human Resource Management",
        "description": "Employee management and HR systems",
        "default_scenarios": ["employee_management", "leave_management", "attendance"],
        "priority_areas": ["user_roles", "workflows", "compliance"],
        "estimated_duration": 400
    },
    "financial_banking": {
        "name": "Banking & Financial",
        "description": "Financial services and banking applications",
        "default_scenarios": ["account_management", "transactions", "security"],
        "priority_areas": ["security", "compliance", "audit"],
        "estimated_duration": 500
    },
    "healthcare": {
        "name": "Healthcare",
        "description": "Medical and healthcare management systems",
        "default_scenarios": ["patient_management", "appointments", "records"],
        "priority_areas": ["privacy", "compliance", "security"],
        "estimated_duration": 450
    },
    "education": {
        "name": "Education",
        "description": "Learning management and educational systems",
        "default_scenarios": ["student_management", "courses", "assessments"],
        "priority_areas": ["user_management", "content", "progress"],
        "estimated_duration": 350
    }
}

# Status Messages
STATUS_MESSAGES = {
    "pending": "Test execution is queued and waiting to start",
    "initializing": "Setting up test environment and loading configuration",
    "discovering": "Analyzing application and discovering elements",
    "generating": "Creating test automation code",
    "reviewing": "Reviewing and optimizing generated tests",
    "executing": "Running test automation suite",
    "reporting": "Generating comprehensive test reports",
    "completed": "Test execution completed successfully",
    "failed": "Test execution failed with errors",
    "cancelled": "Test execution was cancelled by user",
    "timeout": "Test execution exceeded maximum time limit"
}

# Error Codes
ERROR_CODES = {
    "INVALID_URL": "The provided URL is not valid or accessible",
    "UNSUPPORTED_APP_TYPE": "The application type is not supported",
    "QUOTA_EXCEEDED": "API usage quota has been exceeded",
    "CONCURRENT_LIMIT": "Maximum concurrent executions reached",
    "TIMEOUT": "Operation exceeded maximum time limit",
    "INVALID_CONFIG": "Configuration parameters are invalid",
    "NETWORK_ERROR": "Network connectivity issues detected",
    "BROWSER_ERROR": "Browser automation encountered errors",
    "PARSING_ERROR": "Failed to parse application structure",
    "GENERATION_ERROR": "Test code generation failed",
    "EXECUTION_ERROR": "Test execution encountered errors"
}
