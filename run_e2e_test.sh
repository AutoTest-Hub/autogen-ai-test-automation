#!/bin/bash

# End-to-End Test Script for AutoGen AI Test Automation Framework
# This script runs the entire workflow from discovery to test execution

set -e  # Exit on error

# Create necessary directories
mkdir -p screenshots work_dir

# Step 1: Run the real browser discovery agent
echo "Step 1: Running real browser discovery agent..."
python test_real_browser_discovery.py

# Step 2: Find the latest discovery results
LATEST_RESULTS=$(find work_dir/ -name "discovery_results_*.json" | sort -r | head -n 1)

if [ -z "$LATEST_RESULTS" ]; then
    echo "Error: No discovery results found."
    exit 1
fi

echo "Found discovery results: $LATEST_RESULTS"

# Step 3: Generate tests using the Jinja2-based generator
echo "Step 3: Generating tests from discovery results..."
python dynamic_test_generator_jinja.py --discovery-results "$LATEST_RESULTS"

# Step 4: Install required packages if not already installed
echo "Step 4: Installing required packages..."
pip install pytest pytest-asyncio playwright jinja2 --quiet

# Step 5: Install Playwright browsers if not already installed
echo "Step 5: Installing Playwright browsers..."
if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()" &>/dev/null; then
    python -m playwright install chromium
fi

# Step 6: Run the generated tests
echo "Step 6: Running the generated tests..."
python -m pytest tests/test_*.py -v

echo "End-to-end test completed successfully!"

