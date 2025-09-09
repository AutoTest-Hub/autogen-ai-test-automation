# Proper Multi-Agent Workflow Guide

This guide explains how to use the proper multi-agent workflow to generate, execute, and maintain test automation without manual intervention.

## Overview

The proper multi-agent workflow uses all six agents in the AI test automation framework:

1. **Planning Agent**: Creates test plans based on requirements
2. **Discovery Agent**: Discovers elements on web pages using real browser automation
3. **Test Creation Agent**: Generates tests based on discovery results
4. **Review Agent**: Reviews and improves generated tests
5. **Execution Agent**: Executes tests and collects results
6. **Reporting Agent**: Generates reports from test results

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- Internet connection

## Installation

The workflow script will automatically install the required packages, but you can also install them manually:

```bash
pip install pytest pytest-asyncio playwright pyautogen
playwright install chromium
```

## Usage

### Basic Usage

To run the workflow for a website:

```bash
./run_proper_multi_agent_workflow.sh --url "https://example.com" --name "Example"
```

This will:
1. Create a test plan
2. Discover elements on the website
3. Generate tests
4. Review and improve the tests
5. Execute the tests
6. Generate a report

### Options

- `--url` or `-u`: URL of the website to test (required)
- `--name` or `-n`: Name of the website (required)
- `--no-headless`: Run the browser with UI visible (default: headless)

### Example

```bash
# Run with headless browser (default)
./run_proper_multi_agent_workflow.sh --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" --name "OrangeHRM"

# Run with browser UI visible
./run_proper_multi_agent_workflow.sh --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" --name "OrangeHRM" --no-headless
```

## Workflow Steps

### 1. Create Test Plan

The Planning Agent analyzes the website and creates a test plan with test cases, priorities, and steps.

### 2. Discover Elements

The Discovery Agent launches a real browser and discovers elements on the website, including:
- Input fields
- Buttons
- Links
- Text elements
- Navigation elements

### 3. Create Tests

The Test Creation Agent generates tests based on the test plan and discovery results, including:
- Page objects
- Test files
- Configuration files

### 4. Review Tests

The Review Agent reviews the generated tests and suggests improvements, including:
- Better error handling
- More detailed assertions
- Better comments
- Better logging

### 5. Execute Tests

The Execution Agent executes the tests and collects results, including:
- Test execution status
- Test execution logs
- Screenshots

### 6. Generate Report

The Reporting Agent generates a report from the test results, including:
- HTML report
- Text report
- Summary
- Detailed results

## Output Files

The workflow generates the following files:

- **Test Plan**: `work_dir/PlanningAgent/test_plan_*.json`
- **Discovery Results**: `work_dir/DiscoveryAgent/discovery_results_*.json`
- **Created Tests**: `tests/test_*.py`
- **Page Objects**: `pages/*.py`
- **Screenshots**: `screenshots/*.png`
- **Reports**: `reports/report_*.html` and `reports/report_*.txt`

## Troubleshooting

### Browser Issues

If you encounter browser-related issues:

- Make sure Playwright is installed: `playwright install chromium`
- Try running with `--no-headless` to see what's happening
- Check the screenshots in the `screenshots` directory

### Test Failures

If tests fail:

- Check the HTML report for details
- Look at the screenshots to see what happened
- Check the test files for issues

### Agent Failures

If an agent fails:

- The workflow will create default outputs and continue
- Check the logs for error messages
- Try running the workflow again

## Advanced Usage

### Using Different Browsers

The workflow uses Chromium by default, but you can modify the code to use other browsers:

```python
# In proper_multi_agent_workflow.py
browser = await playwright.firefox.launch(headless=headless)  # Use Firefox
browser = await playwright.webkit.launch(headless=headless)   # Use WebKit
```

### Custom Test Data

You can modify the default test data in the `_create_default_test_plan` and `_create_default_tests` methods.

### Integration with CI/CD

You can integrate the workflow with CI/CD systems by running it in headless mode and capturing the reports.

## Conclusion

The proper multi-agent workflow provides a complete solution for generating, executing, and maintaining test automation without manual intervention. It uses all six agents in the AI test automation framework to create a seamless workflow that can be used for any website.

