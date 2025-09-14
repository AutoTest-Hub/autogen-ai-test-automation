# Testing New Websites Guide

This guide provides step-by-step instructions for testing new websites using the AutoGen AI Test Automation Framework.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.6 or higher
- Playwright
- pytest and pytest-asyncio
- AutoGen library (if using the full agent workflow)

You can install these dependencies with:

```bash
pip install pytest pytest-asyncio playwright pyautogen
python -m playwright install chromium
```

## Option 1: Quick Test for Any Website

Use the `test_new_website.py` script to quickly generate and run tests for any website:

```bash
python test_new_website.py --url "https://example.com" --name "Example"
```

This will:
1. Create discovery results for the website
2. Generate page objects and test files
3. Run the tests automatically

## Option 2: Testing Advantage Online Shopping

We've created a specific script for testing the Advantage Online Shopping website:

```bash
python test_advantage_shopping.py
```

This will:
1. Create discovery results for Advantage Online Shopping
2. Generate page objects and test files
3. Create a custom end-to-end test for searching and adding products to cart
4. Run the tests automatically

## Option 3: Full Agent Workflow

For the complete AI agent workflow experience:

1. **Run the Real Browser Discovery Agent**:
   ```bash
   python test_real_browser_discovery.py --url "https://example.com"
   ```

2. **Generate Tests from Discovery Results**:
   ```bash
   python simple_test_generator.py
   ```
   (The script will automatically find the latest discovery results)

3. **Run the Generated Tests**:
   ```bash
   python -m pytest tests/test_*.py -v
   ```

## Customizing Tests

You can customize the generated tests by:

1. **Modifying Page Objects**:
   - Edit files in the `pages/` directory
   - Add new methods for specific interactions
   - Update selectors if needed

2. **Enhancing Test Files**:
   - Edit files in the `tests/` directory
   - Add more test cases
   - Implement more assertions

3. **Creating Custom Workflows**:
   - Create new test files that combine multiple page objects
   - Implement end-to-end scenarios

## Troubleshooting

If you encounter issues:

1. **Selector Problems**:
   - Use browser developer tools to verify selectors
   - Update selectors in page objects if they've changed

2. **Timing Issues**:
   - Add `await page.wait_for_load_state("networkidle")` after navigation
   - Add `await page.wait_for_timeout(1000)` for animations

3. **Browser Compatibility**:
   - Try different browsers: `playwright.firefox` or `playwright.webkit`
   - Update browser launch options for specific requirements

## Advanced Usage

For advanced usage:

1. **Headful Mode**:
   - Modify browser launch options to `headless=False`
   - Add `slow_mo=100` to slow down operations for debugging

2. **Recording Videos**:
   - Add video recording options to context creation
   - Use for debugging or documentation

3. **Parallel Testing**:
   - Use pytest-xdist to run tests in parallel
   - Create independent tests that don't share state

## Next Steps

After successfully testing your website:

1. **Integrate with CI/CD**:
   - Add GitHub Actions workflow
   - Schedule regular test runs

2. **Expand Test Coverage**:
   - Add more test scenarios
   - Test edge cases and error conditions

3. **Implement Reporting**:
   - Add HTML reports with pytest-html
   - Integrate with test management systems

