#!/usr/bin/env python3
"""
Test Creation Agent Enhancement Validator
========================================
This script tests the current Test Creation Agent to identify what needs enhancement
for generating real working code instead of templates.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import required components
from agents.test_creation_agent import TestCreationAgent
from agents.discovery_agent import DiscoveryAgent
from models.local_ai_provider import LocalAIProvider
from parsers.unified_parser import UnifiedTestFileParser

class TestCreationEnhancementValidator:
    """Validate current Test Creation Agent and identify enhancement needs"""
    
    def __init__(self):
        self.ai_provider = LocalAIProvider()
        self.test_creation_agent = TestCreationAgent(local_ai_provider=self.ai_provider)
        self.discovery_agent = DiscoveryAgent(local_ai_provider=self.ai_provider)
        self.parser = UnifiedTestFileParser()
        
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "enhancement_needs": [],
            "summary": {}
        }
    
    async def test_current_code_generation(self):
        """Test what the current Test Creation Agent actually generates"""
        logger.info("🧪 Testing current code generation capabilities")
        
        try:
            # Create a simple test scenario
            task_data = {
                "test_plan": {
                    "test_cases": [
                        {
                            "name": "login_test",
                            "description": "Test user login functionality",
                            "steps": [
                                "Navigate to login page",
                                "Enter username 'testuser'",
                                "Enter password 'testpass'",
                                "Click login button",
                                "Verify successful login"
                            ],
                            "framework": "playwright"
                        }
                    ],
                    "framework": "playwright"
                },
                "application_data": {
                    "selectors": {
                        "username_field": "#username",
                        "password_field": "#password",
                        "login_button": "#loginBtn",
                        "success_indicator": ".welcome-message"
                    },
                    "base_url": "https://advantageonlineshopping.com"
                }
            }
            
            result = await self.test_creation_agent.process_task(task_data)
            
            # Analyze the generated code
            if result.get("status") == "completed":
                generated_files = result.get("generated_files", [])
                logger.info(f"✅ Generated {len(generated_files)} files")
                
                # Check each generated file
                for file_info in generated_files:
                    file_path = file_info.get("path")
                    if file_path and Path(file_path).exists():
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Analyze code quality
                        analysis = self.analyze_generated_code(content, file_info.get("type", "unknown"))
                        logger.info(f"📄 {Path(file_path).name}: {analysis['summary']}")
                        
                        self.validation_results["tests"][f"generated_{file_info.get('type', 'file')}"] = {
                            "file_path": file_path,
                            "analysis": analysis,
                            "content_preview": content[:200] + "..." if len(content) > 200 else content
                        }
                
                return True
            else:
                logger.error(f"❌ Code generation failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}")
            self.validation_results["tests"]["current_code_generation"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def analyze_generated_code(self, content: str, file_type: str) -> dict:
        """Analyze the quality and completeness of generated code"""
        analysis = {
            "summary": "",
            "issues": [],
            "strengths": [],
            "enhancement_needs": []
        }
        
        # Check for real vs template code
        if "{{" in content and "}}" in content:
            analysis["issues"].append("Contains template placeholders instead of real code")
            analysis["enhancement_needs"].append("Replace templates with real executable code")
        else:
            analysis["strengths"].append("No template placeholders found")
        
        # Check for proper imports
        if file_type == "test" and "import" in content:
            if "playwright" in content or "selenium" in content:
                analysis["strengths"].append("Contains proper framework imports")
            else:
                analysis["issues"].append("Missing test framework imports")
        
        # Check for real selectors
        if "#" in content or "." in content or "[" in content:
            analysis["strengths"].append("Contains CSS selectors")
        else:
            analysis["issues"].append("No element selectors found")
        
        # Check for assertions
        if "assert" in content or "expect" in content or "should" in content:
            analysis["strengths"].append("Contains test assertions")
        else:
            analysis["issues"].append("No test assertions found")
            analysis["enhancement_needs"].append("Add proper test assertions")
        
        # Check for error handling
        if "try:" in content or "except:" in content or "catch" in content:
            analysis["strengths"].append("Contains error handling")
        else:
            analysis["issues"].append("No error handling found")
            analysis["enhancement_needs"].append("Add error handling")
        
        # Check for configuration
        if "config" in content.lower() or "setup" in content.lower():
            analysis["strengths"].append("Contains configuration/setup")
        else:
            analysis["issues"].append("No configuration found")
            analysis["enhancement_needs"].append("Add proper test configuration")
        
        # Generate summary
        issue_count = len(analysis["issues"])
        strength_count = len(analysis["strengths"])
        
        if issue_count == 0:
            analysis["summary"] = f"✅ High quality ({strength_count} strengths)"
        elif issue_count <= 2:
            analysis["summary"] = f"⚠️ Good with issues ({issue_count} issues, {strength_count} strengths)"
        else:
            analysis["summary"] = f"❌ Needs work ({issue_count} issues, {strength_count} strengths)"
        
        return analysis
    
    async def test_with_discovery_integration(self):
        """Test Test Creation Agent with real Discovery Agent data"""
        logger.info("🧪 Testing integration with Discovery Agent")
        
        try:
            # Get real discovery data
            discovery_task = {
                "task_type": "analyze_application",
                "application_url": "https://advantageonlineshopping.com",
                "analysis_depth": "basic"
            }
            
            discovery_result = await self.discovery_agent.process_task(discovery_task)
            
            if discovery_result.get("status") == "completed":
                # Use discovery data for test creation
                test_task = {
                    "test_plan": {
                        "test_cases": [
                            {
                                "name": "discovered_element_test",
                                "description": "Test using discovered elements",
                                "steps": [
                                    "Navigate to application",
                                    "Interact with discovered elements",
                                    "Verify expected behavior"
                                ],
                                "framework": "playwright"
                            }
                        ],
                        "framework": "playwright"
                    },
                    "application_data": discovery_result.get("analysis_result", {})
                }
                
                creation_result = await self.test_creation_agent.process_task(test_task)
                
                if creation_result.get("status") == "completed":
                    logger.info("✅ Integration with Discovery Agent successful")
                    
                    # Analyze if discovery data was actually used
                    generated_files = creation_result.get("generated_files", [])
                    discovery_data_used = False
                    
                    for file_info in generated_files:
                        if file_info.get("path") and Path(file_info["path"]).exists():
                            with open(file_info["path"], 'r') as f:
                                content = f.read()
                            
                            # Check if discovery selectors were used
                            discovery_selectors = discovery_result.get("analysis_result", {}).get("discovered_pages", [])
                            for page in discovery_selectors:
                                for element in page.get("elements", []):
                                    if element.get("selector", "") in content:
                                        discovery_data_used = True
                                        break
                    
                    if discovery_data_used:
                        logger.info("✅ Discovery data was integrated into generated code")
                    else:
                        logger.warning("⚠️ Discovery data was not used in generated code")
                        self.validation_results["enhancement_needs"].append(
                            "Integrate Discovery Agent data into code generation"
                        )
                    
                    return True
                else:
                    logger.error("❌ Test creation failed with discovery data")
                    return False
            else:
                logger.error("❌ Discovery agent failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Integration test failed: {str(e)}")
            return False
    
    async def identify_enhancement_priorities(self):
        """Identify the top priorities for enhancing Test Creation Agent"""
        logger.info("🎯 Identifying enhancement priorities")
        
        # Collect all enhancement needs
        all_needs = set(self.validation_results["enhancement_needs"])
        
        # Add needs from code analysis
        for test_name, test_data in self.validation_results["tests"].items():
            if "analysis" in test_data:
                all_needs.update(test_data["analysis"].get("enhancement_needs", []))
        
        # Prioritize enhancement needs
        priority_map = {
            "Replace templates with real executable code": 1,  # Highest priority
            "Add proper test assertions": 2,
            "Integrate Discovery Agent data into code generation": 3,
            "Add error handling": 4,
            "Add proper test configuration": 5
        }
        
        prioritized_needs = sorted(all_needs, key=lambda x: priority_map.get(x, 99))
        
        logger.info("🎯 Enhancement Priorities:")
        for i, need in enumerate(prioritized_needs, 1):
            logger.info(f"  {i}. {need}")
        
        self.validation_results["enhancement_priorities"] = prioritized_needs
        
        return prioritized_needs
    
    async def run_validation(self):
        """Run complete validation of Test Creation Agent"""
        logger.info("🚀 Starting Test Creation Agent Enhancement Validation")
        
        # Run tests
        test1 = await self.test_current_code_generation()
        test2 = await self.test_with_discovery_integration()
        
        # Identify priorities
        priorities = await self.identify_enhancement_priorities()
        
        # Calculate summary
        total_tests = 2
        passed_tests = sum([test1, test2])
        success_rate = (passed_tests / total_tests) * 100
        
        self.validation_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "top_priority": priorities[0] if priorities else "No priorities identified",
            "enhancement_count": len(priorities)
        }
        
        # Save results
        results_file = f"test_creation_enhancement_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        logger.info(f"📊 Validation Results:")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Top Priority: {self.validation_results['summary']['top_priority']}")
        logger.info(f"   Enhancement Needs: {len(priorities)}")
        logger.info(f"   Results saved to: {results_file}")
        
        return self.validation_results

async def main():
    """Main validation function"""
    validator = TestCreationEnhancementValidator()
    results = await validator.run_validation()
    
    print("\n" + "="*80)
    print("TEST CREATION AGENT ENHANCEMENT VALIDATION")
    print("="*80)
    
    summary = results["summary"]
    print(f"\nValidation Results:")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print(f"  Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
    print(f"  Enhancement Needs: {summary['enhancement_count']}")
    
    print(f"\nTop Enhancement Priority:")
    print(f"  🎯 {summary['top_priority']}")
    
    print(f"\nAll Enhancement Priorities:")
    for i, priority in enumerate(results.get("enhancement_priorities", []), 1):
        print(f"  {i}. {priority}")
    
    print(f"\nNext Steps:")
    print(f"  1. Address the top priority enhancement")
    print(f"  2. Implement real code generation instead of templates")
    print(f"  3. Integrate Discovery Agent data properly")
    print(f"  4. Add comprehensive test assertions and error handling")
    
    if summary['success_rate'] >= 75:
        print(f"\n✅ Test Creation Agent foundation is solid!")
        print(f"Ready for enhancement to generate real working code.")
    else:
        print(f"\n⚠️ Test Creation Agent needs significant work.")
        print(f"Focus on addressing the identified issues first.")

if __name__ == "__main__":
    asyncio.run(main())

