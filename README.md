# AI Test Automation Framework

This is a comprehensive, AI-powered test automation framework that uses a multi-agent system to automate the entire testing lifecycle, from requirements analysis to test execution and reporting.

## Features

- **Multi-Agent System**: The framework uses a team of specialized AI agents to handle different aspects of the testing process, including planning, test creation, execution, review, and reporting.
- **Three-Tier Step Generation**: The framework uses a three-tier system to generate test steps, with a local Qwen 2.5 Coder 7B model as the primary generator, the OpenAI API as a fallback, and a template-based generator as a last resort.
- **Real Browser Integration**: The framework can interact with real browsers to execute tests and validate the functionality of web applications.
- **Comprehensive Error Handling**: The framework includes a comprehensive error handling and recovery system that can gracefully handle agent failures and other unexpected errors.
- **Production-Ready**: The framework is designed to be production-ready, with a clean architecture, comprehensive testing, and detailed documentation.

## Getting Started

To get started with the AI Test Automation Framework, you will need to:

1. **Install the dependencies**: The framework requires Python 3.11 or higher, as well as a number of other libraries. You can install all of the dependencies by running the following command:

```
pip install -r requirements.txt
```

2. **Configure the framework**: The framework can be configured by editing the `config/settings.py` file. This file allows you to specify the LLM provider, the test framework, and other settings.

3. **Run the framework**: You can run the framework by executing the `proper_multi_agent_workflow.py` file. This file will start the multi-agent system and begin the testing process.

## Usage

To use the framework, you will need to create a `requirements.json` file that specifies the application to be tested and the test cases to be executed. The framework will then use this file to generate and execute the tests.

## Contributing

Contributions to the AI Test Automation Framework are welcome. If you would like to contribute, please fork the repository and submit a pull request.

