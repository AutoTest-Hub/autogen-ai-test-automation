#!/usr/bin/env python3
"""
Test Discovery Agent
===================
Test the Discovery Agent's ability to analyze applications and discover elements.
"""

import asyncio
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Discovery Agent
from agents.discovery_agent import DiscoveryAgent
from models.local_ai_provider import LocalAIProvider

class DiscoveryAgentTester:
    """Test Discovery Agent capabilities"""
    
    def __init__(self):
        # Initialize with local AI provider
        self.ai_provider = LocalAIProvider()
        self.discovery_agent = DiscoveryAgent(local_ai_provider=self.ai_provider)
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    async def test_application_analysis(self):
        """Test full application analysis"""
        logger.info("🧪 Testing application analysis")
        
        try:
            # Test with Advantage Online Shopping
            task_data = {
                "application_url": "https://advantageonlineshopping.com",
                "analysis_depth": "basic"
            }
            
            result = await self.discovery_agent._analyze_application(task_data)
            
            logger.info(f"Analysis Status: {result.get('status')}")
            if result.get('status') == 'completed':
                analysis = result.get('analysis_result', {})
                logger.info(f"Pages Discovered: {len(analysis.get('discovered_pages', []))}")
                logger.info(f"Elements Analyzed: {result.get('elements_analyzed', 0)}")
                logger.info(f"Workflows Identified: {result.get('workflows_identified', 0)}")
                
                # Log discovered pages
                for page in analysis.get('discovered_pages', []):
                    logger.info(f"  📄 {page['name']}: {page['url']}")
                
                # Log workflows
                for workflow in analysis.get('user_workflows', []):
                    logger.info(f"  🔄 {workflow['name']}: {len(workflow['steps'])} steps")
                
                # Log recommendations
                for rec in analysis.get('recommendations', []):
                    logger.info(f"  💡 {rec['title']}: {rec['description']}")
            
            self.test_results["tests"]["application_analysis"] = {
                "status": result.get('status'),
                "success": result.get('status') == 'completed',
                "details": result
            }
            
            return result.get('status') == 'completed'
            
        except Exception as e:
            logger.error(f"Application analysis test failed: {str(e)}")
            self.test_results["tests"]["application_analysis"] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
            return False
    
    async def test_page_element_discovery(self):
        """Test page element discovery"""
        logger.info("🧪 Testing page element discovery")
        
        try:
            task_data = {
                "page_url": "https://advantageonlineshopping.com/login",
                "element_types": ["forms", "buttons", "links"]
            }
            
            result = await self.discovery_agent._discover_page_elements(task_data)
            
            logger.info(f"Element Discovery Status: {result.get('status')}")
            if result.get('status') == 'completed':
                elements = result.get('elements', {})
                logger.info(f"Total Elements Found: {result.get('total_elements', 0)}")
                
                for element_type, element_list in elements.items():
                    logger.info(f"  {element_type}: {len(element_list)} elements")
                    for element in element_list[:2]:  # Show first 2 elements
                        logger.info(f"    - {element.get('name', 'Unknown')}: {element.get('selector', 'No selector')}")
            
            self.test_results["tests"]["page_element_discovery"] = {
                "status": result.get('status'),
                "success": result.get('status') == 'completed',
                "details": result
            }
            
            return result.get('status') == 'completed'
            
        except Exception as e:
            logger.error(f"Page element discovery test failed: {str(e)}")
            self.test_results["tests"]["page_element_discovery"] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
            return False
    
    async def test_workflow_mapping(self):
        """Test workflow mapping"""
        logger.info("🧪 Testing workflow mapping")
        
        try:
            task_data = {
                "application_url": "https://advantageonlineshopping.com",
                "workflow_types": ["authentication", "shopping", "browsing"]
            }
            
            result = await self.discovery_agent._map_user_workflows(task_data)
            
            logger.info(f"Workflow Mapping Status: {result.get('status')}")
            if result.get('status') == 'completed':
                workflows = result.get('workflows', [])
                logger.info(f"Total Workflows Mapped: {result.get('total_workflows', 0)}")
                
                for workflow in workflows:
                    logger.info(f"  🔄 {workflow['name']} ({workflow['type']})")
                    logger.info(f"    Steps: {len(workflow['steps'])}")
                    logger.info(f"    Test Scenarios: {len(workflow['test_scenarios'])}")
            
            self.test_results["tests"]["workflow_mapping"] = {
                "status": result.get('status'),
                "success": result.get('status') == 'completed',
                "details": result
            }
            
            return result.get('status') == 'completed'
            
        except Exception as e:
            logger.error(f"Workflow mapping test failed: {str(e)}")
            self.test_results["tests"]["workflow_mapping"] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
            return False
    
    async def test_selector_generation(self):
        """Test element selector generation"""
        logger.info("🧪 Testing selector generation")
        
        try:
            task_data = {
                "page_url": "https://advantageonlineshopping.com/login",
                "element_descriptions": [
                    "Login button",
                    "Username input field",
                    "Password input field",
                    "Search box"
                ]
            }
            
            result = await self.discovery_agent._generate_element_selectors(task_data)
            
            logger.info(f"Selector Generation Status: {result.get('status')}")
            if result.get('status') == 'completed':
                selectors = result.get('generated_selectors', [])
                logger.info(f"Total Selectors Generated: {result.get('total_elements', 0)}")
                
                for selector_info in selectors:
                    logger.info(f"  🎯 {selector_info['description']}")
                    recommended = selector_info['recommended']
                    logger.info(f"    Recommended: {recommended['type']} = {recommended['value']}")
                    logger.info(f"    Alternatives: {len(selector_info['selectors']) - 1}")
            
            self.test_results["tests"]["selector_generation"] = {
                "status": result.get('status'),
                "success": result.get('status') == 'completed',
                "details": result
            }
            
            return result.get('status') == 'completed'
            
        except Exception as e:
            logger.error(f"Selector generation test failed: {str(e)}")
            self.test_results["tests"]["selector_generation"] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all Discovery Agent tests"""
        logger.info("🚀 Starting Discovery Agent Tests")
        
        # Run tests
        test1 = await self.test_application_analysis()
        test2 = await self.test_page_element_discovery()
        test3 = await self.test_workflow_mapping()
        test4 = await self.test_selector_generation()
        
        # Calculate summary
        total_tests = 4
        passed_tests = sum([test1, test2, test3, test4])
        success_rate = (passed_tests / total_tests) * 100
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate
        }
        
        # Save results
        results_file = f"discovery_agent_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"📊 Discovery Agent Test Results:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Results saved to: {results_file}")
        
        return self.test_results

async def main():
    """Main test function"""
    tester = DiscoveryAgentTester()
    results = await tester.run_all_tests()
    
    print("\n" + "="*60)
    print("DISCOVERY AGENT TEST RESULTS")
    print("="*60)
    
    summary = results["summary"]
    print(f"\nOverall Results:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed_tests']}")
    print(f"  Failed: {summary['failed_tests']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    
    print(f"\nTest Details:")
    for test_name, test_result in results["tests"].items():
        status = "✅ PASS" if test_result["success"] else "❌ FAIL"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
        if not test_result["success"] and "error" in test_result:
            print(f"    Error: {test_result['error']}")
    
    if summary['success_rate'] == 100:
        print(f"\n🎉 All Discovery Agent tests passed!")
        print(f"The Discovery Agent is ready to analyze applications and discover elements.")
    elif summary['success_rate'] >= 75:
        print(f"\n⚠️ Most Discovery Agent tests passed.")
        print(f"The agent is mostly functional but may need minor fixes.")
    else:
        print(f"\n🚨 Discovery Agent needs significant work.")
        print(f"Multiple tests failed - check the detailed results.")

if __name__ == "__main__":
    asyncio.run(main())

