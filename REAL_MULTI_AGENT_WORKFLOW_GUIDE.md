# Real Multi-Agent Workflow Guide

This guide explains how to use the real multi-agent workflow to generate, execute, and maintain test automation without manual intervention.

## Overview

The real multi-agent workflow uses all six agents in the AI test automation framework:

1. **Planning Agent**: Creates test plans based on requirements
2. **Discovery Agent**: Discovers elements on web pages using real browser automation
3. **Test Creation Agent**: Generates tests based on discovery results
4. **Review Agent**: Reviews and improves generated tests
5. **Execution Agent**: Executes tests and collects results
6. **Reporting Agent**: Generates reports from test results

## Prerequisites

- Python 3.6+
- Playwright
- PyAutoGen
- Pytest and pytest-asyncio

## Running the Workflow

To run the complete multi-agent workflow, use the provided script:

```bash
./run_real_multi_agent_workflow.sh --url "https://example.com" --name "Example"
```

For the OrangeHRM demo site:

```bash
./run_real_multi_agent_workflow.sh --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" --name "OrangeHRM"
```

## What Happens During the Workflow

1. **Planning Phase**:
   - The Planning Agent analyzes the application and creates a test plan
   - The test plan includes test scenarios, priorities, and strategies

2. **Discovery Phase**:
   - The Discovery Agent launches a real browser
   - It navigates to the application URL
   - It discovers elements on the page (buttons, inputs, links)
   - It generates selectors for the discovered elements

3. **Test Creation Phase**:
   - The Test Creation Agent uses the test plan and discovery results
   - It generates test files with real selectors
   - It creates page objects for discovered pages
   - It organizes files in the proper project structure

4. **Review Phase**:
   - The Review Agent analyzes the generated tests
   - It suggests improvements and fixes issues
   - It ensures tests follow best practices

5. **Execution Phase**:
   - The Execution Agent runs the generated tests
   - It captures screenshots and logs
   - It collects test results

6. **Reporting Phase**:
   - The Reporting Agent generates a report from test results
   - It includes test status, screenshots, and metrics

## Output Files

The workflow generates the following files:

- **Test Files**: `tests/test_*.py`
- **Page Objects**: `pages/*_page.py`
- **Reports**: `reports/test_report_*.html`
- **Screenshots**: `screenshots/*.png`
- **Work Artifacts**: `work_dir/*`

## Customizing the Workflow

You can customize the workflow by modifying the `real_multi_agent_workflow.py` file:

- Change the browser type (Chromium, Firefox, WebKit)
- Modify the test generation strategy
- Adjust the reporting format
- Add custom test scenarios

## Troubleshooting

If you encounter issues:

1. Check the logs in the console output
2. Look for error messages in the work directory
3. Verify that Playwright browsers are installed
4. Ensure the application URL is accessible

## Advanced Usage

For advanced usage:

```bash
python real_multi_agent_workflow.py --url "https://example.com" --name "Example" --headless false --framework selenium
```

This allows you to:
- Run tests in headed mode (with browser UI)
- Use a different testing framework (Selenium instead of Playwright)
- Customize other parameters

## Next Steps

After running the workflow:

1. Review the generated tests in the `tests/` directory
2. Examine the page objects in the `pages/` directory
3. Check the test reports in the `reports/` directory
4. Run individual tests with pytest:
   ```bash
   python -m pytest tests/test_specific_test.py -v
   ```

The framework now provides a true autonomous test generation experience, allowing you to "hire" AI QA agents that can automatically generate, execute, and maintain test automation without manual intervention.

