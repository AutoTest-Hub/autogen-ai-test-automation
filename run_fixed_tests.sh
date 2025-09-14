#!/bin/bash
# Run the fixed tests

# Generate the tests
echo "Generating tests..."
python fix_test_creation_agent_simple.py

# Run the tests with headless mode
echo "Running tests in headless mode..."
python -m pytest tests/test_orangehrm_login.py::TestLogin::test_valid_login -v

# Run with no-headless mode if specified
if [ "$1" == "--no-headless" ]; then
    echo "Running tests in non-headless mode..."
    PLAYWRIGHT_HEADLESS=false python -m pytest tests/test_orangehrm_login.py::TestLogin::test_valid_login -v
fi

echo "Tests completed!"

