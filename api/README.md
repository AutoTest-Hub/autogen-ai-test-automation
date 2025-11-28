# API Documentation

This document provides detailed information about the REST API for the AI Test Automation SaaS Platform.

## Base URL

- **Production**: `https://api.testautomation.ai`
- **Development**: `http://localhost:8000`

## Authentication

All API endpoints require a bearer token for authentication. Obtain a token by using the `/auth/login` endpoint.

```
Authorization: Bearer <your-token>
```

## Endpoints

### Authentication

- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Authenticate and receive a token.
- `GET /auth/me`: Get information about the current user.

### Test Execution

- `POST /test/execute`: Start a new test execution.
- `GET /test/status/{id}`: Get the status of a test execution.
- `GET /test/results/{id}`: Get the results of a test execution.
- `GET /test/executions`: List all test executions.

### Requirements

- `GET /requirements/templates`: List all available requirements templates.
- `GET /requirements/template/{name}`: Get a specific requirements template.
- `POST /requirements/validate`: Validate a requirements configuration.

### Advanced AI

- `POST /ai/self-heal`: Analyze and heal a broken test.
- `POST /ai/prioritize-tests`: Prioritize a list of test files.
- `POST /ai/cross-browser-plan`: Generate a cross-browser testing plan.
- `POST /ai/predict-performance`: Predict performance bottlenecks.

## Data Models

For detailed information about the request and response models, please see the `api/models.py` file.

