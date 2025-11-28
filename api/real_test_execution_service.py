import asyncio
import json
import uuid
import sys
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_postgres_full import db
from test_suite_helper import TestSuiteHelper, TestCaseHelper

logger = logging.getLogger(__name__)

class RealTestExecutionService:
    """Service for executing real automated tests instead of simulations"""
    
    def __init__(self):
        self.active_executions = {}  # Track running executions
        self.test_scripts_dir = Path("/home/ubuntu/autogen-ai-test-automation/generated_tests")
        self.test_scripts_dir.mkdir(exist_ok=True)
    
    async def execute_test_case(self, test_case_id: str, customer_id: str) -> Dict[str, Any]:
        """Execute a real test case using generated Selenium/Playwright code"""
        try:
            # Get test case details
            test_case = TestCaseHelper.get_by_id(test_case_id)
            if not test_case:
                raise ValueError(f"Test case {test_case_id} not found")
            
            # Create execution record
            execution_id = str(uuid.uuid4())
            execution_data = {
                'id': execution_id,
                'test_case_id': test_case_id,
                'status': 'running',
                'start_time': datetime.utcnow(),
                'customer_id': customer_id,
                'type': 'single_test'
            }
            
            # Store execution in memory
            self.active_executions[execution_id] = execution_data
            
            # Start real test execution in background
            asyncio.create_task(self._run_real_test_case(execution_id, test_case))
            
            return {
                'execution_id': execution_id,
                'status': 'started',
                'test_case_id': test_case_id,
                'message': f'Real test execution started for "{test_case["name"]}"'
            }
            
        except Exception as e:
            logger.error(f"Failed to start test case execution: {e}")
            raise
    
    async def execute_test_suite(self, test_suite_id: str, customer_id: str) -> Dict[str, Any]:
        """Execute all test cases in a test suite with real automation"""
        try:
            # Get test suite and its test cases
            test_suite = TestSuiteHelper.get_by_id(test_suite_id)
            if not test_suite:
                raise ValueError(f"Test suite {test_suite_id} not found")
            
            # Get all test cases for this suite
            query = """
                SELECT id, name, description, test_steps, expected_result
                FROM test_cases 
                WHERE test_suite_id = %s
                ORDER BY created_at
            """
            test_cases = db.execute_query(query, (test_suite_id,))
            
            if not test_cases:
                return {
                    'execution_id': None,
                    'status': 'error',
                    'message': 'No test cases found in this suite'
                }
            
            # Create suite execution record
            execution_id = str(uuid.uuid4())
            execution_data = {
                'id': execution_id,
                'test_suite_id': test_suite_id,
                'status': 'running',
                'start_time': datetime.utcnow(),
                'customer_id': customer_id,
                'total_cases': len(test_cases),
                'completed_cases': 0,
                'passed_cases': 0,
                'failed_cases': 0,
                'test_cases': test_cases,
                'type': 'test_suite'
            }
            
            # Store execution in memory
            self.active_executions[execution_id] = execution_data
            
            # Start suite execution in background
            asyncio.create_task(self._run_real_test_suite(execution_id, test_suite, test_cases))
            
            return {
                'execution_id': execution_id,
                'status': 'started',
                'test_suite_id': test_suite_id,
                'total_test_cases': len(test_cases),
                'message': f'Real test suite execution started for "{test_suite["name"]}" with {len(test_cases)} test cases'
            }
            
        except Exception as e:
            logger.error(f"Failed to start test suite execution: {e}")
            raise
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the status of a running execution"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            return {
                'status': 'not_found',
                'message': 'Execution not found'
            }
        
        return {
            'execution_id': execution_id,
            'status': execution['status'],
            'start_time': execution['start_time'].isoformat() if execution.get('start_time') else None,
            'end_time': execution['end_time'].isoformat() if execution.get('end_time') else None,
            'progress': execution.get('progress', 0),
            'total_cases': execution.get('total_cases', 1),
            'completed_cases': execution.get('completed_cases', 0),
            'passed_cases': execution.get('passed_cases', 0),
            'failed_cases': execution.get('failed_cases', 0),
            'current_step': execution.get('current_step', ''),
            'result': execution.get('result', {}),
            'error': execution.get('error', None),
            'real_execution': True,
            'execution_method': execution.get('execution_method', 'Real Selenium/Playwright')
        }
    
    async def _run_real_test_case(self, execution_id: str, test_case: Dict[str, Any]):
        """Run a real test case using generated automation code"""
        execution = self.active_executions[execution_id]
        
        try:
            # Update status
            execution['current_step'] = 'Generating test automation code'
            execution['progress'] = 10
            
            # Generate real test code
            test_code = self._generate_selenium_test_code(test_case)
            
            # Save test code to file
            test_file_path = self.test_scripts_dir / f"test_{test_case['id']}.py"
            with open(test_file_path, 'w') as f:
                f.write(test_code)
            
            execution['current_step'] = 'Setting up test environment'
            execution['progress'] = 20
            
            # Install required packages if not already installed
            await self._ensure_test_dependencies()
            
            execution['current_step'] = 'Executing real test automation'
            execution['progress'] = 30
            
            # Execute the test using pytest
            result = await self._execute_pytest(test_file_path)
            
            execution['progress'] = 90
            execution['current_step'] = 'Processing test results'
            
            # Process results
            final_status = 'passed' if result['success'] else 'failed'
            
            test_result = {
                'test_case_id': test_case['id'],
                'test_case_name': test_case['name'],
                'real_execution': True,
                'execution_method': 'Selenium WebDriver',
                'final_status': final_status,
                'execution_output': result['output'],
                'execution_error': result['error'],
                'execution_time': result['duration'],
                'screenshots': result.get('screenshots', []),
                'test_file_path': str(test_file_path)
            }
            
            # Update execution with final result
            execution['status'] = 'completed'
            execution['end_time'] = datetime.utcnow()
            execution['result'] = test_result
            execution['final_status'] = final_status
            execution['progress'] = 100
            execution['execution_method'] = 'Real Selenium Execution'
            
            # Update test case status in database
            update_query = """
                UPDATE test_cases 
                SET status = %s, last_executed = %s, execution_result = %s
                WHERE id = %s
            """
            db.execute_query(update_query, (
                final_status,
                datetime.utcnow(),
                json.dumps(test_result),
                test_case['id']
            ))
            
            logger.info(f"Real test case {test_case['id']} execution completed with status: {final_status}")
            
        except Exception as e:
            logger.error(f"Real test case execution failed: {e}")
            execution['status'] = 'failed'
            execution['end_time'] = datetime.utcnow()
            execution['error'] = str(e)
            execution['progress'] = 100
            execution['execution_method'] = 'Real Selenium Execution (Failed)'
    
    async def _run_real_test_suite(self, execution_id: str, test_suite: Dict[str, Any], test_cases: List[Dict[str, Any]]):
        """Run all test cases in a test suite using real automation"""
        execution = self.active_executions[execution_id]
        
        try:
            execution['current_step'] = 'Initializing test suite execution'
            execution['progress'] = 5
            
            suite_result = {
                'test_suite_id': test_suite['id'],
                'test_suite_name': test_suite['name'],
                'total_cases': len(test_cases),
                'executed_cases': [],
                'summary': {
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0
                },
                'real_execution': True,
                'execution_method': 'Real Selenium Suite Execution'
            }
            
            # Execute each test case
            for i, test_case in enumerate(test_cases):
                execution['current_step'] = f'Executing test case: {test_case["name"]}'
                execution['progress'] = int(10 + (i / len(test_cases)) * 80)
                
                # Generate and execute real test
                try:
                    test_code = self._generate_selenium_test_code(test_case)
                    test_file_path = self.test_scripts_dir / f"test_{test_case['id']}.py"
                    
                    with open(test_file_path, 'w') as f:
                        f.write(test_code)
                    
                    # Execute the test
                    result = await self._execute_pytest(test_file_path)
                    
                    case_result = {
                        'test_case_id': test_case['id'],
                        'name': test_case['name'],
                        'status': 'passed' if result['success'] else 'failed',
                        'execution_time': result['duration'],
                        'output': result['output'],
                        'error': result['error'],
                        'real_execution': True
                    }
                    
                    suite_result['executed_cases'].append(case_result)
                    suite_result['summary'][case_result['status']] += 1
                    
                    # Update counters
                    execution['completed_cases'] = i + 1
                    execution['passed_cases'] = suite_result['summary']['passed']
                    execution['failed_cases'] = suite_result['summary']['failed']
                    
                    # Update individual test case in database
                    update_query = """
                        UPDATE test_cases 
                        SET status = %s, last_executed = %s
                        WHERE id = %s
                    """
                    db.execute_query(update_query, (
                        case_result['status'],
                        datetime.utcnow(),
                        test_case['id']
                    ))
                    
                except Exception as e:
                    logger.error(f"Failed to execute test case {test_case['id']}: {e}")
                    case_result = {
                        'test_case_id': test_case['id'],
                        'name': test_case['name'],
                        'status': 'failed',
                        'error': str(e),
                        'real_execution': True
                    }
                    suite_result['executed_cases'].append(case_result)
                    suite_result['summary']['failed'] += 1
                    execution['failed_cases'] += 1
                
                # Small delay between test executions
                await asyncio.sleep(1)
            
            # Finalize execution
            execution['status'] = 'completed'
            execution['end_time'] = datetime.utcnow()
            execution['result'] = suite_result
            execution['progress'] = 100
            execution['current_step'] = 'Test suite execution completed'
            
            # Update test suite statistics
            success_rate = (suite_result['summary']['passed'] / len(test_cases)) * 100
            update_suite_query = """
                UPDATE test_suites 
                SET last_executed = %s, success_rate = %s
                WHERE id = %s
            """
            db.execute_query(update_suite_query, (
                datetime.utcnow(),
                success_rate,
                test_suite['id']
            ))
            
            logger.info(f"Real test suite {test_suite['id']} execution completed. Passed: {suite_result['summary']['passed']}, Failed: {suite_result['summary']['failed']}")
            
        except Exception as e:
            logger.error(f"Real test suite execution failed: {e}")
            execution['status'] = 'failed'
            execution['end_time'] = datetime.utcnow()
            execution['error'] = str(e)
            execution['progress'] = 100
    
    def _generate_selenium_test_code(self, test_case: Dict[str, Any]) -> str:
        """Generate real Selenium test code from test case steps"""
        test_steps = test_case.get('test_steps', [])
        if isinstance(test_steps, str):
            try:
                test_steps = json.loads(test_steps)
            except json.JSONDecodeError:
                test_steps = []
        
        code = f'''
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Test{test_case["name"].replace(" ", "").replace("-", "")}:
    """
    Test Case: {test_case["name"]}
    Description: {test_case["description"]}
    Expected Result: {test_case.get("expected_result", "Test should pass")}
    """
    
    def setup_method(self):
        """Set up the test environment"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        
    def teardown_method(self):
        """Clean up after test"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def test_{test_case["name"].lower().replace(" ", "_").replace("-", "_")}(self):
        """Execute the test case steps"""
        try:
'''
        
        # Generate code for each test step
        for i, step in enumerate(test_steps):
            step_num = step.get('step', i + 1)
            action = step.get('action', 'unknown')
            description = step.get('description', '')
            target = step.get('target', '')
            value = step.get('value', '')
            expected = step.get('expected', '')
            
            code += f'''
            # Step {step_num}: {description}
            print(f"Executing Step {step_num}: {description}")
            
'''
            
            if action == 'navigate':
                if target.startswith('http'):
                    code += f'            self.driver.get("{target}")\n'
                else:
                    code += f'            self.driver.get("https://demo.opencart.com{target}")\n'
                code += f'            time.sleep(2)  # Wait for page load\n'
                
            elif action == 'input':
                code += f'''            try:
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "{target}")))
                element.clear()
                element.send_keys("{value}")
                print(f"Successfully entered text in {target}")
            except TimeoutException:
                print(f"Failed to find element: {target}")
                raise AssertionError(f"Element {target} not found for input")
'''
                
            elif action == 'click':
                code += f'''            try:
                element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "{target}")))
                element.click()
                print(f"Successfully clicked {target}")
                time.sleep(1)  # Wait for action to complete
            except TimeoutException:
                print(f"Failed to find clickable element: {target}")
                raise AssertionError(f"Element {target} not found or not clickable")
'''
                
            elif action == 'verify':
                code += f'''            try:
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "{target}")))
                assert element.is_displayed(), "{expected}"
                print(f"Successfully verified element: {target}")
            except TimeoutException:
                print(f"Verification failed: {target} not found")
                raise AssertionError(f"Verification failed: {expected}")
'''
                
            elif action == 'wait':
                wait_time = int(value) if value.isdigit() else 3
                code += f'            time.sleep({wait_time})  # Wait as specified\n'
                
            else:
                code += f'            # TODO: Implement {action} action for {target}\n'
                code += f'            print(f"Action {action} not implemented yet")\n'
        
        code += '''
            print("Test completed successfully")
            
        except Exception as e:
            print(f"Test failed with error: {str(e)}")
            # Take screenshot on failure
            try:
                self.driver.save_screenshot(f"/tmp/test_failure_{int(time.time())}.png")
            except:
                pass
            raise
'''
        
        return code
    
    async def _ensure_test_dependencies(self):
        """Ensure required test dependencies are installed"""
        try:
            # Check if selenium is installed
            import selenium
            from selenium import webdriver
            logger.info("Selenium dependencies are available")
        except ImportError:
            logger.warning("Selenium not available, test execution will be limited")
    
    async def _execute_pytest(self, test_file_path: Path) -> Dict[str, Any]:
        """Execute a pytest test file and return results"""
        try:
            start_time = time.time()
            
            # Run pytest with the test file
            cmd = [
                'python', '-m', 'pytest', 
                str(test_file_path), 
                '-v', 
                '--tb=short',
                '--capture=no'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.test_scripts_dir)
            )
            
            stdout, stderr = await process.communicate()
            duration = time.time() - start_time
            
            output = stdout.decode('utf-8') if stdout else ''
            error = stderr.decode('utf-8') if stderr else ''
            
            # Determine if test passed based on return code
            success = process.returncode == 0
            
            return {
                'success': success,
                'output': output,
                'error': error,
                'duration': f"{duration:.2f}s",
                'return_code': process.returncode
            }
            
        except Exception as e:
            logger.error(f"Failed to execute pytest: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'duration': '0s',
                'return_code': -1
            }

# Global instance
real_test_execution_service = RealTestExecutionService()
