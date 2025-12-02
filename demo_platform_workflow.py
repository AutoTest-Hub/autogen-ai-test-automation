#!/usr/bin/env python3
"""
AutoGen AI QA Platform - Complete Workflow Demonstration

This script demonstrates the CORRECT platform workflow:

    ┌──────────────────────────────────────────────────────────┐
    │  1. USER WRITES PLAIN-ENGLISH TEST SCENARIOS (.txt)      │
    │                                                          │
    │     Test Name: Valid Login                               │
    │     Steps:                                               │
    │       1. Navigate to login page                          │
    │       2. Enter username "Admin"                          │
    │       3. Click Login button                              │
    └──────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────────────────────────────────────────────────┐
    │  2. PARSER CONVERTS TO STRUCTURED DATA                   │
    │                                                          │
    │     TxtTestFileParser extracts:                          │
    │     - test_name, steps, expected_results                 │
    └──────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────────────────────────────────────────────────┐
    │  3. APPLICATION CONTEXT PROVIDES INTELLIGENCE            │
    │                                                          │
    │     - Discovered selectors (input[name='username'])      │
    │     - Business rules (HR-001: Login Security)            │
    │     - Domain glossary (PIM, ESS, Leave)                  │
    └──────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────────────────────────────────────────────────┐
    │  4. SMART GENERATOR CREATES EXECUTABLE TESTS             │
    │                                                          │
    │     Maps "Enter username" → page.fill(selector, value)   │
    │     Uses real selectors from discovery                   │
    │     References business rules in docstrings              │
    └──────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────────────────────────────────────────────────┐
    │  5. EXECUTABLE PLAYWRIGHT TESTS                          │
    │                                                          │
    │     def test_valid_login(page):                          │
    │         page.fill("input[name='username']", "Admin")     │
    │         page.click("button[type='submit']")              │
    └──────────────────────────────────────────────────────────┘

This is the vision: Users write in plain English, AI generates smart tests.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, '.')


# ============================================================
# STEP 1: LOAD PLAIN-ENGLISH TEST SCENARIOS
# ============================================================

def load_test_scenarios(file_path: str) -> Dict[str, Any]:
    """Load and parse plain-English test scenarios."""
    print("\n" + "="*70)
    print("STEP 1: LOADING PLAIN-ENGLISH TEST SCENARIOS")
    print("="*70)

    from parsers.txt_parser import TxtTestFileParser

    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()

    print(f"   📄 Source file: {file_path}")
    print(f"   📄 File size: {len(content)} characters")

    # Parse with TxtTestFileParser
    parser = TxtTestFileParser()
    parsed = parser.parse_file(file_path, content)

    print(f"\n   ✅ Parsed {len(parsed.scenarios)} test scenarios:")
    for scenario in parsed.scenarios:
        print(f"      - {scenario['test_name']}")
        print(f"        Steps: {len(scenario['test_steps'])}")
        print(f"        Priority: {scenario['priority']}")

    return {
        "parsed_file": parsed,
        "scenarios": parsed.scenarios
    }


# ============================================================
# STEP 2: LOAD APPLICATION CONTEXT (Pre-configured)
# ============================================================

def load_application_context() -> Dict[str, Any]:
    """
    Load application context with discovered elements and business rules.

    In production, this comes from:
    - Onboarding wizard (business rules, tech stack)
    - Browser discovery (actual page selectors)
    - Knowledge ingestion (README, OpenAPI, etc.)
    """
    print("\n" + "="*70)
    print("STEP 2: LOADING APPLICATION CONTEXT")
    print("="*70)

    # Simulated discovery results (in production, from RealBrowserDiscoveryAgent)
    discovered_elements = {
        "username_input": {
            "type": "input",
            "selector": "input[name='username']",
            "placeholder": "Username",
            "required": True
        },
        "password_input": {
            "type": "input",
            "selector": "input[name='password']",
            "input_type": "password",
            "required": True
        },
        "login_button": {
            "type": "button",
            "selector": "button[type='submit']",
            "text": "Login"
        },
        "error_message": {
            "type": "text",
            "selector": "p.oxd-alert-content-text"
        },
        "validation_error": {
            "type": "text",
            "selector": ".oxd-input-field-error-message"
        },
        "dashboard_header": {
            "type": "element",
            "selector": ".oxd-topbar-header"
        }
    }

    # Business rules from onboarding
    business_rules = [
        {
            "rule_id": "HR-001",
            "name": "Login Security",
            "description": "Users must authenticate with valid credentials",
            "applies_to": ["login", "authentication"],
            "test_implications": "Test valid/invalid login scenarios"
        },
        {
            "rule_id": "HR-004",
            "name": "Session Security",
            "description": "Sessions expire after 30 minutes of inactivity",
            "applies_to": ["session", "authentication"],
            "test_implications": "Verify session handling"
        }
    ]

    context = {
        "app_name": "OrangeHRM",
        "app_url": "https://opensource-demo.orangehrmlive.com",
        "tech_stack": {"frontend": "Vue.js", "backend": "PHP/Symfony"},
        "discovered_elements": discovered_elements,
        "business_rules": business_rules
    }

    print(f"   📦 Application: {context['app_name']}")
    print(f"   📦 URL: {context['app_url']}")
    print(f"   📦 Discovered elements: {len(discovered_elements)}")
    for name, elem in discovered_elements.items():
        print(f"      - {name}: {elem['selector']}")
    print(f"   📦 Business rules: {len(business_rules)}")
    for rule in business_rules:
        print(f"      - {rule['rule_id']}: {rule['name']}")

    return context


# ============================================================
# STEP 3: MAP PLAIN-ENGLISH TO SELECTORS
# ============================================================

def map_steps_to_selectors(
    scenarios: List[Dict],
    context: Dict[str, Any]
) -> List[Dict]:
    """
    Map plain-English steps to actual selectors using ApplicationContext.

    This is the "intelligence" layer - understanding what the user means
    and finding the right elements to interact with.
    """
    print("\n" + "="*70)
    print("STEP 3: MAPPING PLAIN-ENGLISH TO SELECTORS")
    print("="*70)

    elements = context["discovered_elements"]

    # Mapping rules: keywords → element types
    step_mappings = {
        "username": "username_input",
        "password": "password_input",
        "login": "login_button",
        "submit": "login_button",
        "click": "login_button",
        "error": "error_message",
        "invalid": "error_message",
        "required": "validation_error",
        "validation": "validation_error",
        "dashboard": "dashboard_header"
    }

    enriched_scenarios = []

    for scenario in scenarios:
        enriched_steps = []
        print(f"\n   📝 Mapping: {scenario['test_name']}")

        for step in scenario.get("test_steps", []):
            step_text = step.action.lower() if hasattr(step, 'action') else str(step).lower()

            # Find matching element
            matched_element = None
            matched_key = None
            for keyword, element_key in step_mappings.items():
                if keyword in step_text:
                    matched_element = elements.get(element_key)
                    matched_key = element_key
                    break

            enriched_step = {
                "original": step.action if hasattr(step, 'action') else str(step),
                "step_number": step.step_number if hasattr(step, 'step_number') else 0,
                "element_key": matched_key,
                "selector": matched_element["selector"] if matched_element else None,
                "element_type": matched_element["type"] if matched_element else None
            }
            enriched_steps.append(enriched_step)

            if matched_element:
                print(f"      ✅ '{enriched_step['original'][:40]}...' → {matched_element['selector']}")
            else:
                print(f"      ⚠️  '{enriched_step['original'][:40]}...' → (navigation/assertion)")

        enriched_scenario = {
            **scenario,
            "enriched_steps": enriched_steps
        }
        enriched_scenarios.append(enriched_scenario)

    return enriched_scenarios


# ============================================================
# STEP 4: GENERATE EXECUTABLE TEST CODE
# ============================================================

def generate_executable_tests(
    enriched_scenarios: List[Dict],
    context: Dict[str, Any],
    output_dir: Path
) -> Path:
    """
    Generate executable Playwright test code from enriched scenarios.

    This uses the SmartTestGenerator to create real, runnable tests.
    """
    print("\n" + "="*70)
    print("STEP 4: GENERATING EXECUTABLE TEST CODE")
    print("="*70)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Build test file
    test_code = f'''"""
{context['app_name']} - Generated Tests from Plain-English Scenarios
Generated by AutoGen AI QA Platform
Date: {datetime.now().isoformat()}

WORKFLOW:
1. User wrote plain-English test scenarios in .txt file
2. Parser extracted structured test data
3. ApplicationContext provided real selectors
4. This code was generated automatically

Source scenarios: {len(enriched_scenarios)}
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def test_credentials():
    """Test credentials - override for your environment."""
    return {{
        "username": "Admin",
        "password": "admin123"
    }}


class Test{context['app_name'].replace(' ', '').replace('-', '')}:
    """Generated tests from plain-English scenarios."""

    BASE_URL = "{context['app_url']}"
    LOGIN_URL = f"{{BASE_URL}}/web/index.php/auth/login"

    # Selectors from ApplicationContext discovery
'''

    # Add selectors as class constants
    for elem_name, elem_data in context['discovered_elements'].items():
        const_name = elem_name.upper()
        test_code += f"    {const_name} = \"{elem_data['selector']}\"\n"

    test_code += "\n"

    # Generate test methods from scenarios
    for scenario in enriched_scenarios:
        test_name = scenario['test_name'].lower().replace(' ', '_').replace('-', '_')
        test_name = ''.join(c for c in test_name if c.isalnum() or c == '_')

        # Find applicable business rules
        rule_refs = []
        for rule in context['business_rules']:
            applies_to = ' '.join(rule.get('applies_to', []))
            if 'login' in scenario['test_name'].lower() or 'login' in applies_to:
                rule_refs.append(rule['rule_id'])

        test_code += f'''
    def test_{test_name}(self, page: Page, test_credentials):
        """
        {scenario['test_name']}

        Original Description: {scenario.get('description', 'N/A')[:100]}
        Business Rules: {', '.join(rule_refs) if rule_refs else 'N/A'}
        Priority: {scenario.get('priority', 'Medium')}
        Generated: {datetime.now().isoformat()}
        """
        # Navigate to login page
        page.goto(self.LOGIN_URL)

'''
        # Generate steps from enriched data
        for step in scenario.get('enriched_steps', []):
            original = step['original']
            selector = step.get('selector')
            elem_type = step.get('element_type')

            if 'navigate' in original.lower():
                test_code += f"        # Step: {original}\n"
                test_code += f"        # (Already navigated above)\n\n"
            elif 'enter username' in original.lower() or 'username' in original.lower() and 'enter' in original.lower():
                test_code += f"        # Step: {original}\n"
                if selector:
                    # Extract the value if present in the step
                    import re
                    match = re.search(r'"([^"]+)"', original)
                    value = match.group(1) if match else 'test_credentials["username"]'
                    if value == 'Admin':
                        value = 'test_credentials["username"]'
                    test_code += f"        page.fill(self.USERNAME_INPUT, {value})\n\n"
                else:
                    test_code += f"        # TODO: Map to selector\n\n"
            elif 'enter password' in original.lower() or 'password' in original.lower() and 'enter' in original.lower():
                test_code += f"        # Step: {original}\n"
                if selector:
                    test_code += f"        page.fill(self.PASSWORD_INPUT, test_credentials[\"password\"])\n\n"
                else:
                    test_code += f"        # TODO: Map to selector\n\n"
            elif 'click' in original.lower() and ('login' in original.lower() or 'button' in original.lower()):
                test_code += f"        # Step: {original}\n"
                test_code += f"        page.click(self.LOGIN_BUTTON)\n\n"
            elif 'verify' in original.lower() or 'check' in original.lower():
                test_code += f"        # Step: {original}\n"
                if 'dashboard' in original.lower():
                    test_code += f"        page.wait_for_url(\"**/dashboard/**\", timeout=10000)\n"
                    test_code += f"        expect(page.locator(self.DASHBOARD_HEADER)).to_be_visible()\n\n"
                elif 'error' in original.lower():
                    test_code += f"        expect(page.locator(self.ERROR_MESSAGE)).to_be_visible()\n\n"
                elif 'validation' in original.lower() or 'required' in original.lower():
                    test_code += f"        expect(page.locator(self.VALIDATION_ERROR)).to_be_visible()\n\n"
                else:
                    test_code += f"        # TODO: Add specific assertion\n\n"
            elif 'leave' in original.lower() and 'empty' in original.lower():
                test_code += f"        # Step: {original}\n"
                test_code += f"        # (Field left empty intentionally)\n\n"
            else:
                test_code += f"        # Step: {original}\n"
                test_code += f"        # TODO: Map this step to action\n\n"

    # Write test file
    test_file = output_dir / f"test_{context['app_name'].lower().replace(' ', '_')}_from_txt.py"
    test_file.write_text(test_code)

    print(f"   ✅ Generated: {test_file}")
    print(f"   📋 Test methods: {len(enriched_scenarios)}")
    print(f"   📋 Selectors used: {len(context['discovered_elements'])}")

    return test_file


# ============================================================
# STEP 5: SUMMARY AND COMPARISON
# ============================================================

def print_summary(
    original_file: str,
    scenarios: List[Dict],
    generated_file: Path
):
    """Print summary showing the transformation."""
    print("\n" + "="*70)
    print("WORKFLOW COMPLETE - SUMMARY")
    print("="*70)

    print(f"""
┌────────────────────────────────────────────────────────────────────┐
│  WHAT HAPPENED                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  INPUT (Plain English):                                            │
│  ─────────────────────                                             │
│  {original_file}
│                                                                    │
│  User wrote tests like:                                            │
│    "1. Navigate to the login page"                                 │
│    "2. Enter username 'Admin'"                                     │
│    "3. Click the Login button"                                     │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  INTELLIGENCE LAYER:                                               │
│  ───────────────────                                               │
│  ApplicationContext provided:                                      │
│    - Real selectors: input[name='username']                        │
│    - Business rules: HR-001 (Login Security)                       │
│    - Tech stack awareness: Vue.js + Playwright                     │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  OUTPUT (Executable Code):                                         │
│  ─────────────────────────                                         │
│  {generated_file}
│                                                                    │
│  Generated code like:                                              │
│    page.fill("input[name='username']", credentials["username"])   │
│    page.click("button[type='submit']")                            │
│    expect(page.locator(".oxd-topbar")).to_be_visible()            │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  SCENARIOS PROCESSED: {len(scenarios)}                                             │
│                                                                    │
│  This is the platform vision: Write in English, get smart tests!  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

🚀 TO RUN GENERATED TESTS:
   cd {generated_file.parent}
   pytest {generated_file.name} -v
""")


# ============================================================
# MAIN
# ============================================================

def main():
    """Run the complete platform workflow demonstration."""
    print("\n" + "🤖 "*20)
    print("AUTOGEN AI QA PLATFORM - WORKFLOW DEMONSTRATION")
    print("From Plain English to Executable Tests")
    print("🤖 "*20)

    # File paths
    scenario_file = "test_scenarios/orangehrm_login.txt"
    output_dir = Path("./generated_tests/from_plain_english")

    # Step 1: Load plain-English scenarios
    result = load_test_scenarios(scenario_file)
    scenarios = result["scenarios"]

    # Step 2: Load application context
    context = load_application_context()

    # Step 3: Map steps to selectors
    enriched_scenarios = map_steps_to_selectors(scenarios, context)

    # Step 4: Generate executable tests
    generated_file = generate_executable_tests(enriched_scenarios, context, output_dir)

    # Step 5: Summary
    print_summary(scenario_file, scenarios, generated_file)

    return {
        "scenarios": scenarios,
        "context": context,
        "generated_file": generated_file
    }


if __name__ == "__main__":
    main()
