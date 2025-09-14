# Complete Multi-Agent Workflow Guide

This guide explains how to use the complete multi-agent workflow to generate, execute, and maintain test automation without manual intervention.

## Overview

The complete multi-agent workflow uses six specialized agents to automate the entire test automation process:

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

1. Clone the repository:
   ```bash
   git clone https://github.com/AutoTest-Hub/autogen-ai-test-automation.git
   cd autogen-ai-test-automation
   ```

2. Install required packages:
   ```bash
   pip install pytest playwright pytest-asyncio
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Usage

### Running the Complete Workflow

To run the complete multi-agent workflow, use the provided script:

```bash
./run_complete_multi_agent_workflow.sh --url "https://example.com" --name "Example"
```

Options:
- `--url` or `-u`: URL of the website to test (required)
- `--name` or `-n`: Name of the website (required)
- `--no-headless`: Run browser with UI visible (optional, default is headless)

Example for OrangeHRM:
```bash
./run_complete_multi_agent_workflow.sh --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" --name "OrangeHRM"
```

### Workflow Steps

The workflow follows these steps:

1. **Planning**: The Planning Agent creates a test plan based on the website name and URL.
2. **Discovery**: The Discovery Agent launches a real browser, navigates to the website, and discovers elements on the page.
3. **Test Creation**: The Test Creation Agent generates tests based on the test plan and discovery results.
4. **Review**: The Review Agent reviews and improves the generated tests.
5. **Execution**: The Execution Agent runs the tests and collects results.
6. **Reporting**: The Reporting Agent generates HTML and text reports from the test results.

### Output

The workflow generates the following output:

- **Test Files**: Located in the `tests/` directory
- **Page Objects**: Located in the `pages/` directory
- **Configuration**: Located in the `config/` directory
- **Reports**: Located in the `reports/` directory
- **Screenshots**: Located in the `screenshots/` directory
- **Work Files**: Located in the `work_dir/` directory

## Running Tests Manually

After generating tests, you can run them manually using pytest:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_orangehrm_login.py -v

# Run tests with browser UI visible
python -m pytest tests/ -v --no-headless
```

## Customizing the Workflow

You can customize the workflow by modifying the agents in the `complete_multi_agent_workflow.py` file:

- **Planning Agent**: Modify the `create_test_plan` method to change the test plan
- **Discovery Agent**: Modify the `discover_elements` method to change how elements are discovered
- **Test Creation Agent**: Modify the `create_tests` method to change how tests are generated
- **Review Agent**: Modify the `review_tests` method to change how tests are reviewed
- **Execution Agent**: Modify the `execute_tests` method to change how tests are executed
- **Reporting Agent**: Modify the `generate_report` method to change how reports are generated

## Troubleshooting

### Browser Launch Issues

If you encounter issues with browser launch:

```bash
# Install Playwright browsers
playwright install chromium

# Check if browsers are installed
playwright install --help
```

### Test Execution Issues

If tests fail to execute:

```bash
# Check if pytest is installed
python -m pytest --version

# Run tests with verbose output
python -m pytest tests/ -v

# Run tests with debug output
python -m pytest tests/ -v --log-cli-level=DEBUG
```

### Path Issues

If you encounter path issues:

```bash
# Check if directories exist
ls -la tests/ pages/ config/ reports/ screenshots/ work_dir/

# Create missing directories
mkdir -p tests pages config reports screenshots work_dir
```

## Advanced Usage

### Running Individual Agents

You can run individual agents by importing them from the `complete_multi_agent_workflow.py` file:

```python
from complete_multi_agent_workflow import DiscoveryAgent

# Create discovery agent
discovery_agent = DiscoveryAgent()

# Discover elements
discovery_results = discovery_agent.discover_elements("https://example.com")
```

### Extending the Workflow

You can extend the workflow by adding new agents or modifying existing ones:

```python
class CustomDiscoveryAgent(DiscoveryAgent):
    def discover_elements(self, url, headless=True):
        # Custom implementation
        pass
```

## Conclusion

The complete multi-agent workflow provides a fully automated solution for test automation. By using six specialized agents, it can generate, execute, and maintain tests without manual intervention, achieving the vision of "hiring" AI QA agents.

