#!/bin/bash
# Run the multi-agent workflow

# Default values
URL="https://the-internet.herokuapp.com/login"
NAME="The Internet"

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
      echo "Usage: $0 [--url URL] [--name NAME]"
      exit 1
      ;;
  esac
done

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install pytest pytest-asyncio playwright pyautogen pydantic-settings
python -m playwright install chromium

# Run the multi-agent workflow
echo "Running multi-agent workflow for $NAME at $URL..."
python orchestrator/simple_orchestrator.py --url "$URL" --name "$NAME"

# Deactivate virtual environment
deactivate

echo "Workflow completed!"

