"""
Pytest Configuration
================
Configuration for pytest.
"""

import pytest

def pytest_addoption(parser):
    """Add command line options to pytest"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=True,
        help="Run tests in headless mode (default)"
    )
    parser.addoption(
        "--no-headless",
        action="store_true",
        default=False,
        help="Run tests in headed mode (with browser UI)"
    )

@pytest.fixture(scope="session")
def headless(request):
    """
    Fixture to determine if tests should run in headless mode
    
    Returns:
        bool: True if headless, False if headed
    """
    no_headless = request.config.getoption("--no-headless")
    if no_headless:
        return False
    return True

