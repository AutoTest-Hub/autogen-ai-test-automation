#!/bin/bash

# End-to-End Test Script for AutoGen AI Test Automation Framework
# This script runs the entire workflow from discovery to test execution

set -e  # Exit on error

# Create necessary directories
mkdir -p screenshots work_dir

# Step 1: Install required packages
echo "Step 1: Installing required packages..."
pip install pytest pytest-asyncio playwright --quiet

# Step 2: Install Playwright browsers if not already installed
echo "Step 2: Installing Playwright browsers..."
python -m playwright install chromium --with-deps

# Step 3: Create a simple working test
echo "Step 3: Creating a simple working test..."
python create_simple_test.py

# Step 4: Run the test
echo "Step 4: Running the test..."
python -m pytest tests/test_login.py -v

echo "End-to-end test completed successfully!"

