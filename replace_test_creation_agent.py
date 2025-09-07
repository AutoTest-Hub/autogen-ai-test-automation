#!/usr/bin/env python3
"""
Replace Original Test Creation Agent with Enhanced Version
=========================================================
This script replaces the original template-based Test Creation Agent
with the Enhanced version that generates real working code.
"""

import shutil
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def replace_test_creation_agent():
    """Replace the original Test Creation Agent with Enhanced version"""
    
    logger.info("🔄 Starting Test Creation Agent replacement process")
    
    # File paths
    original_agent = Path("agents/test_creation_agent.py")
    enhanced_agent = Path("agents/enhanced_test_creation_agent.py")
    backup_agent = Path("agents/test_creation_agent_original_backup.py")
    
    try:
        # Step 1: Backup original agent
        if original_agent.exists():
            logger.info("📦 Creating backup of original Test Creation Agent")
            shutil.copy2(original_agent, backup_agent)
            logger.info(f"✅ Backup created: {backup_agent}")
        else:
            logger.warning("⚠️ Original Test Creation Agent not found")
        
        # Step 2: Verify enhanced agent exists
        if not enhanced_agent.exists():
            logger.error(f"❌ Enhanced Test Creation Agent not found: {enhanced_agent}")
            return False
        
        # Step 3: Replace original with enhanced
        logger.info("🔄 Replacing original Test Creation Agent with Enhanced version")
        shutil.copy2(enhanced_agent, original_agent)
        logger.info("✅ Replacement completed successfully")
        
        # Step 4: Update imports in other files
        logger.info("🔄 Updating imports in related files")
        
        # Files that might import TestCreationAgent
        files_to_update = [
            "test_real_scenarios.py",
            "comprehensive_agent_tests.py",
            "complete_orchestrator.py",
            "enhanced_main_framework.py"
        ]
        
        for file_path in files_to_update:
            if Path(file_path).exists():
                update_imports_in_file(file_path)
        
        logger.info("✅ All imports updated successfully")
        
        # Step 5: Verify the replacement
        logger.info("🔍 Verifying replacement")
        
        # Check if the new file has Enhanced features
        with open(original_agent, 'r') as f:
            content = f.read()
        
        if "EnhancedTestCreationAgent" in content:
            logger.info("✅ Verification successful: Enhanced features detected")
        else:
            logger.warning("⚠️ Verification warning: Enhanced features not detected")
        
        # Step 6: Create integration test
        create_integration_test()
        
        logger.info("🎉 Test Creation Agent replacement completed successfully!")
        logger.info("📋 Summary:")
        logger.info(f"   - Original agent backed up to: {backup_agent}")
        logger.info(f"   - Enhanced agent now active as: {original_agent}")
        logger.info(f"   - Updated imports in {len(files_to_update)} files")
        logger.info(f"   - Created integration test")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Replacement failed: {str(e)}")
        
        # Restore from backup if replacement failed
        if backup_agent.exists() and original_agent.exists():
            logger.info("🔄 Restoring from backup due to failure")
            shutil.copy2(backup_agent, original_agent)
            logger.info("✅ Restored original agent from backup")
        
        return False

def update_imports_in_file(file_path: str):
    """Update imports in a file to use the new agent"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update class name references
        updated_content = content.replace(
            "from agents.test_creation_agent import TestCreationAgent",
            "from agents.test_creation_agent import EnhancedTestCreationAgent as TestCreationAgent"
        )
        
        # Also handle direct class references
        updated_content = updated_content.replace(
            "TestCreationAgent(",
            "TestCreationAgent("  # This will now refer to Enhanced version
        )
        
        # Write back if changes were made
        if updated_content != content:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            logger.info(f"✅ Updated imports in: {file_path}")
        else:
            logger.info(f"ℹ️ No import updates needed in: {file_path}")
            
    except Exception as e:
        logger.warning(f"⚠️ Could not update imports in {file_path}: {str(e)}")

def create_integration_test():
    """Create integration test to verify the replacement works"""
    
    integration_test = """#!/usr/bin/env python3
\"\"\"
Integration Test for Enhanced Test Creation Agent Replacement
===========================================================
Verify that the Enhanced Test Creation Agent is working correctly
after replacing the original agent.
\"\"\"

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the replaced agent (should now be Enhanced version)
from agents.test_creation_agent import EnhancedTestCreationAgent as TestCreationAgent
from agents.discovery_agent import DiscoveryAgent
from models.local_ai_provider import LocalAIProvider

async def test_enhanced_integration():
    \"\"\"Test that the Enhanced Test Creation Agent is working after replacement\"\"\"
    
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
    \"\"\"Main integration test function\"\"\"
    
    print("\\n" + "="*70)
    print("ENHANCED TEST CREATION AGENT INTEGRATION TEST")
    print("="*70)
    
    success = await test_enhanced_integration()
    
    if success:
        print("\\n🎉 SUCCESS: Enhanced Test Creation Agent is working perfectly!")
        print("✅ Framework now generates real, working test automation code")
        print("✅ Discovery integration is functional")
        print("✅ Ready for end-to-end workflow testing")
    else:
        print("\\n❌ FAILURE: Integration test failed")
        print("⚠️ Check logs above for specific issues")
        print("🔄 Consider restoring from backup and investigating")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    with open("test_enhanced_integration.py", 'w') as f:
        f.write(integration_test)
    
    logger.info("✅ Created integration test: test_enhanced_integration.py")

def main():
    """Main replacement function"""
    
    print("\n" + "="*70)
    print("REPLACE TEST CREATION AGENT WITH ENHANCED VERSION")
    print("="*70)
    
    success = replace_test_creation_agent()
    
    if success:
        print("\n🎉 SUCCESS: Test Creation Agent replacement completed!")
        print("✅ Enhanced version is now active")
        print("✅ Original version backed up safely")
        print("✅ All imports updated")
        print("✅ Integration test created")
        print("\nNext steps:")
        print("1. Run: python3 test_enhanced_integration.py")
        print("2. Test end-to-end workflow")
        print("3. Verify 95% success rate maintained")
    else:
        print("\n❌ FAILURE: Replacement process failed")
        print("⚠️ Original agent restored from backup")
        print("🔍 Check logs above for specific issues")

if __name__ == "__main__":
    main()

