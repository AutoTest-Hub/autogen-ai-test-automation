#!/bin/bash
# Run the complete tests

# Default values
URL="https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
NAME="OrangeHRM"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --url|-u)
      URL="$2"
      shift 2
      ;;
    --name|-n)
      NAME="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Install required packages
echo "Installing required packages..."
pip install pytest pytest-asyncio playwright

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Generate tests
echo "Generating tests for $NAME at $URL..."
python generate_complete_tests.py --url "$URL" --name "$NAME"

# Run tests
echo "Running tests..."
python -m pytest tests/test_*.py -v

# Check if the tests passed
if [ $? -eq 0 ]; then
  echo "Tests passed!"
else
  echo "Tests failed!"
fi

