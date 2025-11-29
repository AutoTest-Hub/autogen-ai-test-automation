#!/bin/bash
# Run the proper multi-agent workflow

# Parse command line arguments
URL=""
NAME=""
HEADLESS=true
REQUIREMENTS_FILE=""

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
    --requirements|-r)
      REQUIREMENTS_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 --url <url> --name <name> [--no-headless] [--requirements <file>]"
      exit 1
      ;;
  esac
done

# Check required arguments
if [ -z "$URL" ]; then
  echo "Error: URL is required"
  echo "Usage: $0 --url <url> --name <name> [--no-headless] [--requirements <file>]"
  exit 1
fi

if [ -z "$NAME" ]; then
  echo "Error: Name is required"
  echo "Usage: $0 --url <url> --name <name> [--no-headless] [--requirements <file>]"
  exit 1
fi

# Auto-detect requirements file if not specified
if [ -z "$REQUIREMENTS_FILE" ]; then
  echo "Auto-detecting requirements file based on URL..."
  
  if [[ "$URL" == *"automationexercise"* ]]; then
    REQUIREMENTS_FILE="requirements_ecommerce.json"
    echo "Detected E-commerce application, using $REQUIREMENTS_FILE"
  elif [[ "$URL" == *"orangehrm"* ]]; then
    REQUIREMENTS_FILE="requirements_hrms.json"
    echo "Detected HRMS application, using $REQUIREMENTS_FILE"
  elif [[ "$URL" == *"testfire"* ]]; then
    REQUIREMENTS_FILE="requirements_banking.json"
    echo "Detected Banking application, using $REQUIREMENTS_FILE"
  else
    echo "Could not auto-detect application type from URL"
    echo "Available requirements files:"
    ls -1 requirements_*.json 2>/dev/null || echo "  No requirements files found"
  fi
fi

# Check if requirements file exists and copy it to active location
if [ -n "$REQUIREMENTS_FILE" ] && [ -f "$REQUIREMENTS_FILE" ]; then
  echo "Using requirements file: $REQUIREMENTS_FILE"
  # Copy to a standard location that the workflow can find
  cp "$REQUIREMENTS_FILE" "active_requirements.json"
  echo "✅ Enhanced three-tier system activated with $REQUIREMENTS_FILE"
else
  echo "⚠️  No requirements file specified or found, using basic workflow"
fi

# Install required packages
echo "Installing required packages..."
pip install pytest pytest-asyncio pytest-html pytest-json-report playwright pyautogen

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Run the workflow
echo "=================================================="
echo "🚀 Running Enhanced Three-Tier Multi-Agent Workflow"
echo "=================================================="
echo "Application: $NAME"
echo "URL: $URL"
echo "Headless: $HEADLESS"
if [ -f "active_requirements.json" ]; then
  echo "Enhanced Features: ✅ ENABLED"
  echo "Requirements Config: $(basename "$REQUIREMENTS_FILE")"
else
  echo "Enhanced Features: ⚠️  BASIC MODE"
fi
echo "=================================================="

if [ "$HEADLESS" = true ]; then
  python scripts/workflows/proper_multi_agent_workflow.py --url "$URL" --name "$NAME" --headless
else
  python scripts/workflows/proper_multi_agent_workflow.py --url "$URL" --name "$NAME" --no-headless
fi

# Check if the workflow was successful
if [ $? -eq 0 ]; then
  echo "Workflow completed successfully!"
  
  # Open the HTML report if it exists (prioritize pytest reports)
  PYTEST_REPORT=$(find work_dir/reporting_agent -name "pytest_report_*.html" | sort -r | head -n 1)
  CUSTOM_REPORT=$(find work_dir/reporting_agent -name "test_report_*.html" | sort -r | head -n 1)
  
  if [ -n "$PYTEST_REPORT" ]; then
    REPORT="$PYTEST_REPORT"
    echo "Opening Pytest HTML report: $REPORT"
  elif [ -n "$CUSTOM_REPORT" ]; then
    REPORT="$CUSTOM_REPORT"
    echo "Opening Custom HTML report: $REPORT"
  else
    echo "No HTML report found in work_dir/reporting_agent/"
    REPORT=""
  fi
  
  if [ -n "$REPORT" ]; then
    if command -v xdg-open &> /dev/null; then
      xdg-open "$REPORT"
    elif command -v open &> /dev/null; then
      open "$REPORT"
    else
      echo "Could not open HTML report automatically. Please open it manually: $REPORT"
    fi
  fi
else
  echo "Workflow failed!"
fi

