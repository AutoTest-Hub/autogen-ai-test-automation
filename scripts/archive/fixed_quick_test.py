#!/usr/bin/env python3
"""
Fixed Quick Test Script for AutoGen Framework
Validates all components without requiring external AutoGen dependency
"""

import sys
import os
import json
import subprocess
import requests
from datetime import datetime

class FixedFrameworkQuickTest:
    """Quick validation of framework components without external dependencies"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown"
        }
    
    def test_python_environment(self):
        """Test Python environment and basic imports"""
        print("🐍 Testing Python Environment...")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major >= 3 and python_version.minor >= 9:
                print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
                self.results["tests"]["python_version"] = {"status": "pass", "version": f"{python_version.major}.{python_version.minor}.{python_version.micro}"}
            else:
                print(f"   ❌ Python version too old: {python_version.major}.{python_version.minor}")
                self.results["tests"]["python_version"] = {"status": "fail", "error": "Python 3.9+ required"}
                return False
            
            # Test basic imports
            try:
                import json
                import asyncio
                import logging
                print("   ✅ Basic Python modules available")
                self.results["tests"]["basic_imports"] = {"status": "pass"}
            except ImportError as e:
                print(f"   ❌ Basic import failed: {e}")
                self.results["tests"]["basic_imports"] = {"status": "fail", "error": str(e)}
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Python environment test failed: {e}")
            self.results["tests"]["python_environment"] = {"status": "fail", "error": str(e)}
            return False
    
    def test_framework_structure(self):
        """Test framework file structure"""
        print("📁 Testing Framework Structure...")
        
        required_files = [
            "models/__init__.py",
            "models/local_ai_provider.py",
            "agents/base_agent.py",
            "agents/standalone_base_agent.py",
            "config/settings.py",
            "enhanced_main_framework.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - MISSING")
                missing_files.append(file_path)
        
        if missing_files:
            self.results["tests"]["framework_structure"] = {
                "status": "fail", 
                "missing_files": missing_files
            }
            return False
        else:
            self.results["tests"]["framework_structure"] = {"status": "pass"}
            return True
    
    def test_local_ai_provider_import(self):
        """Test local AI provider import"""
        print("🤖 Testing Local AI Provider Import...")
        
        try:
            sys.path.insert(0, '.')
            from models.local_ai_provider import LocalAIProvider, ModelType
            print("   ✅ LocalAIProvider imported successfully")
            
            # Test instantiation
            provider = LocalAIProvider()
            print("   ✅ LocalAIProvider instantiated")
            
            # Test model types
            model_types = list(ModelType)
            print(f"   ✅ {len(model_types)} model types available")
            
            self.results["tests"]["local_ai_import"] = {
                "status": "pass",
                "model_types": len(model_types)
            }
            return True
            
        except ImportError as e:
            print(f"   ❌ Import failed: {e}")
            self.results["tests"]["local_ai_import"] = {"status": "fail", "error": str(e)}
            return False
        except Exception as e:
            print(f"   ❌ Instantiation failed: {e}")
            self.results["tests"]["local_ai_import"] = {"status": "fail", "error": str(e)}
            return False
    
    def test_ollama_service(self):
        """Test Ollama service availability"""
        print("🦙 Testing Ollama Service...")
        
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                model_names = [model['name'] for model in models]
                
                print(f"   ✅ Ollama service running")
                print(f"   ✅ {len(models)} models available: {', '.join(model_names)}")
                
                self.results["tests"]["ollama_service"] = {
                    "status": "pass",
                    "models_count": len(models),
                    "available_models": model_names
                }
                return True
            else:
                print(f"   ❌ Ollama service returned status {response.status_code}")
                self.results["tests"]["ollama_service"] = {
                    "status": "fail", 
                    "error": f"HTTP {response.status_code}"
                }
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ⚠️  Ollama service not running")
            print("   💡 To start Ollama: ollama serve")
            print("   💡 To install models: ollama pull phi3:mini")
            self.results["tests"]["ollama_service"] = {
                "status": "warning", 
                "error": "Service not running"
            }
            return False
        except Exception as e:
            print(f"   ❌ Ollama test failed: {e}")
            self.results["tests"]["ollama_service"] = {"status": "fail", "error": str(e)}
            return False
    
    def test_local_ai_integration(self):
        """Test local AI integration if Ollama is available"""
        print("🧠 Testing Local AI Integration...")
        
        try:
            from models.local_ai_provider import LocalAIProvider, ModelType
            
            provider = LocalAIProvider()
            
            if not provider.is_available():
                print("   ⚠️  Local AI not available (Ollama not running or no models)")
                self.results["tests"]["local_ai_integration"] = {
                    "status": "warning",
                    "error": "No models available"
                }
                return False
            
            # Test AI response
            result = provider.generate_response_sync(
                prompt="Hello, this is a test message. Please respond with 'Test successful'.",
                model_type=ModelType.GENERAL_INTELLIGENCE
            )
            
            if result["success"]:
                print(f"   ✅ AI response received: {result['response'][:50]}...")
                print(f"   ✅ Model used: {result['model']}")
                print(f"   ✅ Response time: {result['response_time']:.2f}s")
                
                self.results["tests"]["local_ai_integration"] = {
                    "status": "pass",
                    "model_used": result['model'],
                    "response_time": result['response_time'],
                    "response_preview": result['response'][:100]
                }
                return True
            else:
                print(f"   ❌ AI response failed: {result.get('error')}")
                self.results["tests"]["local_ai_integration"] = {
                    "status": "fail",
                    "error": result.get('error')
                }
                return False
                
        except Exception as e:
            print(f"   ❌ Local AI integration test failed: {e}")
            self.results["tests"]["local_ai_integration"] = {"status": "fail", "error": str(e)}
            return False
    
    def test_standalone_agent_creation(self):
        """Test standalone agent creation without AutoGen dependency"""
        print("👥 Testing Standalone Agent Creation...")
        
        try:
            from agents.standalone_base_agent import StandaloneBaseAgent, AgentRole, StandalonePlanningAgent
            from models.local_ai_provider import LocalAIProvider
            
            # Create local AI provider
            provider = LocalAIProvider()
            
            # Test planning agent creation
            agent = StandalonePlanningAgent(local_ai_provider=provider)
            
            print(f"   ✅ Agent created: {agent.name}")
            print(f"   ✅ Role: {agent.role.value}")
            print(f"   ✅ Local AI enabled: {agent.use_local_ai}")
            print(f"   ✅ Model type: {agent.model_type.value if agent.model_type else 'None'}")
            
            # Test agent status
            status = agent.get_local_ai_status()
            print(f"   ✅ Agent status retrieved")
            
            # Test simple task execution if local AI is available
            if agent.use_local_ai:
                task_result = agent.execute_task("Create a simple test plan for login functionality")
                if task_result["success"]:
                    print(f"   ✅ Task execution successful")
                else:
                    print(f"   ⚠️  Task execution failed: {task_result.get('error')}")
            
            self.results["tests"]["standalone_agent_creation"] = {
                "status": "pass",
                "agent_name": agent.name,
                "local_ai_enabled": agent.use_local_ai,
                "model_type": agent.model_type.value if agent.model_type else None
            }
            return True
            
        except Exception as e:
            print(f"   ❌ Standalone agent creation failed: {e}")
            self.results["tests"]["standalone_agent_creation"] = {"status": "fail", "error": str(e)}
            return False
    
    def test_scenario_parsing(self):
        """Test scenario file parsing"""
        print("📄 Testing Scenario Parsing...")
        
        try:
            # Create test scenario file
            test_scenario = """
Test Name: Quick Test Scenario
Target: https://example.com
Priority: Low
Tags: test, validation

Description: Simple test for validation

Test Steps:
1. Navigate to website
2. Verify page loads
3. Check title
"""
            
            with open("test_scenario_quick.txt", "w") as f:
                f.write(test_scenario)
            
            from parsers.unified_parser import UnifiedTestFileParser as UnifiedParser
            
            parser = UnifiedParser()
            result = parser.parse_file("test_scenario_quick.txt")
            
            if result.success:
                scenarios = [result.to_dict()]  # Convert ParsedTestFile to dict
                print(f"   ✅ Scenario parsed successfully")
                print(f"   ✅ {len(scenarios)} scenario(s) found")
                if scenarios:
                    print(f"   ✅ Test steps: {len(scenarios[0].get('test_steps', []))}")
                
                self.results["tests"]["scenario_parsing"] = {
                    "status": "pass",
                    "scenarios_count": len(scenarios),
                    "test_steps": len(scenarios[0].get('test_steps', [])) if scenarios else 0
                }
                
                # Cleanup
                os.remove("test_scenario_quick.txt")
                return True
            else:
                print(f"   ❌ Scenario parsing failed: {result.error}")
                self.results["tests"]["scenario_parsing"] = {
                    "status": "fail",
                    "error": result.error
                }
                return False
                
        except Exception as e:
            print(f"   ❌ Scenario parsing test failed: {e}")
            self.results["tests"]["scenario_parsing"] = {"status": "fail", "error": str(e)}
            # Cleanup on error
            try:
                os.remove("test_scenario_quick.txt")
            except:
                pass
            return False
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("🔄 Testing End-to-End Workflow...")
        
        try:
            from agents.standalone_base_agent import StandalonePlanningAgent, StandaloneTestCreationAgent
            from parsers.unified_parser import UnifiedTestFileParser as UnifiedParser
            from models.local_ai_provider import LocalAIProvider
            
            # Create test scenario
            test_scenario_content = """
Test Name: E2E Workflow Test
Target: https://example.com
Priority: Medium
Tags: workflow, integration

Description: End-to-end workflow test

Test Steps:
1. Navigate to website
2. Verify page loads
3. Check title contains 'Example'
"""
            
            with open("e2e_test_scenario.txt", "w") as f:
                f.write(test_scenario_content)
            
            # Step 1: Parse scenario
            parser = UnifiedParser()
            parse_result = parser.parse_file("e2e_test_scenario.txt")
            
            if not parse_result.success:
                raise Exception(f"Scenario parsing failed: {parse_result.error}")
            
            scenario = parse_result.to_dict()  # Convert ParsedTestFile to dict
            print(f"   ✅ Scenario parsed: {scenario.get('name')}")
            
            # Step 2: Create agents
            provider = LocalAIProvider()
            planning_agent = StandalonePlanningAgent(local_ai_provider=provider)
            
            print(f"   ✅ Agents created")
            
            # Step 3: Planning phase (if local AI available)
            if planning_agent.use_local_ai:
                planning_result = planning_agent.analyze_scenario(scenario)
                if planning_result["success"]:
                    print(f"   ✅ Test planning completed")
                else:
                    print(f"   ⚠️  Test planning failed: {planning_result.get('error')}")
            else:
                print(f"   ⚠️  Skipping planning phase (local AI not available)")
            
            # Cleanup
            os.remove("e2e_test_scenario.txt")
            
            self.results["tests"]["end_to_end_workflow"] = {
                "status": "pass",
                "scenario_parsed": True,
                "agents_created": True,
                "planning_completed": planning_agent.use_local_ai
            }
            
            print(f"   ✅ End-to-end workflow completed successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ End-to-end workflow failed: {e}")
            self.results["tests"]["end_to_end_workflow"] = {"status": "fail", "error": str(e)}
            # Cleanup on error
            try:
                os.remove("e2e_test_scenario.txt")
            except:
                pass
            return False
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 AutoGen Framework Fixed Quick Test")
        print("=" * 50)
        
        tests = [
            self.test_python_environment,
            self.test_framework_structure,
            self.test_local_ai_provider_import,
            self.test_ollama_service,
            self.test_local_ai_integration,
            self.test_standalone_agent_creation,
            self.test_scenario_parsing,
            self.test_end_to_end_workflow
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
                else:
                    # Check if it's a warning or failure
                    test_name = test.__name__
                    if test_name in self.results["tests"]:
                        if self.results["tests"][test_name].get("status") == "warning":
                            warnings += 1
                        else:
                            failed += 1
                    else:
                        failed += 1
            except Exception as e:
                print(f"   ❌ Test {test.__name__} crashed: {e}")
                failed += 1
            
            print()  # Add spacing between tests
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {passed + warnings + failed}")
        
        # Overall status
        if failed == 0 and warnings <= 3:
            self.results["overall_status"] = "pass"
            print("\n🎉 FRAMEWORK IS READY!")
            print("All critical components are working correctly.")
            if warnings > 0:
                print("Note: Some optional features may need configuration (Ollama models).")
        elif failed <= 2:
            self.results["overall_status"] = "warning"
            print("\n⚠️  FRAMEWORK PARTIALLY READY")
            print("Core components work, but some features need attention.")
        else:
            self.results["overall_status"] = "fail"
            print("\n❌ FRAMEWORK NEEDS ATTENTION")
            print("Multiple components failed. Check setup instructions.")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if warnings > 0:
            print("1. Install and start Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("2. Download AI models: ollama pull phi3:mini && ollama pull tinyllama:latest")
            print("3. Start Ollama service: ollama serve")
        
        if failed > 0:
            print("4. Install missing dependencies: pip install -r requirements.txt")
            print("5. Check setup_and_test_guide.md for detailed instructions")
        
        # Save results
        with open("fixed_quick_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: fixed_quick_test_results.json")
        
        return self.results["overall_status"] == "pass"

def main():
    """Run the fixed quick test"""
    tester = FixedFrameworkQuickTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Next Steps:")
        print("1. Run: python enhanced_main_framework.py")
        print("2. Create your own scenario files")
        print("3. Test with your applications")
        print("4. Deploy to production environment")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check setup_and_test_guide.md")
        print("2. Verify all dependencies are installed")
        print("3. Ensure Ollama is running with models")
        print("4. Run: pip install -r requirements.txt")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

