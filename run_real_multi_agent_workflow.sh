#!/bin/bash
# Run the real multi-agent workflow

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
pip install pytest pytest-asyncio playwright pyautogen pydantic-settings

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Run the real multi-agent workflow
echo "Running real multi-agent workflow for $NAME at $URL..."
python real_multi_agent_workflow.py --url "$URL" --name "$NAME"

# Check if the workflow completed successfully
if [ $? -eq 0 ]; then
  echo "Workflow completed successfully!"
  echo "Generated tests are in the tests/ directory"
  echo "Generated page objects are in the pages/ directory"
  echo "Reports are in the reports/ directory"
else
  echo "Workflow failed!"
fi

