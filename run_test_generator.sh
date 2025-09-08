#!/bin/bash

# Find the most recent discovery results file
LATEST_RESULTS=$(find work_dir/ -name "discovery_results_*.json" | sort -r | head -n 1)

if [ -z "$LATEST_RESULTS" ]; then
    echo "No discovery results found. Running discovery agent first..."
    python test_real_browser_discovery.py
    LATEST_RESULTS=$(find work_dir/ -name "discovery_results_*.json" | sort -r | head -n 1)
fi

if [ -z "$LATEST_RESULTS" ]; then
    echo "Error: Still no discovery results found after running discovery agent."
    exit 1
fi

echo "Using discovery results: $LATEST_RESULTS"
python dynamic_test_generator_compatible.py --discovery-results "$LATEST_RESULTS"

