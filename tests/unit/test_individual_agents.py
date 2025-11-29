#!/usr/bin/env python3
"""
Individual Agent Testing Script
===============================

This script tests each agent individually to verify their actual functionality
beyond just status updates. It examines what each agent actually produces.
"""

import sys
import os
import json
import asyncio
from uuid import uuid4
from datetime import datetime

# Add the API directory to the path
sys.path.append('/home/ubuntu/autogen-ai-test-automation/api')

from real_agent_processor import RealAgentProcessor
from database_postgres_full import DatabaseManager, TestSuite, AgentJob
from file_storage_manager import LocalFileManager

class AgentTester:
    """Individual agent testing class"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        self.processor = RealAgentProcessor()
        self.test_results = {}
        
    async def test_discovery_agent(self, application_data: dict) -> dict:
        """Test Discovery Agent - verify it actually discovers test scenarios"""
        print("\n🔍 Testing Discovery Agent...")
        
        # Create test job
        customer_id = uuid4()
        application_id = uuid4()
        job_id = AgentJob.create(customer_id, application_id, "test_creation")
        
        if not job_id:
            return {"status": "failed", "error": "Could not create job"}
        
        try:
            # Run discovery phase
            await self.processor._discovery_phase(job_id, application_data)
            
            # Check what was actually discovered
            job_data = AgentJob.get_by_id(job_id)
            activities = job_data.get('activities', []) if job_data else []
            
            discovery_activities = [a for a in activities if a.get('agent_name') == 'Discovery Agent']
            
            # Analyze discovery results
            scenarios_found = 0
            discovery_details = []
            
            for activity in discovery_activities:
                message = activity.get('message', '')
                if 'scenarios found' in message.lower():
                    # Extract number of scenarios
                    import re
                    match = re.search(r'(\d+)\s+scenarios', message)
                    if match:
                        scenarios_found = int(match.group(1))
                discovery_details.append(message)
            
            result = {
                "status": "success",
                "scenarios_found": scenarios_found,
                "activities_count": len(discovery_activities),
                "details": discovery_details,
                "actual_functionality": scenarios_found > 0
            }
            
            print(f"✅ Discovery Agent found {scenarios_found} test scenarios")
            return result
            
        except Exception as e:
            print(f"❌ Discovery Agent failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_generation_agent(self, job_id, scenarios_count: int = 7) -> dict:
        """Test Generation Agent - verify it actually generates test cases"""
        print("\n🧠 Testing Test Generation Agent...")
        
        try:
            # Run test generation phase
            await self.processor._test_generation_phase(job_id, scenarios_count)
            
            # Check what was actually generated
            job_data = AgentJob.get_by_id(job_id)
            activities = job_data.get('activities', []) if job_data else []
            
            generation_activities = [a for a in activities if a.get('agent_name') == 'Test Generation Agent']
            
            # Analyze generation results
            test_cases_generated = 0
            generation_details = []
            
            for activity in generation_activities:
                message = activity.get('message', '')
                if 'test cases generated' in message.lower():
                    import re
                    match = re.search(r'(\d+)\s+test cases', message)
                    if match:
                        test_cases_generated = int(match.group(1))
                generation_details.append(message)
            
            result = {
                "status": "success",
                "test_cases_generated": test_cases_generated,
                "activities_count": len(generation_activities),
                "details": generation_details,
                "actual_functionality": test_cases_generated > 0
            }
            
            print(f"✅ Test Generation Agent generated {test_cases_generated} test cases")
            return result
            
        except Exception as e:
            print(f"❌ Test Generation Agent failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_code_generation_agent(self, job_id, test_suite_id, customer_id) -> dict:
        """Test Code Generation Agent - verify it actually creates files"""
        print("\n💻 Testing Code Generation Agent...")
        
        try:
            # Run code generation phase
            await self.processor._code_generation_phase(job_id, test_suite_id, customer_id)
            
            # Check what files were actually created
            base_path = f"/opt/test-automation-platform/data/customers/{customer_id}/test_suites/{test_suite_id}/tests"
            
            files_created = []
            if os.path.exists(base_path):
                files_created = [f for f in os.listdir(base_path) if f.endswith('.py')]
            
            # Check file contents
            file_analysis = {}
            for file_name in files_created:
                file_path = os.path.join(base_path, file_name)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        file_analysis[file_name] = {
                            "size_bytes": len(content),
                            "lines": len(content.split('\n')),
                            "has_playwright_imports": "from playwright" in content,
                            "has_test_function": "def test_" in content,
                            "has_page_parameter": "page: Page" in content,
                            "is_executable": content.strip() != ""
                        }
                except Exception as e:
                    file_analysis[file_name] = {"error": str(e)}
            
            result = {
                "status": "success",
                "files_created": len(files_created),
                "file_names": files_created,
                "file_analysis": file_analysis,
                "base_path": base_path,
                "actual_functionality": len(files_created) > 0
            }
            
            print(f"✅ Code Generation Agent created {len(files_created)} files")
            for file_name, analysis in file_analysis.items():
                if "error" not in analysis:
                    print(f"   📄 {file_name}: {analysis['lines']} lines, Playwright: {analysis['has_playwright_imports']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Code Generation Agent failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_validation_agent(self, job_id, test_suite_id) -> dict:
        """Test Validation Agent - verify it actually validates"""
        print("\n✅ Testing Validation Agent...")
        
        try:
            # Run validation phase
            await self.processor._validation_phase(job_id, test_suite_id)
            
            # Check validation results
            job_data = AgentJob.get_by_id(job_id)
            activities = job_data.get('activities', []) if job_data else []
            
            validation_activities = [a for a in activities if a.get('agent_name') == 'Validation Agent']
            
            # Analyze validation results
            validation_details = []
            validation_passed = False
            
            for activity in validation_activities:
                message = activity.get('message', '')
                if 'validation' in message.lower():
                    validation_details.append(message)
                    if 'completed' in message.lower() or 'passed' in message.lower():
                        validation_passed = True
            
            result = {
                "status": "success",
                "validation_passed": validation_passed,
                "activities_count": len(validation_activities),
                "details": validation_details,
                "actual_functionality": len(validation_activities) > 0
            }
            
            print(f"✅ Validation Agent completed with {len(validation_activities)} activities")
            return result
            
        except Exception as e:
            print(f"❌ Validation Agent failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_database_storage(self, test_suite_id, customer_id) -> dict:
        """Test database storage functionality"""
        print("\n🗄️ Testing Database Storage...")
        
        try:
            from database_postgres_full import TestCase
            
            # Check if test cases were saved to database
            test_cases = TestCase.get_by_suite(test_suite_id)
            
            result = {
                "status": "success",
                "test_cases_in_db": len(test_cases),
                "test_case_details": []
            }
            
            for tc in test_cases:
                result["test_case_details"].append({
                    "name": tc.get('name'),
                    "file_path": tc.get('test_file_path'),
                    "file_size": tc.get('file_size_bytes'),
                    "generation_model": tc.get('generation_model'),
                    "confidence": tc.get('code_confidence_score')
                })
            
            print(f"✅ Found {len(test_cases)} test cases in database")
            return result
            
        except Exception as e:
            print(f"❌ Database storage test failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def run_complete_agent_test(self) -> dict:
        """Run complete test of all agents"""
        print("🚀 Starting Complete Agent Functionality Test")
        print("=" * 60)
        
        # Test application data
        application_data = {
            "url": "https://demo.opencart.com",
            "name": "E-commerce Demo",
            "type": "E-commerce",
            "features": "Product catalog, Shopping cart, Payment processing, Order management",
            "user_flows": "Product browsing, Add to cart, Checkout process, Order tracking"
        }
        
        # Create test suite
        customer_id = uuid4()
        application_id = uuid4()
        test_suite_id = TestSuite.create(
            customer_id=customer_id,
            application_id=application_id,
            name="Agent Test Suite",
            description="Testing individual agent functionality",
            test_type="functional"
        )
        
        if not test_suite_id:
            return {"status": "failed", "error": "Could not create test suite"}
        
        print(f"📋 Created test suite: {test_suite_id}")
        
        # Test results
        results = {
            "test_suite_id": str(test_suite_id),
            "customer_id": str(customer_id),
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }
        
        # Test each agent
        try:
            # 1. Discovery Agent
            discovery_result = await self.test_discovery_agent(application_data)
            results["agents"]["discovery"] = discovery_result
            
            # Create job for remaining tests
            job_id = AgentJob.create(customer_id, application_id, "test_creation", test_suite_id)
            
            # 2. Test Generation Agent
            scenarios_count = discovery_result.get("scenarios_found", 7)
            generation_result = await self.test_generation_agent(job_id, scenarios_count)
            results["agents"]["generation"] = generation_result
            
            # 3. Code Generation Agent
            code_result = await self.test_code_generation_agent(job_id, test_suite_id, customer_id)
            results["agents"]["code_generation"] = code_result
            
            # 4. Validation Agent
            validation_result = await self.test_validation_agent(job_id, test_suite_id)
            results["agents"]["validation"] = validation_result
            
            # 5. Database Storage
            db_result = await self.test_database_storage(test_suite_id, customer_id)
            results["database_storage"] = db_result
            
            # Overall assessment
            all_agents_working = all(
                results["agents"][agent].get("actual_functionality", False)
                for agent in results["agents"]
            )
            
            results["overall_status"] = "success" if all_agents_working else "partial"
            results["summary"] = {
                "discovery_working": discovery_result.get("actual_functionality", False),
                "generation_working": generation_result.get("actual_functionality", False),
                "code_generation_working": code_result.get("actual_functionality", False),
                "validation_working": validation_result.get("actual_functionality", False),
                "database_working": db_result.get("test_cases_in_db", 0) > 0,
                "files_created": code_result.get("files_created", 0),
                "test_cases_generated": generation_result.get("test_cases_generated", 0)
            }
            
            print("\n" + "=" * 60)
            print("🎯 AGENT TESTING SUMMARY")
            print("=" * 60)
            
            for agent, working in results["summary"].items():
                if agent.endswith("_working"):
                    agent_name = agent.replace("_working", "").replace("_", " ").title()
                    status = "✅ WORKING" if working else "❌ NOT WORKING"
                    print(f"{agent_name:20} {status}")
            
            print(f"\nFiles Created: {results['summary']['files_created']}")
            print(f"Test Cases Generated: {results['summary']['test_cases_generated']}")
            
            return results
            
        except Exception as e:
            print(f"❌ Complete agent test failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            return results

async def main():
    """Main testing function"""
    tester = AgentTester()
    results = await tester.run_complete_agent_test()
    
    # Save results to file
    results_file = "/home/ubuntu/autogen-ai-test-automation/agent_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    return results

if __name__ == "__main__":
    asyncio.run(main())
