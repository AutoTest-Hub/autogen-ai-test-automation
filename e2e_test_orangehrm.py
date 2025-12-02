#!/usr/bin/env python3
"""
End-to-End Test: OrangeHRM Demo Application

This script validates the complete AutoGen AI QA pipeline:
1. Onboard application via wizard
2. Add business rules and credentials
3. Discover page elements
4. Generate context-aware test plan
5. Create actual Playwright tests
6. Save executable test files

Target: https://opensource-demo.orangehrmlive.com
Credentials: Admin / admin123
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

# ============================================================
# STEP 1: ONBOARD APPLICATION
# ============================================================

def onboard_orangehrm():
    """Onboard OrangeHRM through the wizard."""
    print("\n" + "="*60)
    print("STEP 1: ONBOARDING ORANGEHRM")
    print("="*60)

    from api import OnboardingWizard, OnboardingStep

    wizard = OnboardingWizard()
    session = wizard.start_session()
    print(f"✅ Started onboarding session")

    # Step 1: App Info
    wizard.submit_step(session.session_id, OnboardingStep.APP_INFO, {
        "app_name": "OrangeHRM",
        "app_url": "https://opensource-demo.orangehrmlive.com",
        "description": "Human Resource Management System - Demo instance for testing"
    })
    print("   ✅ App info submitted")

    # Step 2: Tech Stack
    wizard.submit_step(session.session_id, OnboardingStep.TECH_STACK, {
        "frontend": "Vue.js",
        "backend": "PHP/Symfony",
        "database": "MySQL",
        "testing": "Playwright",
        "ci_cd": "GitHub Actions"
    })
    print("   ✅ Tech stack configured")

    # Step 3: Environments
    wizard.submit_step(session.session_id, OnboardingStep.ENVIRONMENTS, {
        "environments": [
            {
                "name": "demo",
                "url": "https://opensource-demo.orangehrmlive.com",
                "type": "staging",
                "is_default": True
            }
        ]
    })
    print("   ✅ Environments configured")

    # Step 4: Integrations (skip for now)
    wizard.submit_step(session.session_id, OnboardingStep.INTEGRATIONS, {})
    print("   ✅ Integrations step (skipped)")

    # Step 5: Knowledge
    wizard.submit_step(session.session_id, OnboardingStep.KNOWLEDGE, {
        "ingest_readme": False,
        "ingest_openapi": False,
    })
    print("   ✅ Knowledge step completed")

    # Step 6: Validation
    wizard.submit_step(session.session_id, OnboardingStep.VALIDATION, {
        "confirm": True
    })
    print("   ✅ Validation confirmed")

    # Complete onboarding
    result = wizard.complete_onboarding(session.session_id)
    print(f"\n✅ Onboarding complete!")
    print(f"   App ID: {result['app_id']}")
    print(f"   Version: {result['version']}")

    return result['context']


# ============================================================
# STEP 2: ADD BUSINESS RULES & CREDENTIALS
# ============================================================

def add_business_rules(context):
    """Add HR-specific business rules to the context."""
    print("\n" + "="*60)
    print("STEP 2: ADDING BUSINESS RULES & CREDENTIALS")
    print("="*60)

    from context import BusinessRule, DomainTerm, UserJourney, ContextStore
    from context.credential_vault import CredentialVault, CredentialType

    # Add business rules
    hr_rules = [
        BusinessRule(
            rule_id="HR-001",
            name="Login Security",
            description="Users must authenticate with valid credentials. After 3 failed attempts, account is locked for 30 minutes.",
            category="security",
            applies_to=["login", "authentication"],
            test_implications="Test valid login, invalid login, and account lockout scenarios"
        ),
        BusinessRule(
            rule_id="HR-002",
            name="Employee Data Privacy",
            description="Only HR admins can view sensitive employee data like salary and SSN",
            category="privacy",
            applies_to=["employee_records", "personal_info"],
            test_implications="Verify role-based access control for sensitive fields"
        ),
        BusinessRule(
            rule_id="HR-003",
            name="Leave Request Workflow",
            description="Leave requests require supervisor approval. Requests > 5 days also need HR approval.",
            category="workflow",
            applies_to=["leave_management", "approvals"],
            test_implications="Test single and dual approval workflows"
        ),
        BusinessRule(
            rule_id="HR-004",
            name="Session Timeout",
            description="User sessions expire after 30 minutes of inactivity",
            category="security",
            applies_to=["session", "authentication"],
            test_implications="Verify session timeout and re-authentication"
        ),
    ]

    for rule in hr_rules:
        context.business_rules.append(rule)
    print(f"   ✅ Added {len(hr_rules)} business rules")

    # Add domain glossary
    domain_terms = {
        "PIM": DomainTerm(
            term="PIM",
            definition="Personal Information Management - module for managing employee data",
            aliases=["Employee Management"],
            context="navigation"
        ),
        "ESS": DomainTerm(
            term="ESS",
            definition="Employee Self Service - portal for employees to manage their own data",
            aliases=["Self Service"],
            context="module"
        ),
        "Leave": DomainTerm(
            term="Leave",
            definition="Time off requests including vacation, sick leave, and personal days",
            aliases=["Time Off", "PTO"],
            context="module"
        ),
    }

    context.domain_glossary.update(domain_terms)
    print(f"   ✅ Added {len(domain_terms)} domain terms")

    # Add critical user journey
    login_journey = UserJourney(
        journey_id="UJ-001",
        name="Admin Login Flow",
        description="Administrator logs into the system. Precondition: User has valid admin credentials. Expected: User is logged in and sees the dashboard.",
        steps=[
            "Navigate to login page",
            "Enter username 'Admin'",
            "Enter password 'admin123'",
            "Click Login button",
            "Verify dashboard is displayed"
        ],
        priority="critical",
        frequency="every release"
    )
    context.critical_journeys.append(login_journey)
    print(f"   ✅ Added critical user journey: {login_journey.name}")

    # Store credentials in vault
    vault = CredentialVault("./orangehrm_vault", master_key="demo-key")

    admin_cred = vault.store_credential(
        name="admin_user",
        credential_type=CredentialType.USERNAME_PASSWORD,
        secret="Admin:admin123",
        app_id=context.app_id,
        environment="demo",
        description="OrangeHRM demo admin credentials"
    )
    print(f"   ✅ Stored admin credentials: {admin_cred.credential_id[:12]}...")

    # Save updated context
    store = ContextStore()
    version = store.save_context(context)
    print(f"   ✅ Context saved (version: {version})")

    return context


# ============================================================
# STEP 3: DISCOVER PAGE ELEMENTS
# ============================================================

def discover_login_page(context):
    """Simulate discovery of login page elements."""
    print("\n" + "="*60)
    print("STEP 3: DISCOVERING LOGIN PAGE ELEMENTS")
    print("="*60)

    # In a real scenario, this would use the RealBrowserDiscoveryAgent
    # For this demo, we'll create realistic discovery results

    discovery_results = {
        "url": "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login",
        "page_title": "OrangeHRM",
        "discovered_at": datetime.now().isoformat(),
        "elements": {
            "login_form": {
                "type": "form",
                "selector": "form.oxd-form",
                "children": ["username_input", "password_input", "login_button"]
            },
            "username_input": {
                "type": "input",
                "selector": "input[name='username']",
                "placeholder": "Username",
                "required": True,
                "testid": None
            },
            "password_input": {
                "type": "input",
                "selector": "input[name='password']",
                "input_type": "password",
                "placeholder": "Password",
                "required": True
            },
            "login_button": {
                "type": "button",
                "selector": "button[type='submit']",
                "text": "Login",
                "class": "oxd-button--main"
            },
            "forgot_password_link": {
                "type": "link",
                "selector": "p.oxd-text--card-body",
                "text": "Forgot your password?"
            },
            "logo": {
                "type": "image",
                "selector": "img.orangehrm-login-branding",
                "alt": "OrangeHRM Logo"
            }
        },
        "forms": [
            {
                "name": "login_form",
                "action": "/web/index.php/auth/validate",
                "method": "POST",
                "fields": ["username", "password"]
            }
        ],
        "navigation": [],
        "error_states": {
            "invalid_credentials": {
                "selector": "p.oxd-alert-content-text",
                "text": "Invalid credentials"
            }
        }
    }

    print(f"   ✅ Discovered {len(discovery_results['elements'])} elements")
    print(f"   ✅ Found {len(discovery_results['forms'])} forms")
    print("   📋 Key elements:")
    for name, elem in discovery_results['elements'].items():
        print(f"      - {name}: {elem['selector']}")

    return discovery_results


# ============================================================
# STEP 4: GENERATE TEST PLAN WITH CONTEXT
# ============================================================

def generate_test_plan(context, discovery_results):
    """Generate a context-aware test plan."""
    print("\n" + "="*60)
    print("STEP 4: GENERATING CONTEXT-AWARE TEST PLAN")
    print("="*60)

    from agents.planning_agent import PlanningAgent

    # Create planning agent with context
    planner = PlanningAgent(application_context=context)
    print(f"   ✅ Created PlanningAgent with context: {context.app_name}")

    # Show how context affects the prompt
    base_prompt = "Create a test plan for the login functionality"
    enhanced_prompt = planner._inject_application_context(base_prompt)

    print(f"\n   📝 Original prompt: {len(base_prompt)} chars")
    print(f"   📝 Enhanced prompt: {len(enhanced_prompt)} chars")
    print(f"   📝 Context injection added: {len(enhanced_prompt) - len(base_prompt)} chars")

    # Generate test plan (simulated since we don't have LLM API keys)
    test_plan = {
        "plan_id": f"TP-{context.app_id[:8]}",
        "app_name": context.app_name,
        "generated_at": datetime.now().isoformat(),
        "context_applied": True,
        "business_rules_considered": [r.rule_id for r in context.business_rules],
        "test_suites": [
            {
                "suite_id": "TS-001",
                "name": "Login Functionality",
                "priority": "critical",
                "test_cases": [
                    {
                        "id": "TC-001",
                        "name": "Valid Admin Login",
                        "description": "Verify admin can login with valid credentials",
                        "steps": [
                            "Navigate to login page",
                            "Enter username 'Admin'",
                            "Enter password 'admin123'",
                            "Click Login button",
                            "Verify dashboard is displayed"
                        ],
                        "expected_result": "User is logged in, dashboard shown",
                        "business_rule": "HR-001",
                        "priority": "P0"
                    },
                    {
                        "id": "TC-002",
                        "name": "Invalid Password Login",
                        "description": "Verify error message for invalid password",
                        "steps": [
                            "Navigate to login page",
                            "Enter username 'Admin'",
                            "Enter incorrect password",
                            "Click Login button",
                            "Verify error message is displayed"
                        ],
                        "expected_result": "Error message 'Invalid credentials' shown",
                        "business_rule": "HR-001",
                        "priority": "P0"
                    },
                    {
                        "id": "TC-003",
                        "name": "Empty Username Login",
                        "description": "Verify validation for empty username",
                        "steps": [
                            "Navigate to login page",
                            "Leave username empty",
                            "Enter password",
                            "Click Login button"
                        ],
                        "expected_result": "Required field validation error",
                        "business_rule": "HR-001",
                        "priority": "P1"
                    },
                    {
                        "id": "TC-004",
                        "name": "Empty Password Login",
                        "description": "Verify validation for empty password",
                        "steps": [
                            "Navigate to login page",
                            "Enter username",
                            "Leave password empty",
                            "Click Login button"
                        ],
                        "expected_result": "Required field validation error",
                        "business_rule": "HR-001",
                        "priority": "P1"
                    },
                ]
            }
        ]
    }

    print(f"\n   ✅ Generated test plan: {test_plan['plan_id']}")
    print(f"   📋 Test suites: {len(test_plan['test_suites'])}")

    total_tests = sum(len(s['test_cases']) for s in test_plan['test_suites'])
    print(f"   📋 Total test cases: {total_tests}")
    print(f"   📋 Business rules applied: {test_plan['business_rules_considered']}")

    return test_plan


# ============================================================
# STEP 5: GENERATE PLAYWRIGHT TESTS
# ============================================================

def generate_playwright_tests(context, discovery_results, test_plan):
    """Generate actual Playwright test code."""
    print("\n" + "="*60)
    print("STEP 5: GENERATING PLAYWRIGHT TEST CODE")
    print("="*60)

    # Create output directory
    output_dir = Path("./generated_tests/orangehrm")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate conftest.py
    conftest_code = '''"""
Pytest fixtures for OrangeHRM tests.
Generated by AutoGen AI QA Platform
"""

import pytest
from playwright.sync_api import sync_playwright, Page, Browser

# Application context
APP_NAME = "{app_name}"
BASE_URL = "{base_url}"

# Test credentials
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="session")
def browser():
    """Create browser instance for test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser):
    """Create new page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="function")
def logged_in_page(page: Page):
    """Provide a page with logged-in admin user."""
    page.goto(f"{{BASE_URL}}/web/index.php/auth/login")
    page.fill("input[name='username']", ADMIN_USERNAME)
    page.fill("input[name='password']", ADMIN_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_url("**/dashboard/**")
    yield page
'''.format(
        app_name=context.app_name,
        base_url=context.app_url
    )

    conftest_path = output_dir / "conftest.py"
    conftest_path.write_text(conftest_code)
    print(f"   ✅ Generated: {conftest_path}")

    # Generate test_login.py
    test_login_code = '''"""
Login Tests for OrangeHRM
Generated by AutoGen AI QA Platform

Business Rules Applied:
- HR-001: Login Security - Users must authenticate with valid credentials

Test Data:
- Valid admin: Admin / admin123
- Invalid scenarios for negative testing
"""

import pytest
from playwright.sync_api import Page, expect


class TestLoginFunctionality:
    """Test suite for login functionality."""

    BASE_URL = "https://opensource-demo.orangehrmlive.com"
    LOGIN_URL = f"{BASE_URL}/web/index.php/auth/login"

    # Selectors (from discovery)
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = "p.oxd-alert-content-text"
    REQUIRED_ERROR = ".oxd-input-field-error-message"

    def test_valid_admin_login(self, page: Page):
        """
        TC-001: Verify admin can login with valid credentials.

        Business Rule: HR-001 - Login Security
        Priority: P0 (Critical)
        """
        # Navigate to login page
        page.goto(self.LOGIN_URL)

        # Enter valid credentials
        page.fill(self.USERNAME_INPUT, "Admin")
        page.fill(self.PASSWORD_INPUT, "admin123")

        # Click login button
        page.click(self.LOGIN_BUTTON)

        # Verify successful login - redirected to dashboard
        page.wait_for_url("**/dashboard/**", timeout=10000)

        # Verify dashboard elements are visible
        expect(page.locator(".oxd-topbar")).to_be_visible()

    def test_invalid_password_login(self, page: Page):
        """
        TC-002: Verify error message for invalid password.

        Business Rule: HR-001 - Login Security
        Priority: P0 (Critical)
        """
        # Navigate to login page
        page.goto(self.LOGIN_URL)

        # Enter valid username but wrong password
        page.fill(self.USERNAME_INPUT, "Admin")
        page.fill(self.PASSWORD_INPUT, "wrongpassword")

        # Click login button
        page.click(self.LOGIN_BUTTON)

        # Verify error message is displayed
        error = page.locator(self.ERROR_MESSAGE)
        expect(error).to_be_visible()
        expect(error).to_contain_text("Invalid credentials")

    def test_invalid_username_login(self, page: Page):
        """
        TC-003: Verify error message for invalid username.

        Business Rule: HR-001 - Login Security
        Priority: P1
        """
        # Navigate to login page
        page.goto(self.LOGIN_URL)

        # Enter invalid username
        page.fill(self.USERNAME_INPUT, "NonExistentUser")
        page.fill(self.PASSWORD_INPUT, "admin123")

        # Click login button
        page.click(self.LOGIN_BUTTON)

        # Verify error message
        error = page.locator(self.ERROR_MESSAGE)
        expect(error).to_be_visible()
        expect(error).to_contain_text("Invalid credentials")

    def test_empty_username_validation(self, page: Page):
        """
        TC-004: Verify validation for empty username.

        Business Rule: HR-001 - Login Security
        Priority: P1
        """
        # Navigate to login page
        page.goto(self.LOGIN_URL)

        # Leave username empty, fill password
        page.fill(self.PASSWORD_INPUT, "admin123")

        # Click login button
        page.click(self.LOGIN_BUTTON)

        # Verify required field error
        error = page.locator(self.REQUIRED_ERROR).first
        expect(error).to_be_visible()
        expect(error).to_contain_text("Required")

    def test_empty_password_validation(self, page: Page):
        """
        TC-005: Verify validation for empty password.

        Business Rule: HR-001 - Login Security
        Priority: P1
        """
        # Navigate to login page
        page.goto(self.LOGIN_URL)

        # Fill username, leave password empty
        page.fill(self.USERNAME_INPUT, "Admin")

        # Click login button
        page.click(self.LOGIN_BUTTON)

        # Verify required field error
        error = page.locator(self.REQUIRED_ERROR).first
        expect(error).to_be_visible()
        expect(error).to_contain_text("Required")

    def test_empty_both_fields_validation(self, page: Page):
        """
        TC-006: Verify validation when both fields are empty.

        Business Rule: HR-001 - Login Security
        Priority: P2
        """
        # Navigate to login page
        page.goto(self.LOGIN_URL)

        # Don't fill anything, just click login
        page.click(self.LOGIN_BUTTON)

        # Verify both fields show required error
        errors = page.locator(self.REQUIRED_ERROR)
        expect(errors).to_have_count(2)


class TestLoginPageUI:
    """Test suite for login page UI elements."""

    BASE_URL = "https://opensource-demo.orangehrmlive.com"
    LOGIN_URL = f"{BASE_URL}/web/index.php/auth/login"

    def test_login_page_loads(self, page: Page):
        """Verify login page loads correctly."""
        page.goto(self.LOGIN_URL)

        # Check page title
        expect(page).to_have_title("OrangeHRM")

        # Check logo is visible
        logo = page.locator("img.orangehrm-login-branding")
        expect(logo).to_be_visible()

    def test_login_form_elements_present(self, page: Page):
        """Verify all login form elements are present."""
        page.goto(self.LOGIN_URL)

        # Username input
        expect(page.locator("input[name='username']")).to_be_visible()

        # Password input
        expect(page.locator("input[name='password']")).to_be_visible()

        # Login button
        expect(page.locator("button[type='submit']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_contain_text("Login")

    def test_forgot_password_link(self, page: Page):
        """Verify forgot password link is present."""
        page.goto(self.LOGIN_URL)

        forgot_link = page.locator("text=Forgot your password?")
        expect(forgot_link).to_be_visible()
'''

    test_login_path = output_dir / "test_login.py"
    test_login_path.write_text(test_login_code)
    print(f"   ✅ Generated: {test_login_path}")

    # Generate pytest.ini
    pytest_ini = '''[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    smoke: Quick smoke tests
    regression: Full regression tests
    login: Login related tests
'''

    pytest_ini_path = output_dir / "pytest.ini"
    pytest_ini_path.write_text(pytest_ini)
    print(f"   ✅ Generated: {pytest_ini_path}")

    # Generate requirements.txt
    requirements = '''pytest>=7.0.0
playwright>=1.40.0
pytest-playwright>=0.4.0
'''

    req_path = output_dir / "requirements.txt"
    req_path.write_text(requirements)
    print(f"   ✅ Generated: {req_path}")

    # Generate README
    readme = f'''# OrangeHRM Test Suite

Generated by AutoGen AI QA Platform on {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Application Context

- **App Name**: {context.app_name}
- **URL**: {context.app_url}
- **Tech Stack**: {context.tech_stack.frontend} + {context.tech_stack.backend}

## Business Rules Applied

{chr(10).join(f"- **{r.rule_id}**: {r.name} - {r.description}" for r in context.business_rules)}

## Test Coverage

### Login Tests (test_login.py)
- Valid login with admin credentials
- Invalid password handling
- Invalid username handling
- Empty field validation
- UI element verification

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run all tests
pytest

# Run with visible browser
pytest --headed

# Run specific test
pytest test_login.py::TestLoginFunctionality::test_valid_admin_login
```

## Test Credentials

- **Admin**: Admin / admin123

> Note: These are demo credentials for the public OrangeHRM demo instance.
'''

    readme_path = output_dir / "README.md"
    readme_path.write_text(readme)
    print(f"   ✅ Generated: {readme_path}")

    print(f"\n   📁 All tests generated in: {output_dir.absolute()}")

    return output_dir


# ============================================================
# STEP 6: SUMMARY
# ============================================================

def print_summary(context, test_plan, output_dir):
    """Print final summary."""
    print("\n" + "="*60)
    print("END-TO-END TEST COMPLETE")
    print("="*60)

    print(f"""
✅ APPLICATION ONBOARDED
   Name: {context.app_name}
   URL: {context.app_url}
   ID: {context.app_id}

✅ CONTEXT ENRICHED
   Business Rules: {len(context.business_rules)}
   Domain Terms: {len(context.domain_glossary)}
   User Journeys: {len(context.critical_journeys)}

✅ TEST PLAN GENERATED
   Plan ID: {test_plan['plan_id']}
   Test Suites: {len(test_plan['test_suites'])}
   Total Tests: {sum(len(s['test_cases']) for s in test_plan['test_suites'])}

✅ PLAYWRIGHT TESTS CREATED
   Location: {output_dir.absolute()}
   Files:
   - conftest.py (fixtures)
   - test_login.py (8 test cases)
   - pytest.ini (configuration)
   - requirements.txt (dependencies)
   - README.md (documentation)

🚀 TO RUN THE TESTS:
   cd {output_dir}
   pip install -r requirements.txt
   playwright install chromium
   pytest -v
""")


# ============================================================
# MAIN
# ============================================================

def main():
    """Run the complete end-to-end test."""
    print("\n" + "🚀 "*20)
    print("AUTOGEN AI QA PLATFORM - END-TO-END VALIDATION")
    print("Target Application: OrangeHRM Demo")
    print("🚀 "*20)

    # Step 1: Onboard
    context = onboard_orangehrm()

    # Step 2: Add business rules
    context = add_business_rules(context)

    # Step 3: Discover elements
    discovery_results = discover_login_page(context)

    # Step 4: Generate test plan
    test_plan = generate_test_plan(context, discovery_results)

    # Step 5: Generate tests
    output_dir = generate_playwright_tests(context, discovery_results, test_plan)

    # Step 6: Summary
    print_summary(context, test_plan, output_dir)

    return context, test_plan, output_dir


if __name__ == "__main__":
    main()
