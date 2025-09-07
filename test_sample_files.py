"""
Test script for AutoGen Test Automation Framework
Tests core components without full agent initialization
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add framework to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.unified_parser import UnifiedTestFileParser
from config.settings import settings, AgentRole


async def test_parser_functionality():
    """Test the parser functionality"""
    print("🧪 Testing Parser Functionality")
    print("=" * 40)
    
    try:
        # Create parser
        parser = UnifiedTestFileParser()
        print("✅ Parser created successfully")
        
        # Generate sample files
        samples_dir = "./test_samples"
        os.makedirs(samples_dir, exist_ok=True)
        
        sample_files = parser.generate_sample_files(samples_dir)
        print(f"✅ Generated sample files: {list(sample_files.keys())}")
        
        # Test parsing each file
        for file_format, file_path in sample_files.items():
            print(f"\n📄 Testing {file_format.upper()} file: {os.path.basename(file_path)}")
            
            # Parse file
            parsed_file = parser.parse_file(file_path)
            print(f"   ✅ Parsed successfully")
            print(f"   📝 Test Name: {parsed_file.test_name}")
            print(f"   🔢 Steps: {len(parsed_file.test_steps)}")
            print(f"   🏷️  Tags: {parsed_file.tags}")
            print(f"   ⚡ Complexity: {parsed_file.metadata.get('complexity_analysis', {}).get('estimated_complexity', 'unknown')}")
            
            # Validate file
            if file_format == "txt":
                validation = parser.txt_parser.validate_parsed_file(parsed_file)
            else:
                validation = parser.json_parser.validate_parsed_file(parsed_file)
            
            print(f"   ✅ Validation: {'PASSED' if validation['is_valid'] else 'FAILED'}")
            if validation.get('warnings'):
                print(f"   ⚠️  Warnings: {len(validation['warnings'])}")
            if validation.get('suggestions'):
                print(f"   💡 Suggestions: {len(validation['suggestions'])}")
        
        # Test batch validation
        print(f"\n📊 Testing Batch Validation")
        all_files = list(sample_files.values())
        parsed_files = parser.parse_multiple_files(all_files)
        validation_results = parser.validate_parsed_files(parsed_files)
        
        print(f"   ✅ Batch validation completed")
        print(f"   📁 Total files: {validation_results['total_files']}")
        print(f"   ✅ Valid files: {validation_results['valid_files']}")
        print(f"   ❌ Invalid files: {validation_results['invalid_files']}")
        print(f"   📈 Overall status: {validation_results['overall_status']}")
        
        # Test statistics
        stats = parser.get_parsing_statistics()
        print(f"\n📈 Parser Statistics")
        print(f"   📊 Success rate: {stats['success_rate']}%")
        print(f"   📁 Files processed: {stats['total_files_parsed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration system"""
    print("\n🔧 Testing Configuration System")
    print("=" * 40)
    
    try:
        # Test settings access
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ App version: {settings.app_version}")
        print(f"✅ Default LLM: {settings.default_llm_provider}")
        print(f"✅ Default framework: {settings.default_test_framework}")
        
        # Test LLM config
        llm_config = settings.get_llm_config()
        print(f"✅ LLM config loaded: {llm_config['model']}")
        
        # Test agent roles
        print(f"✅ Agent roles: {[role.value for role in AgentRole]}")
        
        # Test agent config
        for role in AgentRole:
            agent_config = settings.get_agent_config(role)
            print(f"   📝 {role.value}: {agent_config['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def create_advantage_shopping_test_files():
    """Create test files for Advantage Online Shopping"""
    print("\n🛒 Creating Advantage Online Shopping Test Files")
    print("=" * 50)
    
    try:
        os.makedirs("./advantage_tests", exist_ok=True)
        
        # Create TXT format test
        txt_content = '''Test Name: Complete Shopping Workflow - Advantage Online Shopping
Target: https://www.advantageonlineshopping.com/#/
Priority: High
Tags: e-commerce, shopping, checkout, end-to-end

Description:
Complete end-to-end shopping workflow testing user login, product browsing, cart management, and checkout process on Advantage Online Shopping website.

Test Steps:
1. Navigate to https://www.advantageonlineshopping.com/#/
2. Click on the user account icon to access login
3. Enter username "helios" and password "Password123"
4. Click the Sign In button to authenticate
5. Verify successful login and user dashboard display
6. Navigate to LAPTOPS category from the main menu
7. Select HP EliteBook Folio 9470m product
8. Add the selected product to shopping cart
9. Verify product appears in cart with correct details
10. Proceed to checkout process
11. Fill in shipping and billing information
12. Select payment method and enter payment details
13. Review order summary and confirm purchase
14. Complete the order and verify order confirmation
15. Verify order appears in user account order history

Expected Results:
- User successfully logs in with provided credentials
- Product catalog displays correctly with all categories
- Selected product can be added to cart successfully
- Cart displays correct product information and pricing
- Checkout process completes without errors
- Payment processing works correctly
- Order confirmation is displayed with order number
- Order appears in user account history

Test Data:
username: helios
password: Password123
product_category: LAPTOPS
product_name: HP EliteBook Folio 9470m
payment_method: credit_card

Environment:
browser: chrome
headless: false
timeout: 30000
viewport_width: 1920
viewport_height: 1080
'''
        
        txt_file = "./advantage_tests/complete_shopping_workflow.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        # Create JSON format test
        json_content = {
            "testName": "Complete Shopping Workflow - Advantage Online Shopping",
            "description": "Complete end-to-end shopping workflow testing user login, product browsing, cart management, and checkout process",
            "priority": "High",
            "tags": ["e-commerce", "shopping", "checkout", "end-to-end"],
            "application": "https://www.advantageonlineshopping.com/#/",
            "testSteps": [
                {
                    "step": 1,
                    "action": "Navigate to the Advantage Online Shopping website",
                    "expectedResult": "Website loads successfully and homepage is displayed",
                    "timeout": 30000,
                    "screenshot": True
                },
                {
                    "step": 2,
                    "action": "Click on the user account icon",
                    "expectedResult": "Login form is displayed",
                    "selector": "[data-testid='user-icon']",
                    "timeout": 10000
                },
                {
                    "step": 3,
                    "action": "Enter login credentials",
                    "expectedResult": "Username and password are entered correctly",
                    "data": {
                        "username": "helios",
                        "password": "Password123"
                    },
                    "timeout": 5000
                },
                {
                    "step": 4,
                    "action": "Click Sign In button",
                    "expectedResult": "User is authenticated and logged in",
                    "timeout": 15000,
                    "screenshot": True
                },
                {
                    "step": 5,
                    "action": "Navigate to LAPTOPS category",
                    "expectedResult": "Laptop products are displayed",
                    "timeout": 10000
                },
                {
                    "step": 6,
                    "action": "Select HP EliteBook Folio 9470m product",
                    "expectedResult": "Product details page is displayed",
                    "data": {
                        "product_name": "HP EliteBook Folio 9470m"
                    },
                    "timeout": 10000
                },
                {
                    "step": 7,
                    "action": "Add product to shopping cart",
                    "expectedResult": "Product is added to cart successfully",
                    "timeout": 10000,
                    "screenshot": True
                },
                {
                    "step": 8,
                    "action": "Proceed to checkout",
                    "expectedResult": "Checkout process begins",
                    "timeout": 15000
                },
                {
                    "step": 9,
                    "action": "Complete checkout and place order",
                    "expectedResult": "Order is placed successfully with confirmation",
                    "timeout": 30000,
                    "screenshot": True
                }
            ],
            "expectedResults": [
                "User successfully logs in with provided credentials",
                "Product catalog displays correctly",
                "Selected product can be added to cart",
                "Checkout process completes without errors",
                "Order confirmation is displayed"
            ],
            "testData": {
                "credentials": {
                    "username": "helios",
                    "password": "Password123"
                },
                "testInputs": {
                    "product_category": "LAPTOPS",
                    "product_name": "HP EliteBook Folio 9470m",
                    "payment_method": "credit_card"
                }
            },
            "environment": {
                "browser": "chromium",
                "headless": False,
                "timeout": 30000,
                "viewport": {
                    "width": 1920,
                    "height": 1080
                },
                "baseUrl": "https://www.advantageonlineshopping.com/#/"
            },
            "configuration": {
                "framework": "playwright",
                "parallel": False,
                "retries": 3,
                "reportFormat": ["html", "json"]
            },
            "metadata": {
                "author": "AutoGen Test Framework",
                "created": datetime.now().isoformat(),
                "version": "1.0.0",
                "requirements": ["User authentication", "E-commerce workflow", "Payment processing"]
            }
        }
        
        json_file = "./advantage_tests/complete_shopping_workflow.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, indent=2)
        
        print(f"✅ Created TXT test file: {txt_file}")
        print(f"✅ Created JSON test file: {json_file}")
        
        return [txt_file, json_file]
        
    except Exception as e:
        print(f"❌ Failed to create test files: {e}")
        return []


async def test_advantage_shopping_files():
    """Test parsing of Advantage Shopping test files"""
    print("\n🧪 Testing Advantage Shopping Test Files")
    print("=" * 45)
    
    try:
        # Create test files
        test_files = create_advantage_shopping_test_files()
        
        if not test_files:
            print("❌ No test files to process")
            return False
        
        # Parse files
        parser = UnifiedTestFileParser()
        
        for file_path in test_files:
            print(f"\n📄 Processing: {os.path.basename(file_path)}")
            
            # Parse file
            parsed_file = parser.parse_file(file_path)
            
            print(f"   ✅ Parsed successfully")
            print(f"   📝 Test: {parsed_file.test_name}")
            print(f"   🎯 Target: {parsed_file.application_url}")
            print(f"   🔢 Steps: {len(parsed_file.test_steps)}")
            print(f"   🏷️  Tags: {', '.join(parsed_file.tags)}")
            print(f"   ⚡ Complexity: {parsed_file.metadata.get('complexity_analysis', {}).get('estimated_complexity', 'unknown')}")
            
            # Show first few steps
            print(f"   📋 First 3 steps:")
            for i, step in enumerate(parsed_file.test_steps[:3]):
                print(f"      {step.step_number}. {step.action}")
            
            # Validate
            if parsed_file.file_format == "txt":
                validation = parser.txt_parser.validate_parsed_file(parsed_file)
            else:
                validation = parser.json_parser.validate_parsed_file(parsed_file)
            
            print(f"   ✅ Validation: {'PASSED' if validation['is_valid'] else 'FAILED'}")
            
            if validation.get('errors'):
                print(f"   ❌ Errors: {validation['errors']}")
            if validation.get('warnings'):
                print(f"   ⚠️  Warnings: {len(validation['warnings'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advantage Shopping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 AutoGen Test Automation Framework - Component Testing")
    print("=" * 60)
    
    test_results = []
    
    # Test configuration
    config_result = test_configuration()
    test_results.append(("Configuration", config_result))
    
    # Test parser
    parser_result = await test_parser_functionality()
    test_results.append(("Parser", parser_result))
    
    # Test Advantage Shopping files
    advantage_result = await test_advantage_shopping_files()
    test_results.append(("Advantage Shopping Tests", advantage_result))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All component tests passed! Framework is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())

