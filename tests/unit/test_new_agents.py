#!/usr/bin/env python3
"""
Test script for new specialized agents in AutoGen Test Automation Framework
Tests Review Agent, Execution Agent, and Reporting Agent
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
from agents.review_agent import ReviewAgent
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewAgentsTester:
    """Test suite for new specialized agents"""
    
    def __init__(self):
        self.local_ai_provider = None
        self.agents = {}
        self.test_results = {
            "test_session": {
                "start_time": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "test_environment": "new_agents_validation"
            },
            "agent_tests": {},
            "summary": {}
        }
        
    async def initialize(self):
        """Initialize the testing environment"""
        logger.info("🚀 Initializing New Agents Testing Suite")
        
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
        """Create new agents for testing"""
        logger.info("Creating new specialized agents for testing...")
        
        # Review Agent
        self.agents["review"] = ReviewAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Execution Agent
        self.agents["execution"] = ExecutionAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        # Reporting Agent
        self.agents["reporting"] = ReportingAgent(
            local_ai_provider=self.local_ai_provider
        )
        
        logger.info(f"✅ Created {len(self.agents)} new specialized agents for testing")
        
    async def run_all_tests(self):
        """Run comprehensive test suite for new agents"""
        logger.info("🧪 Starting New Agents Testing")
        
        # Test individual agents
        await self._test_review_agent()
        await self._test_execution_agent()
        await self._test_reporting_agent()
        
        # Test agent integration
        await self._test_agent_integration()
        
        # Generate final report
        await self._generate_test_report()
        
        logger.info("✅ New agents testing completed")
        
    async def _test_review_agent(self):
        """Test Review Agent capabilities"""
        logger.info("🔍 Testing Review Agent Capabilities")
        
        review_agent = self.agents["review"]
        test_results = {
            "agent_name": "ReviewAgent",
            "test_start": datetime.now().isoformat(),
            "test_cases": {},
            "errors": []
        }
        
        # Test 1: Code Review
        try:
            logger.info("  📝 Testing code review functionality...")
            start_time = time.time()
            
            sample_test_code = '''
import pytest
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        await page.click("#login")
        await browser.close()
'''
            
            review_result = await review_agent.process_task({
                "type": "review_code",
                "test_code": sample_test_code
            })
            
            test_results["test_cases"]["code_review"] = {
                "status": "passed" if review_result else "failed",
                "execution_time": time.time() - start_time,
                "review_score": review_result.get("overall_score", 0),
                "issues_found": review_result.get("total_files_reviewed", 0)
            }
            
            logger.info(f"    ✅ Code review completed in {test_results['test_cases']['code_review']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Code review failed: {str(e)}")
            logger.error(f"    ❌ Code review failed: {e}")
            
        # Test 2: Scenario Validation
        try:
            logger.info("  ✅ Testing scenario validation...")
            start_time = time.time()
            
            test_scenarios = [
                {
                    "name": "Login Test",
                    "description": "Test user login functionality",
                    "test_steps": [
                        "Navigate to login page",
                        "Enter credentials",
                        "Click login button",
                        "Verify successful login"
                    ],
                    "expected_results": "User should be logged in successfully"
                },
                {
                    "name": "Incomplete Test",
                    "description": "Test with missing information"
                    # Missing test_steps intentionally
                }
            ]
            
            validation_result = await review_agent.process_task({
                "type": "validate_scenarios",
                "scenarios": test_scenarios
            })
            
            test_results["test_cases"]["scenario_validation"] = {
                "status": "passed" if validation_result else "failed",
                "execution_time": time.time() - start_time,
                "scenarios_validated": validation_result.get("total_scenarios", 0),
                "valid_scenarios": validation_result.get("valid_scenarios", 0)
            }
            
            logger.info(f"    ✅ Scenario validation completed in {test_results['test_cases']['scenario_validation']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Scenario validation failed: {str(e)}")
            logger.error(f"    ❌ Scenario validation failed: {e}")
            
        test_results["test_end"] = datetime.now().isoformat()
        test_results["total_tests"] = len(test_results["test_cases"])
        test_results["passed_tests"] = len([t for t in test_results["test_cases"].values() if t["status"] == "passed"])
        test_results["success_rate"] = (test_results["passed_tests"] / test_results["total_tests"]) * 100 if test_results["total_tests"] > 0 else 0
        
        self.test_results["agent_tests"]["review_agent"] = test_results
        logger.info(f"📊 Review Agent Testing: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({test_results['success_rate']:.1f}%)")
        
    async def _test_execution_agent(self):
        """Test Execution Agent capabilities"""
        logger.info("⚡ Testing Execution Agent Capabilities")
        
        execution_agent = self.agents["execution"]
        test_results = {
            "agent_name": "ExecutionAgent",
            "test_start": datetime.now().isoformat(),
            "test_cases": {},
            "errors": []
        }
        
        # Test 1: Environment Setup
        try:
            logger.info("  🔧 Testing environment setup...")
            start_time = time.time()
            
            setup_result = await execution_agent.process_task({
                "type": "setup_environment",
                "config": {
                    "auto_install": False,
                    "setup_browsers": False  # Skip browser setup for faster testing
                }
            })
            
            test_results["test_cases"]["environment_setup"] = {
                "status": "passed" if setup_result.get("success", False) else "failed",
                "execution_time": time.time() - start_time,
                "setup_successful": setup_result.get("success", False),
                "steps_completed": len(setup_result.get("steps_completed", []))
            }
            
            logger.info(f"    ✅ Environment setup completed in {test_results['test_cases']['environment_setup']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Environment setup failed: {str(e)}")
            logger.error(f"    ❌ Environment setup failed: {e}")
            
        # Test 2: Test Execution Simulation
        try:
            logger.info("  🏃 Testing test execution simulation...")
            start_time = time.time()
            
            # Create a simple test file for execution
            simple_test_content = '''
import time
print("Test started")
time.sleep(1)
print("Test completed successfully")
'''
            
            # Save test file
            test_file_path = "/tmp/simple_test.py"
            with open(test_file_path, 'w') as f:
                f.write(simple_test_content)
            
            execution_result = await execution_agent.process_task({
                "type": "execute_tests",
                "test_files": [test_file_path],
                "execution_config": {
                    "verbose": True
                }
            })
            
            test_results["test_cases"]["test_execution"] = {
                "status": "passed" if execution_result.get("success", False) else "failed",
                "execution_time": time.time() - start_time,
                "tests_executed": len(execution_result.get("execution_results", {}).get("test_results", [])),
                "execution_successful": execution_result.get("success", False)
            }
            
            logger.info(f"    ✅ Test execution completed in {test_results['test_cases']['test_execution']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Test execution failed: {str(e)}")
            logger.error(f"    ❌ Test execution failed: {e}")
            
        test_results["test_end"] = datetime.now().isoformat()
        test_results["total_tests"] = len(test_results["test_cases"])
        test_results["passed_tests"] = len([t for t in test_results["test_cases"].values() if t["status"] == "passed"])
        test_results["success_rate"] = (test_results["passed_tests"] / test_results["total_tests"]) * 100 if test_results["total_tests"] > 0 else 0
        
        self.test_results["agent_tests"]["execution_agent"] = test_results
        logger.info(f"📊 Execution Agent Testing: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({test_results['success_rate']:.1f}%)")
        
    async def _test_reporting_agent(self):
        """Test Reporting Agent capabilities"""
        logger.info("📊 Testing Reporting Agent Capabilities")
        
        reporting_agent = self.agents["reporting"]
        test_results = {
            "agent_name": "ReportingAgent",
            "test_start": datetime.now().isoformat(),
            "test_cases": {},
            "errors": []
        }
        
        # Test 1: Report Generation
        try:
            logger.info("  📄 Testing report generation...")
            start_time = time.time()
            
            # Sample execution data for report generation
            sample_execution_data = {
                "summary": {
                    "total_tests": 5,
                    "passed": 4,
                    "failed": 1,
                    "success_rate": 80.0,
                    "total_execution_time": 25.5
                },
                "performance_metrics": {
                    "average_execution_time": 5.1,
                    "fastest_test": 2.3,
                    "slowest_test": 8.7
                },
                "test_results": [
                    {
                        "test_file": "test_login.py",
                        "status": "passed",
                        "execution_time": 3.2,
                        "metrics": {"tests_run": 2}
                    },
                    {
                        "test_file": "test_checkout.py",
                        "status": "failed",
                        "execution_time": 8.7,
                        "metrics": {"tests_run": 3}
                    }
                ]
            }
            
            sample_review_data = {
                "overall_score": 7.5,
                "reviews": [
                    {
                        "filename": "test_login.py",
                        "score": 8.0,
                        "issues": ["Missing error handling"],
                        "strengths": ["Good test structure", "Clear assertions"]
                    }
                ],
                "recommendations": ["Add comprehensive error handling", "Improve test documentation"]
            }
            
            report_result = await reporting_agent.process_task({
                "type": "generate_report",
                "execution_data": sample_execution_data,
                "review_data": sample_review_data
            })
            
            test_results["test_cases"]["report_generation"] = {
                "status": "passed" if report_result else "failed",
                "execution_time": time.time() - start_time,
                "report_generated": bool(report_result.get("report")),
                "html_report_created": bool(report_result.get("html_report_path")),
                "json_report_created": bool(report_result.get("json_report_path"))
            }
            
            logger.info(f"    ✅ Report generation completed in {test_results['test_cases']['report_generation']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Report generation failed: {str(e)}")
            logger.error(f"    ❌ Report generation failed: {e}")
            
        # Test 2: Data Export
        try:
            logger.info("  💾 Testing data export...")
            start_time = time.time()
            
            export_data = {
                "test_results": [
                    {"test": "login", "status": "passed", "time": 3.2},
                    {"test": "checkout", "status": "failed", "time": 8.7}
                ],
                "summary": {"total": 2, "passed": 1, "failed": 1}
            }
            
            export_result = await reporting_agent.process_task({
                "type": "export_data",
                "data": export_data,
                "format": "json"
            })
            
            test_results["test_cases"]["data_export"] = {
                "status": "passed" if export_result.get("success", False) else "failed",
                "execution_time": time.time() - start_time,
                "export_successful": export_result.get("success", False),
                "files_exported": len(export_result.get("exported_files", []))
            }
            
            logger.info(f"    ✅ Data export completed in {test_results['test_cases']['data_export']['execution_time']:.2f}s")
            
        except Exception as e:
            test_results["errors"].append(f"Data export failed: {str(e)}")
            logger.error(f"    ❌ Data export failed: {e}")
            
        test_results["test_end"] = datetime.now().isoformat()
        test_results["total_tests"] = len(test_results["test_cases"])
        test_results["passed_tests"] = len([t for t in test_results["test_cases"].values() if t["status"] == "passed"])
        test_results["success_rate"] = (test_results["passed_tests"] / test_results["total_tests"]) * 100 if test_results["total_tests"] > 0 else 0
        
        self.test_results["agent_tests"]["reporting_agent"] = test_results
        logger.info(f"📊 Reporting Agent Testing: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({test_results['success_rate']:.1f}%)")
        
    async def _test_agent_integration(self):
        """Test integration between new agents"""
        logger.info("🔗 Testing Agent Integration")
        
        integration_results = {
            "test_start": datetime.now().isoformat(),
            "integration_tests": {},
            "errors": []
        }
        
        # Test 1: Review → Execution → Reporting workflow
        try:
            logger.info("  🔄 Testing Review → Execution → Reporting workflow...")
            start_time = time.time()
            
            # Step 1: Review some test code
            sample_code = '''
import pytest

def test_example():
    assert 1 + 1 == 2
    print("Test passed")
'''
            
            review_result = await self.agents["review"].process_task({
                "type": "review_code",
                "test_code": sample_code
            })
            
            # Step 2: Set up execution environment
            execution_setup = await self.agents["execution"].process_task({
                "type": "setup_environment",
                "config": {"auto_install": False, "setup_browsers": False}
            })
            
            # Step 3: Generate a report combining review and execution data
            report_result = await self.agents["reporting"].process_task({
                "type": "generate_report",
                "execution_data": {
                    "summary": {"total_tests": 1, "success_rate": 100.0, "total_execution_time": 1.5},
                    "test_results": [{"test_file": "test_example.py", "status": "passed", "execution_time": 1.5}]
                },
                "review_data": review_result.get("review_results", {})
            })
            
            integration_results["integration_tests"]["full_workflow"] = {
                "status": "passed" if all([review_result, execution_setup, report_result]) else "failed",
                "execution_time": time.time() - start_time,
                "review_successful": bool(review_result),
                "execution_setup_successful": execution_setup.get("success", False),
                "report_generated": bool(report_result)
            }
            
            logger.info(f"    ✅ Full workflow integration completed in {integration_results['integration_tests']['full_workflow']['execution_time']:.2f}s")
            
        except Exception as e:
            integration_results["errors"].append(f"Full workflow integration failed: {str(e)}")
            logger.error(f"    ❌ Full workflow integration failed: {e}")
            
        integration_results["test_end"] = datetime.now().isoformat()
        integration_results["total_tests"] = len(integration_results["integration_tests"])
        integration_results["passed_tests"] = len([t for t in integration_results["integration_tests"].values() if t["status"] == "passed"])
        integration_results["success_rate"] = (integration_results["passed_tests"] / integration_results["total_tests"]) * 100 if integration_results["total_tests"] > 0 else 0
        
        self.test_results["integration_tests"] = integration_results
        logger.info(f"📊 Agent Integration Testing: {integration_results['passed_tests']}/{integration_results['total_tests']} tests passed ({integration_results['success_rate']:.1f}%)")
        
    async def _generate_test_report(self):
        """Generate final test report"""
        logger.info("📋 Generating New Agents Test Report")
        
        # Calculate overall statistics
        total_tests = 0
        passed_tests = 0
        
        for agent_name, results in self.test_results["agent_tests"].items():
            total_tests += results.get("total_tests", 0)
            passed_tests += results.get("passed_tests", 0)
        
        # Add integration tests
        if "integration_tests" in self.test_results:
            total_tests += self.test_results["integration_tests"].get("total_tests", 0)
            passed_tests += self.test_results["integration_tests"].get("passed_tests", 0)
        
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": round(overall_success_rate, 1),
            "framework_status": "production_ready" if overall_success_rate >= 80 else "needs_improvement",
            "test_end_time": datetime.now().isoformat()
        }
        
        # Save detailed report
        report_filename = f"new_agents_test_report_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info("📊 New Agents Test Report Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed Tests: {passed_tests}")
        logger.info(f"   Success Rate: {overall_success_rate:.1f}%")
        logger.info(f"   Framework Status: {self.test_results['summary']['framework_status']}")
        logger.info(f"   Detailed Report: {report_filename}")


async def main():
    """Main test execution function"""
    tester = NewAgentsTester()
    
    # Initialize testing environment
    if not await tester.initialize():
        logger.error("Failed to initialize testing environment")
        return
    
    # Run all tests
    await tester.run_all_tests()
    
    logger.info("🎉 New Agents Testing Completed!")


if __name__ == "__main__":
    asyncio.run(main())

