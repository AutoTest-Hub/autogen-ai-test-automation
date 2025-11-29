#!/usr/bin/env python3
"""
Test Real Scenarios with Advantage Online Shopping
==================================================
This script tests our agents with comprehensive real-world scenarios
to see what they actually generate and identify gaps.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our components
from complete_orchestrator import CompleteOrchestrator
from parsers.unified_parser import UnifiedTestFileParser
from parsers.txt_parser import TestStep

class RealScenarioTester:
    """Test agents with real Advantage Online Shopping scenarios"""
    
    def __init__(self):
        self.orchestrator = CompleteOrchestrator()
        self.parser = UnifiedTestFileParser()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios_tested": [],
            "agent_outputs": {},
            "generated_code": {},
            "issues_found": [],
            "insights": []
        }
    
    async def test_scenario_parsing(self):
        """Test if our parser can handle the real scenarios"""
        logger.info("🧪 Testing scenario parsing with real Advantage Shopping scenarios")
        
        try:
            scenario_file = "advantage_shopping_scenarios.txt"
            if not os.path.exists(scenario_file):
                self.test_results["issues_found"].append(f"Scenario file not found: {scenario_file}")
                return False
            
            # Parse the scenarios
            parsed_file = self.parser.parse_file(scenario_file)
            parsed_scenarios = parsed_file.scenarios if hasattr(parsed_file, 'scenarios') else []
            logger.info(f"Parsed {len(parsed_scenarios)} scenarios")
            
            # Log what we got
            for i, scenario in enumerate(parsed_scenarios):
                logger.info(f"Scenario {i+1}: {scenario.get('testName', 'Unknown')}")
                logger.info(f"  Steps: {len(scenario.get('testSteps', []))}")
                logger.info(f"  Priority: {scenario.get('priority', 'Not set')}")
            
            self.test_results["scenarios_tested"] = parsed_scenarios
            self.test_results["parsing_success"] = True
            
            return True, parsed_scenarios
            
        except Exception as e:
            logger.error(f"Scenario parsing failed: {str(e)}")
            self.test_results["issues_found"].append(f"Scenario parsing error: {str(e)}")
            return False, []
    
    async def test_planning_agent_with_real_scenarios(self, scenarios):
        """Test Planning Agent with real scenarios"""
        logger.info("🧪 Testing Planning Agent with real scenarios")
        
        try:
            # Take first 2 scenarios to avoid overwhelming the test
            test_scenarios = scenarios[:2] if len(scenarios) > 2 else scenarios
            
            # Create task for planning agent
            task_data = {
                "task_type": "planning",
                "test_files": test_scenarios
            }
            
            # Get planning result
            planning_agent = self.orchestrator.agents.get("planning")
            planning_result = await planning_agent.process_task(task_data)

            
            logger.info("Planning Agent Results:")
            logger.info(f"  Status: {planning_result.get('status', 'Unknown')}")
            
            if 'test_plan' in planning_result:
                test_plan = planning_result['test_plan']
                logger.info(f"  Total scenarios planned: {test_plan.get('resource_estimation', {}).get('total_scenarios', 0)}")
                logger.info(f"  Estimated duration: {test_plan.get('resource_estimation', {}).get('total_hours', 0)} hours")
                logger.info(f"  Risk level: {test_plan.get('risk_assessment', {}).get('overall_risk', 'Unknown')}")
                logger.info(f"  Recommended framework: {test_plan.get('execution_strategy', {}).get('framework', 'Unknown')}")
            
            self.test_results["agent_outputs"]["planning"] = planning_result
            
            return True, planning_result
            
        except Exception as e:
            logger.error(f"Planning Agent test failed: {str(e)}")
            self.test_results["issues_found"].append(f"Planning Agent error: {str(e)}")
            return False, None
    
    async def test_test_creation_with_real_scenarios(self, planning_result):
        """Test Test Creation Agent with real planning output"""
        logger.info("🧪 Testing Test Creation Agent with real planning output")
        
        try:
            if not planning_result or 'test_plan' not in planning_result:
                logger.warning("No valid planning result to work with")
                return False, None
            
            # Create task for test creation agent
            task_data = {
                "task_type": "test_creation",
                "test_plan": planning_result['test_plan']
            }
            
            # Get test creation result
            creation_result = await self.orchestrator.agents.get("test_creation").process_task(task_data)

            
            logger.info("Test Creation Agent Results:")
            logger.info(f"  Status: {creation_result.get('status', 'Unknown')}")
            
            # Check what files were generated
            if 'test_files' in creation_result:
                logger.info(f"  Generated {len(creation_result['test_files'])} test files")
                for file_info in creation_result['test_files']:
                    logger.info(f"    - {file_info}")
            
            # Check for generated code
            if 'generated_tests' in creation_result:
                logger.info(f"  Generated {len(creation_result['generated_tests'])} test cases")
            
            self.test_results["agent_outputs"]["test_creation"] = creation_result
            
            # Try to read generated files to see actual code
            await self._analyze_generated_code(creation_result)
            
            return True, creation_result
            
        except Exception as e:
            logger.error(f"Test Creation Agent test failed: {str(e)}")
            self.test_results["issues_found"].append(f"Test Creation Agent error: {str(e)}")
            return False, None
    
    async def _analyze_generated_code(self, creation_result):
        """Analyze the actual generated test code"""
        logger.info("🔍 Analyzing generated test code")
        
        try:
            # Look for generated files in work_dir
            work_dir = Path("work_dir/test_creation_agent")
            if work_dir.exists():
                generated_files = list(work_dir.glob("*.py")) + list(work_dir.glob("*.js"))
                
                for file_path in generated_files:
                    logger.info(f"📄 Analyzing file: {file_path.name}")
                    
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Analyze the content
                        analysis = self._analyze_code_content(content, file_path.name)
                        self.test_results["generated_code"][file_path.name] = analysis
                        
                        logger.info(f"  Lines of code: {analysis['lines_of_code']}")
                        logger.info(f"  Contains selectors: {analysis['has_selectors']}")
                        logger.info(f"  Contains assertions: {analysis['has_assertions']}")
                        logger.info(f"  Contains waits: {analysis['has_waits']}")
                        logger.info(f"  Is template: {analysis['is_template']}")
                        
                    except Exception as e:
                        logger.warning(f"Could not analyze {file_path.name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Code analysis failed: {str(e)}")
    
    def _analyze_code_content(self, content: str, filename: str) -> dict:
        """Analyze the content of generated code"""
        analysis = {
            "filename": filename,
            "lines_of_code": len(content.split('\n')),
            "has_selectors": False,
            "has_assertions": False,
            "has_waits": False,
            "has_real_urls": False,
            "is_template": False,
            "issues": []
        }
        
        # Check for selectors
        selector_patterns = ['#', '.', '[data-', 'css=', 'xpath=', 'text=']
        analysis["has_selectors"] = any(pattern in content for pattern in selector_patterns)
        
        # Check for assertions
        assertion_patterns = ['expect(', 'assert', 'should', 'toBe', 'toEqual', 'toContain']
        analysis["has_assertions"] = any(pattern in content for pattern in assertion_patterns)
        
        # Check for waits
        wait_patterns = ['waitFor', 'wait(', 'sleep', 'delay', 'timeout']
        analysis["has_waits"] = any(pattern in content for pattern in wait_patterns)
        
        # Check for real URLs
        analysis["has_real_urls"] = 'advantageonlineshopping.com' in content
        
        # Check if it's just a template
        template_indicators = ['{', '}', 'placeholder', 'TODO', 'REPLACE', '{{', '}}']
        analysis["is_template"] = any(indicator in content for indicator in template_indicators)
        
        # Identify issues
        if not analysis["has_selectors"]:
            analysis["issues"].append("No element selectors found")
        
        if not analysis["has_assertions"]:
            analysis["issues"].append("No test assertions found")
        
        if analysis["is_template"]:
            analysis["issues"].append("Code appears to be template with placeholders")
        
        if not analysis["has_real_urls"]:
            analysis["issues"].append("No real application URLs found")
        
        return analysis
    
    async def test_complete_workflow(self):
        """Test the complete workflow with real scenarios"""
        logger.info("🧪 Testing complete agent workflow with real scenarios")
        
        try:
            # Use the complete orchestrator
            input_files = ["advantage_shopping_scenarios.txt"]
            
            # Run the complete workflow
            workflow_result = await self.orchestrator.execute_complete_workflow(input_files)
            
            logger.info("Complete Workflow Results:")
            logger.info(f"  Success: {workflow_result.get('success', False)}")
            logger.info(f"  Total steps: {len(workflow_result.get('steps', []))}")
            
            # Log each step result
            for step in workflow_result.get('steps', []):
                logger.info(f"  Step '{step['step']}': {step['success']}")
                if not step['success'] and 'error' in step:
                    logger.warning(f"    Error: {step['error']}")
            
            self.test_results["complete_workflow"] = workflow_result
            
            return True, workflow_result
            
        except Exception as e:
            logger.error(f"Complete workflow test failed: {str(e)}")
            self.test_results["issues_found"].append(f"Complete workflow error: {str(e)}")
            return False, None
    
    async def generate_insights(self):
        """Generate insights from the test results"""
        logger.info("🧠 Generating insights from test results")
        
        insights = []
        
        # Analyze parsing success
        if self.test_results.get("parsing_success", False):
            insights.append("✅ Scenario parsing works correctly")
        else:
            insights.append("❌ Scenario parsing needs improvement")
        
        # Analyze agent outputs
        if "planning" in self.test_results["agent_outputs"]:
            insights.append("✅ Planning Agent processes real scenarios")
        
        if "test_creation" in self.test_results["agent_outputs"]:
            insights.append("✅ Test Creation Agent generates output")
        
        # Analyze generated code
        code_issues = []
        for filename, analysis in self.test_results["generated_code"].items():
            if analysis["is_template"]:
                code_issues.append(f"❌ {filename} is still template-based")
            if not analysis["has_selectors"]:
                code_issues.append(f"❌ {filename} lacks element selectors")
            if not analysis["has_assertions"]:
                code_issues.append(f"❌ {filename} lacks test assertions")
            if analysis["has_real_urls"]:
                insights.append(f"✅ {filename} contains real application URLs")
        
        if code_issues:
            insights.extend(code_issues)
        else:
            insights.append("✅ Generated code quality is good")
        
        # Overall assessment
        if len(self.test_results["issues_found"]) == 0:
            insights.append("🎉 All tests passed - framework is working well")
        elif len(self.test_results["issues_found"]) < 3:
            insights.append("⚠️ Minor issues found - framework mostly working")
        else:
            insights.append("🚨 Multiple issues found - framework needs significant work")
        
        self.test_results["insights"] = insights
        
        # Log insights
        logger.info("📊 Test Insights:")
        for insight in insights:
            logger.info(f"  {insight}")
    
    async def run_all_tests(self):
        """Run all real scenario tests"""
        logger.info("🚀 Starting Real Scenario Testing")
        
        # Test 1: Parse real scenarios
        parsing_success, scenarios = await self.test_scenario_parsing()
        
        # Test 2: Planning Agent with real scenarios
        planning_success, planning_result = False, None
        if parsing_success and scenarios:
            planning_success, planning_result = await self.test_planning_agent_with_real_scenarios(scenarios)
        
        # Test 3: Test Creation Agent with real planning
        creation_success, creation_result = False, None
        if planning_success and planning_result:
            creation_success, creation_result = await self.test_test_creation_with_real_scenarios(planning_result)
        
        # Test 4: Complete workflow
        workflow_success, workflow_result = await self.test_complete_workflow()
        
        # Generate insights
        await self.generate_insights()
        
        # Save results
        results_file = f"real_scenario_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            def default_serializer(o):
                if isinstance(o, (datetime, TestStep)):
                    return str(o)
                raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
            json.dump(self.test_results, f, indent=2, default=default_serializer)

        
        # Summary
        total_tests = 4
        passed_tests = sum([parsing_success, planning_success, creation_success, workflow_success])
        
        logger.info(f"📊 Real Scenario Test Results:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Success Rate: {(passed_tests / total_tests) * 100:.1f}%")
        logger.info(f"   Results saved to: {results_file}")
        
        return self.test_results

async def main():
    """Main test function"""
    tester = RealScenarioTester()
    await tester.orchestrator.initialize()
    results = await tester.run_all_tests()
    
    print("\n" + "="*60)
    print("REAL SCENARIO TEST RESULTS")
    print("="*60)
    
    print("\nKey Insights:")
    for insight in results.get("insights", []):
        print(f"  {insight}")
    
    if results.get("issues_found"):
        print("\nIssues Found:")
        for issue in results["issues_found"]:
            print(f"  🚨 {issue}")
    
    print("\nGenerated Code Analysis:")
    for filename, analysis in results.get("generated_code", {}).items():
        print(f"  📄 {filename}:")
        print(f"    Lines: {analysis['lines_of_code']}")
        print(f"    Has selectors: {analysis['has_selectors']}")
        print(f"    Has assertions: {analysis['has_assertions']}")
        print(f"    Is template: {analysis['is_template']}")
        if analysis['issues']:
            for issue in analysis['issues']:
                print(f"    ❌ {issue}")
    
    print("\nNext Steps:")
    code_analysis = results.get("generated_code", {})
    if any(analysis.get("is_template", False) for analysis in code_analysis.values()):
        print("  🔧 Priority: Fix test code generation - currently generating templates")
    if any(not analysis.get("has_selectors", True) for analysis in code_analysis.values()):
        print("  🔧 Priority: Add element selector generation")
    if any(not analysis.get("has_assertions", True) for analysis in code_analysis.values()):
        print("  🔧 Priority: Add test assertion generation")
    
    if not results.get("issues_found") and code_analysis:
        print("  ✅ Framework is working well with real scenarios!")
        print("  ✅ Ready to enhance test code generation quality")

if __name__ == "__main__":
    asyncio.run(main())

