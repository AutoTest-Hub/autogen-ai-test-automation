# AutoGen AI Test Automation Framework - Project Structure

## Overview

This document outlines the proper project structure for the AutoGen AI Test Automation Framework. The framework follows industry best practices for test automation project organization, with clear separation of concerns between tests, page objects, and configuration.

## Directory Structure

```
autogen-ai-test-automation/
├── agents/                     # Agent implementations
│   ├── base_agent.py           # Base agent class
│   ├── discovery_agent.py      # Discovery agent
│   ├── execution_agent.py      # Execution agent
│   ├── planning_agent.py       # Planning agent
│   ├── real_browser_discovery_agent.py  # Real browser discovery agent
│   ├── reporting_agent.py      # Reporting agent
│   ├── review_agent.py         # Review agent
│   └── test_creation_agent.py  # Test creation agent
├── config/                     # Configuration files
│   ├── __init__.py             # Package initialization
│   └── settings.py             # Framework settings
├── orchestrator/               # Orchestration components
│   ├── __init__.py             # Package initialization
│   └── workflow_orchestrator.py # Workflow orchestrator
├── pages/                      # Page object models
│   ├── __init__.py             # Package initialization
│   ├── base_page.py            # Base page object class
│   ├── login_page.py           # Login page object
│   ├── product_catalog_page.py # Product catalog page object
│   └── ...                     # Other page objects
├── tests/                      # Test files
│   ├── __init__.py             # Package initialization
│   ├── conftest.py             # Pytest configuration
│   ├── test_user_login.py      # User login tests
│   ├── test_product_search.py  # Product search tests
│   └── ...                     # Other test files
├── utils/                      # Utility functions and helpers
│   ├── __init__.py             # Package initialization
│   ├── selector_helpers.py     # Selector utility functions
│   └── test_helpers.py         # Test utility functions
├── models/                     # Data models and schemas
│   ├── __init__.py             # Package initialization
│   └── local_ai_provider.py    # Local AI provider model
├── parsers/                    # Parsers for different file formats
│   ├── __init__.py             # Package initialization
│   └── txt_parser.py           # Text file parser
├── screenshots/                # Screenshots for debugging and reporting
├── reports/                    # Test execution reports
├── work_dir/                   # Working directory for agents
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Key Components

### 1. Tests Directory

The `tests/` directory contains all test files. Each test file should:

- Focus on a specific feature or functionality
- Use proper naming convention (`test_*.py`)
- Import page objects from the `pages/` directory
- Use fixtures from `conftest.py`
- Follow the Arrange-Act-Assert pattern

Example test file structure:

```python
"""
Test user authentication workflow
"""

import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage

class TestUserLogin:
    """Test class for user login functionality"""
    
    @pytest.mark.asyncio
    async def test_valid_login(self, browser_setup):
        """Test login with valid credentials"""
        page, browser, context, playwright = browser_setup
        
        # Arrange
        login_page = LoginPage(page)
        home_page = HomePage(page)
        
        # Act
        await login_page.navigate()
        await login_page.login("testuser", "password123")
        
        # Assert
        assert await home_page.is_logged_in(), "User should be logged in"
```

### 2. Pages Directory

The `pages/` directory contains page object models. Each page object should:

- Represent a single page or component
- Encapsulate page elements and actions
- Use proper naming convention (`*_page.py`)
- Extend the `BasePage` class
- Provide methods for page interactions

Example page object structure:

```python
"""
Login Page Object
"""

from pages.base_page import BasePage

class LoginPage(BasePage):
    """Page object for Login Page"""
    
    def __init__(self, page):
        super().__init__(page)
        self.url = "/login"
        
        # Element selectors
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "#loginBtn"
        
    async def navigate(self):
        """Navigate to Login Page"""
        await self.page.goto(self.base_url + self.url)
        await self.page.wait_for_load_state("networkidle")
    
    async def login(self, username, password):
        """Login with provided credentials"""
        await self.page.fill(self.username_input, username)
        await self.page.fill(self.password_input, password)
        await self.page.click(self.login_button)
        await self.page.wait_for_load_state("networkidle")
```

### 3. Config Directory

The `config/` directory contains configuration files. The main configuration file is `settings.py`, which defines:

- Framework settings
- Environment variables
- Test execution parameters
- Agent configurations

Example configuration structure:

```python
"""
AutoGen-Based Agentic Test Automation Framework Configuration
"""

import os
from typing import Dict, List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum

class TestFramework(str, Enum):
    """Supported test automation frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    REQUESTS = "requests"

class AutoGenTestFrameworkSettings(BaseSettings):
    """Configuration settings for the AutoGen Test Automation Framework"""
    
    # Application settings
    app_name: str = Field(default="AutoGen Test Automation Framework")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # Test execution settings
    default_framework: TestFramework = Field(default=TestFramework.PLAYWRIGHT)
    headless: bool = Field(default=True)
    timeout: int = Field(default=30000)
    
    # Base URLs for different environments
    base_urls: Dict[str, str] = Field(default={
        "dev": "https://dev.example.com",
        "staging": "https://staging.example.com",
        "prod": "https://example.com"
    })
    
    # Current environment
    environment: str = Field(default="dev")
    
    @property
    def base_url(self) -> str:
        """Get base URL for current environment"""
        return self.base_urls.get(self.environment, self.base_urls["dev"])
```

## Best Practices

1. **Separation of Concerns**
   - Tests should focus on test logic
   - Page objects should encapsulate page interactions
   - Configuration should be centralized

2. **Naming Conventions**
   - Test files: `test_*.py`
   - Page objects: `*_page.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

3. **Import Structure**
   - Use relative imports within packages
   - Use absolute imports between packages
   - Avoid circular imports

4. **File Organization**
   - Group related tests in the same file
   - Group related page objects in the same file
   - Keep files focused and not too large

5. **Documentation**
   - Include docstrings for all classes and methods
   - Document the purpose of each test
   - Document the structure of page objects

## Migration Guide

To migrate from the current structure to the new structure:

1. Move test files from `work_dir/EnhancedTestCreationAgent/` to `tests/`
2. Move page object files from `work_dir/EnhancedTestCreationAgent/` to `pages/`
3. Fix import paths in all files
4. Update file names to follow naming conventions
5. Create base classes for tests and page objects
6. Update the test creation agent to generate files in the correct locations

## Conclusion

Following this project structure will improve maintainability, readability, and scalability of the AutoGen AI Test Automation Framework. It aligns with industry best practices and provides a clear separation of concerns between different components of the framework.

