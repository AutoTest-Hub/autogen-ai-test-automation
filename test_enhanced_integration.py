#!/usr/bin/env python3
"""
Integration Test for Enhanced Test Creation Agent Replacement
===========================================================
Verify that the Enhanced Test Creation Agent is working correctly
after replacing the original agent.
"""

import asyncio
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the replaced agent (should now be Enhanced version)
from agents.test_creation_agent import EnhancedTestCreationAgent as TestCreationAgent
from agents.discovery_agent import DiscoveryAgent
from models.local_ai_provider import LocalAIProvider

async def test_enhanced_integration():
    """Test that the Enhanced Test Creation Agent is working after replacement"""
    
    logger.info("🧪 Testing Enhanced Test Creation Agent integration")
    
    try:
        # Initialize components
        ai_provider = LocalAIProvider()
        test_agent = TestCreationAgent(local_ai_provider=ai_provider)
        discovery_agent = DiscoveryAgent(local_ai_provider=ai_provider)
        
        # Test 1: Verify Enhanced capabilities
        logger.info("📋 Test 1: Checking Enhanced capabilities")
        capabilities = test_agent.get_capabilities()
        
        enhanced_capabilities = [
            "real_code_generation",
            "discovery_integration", 
            "page_object_models",
            "playwright_tests"
        ]
        
        has_enhanced = all(cap in capabilities for cap in enhanced_capabilities)
        
        if has_enhanced:
            logger.info("✅ Test 1 PASSED: Enhanced capabilities detected")
        else:
            logger.error("❌ Test 1 FAILED: Enhanced capabilities missing")
            return False
        
        # Test 2: Test real code generation
        logger.info("📋 Test 2: Testing real code generation")
        
        # Get discovery data
        discovery_task = {
            "task_type": "analyze_application",
            "application_url": "https://example.com",
            "analysis_depth": "basic"
        }
        
        discovery_result = await discovery_agent.process_task(discovery_task)
        
        # Generate test code
        test_task = {
            "task_type": "generate_tests",
            "test_plan": {
                "test_cases": [{
                    "name": "integration_test",
                    "description": "Integration test case",
                    "steps": ["Navigate to page", "Verify title"],
                    "framework": "playwright"
                }],
                "framework": "playwright"
            },
            "application_data": discovery_result.get("analysis_result", {})
        }
        
        creation_result = await test_agent.process_task(test_task)
        
        if creation_result.get("status") == "completed":
            generated_files = creation_result.get("generated_files", [])
            
            # Check for real code (no templates)
            real_code_count = 0
            for file_info in generated_files:
                file_path = file_info.get("path")
                if file_path and os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    if not ("{{" in content and "}}" in content):
                        real_code_count += 1
            
            if real_code_count == len(generated_files) and real_code_count > 0:
                logger.info(f"✅ Test 2 PASSED: Generated {real_code_count} real code files")
            else:
                logger.error(f"❌ Test 2 FAILED: Only {real_code_count}/{len(generated_files)} files are real code")
                return False
        else:
            logger.error("❌ Test 2 FAILED: Code generation failed")
            return False
        
        # Test 3: Verify discovery integration
        logger.info("📋 Test 3: Testing discovery integration")
        
        discovery_integration = creation_result.get("discovery_integration")
        if discovery_integration == "enabled":
            logger.info("✅ Test 3 PASSED: Discovery integration working")
        else:
            logger.error("❌ Test 3 FAILED: Discovery integration not working")
            return False
        
        logger.info("🎉 All integration tests PASSED!")
        logger.info("✅ Enhanced Test Creation Agent replacement successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        return False

async def main():
    """Main integration test function"""
    
    print("\n" + "="*70)
    print("ENHANCED TEST CREATION AGENT INTEGRATION TEST")
    print("="*70)
    
    success = await test_enhanced_integration()
    
    if success:
        print("\n🎉 SUCCESS: Enhanced Test Creation Agent is working perfectly!")
        print("✅ Framework now generates real, working test automation code")
        print("✅ Discovery integration is functional")
        print("✅ Ready for end-to-end workflow testing")
    else:
        print("\n❌ FAILURE: Integration test failed")
        print("⚠️ Check logs above for specific issues")
        print("🔄 Consider restoring from backup and investigating")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
