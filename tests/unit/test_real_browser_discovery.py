"""
Test Real Browser Discovery Agent
================================
Test the Real Browser Discovery Agent's ability to analyze applications and discover elements.
"""

import asyncio
import json
import logging
from datetime import datetime
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Real Browser Discovery Agent
from agents.real_browser_discovery_agent import RealBrowserDiscoveryAgent
from models.local_ai_provider import LocalAIProvider

class RealBrowserDiscoveryTester:
    """Test Real Browser Discovery Agent capabilities"""
    
    def __init__(self):
        # Initialize with local AI provider
        self.ai_provider = LocalAIProvider()
        self.discovery_agent = RealBrowserDiscoveryAgent(local_ai_provider=self.ai_provider)
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
        # Ensure screenshots directory exists
        self.screenshots_dir = Path("./screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    async def test_page_element_discovery(self):
        """Test real browser element discovery"""
        logger.info("🧪 Testing real browser element discovery")
        
        try:
            # Test with a simple login page
            task_data = {
                "page_url": "https://the-internet.herokuapp.com/login",
                "element_types": ["inputs", "buttons", "forms"]
            }
            
            result = await self.discovery_agent._discover_page_elements(task_data)
            
            logger.info(f"Element Discovery Status: {result.get('status')}")
            if result.get('status') == 'completed':
                elements = result.get('elements', {})
                total_elements = result.get('total_elements', 0)
                
                logger.info(f"Total Elements Found: {total_elements}")
                
                # Log discovered elements by type
                for element_type, type_elements in elements.items():
                    logger.info(f"  {element_type}: {len(type_elements)} elements")
                    
                    # Log first 3 elements of each type
                    for i, element in enumerate(type_elements[:3]):
                        if element_type == "inputs":
                            logger.info(f"    - {element.get('type', 'unknown')} input: {element.get('css', 'no selector')}")
                        elif element_type == "buttons":
                            logger.info(f"    - button: {element.get('text', 'no text')} - {element.get('css', 'no selector')}")
                        elif element_type == "forms":
                            logger.info(f"    - form: {element.get('action', 'no action')} - {element.get('css', 'no selector')}")
                        elif element_type == "links":
                            logger.info(f"    - link: {element.get('text', 'no text')} - {element.get('css', 'no selector')}")
                
                # Save screenshot path for reference
                screenshot_path = result.get('screenshot')
                if screenshot_path:
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                
                self.test_results["tests"]["page_element_discovery"] = {
                    "status": "passed",
                    "total_elements": total_elements,
                    "element_types": list(elements.keys()),
                    "screenshot": screenshot_path
                }
                return True
            else:
                error = result.get('error', 'Unknown error')
                logger.error(f"Element Discovery Failed: {error}")
                self.test_results["tests"]["page_element_discovery"] = {
                    "status": "failed",
                    "error": error
                }
                return False
                
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}")
            self.test_results["tests"]["page_element_discovery"] = {
                "status": "failed",
                "error": str(e)
            }
            return False
    
    async def test_element_selector_generation(self):
        """Test accurate element selector generation"""
        logger.info("🧪 Testing element selector generation")
        
        try:
            # Test with specific element descriptions
            task_data = {
                "page_url": "https://the-internet.herokuapp.com/login",
                "element_descriptions": [
                    "username input",
                    "password input",
                    "login button",
                    "forgot password link"
                ]
            }
            
            result = await self.discovery_agent._generate_element_selectors(task_data)
            
            logger.info(f"Selector Generation Status: {result.get('status')}")
            if result.get('status') == 'completed':
                selectors = result.get('generated_selectors', [])
                total_selectors = result.get('total_elements', 0)
                
                logger.info(f"Total Selectors Generated: {total_selectors}")
                
                # Log generated selectors
                for selector_info in selectors:
                    description = selector_info.get('description', 'unknown')
                    recommended = selector_info.get('recommended', {})
                    alternatives = len(selector_info.get('selectors', [])) - 1
                    
                    logger.info(f"  🎯 {description}")
                    logger.info(f"    Recommended: {recommended.get('type', 'css')} = {recommended.get('value', 'unknown')}")
                    logger.info(f"    Alternatives: {alternatives}")
                
                # Save screenshot path for reference
                screenshot_path = result.get('screenshot')
                if screenshot_path:
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                
                self.test_results["tests"]["element_selector_generation"] = {
                    "status": "passed",
                    "total_selectors": total_selectors,
                    "selectors": [s.get('description') for s in selectors],
                    "screenshot": screenshot_path
                }
                return True
            else:
                error = result.get('error', 'Unknown error')
                logger.error(f"Selector Generation Failed: {error}")
                self.test_results["tests"]["element_selector_generation"] = {
                    "status": "failed",
                    "error": error
                }
                return False
                
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}")
            self.test_results["tests"]["element_selector_generation"] = {
                "status": "failed",
                "error": str(e)
            }
            return False
    
    async def test_application_analysis(self):
        """Test full application analysis with real browser"""
        logger.info("🧪 Testing application analysis with real browser")
        
        try:
            # Test with a simple demo site
            task_data = {
                "application_url": "https://the-internet.herokuapp.com/",
                "analysis_depth": "basic"
            }
            
            result = await self.discovery_agent._analyze_application(task_data)
            
            logger.info(f"Application Analysis Status: {result.get('status')}")
            if result.get('status') == 'completed':
                analysis = result.get('analysis_result', {})
                
                # Log discovered pages
                pages = analysis.get('discovered_pages', [])
                logger.info(f"Discovered Pages: {len(pages)}")
                for i, page in enumerate(pages[:5]):  # Show first 5 pages
                    logger.info(f"  📄 {page.get('name', 'unknown')}: {page.get('url', 'no url')}")
                
                # Log navigation structure
                navigation = analysis.get('navigation', [])
                logger.info(f"Navigation Links: {len(navigation)}")
                for i, nav in enumerate(navigation[:5]):  # Show first 5 navigation items
                    logger.info(f"  🔗 {nav.get('text', 'unknown')}: {nav.get('href', 'no url')}")
                
                # Log main page elements
                main_elements = analysis.get('main_page_elements', {})
                for element_type, elements in main_elements.items():
                    logger.info(f"  {element_type}: {len(elements)} elements")
                
                # Save screenshot path for reference
                screenshot_path = analysis.get('screenshot')
                if screenshot_path:
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                
                self.test_results["tests"]["application_analysis"] = {
                    "status": "passed",
                    "discovered_pages": len(pages),
                    "navigation_links": len(navigation),
                    "screenshot": screenshot_path
                }
                return True
            else:
                error = result.get('error', 'Unknown error')
                logger.error(f"Application Analysis Failed: {error}")
                self.test_results["tests"]["application_analysis"] = {
                    "status": "failed",
                    "error": error
                }
                return False
                
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}")
            self.test_results["tests"]["application_analysis"] = {
                "status": "failed",
                "error": str(e)
            }
            return False
    
    async def test_workflow_mapping(self):
        """Test workflow mapping with real browser"""
        logger.info("🧪 Testing workflow mapping with real browser")
        
        try:
            # Test with a simple e-commerce demo
            task_data = {
                "application_url": "https://www.saucedemo.com/",
                "workflow_types": ["authentication", "shopping"]
            }
            
            result = await self.discovery_agent._map_user_workflows(task_data)
            
            logger.info(f"Workflow Mapping Status: {result.get('status')}")
            if result.get('status') == 'completed':
                workflows = result.get('workflows', [])
                total_workflows = result.get('total_workflows', 0)
                
                logger.info(f"Total Workflows Mapped: {total_workflows}")
                
                # Log mapped workflows
                for workflow in workflows:
                    name = workflow.get('name', 'unknown')
                    workflow_type = workflow.get('type', 'unknown')
                    steps = len(workflow.get('steps', []))
                    scenarios = len(workflow.get('test_scenarios', []))
                    
                    logger.info(f"  🔄 {name} ({workflow_type})")
                    logger.info(f"    Steps: {steps}")
                    logger.info(f"    Test Scenarios: {scenarios}")
                
                # Save screenshot path for reference
                screenshot_path = result.get('screenshot')
                if screenshot_path:
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                
                self.test_results["tests"]["workflow_mapping"] = {
                    "status": "passed",
                    "total_workflows": total_workflows,
                    "workflow_types": [w.get('type') for w in workflows],
                    "screenshot": screenshot_path
                }
                return True
            else:
                error = result.get('error', 'Unknown error')
                logger.error(f"Workflow Mapping Failed: {error}")
                self.test_results["tests"]["workflow_mapping"] = {
                    "status": "failed",
                    "error": error
                }
                return False
                
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}")
            self.test_results["tests"]["workflow_mapping"] = {
                "status": "failed",
                "error": str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all tests and generate summary"""
        logger.info("🧪 Running all Real Browser Discovery Agent tests")
        
        # Run all tests
        element_discovery_result = await self.test_page_element_discovery()
        selector_generation_result = await self.test_element_selector_generation()
        application_analysis_result = await self.test_application_analysis()
        workflow_mapping_result = await self.test_workflow_mapping()
        
        # Calculate summary
        total_tests = 4
        passed_tests = sum([
            element_discovery_result,
            selector_generation_result,
            application_analysis_result,
            workflow_mapping_result
        ])
        
        success_rate = (passed_tests / total_tests) * 100
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate
        }
        
        # Save test results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"real_browser_discovery_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"📊 Real Browser Discovery Agent Test Results:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Success Rate: {success_rate}%")
        logger.info(f"   Results saved to: {results_file}")
        
        # Print summary in a nice format
        print("=" * 60)
        print("REAL BROWSER DISCOVERY AGENT TEST RESULTS")
        print("=" * 60)
        print("Overall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {success_rate}%")
        print("Test Details:")
        print(f"  {'✅' if element_discovery_result else '❌'} {'PASS' if element_discovery_result else 'FAIL'} Page Element Discovery")
        print(f"  {'✅' if selector_generation_result else '❌'} {'PASS' if selector_generation_result else 'FAIL'} Element Selector Generation")
        print(f"  {'✅' if application_analysis_result else '❌'} {'PASS' if application_analysis_result else 'FAIL'} Application Analysis")
        print(f"  {'✅' if workflow_mapping_result else '❌'} {'PASS' if workflow_mapping_result else 'FAIL'} Workflow Mapping")
        
        if passed_tests == total_tests:
            print("🎉 All Real Browser Discovery Agent tests passed!")
            print("The Real Browser Discovery Agent is ready to analyze applications and discover elements.")
        else:
            print("⚠️ Some tests failed. Check the logs for details.")
        
        return self.test_results

# Run tests if executed directly
if __name__ == "__main__":
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
    
    # Run tests
    tester = RealBrowserDiscoveryTester()
    asyncio.run(tester.run_all_tests())

