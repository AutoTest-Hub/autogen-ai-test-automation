"""
Test Data Configuration for AutoGen Test Automation Framework

This module provides externalized test data configuration to avoid
hardcoded credentials and test values in the agent code.

Test data can be overridden via environment variables or configuration files.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import json


@dataclass
class TestCredentials:
    """Test credentials configuration"""
    username: str = ""
    password: str = ""

    @classmethod
    def from_env(cls, prefix: str = "TEST") -> "TestCredentials":
        """Load credentials from environment variables"""
        return cls(
            username=os.getenv(f"{prefix}_USERNAME", ""),
            password=os.getenv(f"{prefix}_PASSWORD", "")
        )


@dataclass
class TestDataConfig:
    """
    Test data configuration.

    All test data should be loaded from this configuration rather than
    hardcoded in agent code.
    """
    # Default test credentials (should be overridden in config file or env vars)
    default_credentials: TestCredentials = field(default_factory=TestCredentials)

    # Named credential sets for different test scenarios
    credential_sets: Dict[str, TestCredentials] = field(default_factory=dict)

    # Test data values
    test_values: Dict[str, Any] = field(default_factory=dict)

    # Placeholder patterns for test generation
    placeholders: Dict[str, str] = field(default_factory=lambda: {
        "username": "${TEST_USERNAME}",
        "password": "${TEST_PASSWORD}",
        "email": "${TEST_EMAIL}",
        "api_key": "${TEST_API_KEY}"
    })

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "TestDataConfig":
        """
        Load test data configuration from file or environment.

        Priority:
        1. Explicit config file path
        2. test_data.yaml in current directory
        3. test_data.json in current directory
        4. Environment variables
        5. Default empty values
        """
        config = cls()

        # Try to find config file
        if config_path and Path(config_path).exists():
            config = cls._load_from_file(config_path)
        elif Path("test_data.yaml").exists():
            config = cls._load_from_file("test_data.yaml")
        elif Path("test_data.json").exists():
            config = cls._load_from_file("test_data.json")
        elif Path("config/test_data.yaml").exists():
            config = cls._load_from_file("config/test_data.yaml")

        # Override with environment variables
        config._load_from_env()

        return config

    @classmethod
    def _load_from_file(cls, path: str) -> "TestDataConfig":
        """Load configuration from YAML or JSON file"""
        config = cls()

        try:
            with open(path, 'r') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    data = yaml.safe_load(f) or {}
                else:
                    data = json.load(f)

            # Load default credentials
            if "default_credentials" in data:
                creds = data["default_credentials"]
                config.default_credentials = TestCredentials(
                    username=creds.get("username", ""),
                    password=creds.get("password", "")
                )

            # Load credential sets
            if "credential_sets" in data:
                for name, creds in data["credential_sets"].items():
                    config.credential_sets[name] = TestCredentials(
                        username=creds.get("username", ""),
                        password=creds.get("password", "")
                    )

            # Load test values
            if "test_values" in data:
                config.test_values = data["test_values"]

            # Load placeholders
            if "placeholders" in data:
                config.placeholders.update(data["placeholders"])

        except Exception as e:
            print(f"Warning: Could not load test data config from {path}: {e}")

        return config

    def _load_from_env(self):
        """Override configuration with environment variables"""
        # Load default credentials from env
        env_username = os.getenv("TEST_USERNAME")
        env_password = os.getenv("TEST_PASSWORD")

        if env_username:
            self.default_credentials.username = env_username
        if env_password:
            self.default_credentials.password = env_password

    def get_credentials(self, credential_set: Optional[str] = None) -> TestCredentials:
        """Get credentials for a specific set or default"""
        if credential_set and credential_set in self.credential_sets:
            return self.credential_sets[credential_set]
        return self.default_credentials

    def get_placeholder(self, key: str) -> str:
        """Get placeholder pattern for a test value"""
        return self.placeholders.get(key, f"${{{key.upper()}}}")

    def get_test_value(self, key: str, default: Any = None) -> Any:
        """Get a test value by key"""
        return self.test_values.get(key, default)

    def generate_test_code_with_placeholders(self,
                                             username_var: str = "username",
                                             password_var: str = "password") -> Dict[str, str]:
        """
        Generate test code snippets that use environment variables
        instead of hardcoded values.
        """
        return {
            "env_setup": f'''
import os

# Load test credentials from environment variables
{username_var} = os.getenv("TEST_USERNAME", "")
{password_var} = os.getenv("TEST_PASSWORD", "")

# Validate credentials are set
if not {username_var} or not {password_var}:
    raise ValueError("TEST_USERNAME and TEST_PASSWORD environment variables must be set")
''',
            "fixture": f'''
@pytest.fixture
def test_credentials():
    """Fixture to provide test credentials"""
    username = os.getenv("TEST_USERNAME", "")
    password = os.getenv("TEST_PASSWORD", "")
    if not username or not password:
        pytest.skip("TEST_USERNAME and TEST_PASSWORD must be set")
    return {{"username": username, "password": password}}
''',
            "login_call": f'''
# Use credentials from environment/fixture
page_obj.login({username_var}, {password_var})
''',
            "fill_username": f'''
page_obj.fill_username({username_var})
''',
            "fill_password": f'''
page_obj.fill_password({password_var})
'''
        }


# Global test data configuration instance
test_data_config = TestDataConfig.load()


def get_test_credentials(credential_set: Optional[str] = None) -> TestCredentials:
    """Convenience function to get test credentials"""
    return test_data_config.get_credentials(credential_set)


def get_test_placeholder(key: str) -> str:
    """Convenience function to get a placeholder"""
    return test_data_config.get_placeholder(key)


def get_test_value(key: str, default: Any = None) -> Any:
    """Convenience function to get a test value"""
    return test_data_config.get_test_value(key, default)
