#!/bin/bash
# Run the proper multi-agent workflow

# Parse command line arguments
URL=""
NAME=""
HEADLESS=true

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
    --no-headless)
      HEADLESS=false
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check required arguments
if [ -z "$URL" ]; then
  echo "Error: URL is required"
  echo "Usage: $0 --url <url> --name <name> [--no-headless]"
  exit 1
fi

if [ -z "$NAME" ]; then
  echo "Error: Name is required"
  echo "Usage: $0 --url <url> --name <name> [--no-headless]"
  exit 1
fi

# Install required packages
echo "Installing required packages..."
pip install pytest pytest-asyncio playwright pyautogen

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Run the workflow
echo "Running proper multi-agent workflow for $NAME at $URL..."
if [ "$HEADLESS" = true ]; then
  python proper_multi_agent_workflow.py --url "$URL" --name "$NAME" --headless
else
  python proper_multi_agent_workflow.py --url "$URL" --name "$NAME" --no-headless
fi

# Check if the workflow was successful
if [ $? -eq 0 ]; then
  echo "Workflow completed successfully!"
  
  # Open the HTML report if it exists
  REPORT=$(find reports -name "report_*.html" | sort -r | head -n 1)
  if [ -n "$REPORT" ]; then
    echo "Opening HTML report: $REPORT"
    if command -v xdg-open &> /dev/null; then
      xdg-open "$REPORT"
    elif command -v open &> /dev/null; then
      open "$REPORT"
    else
      echo "Could not open HTML report automatically. Please open it manually."
    fi
  fi
else
  echo "Workflow failed!"
fi

