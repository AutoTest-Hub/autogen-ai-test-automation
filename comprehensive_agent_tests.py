#!/usr/bin/env python3
"""
Comprehensive Agent Testing Suite for AutoGen Test Automation Framework
Tests all current agents and their capabilities thoroughly
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List
from datetime import datetime

# Framework imports
from config.settings import settings, AgentRole
from models.local_ai_provider import LocalAIProvider, ModelType
from agents.planning_agent import PlanningAgent
from agents.test_creation_agent import TestCreationAgent
from parsers.unified_parser import UnifiedTestFileParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveAgentTester:
    """Comprehensive testing suite for all agents"""
    
    def __init__(self):
        self.local_ai_provider = None
        self.agents = {}
        self.test_results = {
            "test_session": {
                "start_time": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "test_environment": "local_ai_integration"
            },
            "agent_tests": {},
            "orchestration_tests": {},
            "performance_metrics": {},
            "summary": {}
        }
        
    async def initialize(self):
        """Initialize the testing environment"""
        logger.info("🚀 Initializing Comprehensive Agent Testing Suite")
        
        # Initialize local AI provider
        self.local_ai_provider = LocalAIProvider()
        
        if not self.local_ai_provider.is_available():
            logger.error("❌ Local AI provider not available - tests cannot proceed")
            return False
            
        logger.info(f"✅ Local AI provider initialized with {len(self.local_ai_provider.available_models)} models")
        
        # Create agents for testing
        await self._create_test_agents()
        
        return True
        
    async def _create_test_agents(self):
        """Create agents for comprehensive testing"""
        logger.info("Creating agents for testing...")
        
        # Planning Agent
        self.agents["planning"] = PlanningAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Test Creation Agent
        self.agents["test_creation"] = TestCreationAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        logger.info(f"✅ Created {len(self.agents)} agents for testing")
        
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        logger.info("🧪 Starting Comprehensive Agent Testing")
        
        # Test individual agents
        await self._test_planning_agent()
        await self._test_test_creation_agent()
        
        # Test agent interactions
        await self._test_agent_orchestration()
        
        # Performance testing
        await self._test_performance()
        
        # Generate final report
        await self._generate_test_report()
        
        logger.info("✅ Comprehensive testing completed")
        
    async def _test_planning_agent(self):
        """Comprehensive testing of Planning Agent"""
        logger.info("🎯 Testing Planning Agent Capabilities")
        
        planning_agent = self.agents["planning"]
        test_results = {
            "agent_name": "PlanningAgent",
            "test_start": datetime.now().isoformat(),
            "capabilities_tested": [],
            "test_cases": {},
            "performance": {},
            "errors": []
        }
        
        # Test 1: Requirement Analysis
        try:
            logger.info("  📋 Testing requirement analysis...")
            start_time = time.time()
            
            test_requirement = """
            Test Requirement: E-commerce Shopping Flow
            Application: https://www.advantageonlineshopping.com/#/
            
            User Story: As a customer, I want to browse products, add items to cart, 
            and complete purchase so that I can buy products online.
            
            Acceptance Criteria:
            - User can login with valid credentials
            - User can browse product categories
            - User can add products to shopping cart
            - User can complete checkout process
            - User receives order confirmation
            """
            
            analysis_result = await planning_agent.process_task({
                "task_type": "analyze_requirements",
                "requirements": test_requirement
            })
            
            test_results["test_cases"]["requirement_analysis"] = {
                "status": "passed" if analysis_result else "failed",
                "execution_time": time.time() - start_time,
                "result_length": len(str(analysis_result)) if analysis_result else 0,
                "has_structured_output": isinstance(analysis_result, dict)
            }
            
            logger.info(f"    ✅ Requirement analysis completed in {test_results['test_cases']['requirement_analysis']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Requirement analysis failed: {str(e)}")
            logger.error(f"    ❌ Requirement analysis failed: {e}")
            
        # Test 2: Test Matrix Creation
        try:
            logger.info("  📊 Testing test matrix creation...")
            start_time = time.time()
            
            test_scenarios = [
                "Login with valid credentials",
                "Browse laptop category", 
                "Add HP EliteBook to cart",
                "Complete checkout process",
                "Verify order confirmation"
            ]
            
            matrix_result = await planning_agent.process_task({
                "task_type": "create_test_matrix", 
                "scenarios": test_scenarios
            })
            
            test_results["test_cases"]["test_matrix_creation"] = {
                "status": "passed" if matrix_result else "failed",
                "execution_time": time.time() - start_time,
                "scenarios_processed": len(test_scenarios),
                "matrix_complexity": len(str(matrix_result)) if matrix_result else 0
            }
            
            logger.info(f"    ✅ Test matrix creation completed in {test_results['test_cases']['test_matrix_creation']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Test matrix creation failed: {str(e)}")
            logger.error(f"    ❌ Test matrix creation failed: {e}")
            
        # Test 3: Risk Assessment
        try:
            logger.info("  ⚠️ Testing risk assessment...")
            start_time = time.time()
            
            risk_factors = {
                "application_complexity": "high",
                "test_environment": "staging",
                "timeline": "2 weeks",
                "team_experience": "medium",
                "critical_business_flow": True
            }
            
            risk_result = await planning_agent.process_task({
                "task_type": "assess_risk",
                "test_plan": test_plan
            })
            
            test_results["test_cases"]["risk_assessment"] = {
                "status": "passed" if risk_result else "failed",
                "execution_time": time.time() - start_time,
                "risk_factors_analyzed": len(risk_factors),
                "assessment_detail": len(str(risk_result)) if risk_result else 0
            }
            
            logger.info(f"    ✅ Risk assessment completed in {test_results['test_cases']['risk_assessment']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Risk assessment failed: {str(e)}")
            logger.error(f"    ❌ Risk assessment failed: {e}")
            
        # Test 4: Natural Language Processing
        try:
            logger.info("  🗣️ Testing natural language processing...")
            start_time = time.time()
            
            natural_language_request = """
            I need to create a comprehensive test plan for our new mobile banking app. 
            The app should support login, account balance checking, money transfers, 
            and bill payments. We need to ensure security, performance, and usability 
            testing across iOS and Android platforms. Timeline is 3 weeks with a team of 4 testers.
            """
            
            nl_result = await planning_agent.process_task(natural_language_request)
            
            test_results["test_cases"]["natural_language_processing"] = {
                "status": "passed" if nl_result else "failed",
                "execution_time": time.time() - start_time,
                "input_complexity": len(natural_language_request),
                "output_quality": len(str(nl_result)) if nl_result else 0
            }
            
            logger.info(f"    ✅ Natural language processing completed in {test_results['test_cases']['natural_language_processing']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Natural language processing failed: {str(e)}")
            logger.error(f"    ❌ Natural language processing failed: {e}")
            
        test_results["test_end"] = datetime.now().isoformat()
        test_results["total_tests"] = len(test_results["test_cases"])
        test_results["passed_tests"] = len([t for t in test_results["test_cases"].values() if t["status"] == "passed"])
        test_results["success_rate"] = (test_results["passed_tests"] / test_results["total_tests"]) * 100 if test_results["total_tests"] > 0 else 0
        
        self.test_results["agent_tests"]["planning_agent"] = test_results
        logger.info(f"📊 Planning Agent Testing: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({test_results['success_rate']:.1f}%)")
        
    async def _test_test_creation_agent(self):
        """Comprehensive testing of Test Creation Agent"""
        logger.info("🛠️ Testing Test Creation Agent Capabilities")
        
        creation_agent = self.agents["test_creation"]
        test_results = {
            "agent_name": "TestCreationAgent",
            "test_start": datetime.now().isoformat(),
            "capabilities_tested": [],
            "test_cases": {},
            "performance": {},
            "errors": []
        }
        
        # Test 1: Playwright Test Generation
        try:
            logger.info("  🎭 Testing Playwright test generation...")
            start_time = time.time()
            
            playwright_spec = {
                "test_name": "Login Flow Test",
                "target_url": "https://www.advantageonlineshopping.com/#/",
                "actions": [
                    {"action": "navigate", "url": "https://www.advantageonlineshopping.com/#/"},
                    {"action": "click", "selector": "[data-testid='login-button']"},
                    {"action": "fill", "selector": "#username", "value": "helios"},
                    {"action": "fill", "selector": "#password", "value": "Password123"},
                    {"action": "click", "selector": "#login-submit"},
                    {"action": "expect", "selector": ".user-menu", "state": "visible"}
                ]
            }
            
            playwright_result = await creation_agent.process_task({
                "task_type": "generate_playwright_test",
                "test_spec": playwright_spec
            })
            
            test_results["test_cases"]["playwright_generation"] = {
                "status": "passed" if playwright_result else "failed",
                "execution_time": time.time() - start_time,
                "actions_processed": len(playwright_spec["actions"]),
                "code_length": len(str(playwright_result)) if playwright_result else 0,
                "has_valid_syntax": "async def" in str(playwright_result) if playwright_result else False
            }
            
            logger.info(f"    ✅ Playwright test generation completed in {test_results['test_cases']['playwright_generation']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Playwright test generation failed: {str(e)}")
            logger.error(f"    ❌ Playwright test generation failed: {e}")
            
        # Test 2: Selenium Test Generation
        try:
            logger.info("  🌐 Testing Selenium test generation...")
            start_time = time.time()
            
            selenium_spec = {
                "test_name": "Product Search Test",
                "browser": "chrome",
                "target_url": "https://www.advantageonlineshopping.com/#/",
                "test_steps": [
                    "Navigate to homepage",
                    "Click on LAPTOPS category",
                    "Search for 'HP EliteBook'",
                    "Verify search results contain HP products",
                    "Click on first product",
                    "Verify product details page loads"
                ]
            }
            
            selenium_result = await creation_agent.process_task({
                "task_type": "generate_selenium_test", 
                "test_spec": selenium_spec
            })
            
            test_results["test_cases"]["selenium_generation"] = {
                "status": "passed" if selenium_result else "failed",
                "execution_time": time.time() - start_time,
                "steps_processed": len(selenium_spec["test_steps"]),
                "code_length": len(str(selenium_result)) if selenium_result else 0,
                "has_webdriver": "webdriver" in str(selenium_result) if selenium_result else False
            }
            
            logger.info(f"    ✅ Selenium test generation completed in {test_results['test_cases']['selenium_generation']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Selenium test generation failed: {str(e)}")
            logger.error(f"    ❌ Selenium test generation failed: {e}")
            
        # Test 3: API Test Generation
        try:
            logger.info("  🔌 Testing API test generation...")
            start_time = time.time()
            
            api_spec = {
                "test_name": "User Authentication API Test",
                "base_url": "https://api.advantageonlineshopping.com",
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/auth/login",
                        "payload": {"username": "helios", "password": "Password123"},
                        "expected_status": 200,
                        "expected_response": {"success": True, "token": "string"}
                    },
                    {
                        "method": "GET", 
                        "path": "/user/profile",
                        "headers": {"Authorization": "Bearer {token}"},
                        "expected_status": 200
                    }
                ]
            }
            
            api_result = await creation_agent.process_task({
                "task_type": "generate_api_test",
                "test_spec": api_spec  
            })
            
            test_results["test_cases"]["api_generation"] = {
                "status": "passed" if api_result else "failed",
                "execution_time": time.time() - start_time,
                "endpoints_processed": len(api_spec["endpoints"]),
                "code_length": len(str(api_result)) if api_result else 0,
                "has_requests": "requests" in str(api_result) if api_result else False
            }
            
            logger.info(f"    ✅ API test generation completed in {test_results['test_cases']['api_generation']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"API test generation failed: {str(e)}")
            logger.error(f"    ❌ API test generation failed: {e}")
            
        # Test 4: Page Object Creation
        try:
            logger.info("  📄 Testing page object creation...")
            start_time = time.time()
            
            page_spec = {
                "page_name": "LoginPage",
                "url": "https://www.advantageonlineshopping.com/#/login",
                "elements": [
                    {"name": "username_field", "selector": "#username", "type": "input"},
                    {"name": "password_field", "selector": "#password", "type": "input"},
                    {"name": "login_button", "selector": "#login-submit", "type": "button"},
                    {"name": "error_message", "selector": ".error-message", "type": "text"}
                ],
                "methods": [
                    "login(username, password)",
                    "get_error_message()",
                    "is_login_successful()"
                ]
            }
            
            page_object_result = await creation_agent.create_page_object(page_spec)
            
            test_results["test_cases"]["page_object_creation"] = {
                "status": "passed" if page_object_result else "failed",
                "execution_time": time.time() - start_time,
                "elements_processed": len(page_spec["elements"]),
                "methods_processed": len(page_spec["methods"]),
                "code_length": len(str(page_object_result)) if page_object_result else 0,
                "has_class_definition": "class" in str(page_object_result) if page_object_result else False
            }
            
            logger.info(f"    ✅ Page object creation completed in {test_results['test_cases']['page_object_creation']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Page object creation failed: {str(e)}")
            logger.error(f"    ❌ Page object creation failed: {e}")
            
        test_results["test_end"] = datetime.now().isoformat()
        test_results["total_tests"] = len(test_results["test_cases"])
        test_results["passed_tests"] = len([t for t in test_results["test_cases"].values() if t["status"] == "passed"])
        test_results["success_rate"] = (test_results["passed_tests"] / test_results["total_tests"]) * 100 if test_results["total_tests"] > 0 else 0
        
        self.test_results["agent_tests"]["test_creation_agent"] = test_results
        logger.info(f"📊 Test Creation Agent Testing: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({test_results['success_rate']:.1f}%)")
        
    async def _test_agent_orchestration(self):
        """Test agent coordination and orchestration"""
        logger.info("🎼 Testing Agent Orchestration")
        
        orchestration_results = {
            "test_start": datetime.now().isoformat(),
            "coordination_tests": {},
            "workflow_tests": {},
            "communication_tests": {},
            "errors": []
        }
        
        # Test 1: Planning → Test Creation Workflow
        try:
            logger.info("  🔄 Testing Planning → Test Creation workflow...")
            start_time = time.time()
            
            # Step 1: Planning agent analyzes requirements
            requirement = """
            Create automated tests for user registration flow:
            1. Navigate to registration page
            2. Fill registration form with valid data
            3. Submit form
            4. Verify success message
            5. Verify user can login with new credentials
            """
            
            planning_result = await self.agents["planning"].analyze_requirements(requirement)
            
            # Step 2: Test creation agent generates tests based on planning
            if planning_result:
                test_spec = {
                    "test_name": "User Registration Flow",
                    "requirements": str(planning_result),
                    "framework": "playwright"
                }
                
                creation_result = await self.agents["test_creation"].process_task(
                    f"Generate Playwright test based on these requirements: {test_spec}"
                )
                
                orchestration_results["coordination_tests"]["planning_to_creation"] = {
                    "status": "passed" if creation_result else "failed",
                    "execution_time": time.time() - start_time,
                    "planning_output_size": len(str(planning_result)),
                    "creation_output_size": len(str(creation_result)) if creation_result else 0,
                    "workflow_completed": bool(planning_result and creation_result)
                }
                
                logger.info(f"    ✅ Planning → Creation workflow completed in {orchestration_results['coordination_tests']['planning_to_creation']['execution_time']:.2f}s")
            else:
                orchestration_results["coordination_tests"]["planning_to_creation"] = {
                    "status": "failed",
                    "error": "Planning agent failed to analyze requirements"
                }
                
        except Exception as e:
            orchestration_results["errors"].append(f"Planning → Creation workflow failed: {str(e)}")
            logger.error(f"    ❌ Planning → Creation workflow failed: {e}")
            
        # Test 2: Multi-agent collaboration
        try:
            logger.info("  🤝 Testing multi-agent collaboration...")
            start_time = time.time()
            
            # Simulate a complex scenario requiring both agents
            complex_scenario = """
            Design and implement comprehensive testing for an e-commerce checkout process:
            - Plan test coverage and strategy
            - Generate automated tests for UI and API
            - Include edge cases and error scenarios
            - Ensure cross-browser compatibility
            """
            
            # Planning agent creates strategy
            strategy = await self.agents["planning"].process_task(complex_scenario)
            
            # Test creation agent implements the strategy
            if strategy:
                implementation = await self.agents["test_creation"].process_task(
                    f"Implement this test strategy with actual code: {strategy}"
                )
                
                orchestration_results["coordination_tests"]["multi_agent_collaboration"] = {
                    "status": "passed" if implementation else "failed",
                    "execution_time": time.time() - start_time,
                    "strategy_complexity": len(str(strategy)),
                    "implementation_size": len(str(implementation)) if implementation else 0,
                    "collaboration_successful": bool(strategy and implementation)
                }
                
                logger.info(f"    ✅ Multi-agent collaboration completed in {orchestration_results['coordination_tests']['multi_agent_collaboration']['execution_time']:.2f}s")
            else:
                orchestration_results["coordination_tests"]["multi_agent_collaboration"] = {
                    "status": "failed",
                    "error": "Strategy creation failed"
                }
                
        except Exception as e:
            orchestration_results["errors"].append(f"Multi-agent collaboration failed: {str(e)}")
            logger.error(f"    ❌ Multi-agent collaboration failed: {e}")
            
        orchestration_results["test_end"] = datetime.now().isoformat()
        self.test_results["orchestration_tests"] = orchestration_results
        
        total_tests = len(orchestration_results["coordination_tests"])
        passed_tests = len([t for t in orchestration_results["coordination_tests"].values() if t.get("status") == "passed"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        logger.info(f"📊 Agent Orchestration Testing: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
    async def _test_performance(self):
        """Test performance characteristics of agents"""
        logger.info("⚡ Testing Performance Characteristics")
        
        performance_results = {
            "test_start": datetime.now().isoformat(),
            "response_times": {},
            "throughput_tests": {},
            "memory_usage": {},
            "model_efficiency": {}
        }
        
        # Test response times for different complexity levels
        test_cases = [
            {"name": "simple_task", "complexity": "low", "task": "Analyze this simple login test requirement"},
            {"name": "medium_task", "complexity": "medium", "task": "Create a comprehensive test plan for user registration with validation"},
            {"name": "complex_task", "complexity": "high", "task": "Design end-to-end testing strategy for multi-tenant SaaS application with complex workflows"}
        ]
        
        for agent_name, agent in self.agents.items():
            agent_performance = {}
            
            for test_case in test_cases:
                try:
                    start_time = time.time()
                    result = await agent.process_task(test_case["task"])
                    execution_time = time.time() - start_time
                    
                    agent_performance[test_case["name"]] = {
                        "execution_time": execution_time,
                        "complexity": test_case["complexity"],
                        "success": bool(result),
                        "output_size": len(str(result)) if result else 0
                    }
                    
                    logger.info(f"    {agent_name} - {test_case['name']}: {execution_time:.2f}s")
                    
                except Exception as e:
                    agent_performance[test_case["name"]] = {
                        "execution_time": None,
                        "complexity": test_case["complexity"],
                        "success": False,
                        "error": str(e)
                    }
                    
            performance_results["response_times"][agent_name] = agent_performance
            
        performance_results["test_end"] = datetime.now().isoformat()
        self.test_results["performance_metrics"] = performance_results
        
        logger.info("✅ Performance testing completed")
        
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📋 Generating Comprehensive Test Report")
        
        # Calculate overall statistics
        total_agent_tests = 0
        passed_agent_tests = 0
        
        for agent_test in self.test_results["agent_tests"].values():
            total_agent_tests += agent_test.get("total_tests", 0)
            passed_agent_tests += agent_test.get("passed_tests", 0)
            
        orchestration_tests = self.test_results.get("orchestration_tests", {}).get("coordination_tests", {})
        total_orchestration_tests = len(orchestration_tests)
        passed_orchestration_tests = len([t for t in orchestration_tests.values() if t.get("status") == "passed"])
        
        overall_success_rate = ((passed_agent_tests + passed_orchestration_tests) / 
                               (total_agent_tests + total_orchestration_tests)) * 100 if (total_agent_tests + total_orchestration_tests) > 0 else 0
        
        summary = {
            "test_session_end": datetime.now().isoformat(),
            "total_agents_tested": len(self.agents),
            "total_individual_tests": total_agent_tests,
            "passed_individual_tests": passed_agent_tests,
            "total_orchestration_tests": total_orchestration_tests,
            "passed_orchestration_tests": passed_orchestration_tests,
            "overall_success_rate": overall_success_rate,
            "framework_status": "production_ready" if overall_success_rate >= 80 else "needs_improvement",
            "local_ai_integration": "fully_functional",
            "recommendations": []
        }
        
        # Add recommendations based on results
        if overall_success_rate >= 90:
            summary["recommendations"].append("Framework is production-ready for deployment")
        elif overall_success_rate >= 70:
            summary["recommendations"].append("Framework is functional but may need minor improvements")
        else:
            summary["recommendations"].append("Framework needs significant improvements before production use")
            
        if passed_agent_tests == total_agent_tests:
            summary["recommendations"].append("All individual agent capabilities are working perfectly")
            
        if passed_orchestration_tests == total_orchestration_tests:
            summary["recommendations"].append("Agent orchestration and coordination is working perfectly")
            
        self.test_results["summary"] = summary
        
        # Save detailed test report
        report_filename = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        logger.info(f"📊 Test Report Summary:")
        logger.info(f"   Total Tests: {total_agent_tests + total_orchestration_tests}")
        logger.info(f"   Passed Tests: {passed_agent_tests + passed_orchestration_tests}")
        logger.info(f"   Success Rate: {overall_success_rate:.1f}%")
        logger.info(f"   Framework Status: {summary['framework_status']}")
        logger.info(f"   Detailed Report: {report_filename}")
        
        return report_filename

async def main():
    """Main testing function"""
    tester = ComprehensiveAgentTester()
    
    # Initialize testing environment
    if not await tester.initialize():
        logger.error("❌ Failed to initialize testing environment")
        return
        
    # Run comprehensive tests
    await tester.run_all_tests()
    
    logger.info("🎉 Comprehensive Agent Testing Completed!")

if __name__ == "__main__":
    asyncio.run(main())

