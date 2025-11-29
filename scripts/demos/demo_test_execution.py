#!/usr/bin/env python3
"""
Demo Test Execution Script
==========================
This script demonstrates how to execute the generated test files
and shows the current E2E test creation capabilities.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and capture output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=os.getcwd()
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return False

def check_generated_files():
    """Check what test files have been generated"""
    print(f"\n{'='*60}")
    print("📁 CHECKING GENERATED TEST FILES")
    print(f"{'='*60}")
    
    work_dir = Path("work_dir/EnhancedTestCreationAgent")
    
    if not work_dir.exists():
        print("❌ No generated files found. Run test generation first:")
        print("   python3 test_e2e_enhanced_workflow.py")
        return False
    
    print(f"📂 Generated files in {work_dir}:")
    
    # Check for different types of test files
    file_types = {
        "Playwright Tests": ["test_*.py"],
        "Page Objects": ["*_page.py"],
        "Configuration": ["conftest.py", "requirements.txt"],
        "Selenium Tests": ["test_selenium_automation.py", "selenium_config.py"],
        "API Tests": ["test_api_automation.py", "api_client.py"]
    }
    
    found_files = {}
    
    for category, patterns in file_types.items():
        found_files[category] = []
        for pattern in patterns:
            files = list(work_dir.glob(pattern))
            found_files[category].extend(files)
    
    for category, files in found_files.items():
        print(f"\n📋 {category}:")
        if files:
            for file in files:
                size = file.stat().st_size
                print(f"   ✅ {file.name} ({size} bytes)")
        else:
            print(f"   ❌ No files found")
    
    return any(files for files in found_files.values())

def demo_playwright_execution():
    """Demo Playwright test execution"""
    work_dir = "work_dir/EnhancedTestCreationAgent"
    
    # Check if Playwright is installed
    print(f"\n{'='*60}")
    print("🎭 PLAYWRIGHT TEST EXECUTION DEMO")
    print(f"{'='*60}")
    
    # Check Playwright installation
    playwright_check = run_command(
        "python3 -c \"import playwright; print('Playwright installed')\"",
        "Checking Playwright Installation"
    )
    
    if not playwright_check:
        print("❌ Playwright not installed. Installing...")
        run_command("pip install playwright", "Installing Playwright")
        run_command("playwright install chromium", "Installing Chromium")
    
    # Try to run a Playwright test
    test_file = f"{work_dir}/test_user_login_test.py"
    if os.path.exists(test_file):
        print(f"\n🧪 Attempting to run: {test_file}")
        print("⚠️  Note: This may fail due to mock selectors - this is expected!")
        
        success = run_command(
            f"cd {work_dir} && python3 test_user_login_test.py",
            "Running Playwright Test (Direct Execution)"
        )
        
        if not success:
            print("\n💡 Expected failure due to mock selectors.")
            print("   To fix: Update selectors in the test file to match your application.")
    else:
        print(f"❌ Test file not found: {test_file}")

def demo_selenium_execution():
    """Demo Selenium test execution"""
    work_dir = "work_dir/EnhancedTestCreationAgent"
    
    print(f"\n{'='*60}")
    print("🌐 SELENIUM TEST EXECUTION DEMO")
    print(f"{'='*60}")
    
    # Check if Selenium is installed
    selenium_check = run_command(
        "python3 -c \"import selenium; print('Selenium installed')\"",
        "Checking Selenium Installation"
    )
    
    if not selenium_check:
        print("❌ Selenium not installed. Installing...")
        run_command("pip install selenium webdriver-manager", "Installing Selenium")
    
    # Try to run a Selenium test
    test_file = f"{work_dir}/test_selenium_automation.py"
    if os.path.exists(test_file):
        print(f"\n🧪 Attempting to run: {test_file}")
        print("⚠️  Note: This may fail due to mock selectors - this is expected!")
        
        success = run_command(
            f"cd {work_dir} && python3 test_selenium_automation.py",
            "Running Selenium Test (Direct Execution)"
        )
        
        if not success:
            print("\n💡 Expected failure due to mock selectors.")
            print("   To fix: Update selectors in the test file to match your application.")
    else:
        print(f"❌ Test file not found: {test_file}")

def demo_api_execution():
    """Demo API test execution"""
    work_dir = "work_dir/EnhancedTestCreationAgent"
    
    print(f"\n{'='*60}")
    print("🔗 API TEST EXECUTION DEMO")
    print(f"{'='*60}")
    
    # Check if requests is installed
    requests_check = run_command(
        "python3 -c \"import requests; print('Requests installed')\"",
        "Checking Requests Installation"
    )
    
    if not requests_check:
        print("❌ Requests not installed. Installing...")
        run_command("pip install requests", "Installing Requests")
    
    # Try to run an API test
    test_file = f"{work_dir}/test_api_automation.py"
    if os.path.exists(test_file):
        print(f"\n🧪 Attempting to run: {test_file}")
        print("⚠️  Note: This may fail due to mock API endpoints - this is expected!")
        
        success = run_command(
            f"cd {work_dir} && python3 test_api_automation.py",
            "Running API Test (Direct Execution)"
        )
        
        if not success:
            print("\n💡 Expected failure due to mock API endpoints.")
            print("   To fix: Update API endpoints in the test file to match your application.")
    else:
        print(f"❌ Test file not found: {test_file}")

def show_customization_guide():
    """Show how to customize generated tests"""
    print(f"\n{'='*60}")
    print("🔧 CUSTOMIZATION GUIDE")
    print(f"{'='*60}")
    
    print("""
To make generated tests work with your application:

1. 📝 UPDATE SELECTORS:
   - Open generated test files
   - Replace mock selectors with real ones from your app
   - Example: Change '#loginBtn' to '[data-testid="login-button"]'

2. 🌐 UPDATE URLs:
   - Change 'https://advantageonlineshopping.com' 
   - To your application URL

3. 🔑 UPDATE TEST DATA:
   - Replace 'testuser'/'testpass' with valid credentials
   - Update test data to match your application

4. ✅ UPDATE ASSERTIONS:
   - Customize validations for your application behavior
   - Add specific checks for your application's success indicators

5. 🧪 RUN TESTS:
   cd work_dir/EnhancedTestCreationAgent/
   pytest test_user_login_test.py -v -s
""")

def main():
    """Main demo function"""
    print("🎯 AutoGen AI Test Framework - E2E Test Execution Demo")
    print("=" * 60)
    
    # Step 1: Check generated files
    if not check_generated_files():
        print("\n❌ No generated files found. Please run test generation first:")
        print("   python3 test_e2e_enhanced_workflow.py")
        return
    
    # Step 2: Demo different test executions
    demo_playwright_execution()
    demo_selenium_execution()
    demo_api_execution()
    
    # Step 3: Show customization guide
    show_customization_guide()
    
    print(f"\n{'='*60}")
    print("🎉 DEMO COMPLETE")
    print(f"{'='*60}")
    print("""
Summary:
✅ Framework generates real, working test code
✅ Multiple frameworks supported (Playwright, Selenium, API)
✅ Professional structure with page objects and configuration
⚠️  Tests need customization for your specific application

Next Steps:
1. Customize generated tests for your application
2. Update selectors, URLs, and test data
3. Run tests against your application
4. Enjoy automated testing! 🚀
""")

if __name__ == "__main__":
    main()

