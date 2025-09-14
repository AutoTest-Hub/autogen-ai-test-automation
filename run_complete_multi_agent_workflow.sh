#!/bin/bash
# Run Complete Multi-Agent Workflow
# This script runs the complete multi-agent workflow for test automation.

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
pip install pytest playwright pytest-asyncio

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Run workflow
echo "Running complete multi-agent workflow for $NAME at $URL..."

if [ "$HEADLESS" = true ]; then
  python complete_multi_agent_workflow.py --url "$URL" --name "$NAME" --headless
else
  python complete_multi_agent_workflow.py --url "$URL" --name "$NAME" --no-headless
fi

# Check if workflow succeeded
if [ $? -eq 0 ]; then
  echo "Workflow completed successfully!"
  
  # Open HTML report if it exists
  REPORT=$(find reports -name "report_*.html" | sort -r | head -n 1)
  if [ -n "$REPORT" ]; then
    echo "HTML report: $REPORT"
    
    # Try to open the report in a browser
    if command -v open &> /dev/null; then
      open "$REPORT"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "$REPORT"
    else
      echo "To view the report, open $REPORT in your browser"
    fi
  fi
else
  echo "Workflow failed!"
fi

