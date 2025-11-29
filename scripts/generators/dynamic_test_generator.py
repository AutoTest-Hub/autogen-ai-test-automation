#!/usr/bin/env python3
"""
Dynamic Test Generator
=====================
This script dynamically generates test files and page objects based on discovered elements.
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

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
        # Create directories if they don't exist
        self.tests_dir = Path("./tests")
        self.pages_dir = Path("./pages")
        self.utils_dir = Path("./utils")
        
        self.tests_dir.mkdir(exist_ok=True)
        self.pages_dir.mkdir(exist_ok=True)
        self.utils_dir.mkdir(exist_ok=True)
        
        # Templates directory
        self.templates_dir = Path("./templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default templates if they don't exist"""
        # Test file template
        test_template_path = self.templates_dir / "test_template.py.txt"
        if not test_template_path.exists():
            test_template = '''"""
{test_name} Test
==============
{test_description}
"""

import pytest
import logging
from datetime import datetime

from pages.{page_module} import {page_class}

class {test_class}:
    """Test class for {test_name}"""
    
    @pytest.mark.asyncio
    async def test_{test_function}(self, browser_setup):
        """
        Test {test_name}
        
        Args:
            browser_setup: Browser setup fixture
        """
        page, browser, context, playwright = browser_setup
        
        try:
            # Initialize page object
            {page_var} = {page_class}(page)
            
            # Navigate to page
            await {page_var}.navigate()
            
            # Take screenshot before actions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/{test_function}_before_{{timestamp}}.png")
            
{test_steps}
            
            # Take screenshot after actions
            await page.screenshot(path=f"screenshots/{test_function}_after_{{timestamp}}.png")
            
{assertions}
            
        except Exception as e:
            # Take screenshot on failure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/{test_function}_failure_{{timestamp}}.png")
            
            logging.error(f"Test failed: {{str(e)}}")
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
{page_name} Page Object
======================
Page object for {page_name} page.
"""

from pages.base_page import BasePage

class {page_class}(BasePage):
    """Page object for {page_name} page"""
    
    def __init__(self, page):
        """
        Initialize {page_name} page object
        
        Args:
            page: Playwright page object
        """
        super().__init__(page)
        self.url = "{page_url}"  # URL path relative to base URL
        
        # Element selectors
{element_selectors}
    
{element_methods}
'''
            with open(page_template_path, 'w') as f:
                f.write(page_template)
    
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
        logger.info(f"Generating test file for {test_name}")
        
        # Prepare variables
        test_class = f"Test{test_name.replace('_', ' ').title().replace(' ', '')}"
        test_function = test_name.lower().replace(' ', '_')
        page_class = f"{page_name.replace('_', ' ').title().replace(' ', '')}Page"
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
                steps_code.append(f"            # {description}")
                steps_code.append(f"            await page.goto(\"{target}\")")
                steps_code.append(f"            await page.wait_for_load_state(\"networkidle\")")
                steps_code.append("")
            elif action == "click":
                steps_code.append(f"            # {description}")
                steps_code.append(f"            await {page_var}.click(\"{target}\")")
                steps_code.append(f"            await page.wait_for_load_state(\"networkidle\")")
                steps_code.append("")
            elif action == "input":
                steps_code.append(f"            # {description}")
                steps_code.append(f"            await {page_var}.fill(\"{target}\", \"{value}\")")
                steps_code.append("")
            elif action == "assert":
                steps_code.append(f"            # {description}")
                steps_code.append(f"            assert await {page_var}.is_visible(\"{target}\"), \"{description} failed\"")
                steps_code.append("")
        
        # Generate assertions
        assertions = []
        assertions.append("            # Add assertions here")
        assertions.append("            assert await page.title() != \"\", \"Page title should not be empty\"")
        
        # Load template
        template_path = self.templates_dir / "test_template.py.txt"
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Fill template
        test_content = template.format(
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
        test_file_path = self.tests_dir / f"test_{test_function}.py"
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        logger.info(f"Generated test file: {test_file_path}")
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
        logger.info(f"Generating page object for {page_name}")
        
        # Prepare variables
        page_class = f"{page_name.replace('_', ' ').title().replace(' ', '')}Page"
        
        # Generate element selectors
        element_selectors = []
        
        # Process inputs
        for input_el in elements.get("inputs", []):
            name = input_el.get("id") or input_el.get("name") or f"{input_el.get('type', 'input')}_{len(element_selectors) + 1}"
            name = name.lower().replace('-', '_').replace(' ', '_')
            selector = input_el.get("css", "")
            element_selectors.append(f"        self.{name}_selector = \"{selector}\"")
        
        # Process buttons
        for button in elements.get("buttons", []):
            name = button.get("id") or button.get("text", "").lower().replace(' ', '_') or f"button_{len(element_selectors) + 1}"
            name = name.lower().replace('-', '_').replace(' ', '_')
            selector = button.get("css", "")
            element_selectors.append(f"        self.{name}_selector = \"{selector}\"")
        
        # Process links
        for link in elements.get("links", []):
            name = link.get("id") or link.get("text", "").lower().replace(' ', '_') or f"link_{len(element_selectors) + 1}"
            name = name.lower().replace('-', '_').replace(' ', '_')
            selector = link.get("css", "")
            element_selectors.append(f"        self.{name}_selector = \"{selector}\"")
        
        # Generate element methods
        element_methods = []
        
        # Methods for inputs
        element_methods.append("    # Input methods")
        for input_el in elements.get("inputs", []):
            name = input_el.get("id") or input_el.get("name") or f"{input_el.get('type', 'input')}_{len(element_selectors) + 1}"
            name = name.lower().replace('-', '_').replace(' ', '_')
            method_name = f"fill_{name}"
            
            element_methods.append(f"""
    async def {method_name}(self, value):
        """
        Fill {name} input
        
        Args:
            value: Value to fill
        """
        await self.fill(self.{name}_selector, value)""")
        
        # Methods for buttons
        element_methods.append("\n    # Button methods")
        for button in elements.get("buttons", []):
            name = button.get("id") or button.get("text", "").lower().replace(' ', '_') or f"button_{len(element_selectors) + 1}"
            name = name.lower().replace('-', '_').replace(' ', '_')
            method_name = f"click_{name}"
            
            element_methods.append(f"""
    async def {method_name}(self):
        """Click {name} button"""
        await self.click(self.{name}_selector)""")
        
        # Methods for links
        element_methods.append("\n    # Link methods")
        for link in elements.get("links", []):
            name = link.get("id") or link.get("text", "").lower().replace(' ', '_') or f"link_{len(element_selectors) + 1}"
            name = name.lower().replace('-', '_').replace(' ', '_')
            method_name = f"click_{name}"
            
            element_methods.append(f"""
    async def {method_name}(self):
        """Click {name} link"""
        await self.click(self.{name}_selector)""")
        
        # Load template
        template_path = self.templates_dir / "page_template.py.txt"
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Fill template
        page_content = template.format(
            page_name=page_name.replace('_', ' ').title(),
            page_class=page_class,
            page_url=page_url,
            element_selectors="\n".join(element_selectors),
            element_methods="\n".join(element_methods)
        )
        
        # Write page object file
        page_file_path = self.pages_dir / f"{page_name.lower().replace(' ', '_')}_page.py"
        with open(page_file_path, 'w') as f:
            f.write(page_content)
        
        logger.info(f"Generated page object: {page_file_path}")
        return str(page_file_path)
    
    def generate_from_discovery_results(self, discovery_results_path: str) -> Dict[str, Any]:
        """
        Generate test files and page objects from discovery results
        
        Args:
            discovery_results_path: Path to discovery results JSON file
            
        Returns:
            Dict[str, Any]: Dictionary with generated files
        """
        logger.info(f"Generating from discovery results: {discovery_results_path}")
        
        # Load discovery results
        with open(discovery_results_path, 'r') as f:
            discovery_results = json.load(f)
        
        # Extract data
        application_url = discovery_results.get("application_url", "")
        discovered_pages = discovery_results.get("discovered_pages", [])
        page_elements = discovery_results.get("page_elements", {})
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
            test_name = f"{page_name.lower().replace(' ', '_')}_test"
            test_description = f"Test for {page_name} page"
            
            # Create test steps
            test_steps = []
            
            # Add navigation step
            test_steps.append({
                "action": "navigate",
                "target": page_url,
                "description": f"Navigate to {page_name} page"
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
                        "description": f"Fill {input_el.get('id') or input_el.get('name') or 'input'} field"
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
                    "description": f"Click {button.get('text') or button.get('id') or 'button'}"
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
                        f"{workflow_name}_workflow",
                        workflow_description or f"Test for {workflow_name} workflow",
                        first_page_name,
                        first_page_url,
                        workflow_steps
                    )
                    generated_files["test_files"].append(test_file)
        
        logger.info(f"Generated {len(generated_files['page_objects'])} page objects and {len(generated_files['test_files'])} test files")
        return generated_files

async def main():
    """Main function"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Dynamic Test Generator")
    parser.add_argument("--discovery-results", "-d", help="Path to discovery results JSON file")
    args = parser.parse_args()
    
    # Create generator
    generator = DynamicTestGenerator()
    
    if args.discovery_results:
        # Generate from discovery results
        generated_files = generator.generate_from_discovery_results(args.discovery_results)
        print(f"Generated {len(generated_files['page_objects'])} page objects and {len(generated_files['test_files'])} test files")
    else:
        # Example usage
        print("No discovery results provided. Use --discovery-results to specify a JSON file.")
        print("Example: python dynamic_test_generator.py --discovery-results work_dir/RealDiscoveryIntegration/discovery_results_20250907_215341.json")

if __name__ == "__main__":
    asyncio.run(main())

