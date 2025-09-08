# Multi-Agent Workflow Guide

This guide explains how to use the multi-agent workflow to generate and execute tests for web applications.

## Overview

The multi-agent workflow uses six specialized agents to automate the entire test creation and execution process:

1. **Planning Agent**: Creates a test plan based on the application requirements
2. **Discovery Agent**: Discovers elements on web pages using real browser automation
3. **Test Creation Agent**: Generates test code based on the test plan and discovery results
4. **Review Agent**: Reviews and improves the generated tests
5. **Execution Agent**: Executes the tests and collects results
6. **Reporting Agent**: Generates reports from test results

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.6 or higher
- Playwright
- pytest and pytest-asyncio
- AutoGen library

You can install these dependencies with:

```bash
pip install pytest pytest-asyncio playwright pyautogen
python -m playwright install chromium
```

## Running the Multi-Agent Workflow

To run the complete multi-agent workflow, use the provided script:

```bash
./run_multi_agent_workflow.sh --url "https://example.com" --name "Example"
```

This script will:

1. Create a virtual environment if it doesn't exist
2. Install required packages
3. Run the multi-agent workflow with the specified URL and name
4. Generate a complete test suite for the application

## Understanding the Workflow

The workflow follows these steps:

1. **Planning**: The Planning Agent analyzes the application and creates a test plan
2. **Discovery**: The Discovery Agent explores the application and discovers elements
3. **Test Creation**: The Test Creation Agent generates test code based on the plan and discovery results
4. **Review**: The Review Agent reviews and improves the generated tests
5. **Execution**: The Execution Agent runs the tests and collects results
6. **Reporting**: The Reporting Agent generates a report from the test results

## Workflow Results

After the workflow completes, you'll find the following files:

- **Test Plan**: `work_dir/test_plan_*.json`
- **Discovery Results**: `work_dir/discovery_results_*.json`
- **Test Creation Results**: `work_dir/test_creation_results_*.json`
- **Review Results**: `work_dir/review_results_*.json`
- **Execution Results**: `work_dir/execution_results_*.json`
- **Report**: `reports/test_report_*.json`

## Customizing the Workflow

You can customize the workflow by modifying the agents or the orchestrator:

- **Agents**: Modify the agent implementations in the `agents/` directory
- **Orchestrator**: Modify the orchestrator in `orchestrator/simple_orchestrator.py`

## Troubleshooting

If you encounter issues:

1. **Agent Failures**: Check the logs for specific agent errors
2. **Browser Issues**: Ensure Playwright is installed correctly
3. **Import Errors**: Verify all dependencies are installed

## Next Steps

After running the workflow:

1. **Review the Generated Tests**: Check the quality of the generated tests
2. **Customize the Tests**: Modify the tests to fit your specific needs
3. **Integrate with CI/CD**: Add the tests to your CI/CD pipeline

## Advanced Usage

For advanced usage:

1. **Custom Test Plans**: Create custom test plans for specific scenarios
2. **Multiple Applications**: Run the workflow for multiple applications
3. **Parallel Execution**: Execute tests in parallel for faster results

