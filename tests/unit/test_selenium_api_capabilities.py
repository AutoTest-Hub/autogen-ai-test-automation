#!/usr/bin/env python3
"""
Test Selenium and API Capabilities
==================================
Test the Enhanced Test Creation Agent with Selenium and API task types
"""

import asyncio
import json
import logging
from agents.test_creation_agent import EnhancedTestCreationAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_selenium_generation():
    """Test Selenium test generation capability"""
    logger.info("🧪 Testing Selenium test generation")
    
    try:
        # Initialize Enhanced Test Creation Agent
        agent = EnhancedTestCreationAgent()
        
        # Create Selenium test task
        selenium_task = {
            "task_type": "generate_selenium_tests",
            "application_url": "https://advantageonlineshopping.com",
            "test_plan": {
                "test_scenarios": [
                    {
                        "name": "login_test",
                        "description": "Test user login functionality",
                        "steps": [
                            "Navigate to login page",
                            "Enter credentials",
                            "Click login button",
                            "Verify successful login"
                        ]
                    }
                ]
            }
        }
        
        # Process the task
        result = await agent.process_task(selenium_task)
        
        # Validate result
        if result.get("status") == "success":
            logger.info("✅ Selenium test generation successful!")
            logger.info(f"Framework: {result.get('framework')}")
            logger.info(f"Generated files: {len(result.get('generated_files', []))}")
            return True
        else:
            logger.error(f"❌ Selenium test generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Selenium test generation error: {str(e)}")
        return False

async def test_api_generation():
    """Test API test generation capability"""
    logger.info("🧪 Testing API test generation")
    
    try:
        # Initialize Enhanced Test Creation Agent
        agent = EnhancedTestCreationAgent()
        
        # Create API test task
        api_task = {
            "task_type": "generate_api_tests",
            "api_base_url": "https://api.advantageonlineshopping.com",
            "test_plan": {
                "api_endpoints": [
                    {
                        "endpoint": "/auth/login",
                        "method": "POST",
                        "description": "User authentication endpoint"
                    },
                    {
                        "endpoint": "/products",
                        "method": "GET", 
                        "description": "Get product catalog"
                    }
                ]
            }
        }
        
        # Process the task
        result = await agent.process_task(api_task)
        
        # Validate result
        if result.get("status") == "success":
            logger.info("✅ API test generation successful!")
            logger.info(f"Framework: {result.get('framework')}")
            logger.info(f"Generated files: {len(result.get('generated_files', []))}")
            return True
        else:
            logger.error(f"❌ API test generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API test generation error: {str(e)}")
        return False

async def test_enhanced_capabilities():
    """Test enhanced capabilities"""
    logger.info("🧪 Testing enhanced capabilities")
    
    try:
        # Initialize Enhanced Test Creation Agent
        agent = EnhancedTestCreationAgent()
        
        # Get capabilities
        capabilities = agent.get_capabilities()
        
        # Check for new capabilities
        expected_capabilities = [
            "selenium_webdriver_tests",
            "api_requests_tests", 
            "multi_framework_support"
        ]
        
        missing_capabilities = []
        for cap in expected_capabilities:
            if cap not in capabilities:
                missing_capabilities.append(cap)
        
        if missing_capabilities:
            logger.error(f"❌ Missing capabilities: {missing_capabilities}")
            return False
        else:
            logger.info("✅ All enhanced capabilities present!")
            logger.info(f"Total capabilities: {len(capabilities)}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Enhanced capabilities test error: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("\n" + "="*70)
    print("TESTING SELENIUM AND API CAPABILITIES")
    print("="*70)
    
    # Test results
    results = {
        "enhanced_capabilities": False,
        "selenium_generation": False,
        "api_generation": False
    }
    
    # Run tests
    results["enhanced_capabilities"] = await test_enhanced_capabilities()
    results["selenium_generation"] = await test_selenium_generation()
    results["api_generation"] = await test_api_generation()
    
    # Calculate success rate
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100
    
    # Print results
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! Selenium and API capabilities are working!")
    elif success_rate >= 66:
        print("\n✅ MOSTLY SUCCESSFUL! Some capabilities working, minor issues to fix.")
    else:
        print("\n⚠️ NEEDS WORK! Major issues with Selenium and API capabilities.")
    
    return success_rate == 100

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

