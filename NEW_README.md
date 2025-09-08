# AutoGen AI Test Automation Framework

This project is an AI-powered test automation framework that uses AutoGen agents to automate the entire test automation lifecycle. The framework enables teams to "hire" AI QA agents that can automatically generate, execute, and maintain test automation without manual intervention.

## Features

- **Real Browser Discovery**: Uses Playwright to analyze live web applications and discover real DOM elements.
- **Zero-Touch Test Generation**: Generates tests that work immediately without any manual selector updates.
- **Proper Project Structure**: Follows industry best practices with separate directories for tests, page objects, and configuration.
- **Multi-Framework Support**: Designed to be extensible and support multiple test automation frameworks (Playwright, Selenium).
- **Page Object Model (POM)**: Implemented with base classes for reusability and scalability.
- **Centralized Configuration**: Easy management of framework settings and test execution parameters.

## Getting Started

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd autogen-ai-test-automation
    ```

2.  **Install dependencies:**

    ```bash
    poetry install
    ```

3.  **Install Playwright browsers:**

    ```bash
    poetry run playwright install
    ```

### Running Tests

To run the example tests, use the following command:

```bash
poetry run pytest tests/
```

To run a specific test file:

```bash
poetry run pytest tests/test_real_application.py
```

## Project Structure

The project follows a clean and maintainable structure:

```
autogen-ai-test-automation/
├── agents/                     # Agent implementations
├── config/                     # Configuration files
├── orchestrator/               # Orchestration components
├── pages/                      # Page object models
├── tests/                      # Test files
├── utils/                      # Utility functions and helpers
├── models/                     # Data models and schemas
├── screenshots/                # Screenshots for debugging and reporting
├── reports/                    # Test execution reports
├── work_dir/                   # Working directory for agents
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

For more details, see `PROJECT_STRUCTURE.md`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.md License. See the `LICENSE` file for details.


