#!/usr/bin/env python3
"""
Test Enhanced Test Creation Agent
================================
Test the enhanced version that generates real working code.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import components
from agents.enhanced_test_creation_agent import EnhancedTestCreationAgent
from agents.discovery_agent import DiscoveryAgent
from models.local_ai_provider import LocalAIProvider

async def test_enhanced_test_creation():
    """Test the enhanced test creation agent"""
    logger.info("🚀 Testing Enhanced Test Creation Agent")
    
    # Initialize components
    ai_provider = LocalAIProvider()
    enhanced_agent = EnhancedTestCreationAgent(local_ai_provider=ai_provider)
    discovery_agent = DiscoveryAgent(local_ai_provider=ai_provider)
    
    try:
        # Step 1: Get real discovery data
        logger.info("📍 Step 1: Getting discovery data")
        discovery_task = {
            "task_type": "analyze_application",
            "application_url": "https://advantageonlineshopping.com",
            "analysis_depth": "comprehensive"
        }
        
        discovery_result = await discovery_agent.process_task(discovery_task)
        
        if discovery_result.get("status") != "completed":
            logger.error("❌ Discovery failed")
            return False
        
        logger.info("✅ Discovery completed successfully")
        
        # Step 2: Create comprehensive test plan
        logger.info("📍 Step 2: Creating test plan with real scenarios")
        test_plan = {
            "test_cases": [
                {
                    "name": "user_login_test",
                    "description": "Test user authentication workflow",
                    "steps": [
                        "Navigate to login page",
                        "Enter valid username",
                        "Enter valid password", 
                        "Click login button",
                        "Verify successful login"
                    ],
                    "framework": "playwright",
                    "priority": "high"
                },
                {
                    "name": "product_search_test",
                    "description": "Test product search functionality",
                    "steps": [
                        "Navigate to home page",
                        "Enter search term in search box",
                        "Click search button",
                        "Verify search results displayed"
                    ],
                    "framework": "playwright",
                    "priority": "medium"
                }
            ],
            "framework": "playwright",
            "strategy": "page_object_model"
        }
        
        # Step 3: Generate real test code using discovery data
        logger.info("📍 Step 3: Generating real test code")
        creation_task = {
            "task_type": "generate_tests",
            "test_plan": test_plan,
            "application_data": discovery_result.get("analysis_result", {})
        }
        
        creation_result = await enhanced_agent.process_task(creation_task)
        
        if creation_result.get("status") != "completed":
            logger.error(f"❌ Test creation failed: {creation_result.get('error')}")
            return False
        
        # Step 4: Analyze generated files
        logger.info("📍 Step 4: Analyzing generated files")
        generated_files = creation_result.get("generated_files", [])
        
        logger.info(f"✅ Generated {len(generated_files)} files:")
        
        real_code_count = 0
        template_count = 0
        
        for file_info in generated_files:
            file_path = Path(file_info["path"])
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check if it's real code or template
                has_templates = "{{" in content and "}}" in content
                has_real_selectors = any(selector in content for selector in ["#", ".", "["])
                has_assertions = any(assertion in content for assertion in ["assert", "expect"])
                has_imports = "import" in content
                
                file_type = file_info.get("type", "unknown")
                
                if has_templates:
                    template_count += 1
                    status = "❌ TEMPLATE"
                else:
                    real_code_count += 1
                    status = "✅ REAL CODE"
                
                logger.info(f"   📄 {file_path.name} ({file_type}): {status}")
                logger.info(f"      - Selectors: {'✅' if has_real_selectors else '❌'}")
                logger.info(f"      - Assertions: {'✅' if has_assertions else '❌'}")
                logger.info(f"      - Imports: {'✅' if has_imports else '❌'}")
                
                # Show preview of generated code
                preview = content[:300].replace('\n', ' ')
                logger.info(f"      - Preview: {preview}...")
        
        # Step 5: Calculate success metrics
        logger.info("📍 Step 5: Calculating success metrics")
        
        total_files = len(generated_files)
        real_code_percentage = (real_code_count / total_files * 100) if total_files > 0 else 0
        
        discovery_integration = creation_result.get("discovery_integration") == "enabled"
        framework_used = creation_result.get("framework")
        total_tests = creation_result.get("total_tests", 0)
        
        # Overall assessment
        if real_code_percentage >= 80 and discovery_integration:
            overall_status = "✅ EXCELLENT"
            success_rate = 95
        elif real_code_percentage >= 60:
            overall_status = "✅ GOOD"
            success_rate = 80
        elif real_code_percentage >= 40:
            overall_status = "⚠️ FAIR"
            success_rate = 60
        else:
            overall_status = "❌ NEEDS WORK"
            success_rate = 30
        
        # Results summary
        logger.info("\n" + "="*60)
        logger.info("ENHANCED TEST CREATION AGENT RESULTS")
        logger.info("="*60)
        logger.info(f"Overall Status: {overall_status}")
        logger.info(f"Success Rate: {success_rate}%")
        logger.info(f"Files Generated: {total_files}")
        logger.info(f"Real Code Files: {real_code_count}")
        logger.info(f"Template Files: {template_count}")
        logger.info(f"Real Code Percentage: {real_code_percentage:.1f}%")
        logger.info(f"Discovery Integration: {'✅' if discovery_integration else '❌'}")
        logger.info(f"Framework: {framework_used}")
        logger.info(f"Test Cases: {total_tests}")
        
        # Save detailed results
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "success_rate": success_rate,
            "files_generated": total_files,
            "real_code_files": real_code_count,
            "template_files": template_count,
            "real_code_percentage": real_code_percentage,
            "discovery_integration": discovery_integration,
            "framework": framework_used,
            "test_cases": total_tests,
            "generated_files": generated_files
        }
        
        results_file = f"enhanced_test_creation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📊 Detailed results saved to: {results_file}")
        
        return success_rate >= 70
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        return False

async def main():
    """Main test function"""
    success = await test_enhanced_test_creation()
    
    if success:
        print("\n🎉 Enhanced Test Creation Agent is working well!")
        print("Ready to replace the original Test Creation Agent.")
    else:
        print("\n⚠️ Enhanced Test Creation Agent needs more work.")
        print("Continue development before replacing the original.")

if __name__ == "__main__":
    asyncio.run(main())

