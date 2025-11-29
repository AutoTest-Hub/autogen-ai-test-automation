#!/usr/bin/env python3
"""
Test Agent Communication and Data Flow
=====================================
This script tests whether our agents can actually communicate and pass data
between each other in a meaningful way.
"""

import asyncio
import json
import logging
import tempfile
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our agents
from agents.planning_agent import PlanningAgent
from agents.test_creation_agent import EnhancedTestCreationAgent as TestCreationAgent
from agents.review_agent import ReviewAgent
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent
from models.local_ai_provider import LocalAIProvider

class AgentCommunicationTester:
    """Test agent communication and data flow"""
    
    def __init__(self):
        self.ai_provider = LocalAIProvider()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "data_flow": {},
            "issues_found": []
        }
    
    async def test_planning_to_test_creation_flow(self):
        """Test if Planning Agent output can be used by Test Creation Agent"""
        logger.info("🧪 Testing Planning → Test Creation data flow")
        
        try:
            # Create a real scenario
            scenario = {
                "testName": "Advantage Online Shopping Login Test",
                "description": "Test user login functionality on Advantage Online Shopping website",
                "testSteps": [
                    "Navigate to https://advantageonlineshopping.com",
                    "Click on user menu icon",
                    "Enter username: testuser@example.com",
                    "Enter password: TestPass123",
                    "Click login button",
                    "Verify user is logged in successfully"
                ],
                "expectedResults": [
                    "Login page should load",
                    "Username field should accept input",
                    "Password field should accept input", 
                    "Login should succeed",
                    "User menu should show logged in state"
                ],
                "priority": "High",
                "tags": ["login", "authentication", "ui"]
            }
            
            # Step 1: Planning Agent creates plan
            planning_agent = PlanningAgent()
            
            # Use the correct method - process_task instead of create_test_plan
            task_data = {
                "task_type": "planning",
                "test_files": [scenario]
            }
            planning_result = await planning_agent.process_task(task_data)
            
            logger.info(f"Planning Agent Result: {json.dumps(planning_result, indent=2)}")
            
            # Step 2: Test Creation Agent uses planning result
            test_creation_agent = TestCreationAgent()
            
            # Check if planning result has the right structure for test creation
            if 'test_plan' in planning_result:
                # Use the correct method - process_task with Enhanced Agent task type
                creation_task = {
                    "task_type": "generate_tests",  # Changed from "test_creation" to "generate_tests"
                    "test_plan": planning_result['test_plan'],
                    "application_url": "https://example.com"  # Added required field
                }
                creation_result = await test_creation_agent.process_task(creation_task)
                logger.info(f"Test Creation Result: {json.dumps(creation_result, indent=2)}")
                
                # Validate data flow
                data_flow_success = self._validate_data_flow(planning_result, creation_result)
                
                self.test_results["tests"]["planning_to_creation"] = {
                    "success": True,
                    "planning_output": planning_result,
                    "creation_input_valid": data_flow_success,
                    "creation_output": creation_result
                }
                
                return True, planning_result, creation_result
            else:
                self.test_results["issues_found"].append("Planning Agent output missing 'test_plan' key")
                return False, planning_result, None
                
        except Exception as e:
            logger.error(f"Planning → Test Creation flow failed: {str(e)}")
            self.test_results["issues_found"].append(f"Planning → Test Creation flow error: {str(e)}")
            return False, None, None
    
    async def test_creation_to_review_flow(self, creation_result):
        """Test if Test Creation output can be used by Review Agent"""
        logger.info("🧪 Testing Test Creation → Review data flow")
        
        try:
            if not creation_result:
                logger.warning("No creation result to test with")
                return False
            
            # Step 3: Review Agent reviews the created tests
            review_agent = ReviewAgent()
            
            # Check if creation result has test files to review (Enhanced Agent structure)
            test_files = creation_result.get('generated_files', [])
            artifacts = creation_result.get('artifacts', [])
            
            if test_files or artifacts or creation_result.get('status') == 'success':
                # Use the correct method - process_task
                review_task = {
                    "task_type": "review_tests",  # Updated task type
                    "test_files": test_files,
                    "artifacts": artifacts,
                    "creation_result": creation_result
                }
                review_result = await review_agent.process_task(review_task)
                logger.info(f"Review Result: {json.dumps(review_result, indent=2)}")
                
                self.test_results["tests"]["creation_to_review"] = {
                    "success": True,
                    "creation_output": creation_result,
                    "review_output": review_result
                }
                
                return True, review_result
            else:
                self.test_results["issues_found"].append("Test Creation output missing test files for review (Enhanced Agent)")
                logger.warning("Creation result doesn't have test files or success status")
                return False, None
                
        except Exception as e:
            logger.error(f"Test Creation → Review flow failed: {str(e)}")
            self.test_results["issues_found"].append(f"Test Creation → Review flow error: {str(e)}")
            return False, None
    
    async def test_review_to_execution_flow(self, review_result):
        """Test if Review output can be used by Execution Agent"""
        logger.info("🧪 Testing Review → Execution data flow")
        
        try:
            if not review_result:
                logger.warning("No review result to test with")
                return False
            
            # Step 4: Execution Agent uses review result
            execution_agent = ExecutionAgent()
            
            execution_task = {
                "task_type": "execution",
                "review_result": review_result
            }
            execution_result = await execution_agent.process_task(execution_task)
            logger.info(f"Execution Result: {json.dumps(execution_result, indent=2)}")
            
            self.test_results["tests"]["review_to_execution"] = {
                "success": True,
                "review_output": review_result,
                "execution_output": execution_result
            }
            
            return True, execution_result
            
        except Exception as e:
            logger.error(f"Review → Execution flow failed: {str(e)}")
            self.test_results["issues_found"].append(f"Review → Execution flow error: {str(e)}")
            return False, None
    
    async def test_execution_to_reporting_flow(self, execution_result):
        """Test if Execution output can be used by Reporting Agent"""
        logger.info("🧪 Testing Execution → Reporting data flow")
        
        try:
            if not execution_result:
                logger.warning("No execution result to test with")
                return False
            
            # Step 5: Reporting Agent creates report
            reporting_agent = ReportingAgent()
            
            reporting_task = {
                "task_type": "reporting",
                "execution_result": execution_result
            }
            reporting_result = await reporting_agent.process_task(reporting_task)
            logger.info(f"Reporting Result: {json.dumps(reporting_result, indent=2)}")
            
            self.test_results["tests"]["execution_to_reporting"] = {
                "success": True,
                "execution_output": execution_result,
                "reporting_output": reporting_result
            }
            
            return True, reporting_result
            
        except Exception as e:
            logger.error(f"Execution → Reporting flow failed: {str(e)}")
            self.test_results["issues_found"].append(f"Execution → Reporting flow error: {str(e)}")
            return False, None
    
    def _validate_data_flow(self, planning_result, creation_result):
        """Validate that data flows properly between agents"""
        logger.info("🔍 Validating data flow structure")
        
        # Check if planning result has structure that creation agent can use
        required_planning_keys = ['test_plan', 'scenarios', 'test_strategy']
        planning_has_required = any(key in planning_result for key in required_planning_keys)
        
        # Check if creation result has meaningful output (Enhanced Agent structure)
        required_creation_keys = ['status', 'generated_files', 'test_files', 'artifacts']
        creation_has_output = (creation_result.get('status') == 'success' or 
                             any(key in creation_result for key in required_creation_keys))
        
        logger.info(f"Planning has required structure: {planning_has_required}")
        logger.info(f"Creation has meaningful output: {creation_has_output}")
        
        return planning_has_required and creation_has_output
    
    async def test_error_handling(self):
        """Test how agents handle errors and invalid input"""
        logger.info("🧪 Testing error handling")
        
        try:
            # Test with invalid input
            planning_agent = PlanningAgent()
            
            # Test with empty scenario
            empty_task = {"task_type": "planning", "test_files": []}
            empty_result = await planning_agent.process_task(empty_task)
            logger.info(f"Empty scenario result: {empty_result}")
            
            # Test with malformed scenario
            malformed_scenario = {"invalid": "data"}
            malformed_task = {"task_type": "planning", "test_files": [malformed_scenario]}
            malformed_result = await planning_agent.process_task(malformed_task)
            logger.info(f"Malformed scenario result: {malformed_result}")
            
            self.test_results["tests"]["error_handling"] = {
                "empty_input": empty_result,
                "malformed_input": malformed_result,
                "success": True
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling test failed: {str(e)}")
            self.test_results["issues_found"].append(f"Error handling failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all communication tests"""
        logger.info("🚀 Starting Agent Communication Tests")
        
        # Test 1: Planning → Test Creation
        planning_success, planning_result, creation_result = await self.test_planning_to_test_creation_flow()
        
        # Test 2: Test Creation → Review (only if previous succeeded)
        review_success, review_result = False, None
        if planning_success and creation_result:
            review_success, review_result = await self.test_creation_to_review_flow(creation_result)
        
        # Test 3: Review → Execution (only if previous succeeded)
        execution_success, execution_result = False, None
        if review_success and review_result:
            execution_success, execution_result = await self.test_review_to_execution_flow(review_result)
        
        # Test 4: Execution → Reporting (only if previous succeeded)
        reporting_success, reporting_result = False, None
        if execution_success and execution_result:
            reporting_success, reporting_result = await self.test_execution_to_reporting_flow(execution_result)
        
        # Test 5: Error handling
        error_handling_success = await self.test_error_handling()
        
        # Summary
        total_tests = 5
        passed_tests = sum([
            planning_success,
            review_success, 
            execution_success,
            reporting_success,
            error_handling_success
        ])
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "overall_success": passed_tests >= 3  # At least 3 out of 5 should pass
        }
        
        # Save results
        results_file = f"agent_communication_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"📊 Test Results Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Success Rate: {self.test_results['summary']['success_rate']:.1f}%")
        logger.info(f"   Overall Success: {self.test_results['summary']['overall_success']}")
        logger.info(f"   Results saved to: {results_file}")
        
        if self.test_results["issues_found"]:
            logger.warning("🚨 Issues Found:")
            for issue in self.test_results["issues_found"]:
                logger.warning(f"   - {issue}")
        
        return self.test_results

async def main():
    """Main test function"""
    tester = AgentCommunicationTester()
    results = await tester.run_all_tests()
    
    print("\n" + "="*60)
    print("AGENT COMMUNICATION TEST RESULTS")
    print("="*60)
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    print(f"Overall Success: {results['summary']['overall_success']}")
    
    if results["issues_found"]:
        print("\nCritical Issues Found:")
        for issue in results["issues_found"]:
            print(f"  ❌ {issue}")
    
    print("\nNext Steps:")
    if results['summary']['success_rate'] < 60:
        print("  🔧 Fix critical agent communication issues")
        print("  🔧 Improve data structure compatibility between agents")
    elif results['summary']['success_rate'] < 80:
        print("  ⚡ Optimize agent data flow")
        print("  ⚡ Enhance error handling")
    else:
        print("  ✅ Agent communication is working well")
        print("  ✅ Ready to test with real scenarios")

if __name__ == "__main__":
    asyncio.run(main())

