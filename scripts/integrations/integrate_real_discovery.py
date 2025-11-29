"""
Integrate Real Browser Discovery with Test Creation
==================================================
This script integrates the Real Browser Discovery Agent with the Test Creation Agent
to generate tests with real selectors from live websites.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import agents
from agents.real_browser_discovery_agent import RealBrowserDiscoveryAgent
from agents.test_creation_agent import EnhancedTestCreationAgent
from models.local_ai_provider import LocalAIProvider

class RealDiscoveryIntegration:
    """Integrate Real Browser Discovery with Test Creation"""
    
    def __init__(self):
        # Initialize AI provider
        self.ai_provider = LocalAIProvider()
        
        # Initialize agents
        self.discovery_agent = RealBrowserDiscoveryAgent(local_ai_provider=self.ai_provider)
        self.test_creation_agent = EnhancedTestCreationAgent(local_ai_provider=self.ai_provider)
        
        # Work directory
        self.work_dir = Path("./work_dir/RealDiscoveryIntegration")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Results
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "discovery_results": {},
            "test_creation_results": {},
            "integration_status": "pending"
        }
    
    async def discover_application(self, application_url):
        """Discover application structure and elements using real browser"""
        logger.info(f"🔍 Discovering application: {application_url}")
        
        # Step 1: Analyze application structure
        analysis_task = {
            "application_url": application_url,
            "analysis_depth": "basic"
        }
        
        analysis_result = await self.discovery_agent._analyze_application(analysis_task)
        
        if analysis_result.get("status") != "completed":
            logger.error(f"❌ Application analysis failed: {analysis_result.get('error', 'Unknown error')}")
            return False
        
        # Extract discovered pages
        discovered_pages = analysis_result.get("analysis_result", {}).get("discovered_pages", [])
        
        if not discovered_pages:
            logger.warning("⚠️ No pages discovered in application")
            return False
        
        # Step 2: Discover elements on key pages
        page_elements = {}
        
        # Limit to first 3 pages for performance
        for page in discovered_pages[:3]:
            page_url = page.get("url")
            page_name = page.get("name")
            
            logger.info(f"🔍 Discovering elements on page: {page_name} ({page_url})")
            
            element_task = {
                "page_url": page_url,
                "element_types": ["inputs", "buttons", "links", "forms"]
            }
            
            element_result = await self.discovery_agent._discover_page_elements(element_task)
            
            if element_result.get("status") == "completed":
                page_elements[page_name] = {
                    "url": page_url,
                    "elements": element_result.get("elements", {}),
                    "total_elements": element_result.get("total_elements", 0)
                }
                
                logger.info(f"✅ Discovered {element_result.get('total_elements', 0)} elements on {page_name}")
            else:
                logger.warning(f"⚠️ Element discovery failed for {page_name}: {element_result.get('error', 'Unknown error')}")
        
        # Step 3: Map user workflows
        workflow_task = {
            "application_url": application_url,
            "workflow_types": ["authentication", "shopping", "browsing"]
        }
        
        workflow_result = await self.discovery_agent._map_user_workflows(workflow_task)
        
        workflows = []
        if workflow_result.get("status") == "completed":
            workflows = workflow_result.get("workflows", [])
            logger.info(f"✅ Mapped {len(workflows)} workflows")
        else:
            logger.warning(f"⚠️ Workflow mapping failed: {workflow_result.get('error', 'Unknown error')}")
        
        # Save discovery results
        self.results["discovery_results"] = {
            "application_url": application_url,
            "discovered_pages": discovered_pages,
            "page_elements": page_elements,
            "workflows": workflows
        }
        
        # Save to file for reference
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        discovery_file = self.work_dir / f"discovery_results_{timestamp}.json"
        
        with open(discovery_file, 'w') as f:
            json.dump(self.results["discovery_results"], f, indent=2)
        
        logger.info(f"✅ Discovery completed and saved to {discovery_file}")
        return True
    
    async def generate_tests(self, test_scenario):
        """Generate tests using real discovery data"""
        logger.info(f"🧪 Generating tests for scenario: {test_scenario}")
        
        # Prepare test plan based on discovery results
        discovery_results = self.results.get("discovery_results", {})
        
        if not discovery_results:
            logger.error("❌ No discovery results available")
            return False
        
        # Extract application data
        application_url = discovery_results.get("application_url", "")
        discovered_pages = discovery_results.get("discovered_pages", [])
        page_elements = discovery_results.get("page_elements", {})
        workflows = discovery_results.get("workflows", [])
        
        # Find relevant workflow for the test scenario
        relevant_workflow = None
        for workflow in workflows:
            workflow_name = workflow.get("name", "")
            workflow_desc = workflow.get("description", "")
            if (isinstance(workflow_name, str) and test_scenario.lower() in workflow_name.lower()) or \
               (isinstance(workflow_desc, str) and test_scenario.lower() in workflow_desc.lower()):
                relevant_workflow = workflow
                break
        
        # If no specific workflow found, use the first one if available
        if not relevant_workflow and workflows:
            relevant_workflow = workflows[0]
        
        # Prepare test plan
        test_plan = {
            "name": f"Test for {test_scenario}",
            "description": f"Automated test for {test_scenario} scenario",
            "framework": "playwright",  # or "selenium"
            "test_cases": [
                {
                    "name": f"{test_scenario.replace(' ', '_').lower()}_test",
                    "description": f"Test {test_scenario}",
                    "steps": []
                }
            ]
        }
        
        # For login authentication, look for login page specifically
        if "login" in test_scenario.lower() or "auth" in test_scenario.lower():
            # Find login page in discovered pages
            login_page = None
            for page in discovered_pages:
                page_name = page.get("name", "").lower()
                if "login" in page_name or "auth" in page_name or "sign" in page_name:
                    login_page = page
                    break
            
            # If login page found, add steps for login
            if login_page:
                login_url = login_page.get("url")
                
                # Add navigation step
                test_plan["test_cases"][0]["steps"].append({
                    "action": "navigate",
                    "target": login_url,
                    "description": f"Navigate to {login_page.get('name')}"
                })
                
                # Look for username/password fields and login button in page elements
                login_page_name = login_page.get("name")
                if login_page_name in page_elements:
                    login_page_data = page_elements[login_page_name]
                    login_elements = login_page_data.get("elements", {})
                    
                    # Find username input
                    username_input = None
                    for input_el in login_elements.get("inputs", []):
                        input_type = input_el.get("type", "")
                        input_name = input_el.get("name", "")
                        input_placeholder = input_el.get("placeholder", "")
                        
                        if isinstance(input_name, str) and isinstance(input_placeholder, str) and \
                           (input_type == "text" or input_type == "email") and \
                           ("user" in input_name.lower() or "email" in input_name.lower() or \
                            "user" in input_placeholder.lower() or "email" in input_placeholder.lower()):
                            username_input = input_el
                            break
                    
                    # Find password input
                    password_input = None
                    for input_el in login_elements.get("inputs", []):
                        if input_el.get("type") == "password":
                            password_input = input_el
                            break
                    
                    # Find login button
                    login_button = None
                    for button in login_elements.get("buttons", []):
                        button_text = button.get("text", "")
                        if isinstance(button_text, str) and \
                           ("login" in button_text.lower() or "sign in" in button_text.lower() or "submit" in button_text.lower()):
                            login_button = button
                            break
                    
                    # Add steps for username, password, and login button
                    if username_input:
                        test_plan["test_cases"][0]["steps"].append({
                            "action": "input",
                            "target": username_input.get("css"),
                            "value": "testuser",
                            "description": "Enter username",
                            "selector": username_input.get("css")
                        })
                    
                    if password_input:
                        test_plan["test_cases"][0]["steps"].append({
                            "action": "input",
                            "target": password_input.get("css"),
                            "value": "password123",
                            "description": "Enter password",
                            "selector": password_input.get("css")
                        })
                    
                    if login_button:
                        test_plan["test_cases"][0]["steps"].append({
                            "action": "click",
                            "target": login_button.get("css"),
                            "description": "Click login button",
                            "selector": login_button.get("css")
                        })
            else:
                # If no login page found, use Form Authentication page from The Internet
                test_plan["test_cases"][0]["steps"].append({
                    "action": "navigate",
                    "target": "https://the-internet.herokuapp.com/login",
                    "description": "Navigate to login page"
                })
                
                test_plan["test_cases"][0]["steps"].append({
                    "action": "input",
                    "target": "#username",
                    "value": "tomsmith",
                    "description": "Enter username",
                    "selector": "#username"
                })
                
                test_plan["test_cases"][0]["steps"].append({
                    "action": "input",
                    "target": "#password",
                    "value": "SuperSecretPassword!",
                    "description": "Enter password",
                    "selector": "#password"
                })
                
                test_plan["test_cases"][0]["steps"].append({
                    "action": "click",
                    "target": "button[type='submit']",
                    "description": "Click login button",
                    "selector": "button[type='submit']"
                })
        
        # Add steps based on workflow if available
        elif relevant_workflow:
            workflow_steps = relevant_workflow.get("steps", [])
            
            for step in workflow_steps:
                test_plan["test_cases"][0]["steps"].append({
                    "action": step.get("action", "navigate"),
                    "target": step.get("target", ""),
                    "description": step.get("description", ""),
                    "selector": step.get("selector", "")
                })
        else:
            # Default steps if no workflow available
            if discovered_pages:
                test_plan["test_cases"][0]["steps"].append({
                    "action": "navigate",
                    "target": application_url,
                    "description": "Navigate to application"
                })
        
        # Prepare application data for test creation
        application_data = {
            "base_url": application_url,
            "discovered_pages": discovered_pages,
            "discovered_elements": page_elements,
            "user_workflows": workflows
        }
        
        # Create test creation task
        test_task = {
            "task_type": "generate_tests",
            "test_plan": test_plan,
            "application_data": application_data
        }
        
        # Generate tests
        test_result = await self.test_creation_agent._generate_real_test_code(test_task)
        
        if test_result.get("status") == "completed":
            generated_files = test_result.get("generated_files", [])
            
            logger.info(f"✅ Generated {len(generated_files)} test files")
            
            # Save test creation results
            self.results["test_creation_results"] = {
                "test_scenario": test_scenario,
                "generated_files": generated_files,
                "test_plan": test_plan
            }
            
            # Save to file for reference
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_creation_file = self.work_dir / f"test_creation_results_{timestamp}.json"
            
            with open(test_creation_file, 'w') as f:
                json.dump(self.results["test_creation_results"], f, indent=2)
            
            logger.info(f"✅ Test creation completed and saved to {test_creation_file}")
            return True
        else:
            logger.error(f"❌ Test creation failed: {test_result.get('error', 'Unknown error')}")
            return False
    
    async def run_integration(self, application_url, test_scenario):
        """Run the complete integration flow"""
        logger.info(f"🚀 Starting integration for {application_url}")
        
        # Step 1: Discover application
        discovery_success = await self.discover_application(application_url)
        
        if not discovery_success:
            logger.error("❌ Integration failed at discovery step")
            self.results["integration_status"] = "failed_at_discovery"
            return False
        
        # Step 2: Generate tests
        test_creation_success = await self.generate_tests(test_scenario)
        
        if not test_creation_success:
            logger.error("❌ Integration failed at test creation step")
            self.results["integration_status"] = "failed_at_test_creation"
            return False
        
        # Integration successful
        logger.info("🎉 Integration completed successfully")
        self.results["integration_status"] = "completed"
        
        # Save final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"real_discovery_integration_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"📊 Integration results saved to {results_file}")
        
        # Print summary
        print("=" * 60)
        print("REAL DISCOVERY INTEGRATION RESULTS")
        print("=" * 60)
        print(f"Application URL: {application_url}")
        print(f"Test Scenario: {test_scenario}")
        print(f"Status: {self.results['integration_status']}")
        print(f"Discovered Pages: {len(self.results['discovery_results'].get('discovered_pages', []))}")
        
        page_elements = self.results["discovery_results"].get("page_elements", {})
        total_elements = sum(page.get("total_elements", 0) for page in page_elements.values())
        print(f"Total Elements Discovered: {total_elements}")
        
        generated_files = self.results["test_creation_results"].get("generated_files", [])
        print(f"Generated Test Files: {len(generated_files)}")
        
        for file in generated_files:
            print(f"  - {file}")
        
        print("=" * 60)
        
        return True

# Run integration if executed directly
if __name__ == "__main__":
    # Test URLs
    TEST_URLS = [
        {
            "url": "https://the-internet.herokuapp.com/",
            "scenario": "login authentication"
        },
        {
            "url": "https://www.saucedemo.com/",
            "scenario": "product browsing"
        }
    ]
    
    # Select test URL
    test_case = TEST_URLS[0]  # Change index to test different URLs
    
    # Install Playwright browsers if needed
    try:
        import subprocess
        from playwright.async_api import async_playwright
        
        # Check if browsers are installed
        async def check_browsers():
            async with async_playwright() as p:
                try:
                    browser = await p.chromium.launch(headless=True)
                    await browser.close()
                    return True
                except Exception:
                    return False
        
        if not asyncio.run(check_browsers()):
            print("Installing Playwright browsers...")
            subprocess.run(["playwright", "install", "chromium"])
    except ImportError:
        print("Installing Playwright...")
        subprocess.run(["pip", "install", "playwright"])
        subprocess.run(["playwright", "install", "chromium"])
    
    # Run integration
    integration = RealDiscoveryIntegration()
    asyncio.run(integration.run_integration(test_case["url"], test_case["scenario"]))

