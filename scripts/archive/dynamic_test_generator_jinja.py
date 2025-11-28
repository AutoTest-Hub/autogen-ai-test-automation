#!/usr/bin/env python3
"""
Dynamic Test Generator with Jinja2
=================================
This script dynamically generates test files and page objects based on discovered elements.
It uses Jinja2 templates for better compatibility across Python versions.
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Try to import Jinja2
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("Jinja2 is not installed. Installing now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jinja2"])
    from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import path manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config.path_manager import path_manager
except ImportError:
    # Fallback if path_manager is not available
    class SimplePathManager:
        def __init__(self):
            self.project_root = Path(os.path.dirname(os.path.abspath(__file__)))
            self.tests_dir = self.project_root / "tests"
            self.pages_dir = self.project_root / "pages"
            self.templates_dir = self.project_root / "templates"
            self.screenshots_dir = self.project_root / "screenshots"
            
            # Create directories if they don't exist
            for directory in [self.tests_dir, self.pages_dir, self.templates_dir, self.screenshots_dir]:
                directory.mkdir(parents=True, exist_ok=True)
        
        def get_discovery_results(self):
            """Find discovery results in common locations"""
            work_dir = self.project_root / "work_dir"
            
            # Check in multiple possible locations
            locations = [
                work_dir / "RealBrowserDiscoveryAgent",
                work_dir / "RealDiscoveryIntegration",
                work_dir / "DiscoveryAgent"
            ]
            
            for location in locations:
                if not location.exists():
                    continue
                    
                # Find discovery results files
                files = list(location.glob("discovery_results_*.json"))
                if files:
                    # Return the most recent file
                    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
            
            return None
    
    path_manager = SimplePathManager()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DynamicTestGenerator:
    """
    Dynamic Test Generator
    
    This class generates test files and page objects based on discovered elements.
    """
    
    def __init__(self):
        """Initialize the dynamic test generator"""
        # Set up directories
        self.tests_dir = path_manager.tests_dir
        self.pages_dir = path_manager.pages_dir
        self.templates_dir = path_manager.templates_dir
        
        # Create directories if they don't exist
        self.tests_dir.mkdir(exist_ok=True)
        self.pages_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_default_templates()
        
        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        logger.info("Dynamic Test Generator initialized")
    
    def _create_default_templates(self):
        """Create default templates if they don't exist"""
        # Test file template
        test_template_path = self.templates_dir / "test_template.py.txt"
        if not test_template_path.exists():
            test_template = '''"""
{{ test_name }} Test
==============
{{ test_description }}
"""

import pytest
import logging
from datetime import datetime

from pages.{{ page_module }} import {{ page_class }}

class {{ test_class }}:
    """Test class for {{ test_name }}"""
    
    @pytest.mark.asyncio
    async def test_{{ test_function }}(self, browser_setup):
        """
        Test {{ test_name }}
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page object
            {{ page_var }} = {{ page_class }}(page)
            
            # Navigate to page
            await {{ page_var }}.navigate()
            
            # Take screenshot before actions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path="screenshots/{{ test_function }}_before_{}.png".format(timestamp))
            
{{ test_steps }}
            
            # Take screenshot after actions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path="screenshots/{{ test_function }}_after_{}.png".format(timestamp))
            
{{ assertions }}
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path="screenshots/{{ test_function }}_failure_{}.png".format(timestamp))
            
            logging.error("Test failed: {}".format(str(e)))
            raise

# Run test if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
'''
            with open(test_template_path, 'w') as f:
                f.write(test_template)
        
        # Page object template
        page_template_path = self.templates_dir / "page_template.py.txt"
        if not page_template_path.exists():
            page_template = '''"""
{{ page_name }} Page Object
======================
Page object for {{ page_name }} page.
"""

from pages.base_page import BasePage

class {{ page_class }}(BasePage):
    """Page object for {{ page_name }} page"""
    
    def __init__(self, page):
        """
        Initialize {{ page_name }} page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = "{{ page_url }}"  # URL path relative to base URL
        
        # Element selectors
{{ element_selectors }}
    
{{ element_methods }}
'''
            with open(page_template_path, 'w') as f:
                f.write(page_template)
        
        # Base page template
        base_page_path = self.pages_dir / "base_page.py"
        if not base_page_path.exists():
            base_page_template_path = self.templates_dir / "base_page.py.txt"
            if base_page_template_path.exists():
                # Copy from template
                with open(base_page_template_path, 'r') as src, open(base_page_path, 'w') as dst:
                    dst.write(src.read())
            else:
                # Create default base page
                base_page = '''"""
Base Page Object
===============
Base class for all page objects.
"""

import logging
from typing import Any, Dict, Optional

class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, page):
        """
        Initialize base page object
        
        Args:
            page: Playwright page object
        """
        self.page = page
        self.url = ""  # URL path relative to base URL
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def navigate(self):
        """Navigate to the page"""
        self.logger.info("Navigating to {}".format(self.url))
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("networkidle")
    
    async def get_title(self) -> str:
        """Get page title"""
        return await self.page.title()
    
    async def get_url(self) -> str:
        """Get current URL"""
        return self.page.url
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> Any:
        """
        Wait for selector to be visible
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            
        Returns:
            Element handle
        """
        self.logger.debug("Waiting for selector: {}".format(selector))
        return await self.page.wait_for_selector(selector, timeout=timeout)
    
    async def click(self, selector: str, timeout: int = 30000):
        """
        Click an element
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
        """
        self.logger.debug("Clicking element: {}".format(selector))
        await self.wait_for_selector(selector, timeout)
        await self.page.click(selector)
    
    async def fill(self, selector: str, value: str, timeout: int = 30000):
        """
        Fill an input field
        
        Args:
            selector: Element selector
            value: Value to fill
            timeout: Timeout in milliseconds
        """
        self.logger.debug("Filling element {} with value: {}".format(selector, value))
        await self.wait_for_selector(selector, timeout)
        await self.page.fill(selector, value)
    
    async def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element is visible, False otherwise
        """
        try:
            await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
            return True
        except Exception:
            return False
'''
                with open(base_page_path, 'w') as f:
                    f.write(base_page)
    
    def generate_test_file(self, 
                          test_name: str, 
                          test_description: str, 
                          page_name: str, 
                          page_url: str, 
                          test_steps: List[Dict[str, Any]]) -> str:
        """
        Generate a test file
        
        Args:
            test_name: Name of the test
            test_description: Description of the test
            page_name: Name of the page
            page_url: URL of the page
            test_steps: List of test steps
            
        Returns:
            str: Path to the generated test file
        """
        logger.info("Generating test file for {}".format(test_name))
        
        # Prepare variables
        test_class = "Test{}".format(test_name.replace('_', ' ').title().replace(' ', ''))
        test_function = test_name.lower().replace(' ', '_')
        page_class = "{}Page".format(page_name.replace('_', ' ').title().replace(' ', ''))
        page_module = page_name.lower().replace(' ', '_') + "_page"
        page_var = page_name.lower().replace(' ', '_') + "_page"
        
        # Generate test steps
        steps_code = []
        for step in test_steps:
            action = step.get("action", "")
            target = step.get("selector", "")
            value = step.get("value", "")
            description = step.get("description", "")
            
            if action == "navigate":
                steps_code.append("            # {}".format(description))
                steps_code.append('            await page.goto("{}")'.format(target))
                steps_code.append('            await page.wait_for_load_state("networkidle")')
                steps_code.append("")
            elif action == "click":
                steps_code.append("            # {}".format(description))
                steps_code.append('            await {}.click("{}")'.format(page_var, target))
                steps_code.append('            await page.wait_for_load_state("networkidle")')
                steps_code.append("")
            elif action == "input":
                steps_code.append("            # {}".format(description))
                steps_code.append('            await {}.fill("{}", "{}")'.format(page_var, target, value))
                steps_code.append("")
            elif action == "assert":
                steps_code.append("            # {}".format(description))
                steps_code.append('            assert await {}.is_visible("{}"), "{} failed"'.format(page_var, target, description))
                steps_code.append("")
        
        # Generate assertions
        assertions = []
        assertions.append("            # Add assertions here")
        assertions.append('            assert await page.title() != "", "Page title should not be empty"')
        
        # Render template
        template = self.jinja_env.get_template("test_template.py.txt")
        test_content = template.render(
            test_name=test_name.replace('_', ' ').title(),
            test_description=test_description,
            test_class=test_class,
            test_function=test_function,
            page_class=page_class,
            page_module=page_module,
            page_var=page_var,
            test_steps="\n".join(steps_code),
            assertions="\n".join(assertions)
        )
        
        # Write test file
        test_file_path = self.tests_dir / "test_{}.py".format(test_function)
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        logger.info("Generated test file: {}".format(test_file_path))
        return str(test_file_path)
    
    def generate_page_object(self, 
                            page_name: str, 
                            page_url: str, 
                            elements: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate a page object
        
        Args:
            page_name: Name of the page
            page_url: URL of the page
            elements: Dictionary of elements by type
            
        Returns:
            str: Path to the generated page object file
        """
        logger.info("Generating page object for {}".format(page_name))
        
        # Prepare variables
        page_class = "{}Page".format(page_name.replace('_', ' ').title().replace(' ', ''))
        
        # Generate element selectors
        element_selectors = []
        
        # Process inputs
        for input_el in elements.get("inputs", []):
            name = input_el.get("id") or input_el.get("name") or "{}_{}".format(input_el.get('type', 'input'), len(element_selectors) + 1)
            name = name.lower().replace('-', '_').replace(' ', '_')
            selector = input_el.get("css", "")
            element_selectors.append('        self.{}_selector = "{}"'.format(name, selector))
        
        # Process buttons
        for button in elements.get("buttons", []):
            name = button.get("id") or button.get("text", "").lower().replace(' ', '_') or "button_{}".format(len(element_selectors) + 1)
            name = name.lower().replace('-', '_').replace(' ', '_')
            selector = button.get("css", "")
            element_selectors.append('        self.{}_selector = "{}"'.format(name, selector))
        
        # Process links
        for link in elements.get("links", []):
            name = link.get("id") or link.get("text", "").lower().replace(' ', '_') or "link_{}".format(len(element_selectors) + 1)
            name = name.lower().replace('-', '_').replace(' ', '_')
            selector = link.get("css", "")
            element_selectors.append('        self.{}_selector = "{}"'.format(name, selector))
        
        # Generate element methods
        element_methods = []
        
        # Methods for inputs
        element_methods.append("    # Input methods")
        for input_el in elements.get("inputs", []):
            name = input_el.get("id") or input_el.get("name") or "{}_{}".format(input_el.get('type', 'input'), len(element_selectors) + 1)
            name = name.lower().replace('-', '_').replace(' ', '_')
            method_name = "fill_{}".format(name)
            
            method_code = """
    async def {method_name}(self, value):
        \"\"\"
        Fill {name} input
        
        Args:
            value: Value to fill
        \"\"\"
        await self.fill(self.{name}_selector, value)""".format(method_name=method_name, name=name)
            
            element_methods.append(method_code)
        
        # Methods for buttons
        element_methods.append("\n    # Button methods")
        for button in elements.get("buttons", []):
            name = button.get("id") or button.get("text", "").lower().replace(' ', '_') or "button_{}".format(len(element_selectors) + 1)
            name = name.lower().replace('-', '_').replace(' ', '_')
            method_name = "click_{}".format(name)
            
            method_code = """
    async def {method_name}(self):
        \"\"\"Click {name} button\"\"\"
        await self.click(self.{name}_selector)""".format(method_name=method_name, name=name)
            
            element_methods.append(method_code)
        
        # Methods for links
        element_methods.append("\n    # Link methods")
        for link in elements.get("links", []):
            name = link.get("id") or link.get("text", "").lower().replace(' ', '_') or "link_{}".format(len(element_selectors) + 1)
            name = name.lower().replace('-', '_').replace(' ', '_')
            method_name = "click_{}".format(name)
            
            method_code = """
    async def {method_name}(self):
        \"\"\"Click {name} link\"\"\"
        await self.click(self.{name}_selector)""".format(method_name=method_name, name=name)
            
            element_methods.append(method_code)
        
        # Render template
        template = self.jinja_env.get_template("page_template.py.txt")
        page_content = template.render(
            page_name=page_name.replace('_', ' ').title(),
            page_class=page_class,
            page_url=page_url,
            element_selectors="\n".join(element_selectors),
            element_methods="\n".join(element_methods)
        )
        
        # Write page object file
        page_file_path = self.pages_dir / "{}_page.py".format(page_name.lower().replace(' ', '_'))
        with open(page_file_path, 'w') as f:
            f.write(page_content)
        
        logger.info("Generated page object: {}".format(page_file_path))
        return str(page_file_path)
    
    def generate_from_discovery_results(self, discovery_results_path: str) -> Dict[str, Any]:
        """
        Generate test files and page objects from discovery results
        
        Args:
            discovery_results_path: Path to discovery results JSON file
            
        Returns:
            Dict[str, Any]: Dictionary with generated files
        """
        logger.info("Generating from discovery results: {}".format(discovery_results_path))
        
        # Load discovery results
        with open(discovery_results_path, 'r') as f:
            discovery_results = json.load(f)
        
        # Extract data
        application_url = discovery_results.get("application_url", discovery_results.get("page_url", ""))
        discovered_pages = discovery_results.get("discovered_pages", [])
        page_elements = discovery_results.get("page_elements", {})
        
        # If page_elements is empty, try to get elements from the discovery results
        if not page_elements and "elements" in discovery_results:
            page_name = "main_page"
            page_url = application_url
            page_elements = {page_name: {"url": page_url, "elements": discovery_results["elements"]}}
        
        # If still no elements, check if there's a direct elements key
        if not page_elements:
            elements = discovery_results.get("elements", {})
            if elements:
                page_name = "main_page"
                page_url = application_url
                page_elements = {page_name: {"url": page_url, "elements": elements}}
        
        workflows = discovery_results.get("workflows", [])
        
        # Generate files for each page
        generated_files = {
            "page_objects": [],
            "test_files": []
        }
        
        for page_name, page_data in page_elements.items():
            page_url = page_data.get("url", "")
            elements = page_data.get("elements", {})
            
            # Generate page object
            page_file = self.generate_page_object(page_name, page_url, elements)
            generated_files["page_objects"].append(page_file)
            
            # Generate test file
            test_name = "{}_test".format(page_name.lower().replace(' ', '_'))
            test_description = "Test for {} page".format(page_name)
            
            # Create test steps
            test_steps = []
            
            # Add navigation step
            test_steps.append({
                "action": "navigate",
                "target": page_url,
                "description": "Navigate to {} page".format(page_name)
            })
            
            # Add steps for inputs
            for input_el in elements.get("inputs", [])[:2]:  # Limit to first 2 inputs
                selector = input_el.get("css", "")
                input_type = input_el.get("type", "")
                
                if input_type == "text" or input_type == "email":
                    test_steps.append({
                        "action": "input",
                        "selector": selector,
                        "value": "test@example.com" if input_type == "email" else "test value",
                        "description": "Fill {} field".format(input_el.get('id') or input_el.get('name') or 'input')
                    })
                elif input_type == "password":
                    test_steps.append({
                        "action": "input",
                        "selector": selector,
                        "value": "password123",
                        "description": "Fill password field"
                    })
            
            # Add steps for buttons
            for button in elements.get("buttons", [])[:1]:  # Limit to first button
                selector = button.get("css", "")
                test_steps.append({
                    "action": "click",
                    "selector": selector,
                    "description": "Click {}".format(button.get('text') or button.get('id') or 'button')
                })
            
            # Generate test file
            test_file = self.generate_test_file(test_name, test_description, page_name, page_url, test_steps)
            generated_files["test_files"].append(test_file)
        
        # Generate workflow tests if available
        for workflow in workflows:
            workflow_name = workflow.get("name", "").lower().replace(' ', '_')
            workflow_description = workflow.get("description", "")
            workflow_steps = workflow.get("steps", [])
            
            if workflow_name and workflow_steps:
                # Find the first page in the workflow
                first_step = workflow_steps[0]
                first_page_url = first_step.get("target", "")
                
                # Find the page name for the first page
                first_page_name = None
                for page_name, page_data in page_elements.items():
                    if page_data.get("url") == first_page_url:
                        first_page_name = page_name
                        break
                
                if first_page_name:
                    # Generate test file for workflow
                    test_file = self.generate_test_file(
                        "{}_workflow".format(workflow_name),
                        workflow_description or "Test for {} workflow".format(workflow_name),
                        first_page_name,
                        first_page_url,
                        workflow_steps
                    )
                    generated_files["test_files"].append(test_file)
        
        logger.info("Generated {} page objects and {} test files".format(
            len(generated_files['page_objects']), len(generated_files['test_files'])
        ))
        return generated_files

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Dynamic Test Generator")
    parser.add_argument("--discovery-results", "-d", help="Path to discovery results JSON file")
    args = parser.parse_args()
    
    # Create generator
    generator = DynamicTestGenerator()
    
    # Get discovery results path
    discovery_results_path = args.discovery_results
    if not discovery_results_path:
        # Try to find discovery results automatically
        discovery_results = path_manager.get_discovery_results()
        if discovery_results:
            discovery_results_path = str(discovery_results)
            logger.info("Found discovery results: {}".format(discovery_results_path))
        else:
            logger.error("No discovery results found. Please specify with --discovery-results")
            sys.exit(1)
    
    # Check if file exists
    if not os.path.exists(discovery_results_path):
        logger.error("Discovery results file not found: {}".format(discovery_results_path))
        sys.exit(1)
    
    # Generate from discovery results
    generated_files = generator.generate_from_discovery_results(discovery_results_path)
    print("Generated {} page objects and {} test files".format(
        len(generated_files['page_objects']), len(generated_files['test_files'])
    ))
    
    # Print generated files
    print("\nGenerated page objects:")
    for page_file in generated_files['page_objects']:
        print("  - {}".format(page_file))
    
    print("\nGenerated test files:")
    for test_file in generated_files['test_files']:
        print("  - {}".format(test_file))
    
    print("\nTo run the tests:")
    print("  pytest {}".format(" ".join(generated_files['test_files'])))

if __name__ == "__main__":
    main()

