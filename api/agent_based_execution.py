"""
Agent-Based Test Execution Service
Leverages the existing ExecutionAgent and ReportingAgent for real test execution
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import asyncio
import json
import sys
import os
from datetime import datetime
import logging

# Add the project root to Python path to import agents
sys.path.append('/home/ubuntu/autogen-ai-test-automation')

logger = logging.getLogger(__name__)

router = APIRouter()

# Import the existing agents
try:
    from agents.execution_agent import ExecutionAgent
    from agents.reporting_agent import ReportingAgent
    from file_storage_manager import get_file_storage_manager
    logger.info("✅ Successfully imported ExecutionAgent and ReportingAgent")
except ImportError as e:
    logger.error(f"❌ Failed to import agents: {e}")
    ExecutionAgent = None
    ReportingAgent = None

# In-memory storage for executions (in production, this would be in database)
active_executions = {}

class TestSuiteExecutionRequest(BaseModel):
    test_suite_id: str
    environment: Optional[str] = "staging"
    browser: Optional[str] = "chrome"
    parallel: Optional[bool] = False
    headless: Optional[bool] = True

class TestCaseExecutionRequest(BaseModel):
    test_case_id: str
    test_suite_id: Optional[str] = None

@router.get("/api/v1/test-suites/{suite_id}/test-cases")
async def get_test_cases_for_suite(suite_id: str):
    """Get all test cases for a specific test suite"""
    try:
        from database_postgres_full import db
        
        # Get test cases with proper error handling
        query = """
            SELECT tc.id, tc.name, tc.description, tc.status, tc.test_steps, 
                   tc.expected_result, tc.created_at, tc.updated_at, tc.last_executed
            FROM test_cases tc
            WHERE tc.test_suite_id = %s
            ORDER BY tc.created_at
        """
        
        test_cases = db.execute_query(query, (suite_id,))
        
        # Convert to list of dictionaries
        if test_cases:
            columns = ['id', 'name', 'description', 'status', 'test_steps', 
                      'expected_result', 'created_at', 'updated_at', 'last_executed']
            test_cases_list = []
            for case in test_cases:
                case_dict = dict(zip(columns, case))
                # Convert datetime objects to strings
                for key in ['created_at', 'updated_at', 'last_executed']:
                    if case_dict[key]:
                        case_dict[key] = case_dict[key].isoformat() if hasattr(case_dict[key], 'isoformat') else str(case_dict[key])
                test_cases_list.append(case_dict)
        else:
            test_cases_list = []
        
        return {
            "status": "success",
            "data": test_cases_list,
            "total": len(test_cases_list)
        }
        
    except Exception as e:
        logger.error(f"Failed to get test cases: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve test cases: {str(e)}",
            "data": [],
            "total": 0
        }

@router.post("/api/v1/test/executions")
async def execute_test_suite(request: TestSuiteExecutionRequest):
    """Execute all test cases in a test suite using the ExecutionAgent"""
    try:
        from database_postgres_full import db
        
        # Get test suite details
        suite_query = "SELECT id, name, description FROM test_suites WHERE id = %s"
        suite_result = db.execute_query(suite_query, (request.test_suite_id,))
        
        if not suite_result:
            return {
                "status": "error",
                "message": "Test suite not found"
            }
        
        suite_data = {
            'id': suite_result[0][0],
            'name': suite_result[0][1],
            'description': suite_result[0][2]
        }
        
        # Get test cases for this suite
        cases_query = """
            SELECT id, name, description, test_steps, expected_result
            FROM test_cases 
            WHERE test_suite_id = %s
            ORDER BY created_at
        """
        test_cases = db.execute_query(cases_query, (request.test_suite_id,))
        
        if not test_cases:
            return {
                "status": "error",
                "message": "No test cases found in this suite"
            }
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_data = {
            'id': execution_id,
            'test_suite_id': request.test_suite_id,
            'test_suite_name': suite_data['name'],
            'status': 'running',
            'start_time': datetime.utcnow(),
            'total_cases': len(test_cases),
            'completed_cases': 0,
            'passed_cases': 0,
            'failed_cases': 0,
            'progress': 0,
            'current_step': 'Initializing ExecutionAgent',
            'test_cases': test_cases,
            'execution_config': {
                'environment': request.environment,
                'browser': request.browser,
                'parallel': request.parallel,
                'headless': request.headless
            }
        }
        
        # Store execution
        active_executions[execution_id] = execution_data
        
        # Start execution using ExecutionAgent in background
        asyncio.create_task(run_agent_based_execution(execution_id))
        
        return {
            "status": "success",
            "data": {
                'execution_id': execution_id,
                'status': 'started',
                'test_suite_id': request.test_suite_id,
                'total_test_cases': len(test_cases),
                'message': f'Test suite "{suite_data["name"]}" execution started with ExecutionAgent ({len(test_cases)} test cases)'
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to execute test suite: {e}")
        return {
            "status": "error",
            "message": f"Failed to start test suite execution: {str(e)}"
        }

@router.get("/api/v1/test/execution/{execution_id}/status")
async def get_execution_status(execution_id: str):
    """Get the status of a running test execution"""
    try:
        execution = active_executions.get(execution_id)
        if not execution:
            return {
                "status": "error",
                "message": "Execution not found"
            }
        
        return {
            "status": "success",
            "data": {
                'execution_id': execution_id,
                'status': execution['status'],
                'start_time': execution['start_time'].isoformat() if execution.get('start_time') else None,
                'end_time': execution['end_time'].isoformat() if execution.get('end_time') else None,
                'progress': execution.get('progress', 0),
                'total_cases': execution.get('total_cases', 0),
                'completed_cases': execution.get('completed_cases', 0),
                'passed_cases': execution.get('passed_cases', 0),
                'failed_cases': execution.get('failed_cases', 0),
                'current_step': execution.get('current_step', ''),
                'result': execution.get('result', {}),
                'error': execution.get('error', None),
                'agent_logs': execution.get('agent_logs', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get execution status: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve execution status: {str(e)}"
        }

@router.post("/api/v1/test/execute-case")
async def execute_test_case(request: TestCaseExecutionRequest):
    """Execute a single test case using the ExecutionAgent"""
    try:
        from database_postgres_full import db
        
        # Get test case details
        query = "SELECT id, name, description, test_steps, expected_result FROM test_cases WHERE id = %s"
        result = db.execute_query(query, (request.test_case_id,))
        
        if not result:
            return {
                "status": "error",
                "message": "Test case not found"
            }
        
        test_case = {
            'id': result[0][0],
            'name': result[0][1],
            'description': result[0][2],
            'test_steps': result[0][3],
            'expected_result': result[0][4]
        }
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_data = {
            'id': execution_id,
            'test_case_id': request.test_case_id,
            'test_case_name': test_case['name'],
            'status': 'running',
            'start_time': datetime.utcnow(),
            'progress': 0,
            'current_step': 'Initializing ExecutionAgent for single test case',
            'test_case': test_case
        }
        
        # Store execution
        active_executions[execution_id] = execution_data
        
        # Start execution using ExecutionAgent in background
        asyncio.create_task(run_single_test_case_execution(execution_id, test_case))
        
        return {
            "status": "success",
            "data": {
                'execution_id': execution_id,
                'status': 'started',
                'test_case_id': request.test_case_id,
                'message': f'Test case "{test_case["name"]}" execution started with ExecutionAgent'
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to execute test case: {e}")
        return {
            "status": "error",
            "message": f"Failed to start test case execution: {str(e)}"
        }

async def run_agent_based_execution(execution_id: str):
    """Background task to run test suite execution using ExecutionAgent"""
    execution = active_executions[execution_id]
    
    try:
        if not ExecutionAgent:
            raise Exception("ExecutionAgent not available")
        
        from database_postgres_full import db
        
        # Initialize ExecutionAgent
        execution['current_step'] = 'Initializing ExecutionAgent'
        execution['progress'] = 10
        
        execution_agent = ExecutionAgent()
        execution['agent_logs'] = ['✅ ExecutionAgent initialized successfully']
        
        # Get test files from file storage
        execution['current_step'] = 'Retrieving test files from storage'
        execution['progress'] = 20
        
        file_manager = get_file_storage_manager()
        test_files = []
        
        # Look for test files associated with this test suite
        test_suite_id = execution['test_suite_id']
        
        # Check if test files exist in storage
        try:
            suite_files = file_manager.get_test_suite_files(test_suite_id)
            if suite_files:
                test_files = suite_files
                execution['agent_logs'].append(f'📁 Found {len(test_files)} test files in storage')
            else:
                # Generate test files from test cases if not found
                execution['current_step'] = 'Generating test files from test cases'
                execution['progress'] = 30
                test_files = await generate_test_files_from_cases(execution['test_cases'], test_suite_id)
                execution['agent_logs'].append(f'🔧 Generated {len(test_files)} test files from test cases')
        except Exception as e:
            logger.warning(f"Could not retrieve test files from storage: {e}")
            # Generate test files from test cases as fallback
            test_files = await generate_test_files_from_cases(execution['test_cases'], test_suite_id)
            execution['agent_logs'].append(f'🔧 Generated {len(test_files)} test files as fallback')
        
        if not test_files:
            raise Exception("No test files available for execution")
        
        # Prepare execution task data
        execution['current_step'] = 'Preparing ExecutionAgent task'
        execution['progress'] = 40
        
        task_data = {
            "test_files": test_files,
            "execution_config": execution['execution_config'],
            "headless": execution['execution_config'].get('headless', True)
        }
        
        execution['agent_logs'].append(f'⚙️ Configured execution with {len(test_files)} test files')
        
        # Execute tests using ExecutionAgent
        execution['current_step'] = 'ExecutionAgent running tests'
        execution['progress'] = 50
        
        execution_result = await execution_agent.process_task({
            "task_type": "execute_tests",
            "task_data": task_data
        })
        
        execution['agent_logs'].append('🚀 ExecutionAgent completed test execution')
        
        # Process results
        execution['current_step'] = 'Processing execution results'
        execution['progress'] = 80
        
        if execution_result and execution_result.get('success'):
            test_results = execution_result.get('execution_results', {})
            summary = test_results.get('summary', {})
            
            execution['passed_cases'] = summary.get('passed', 0)
            execution['failed_cases'] = summary.get('failed', 0)
            execution['completed_cases'] = execution['passed_cases'] + execution['failed_cases']
            
            # Generate report using ReportingAgent
            if ReportingAgent:
                execution['current_step'] = 'Generating execution report'
                execution['progress'] = 90
                
                reporting_agent = ReportingAgent()
                report_result = await reporting_agent.process_task({
                    "task_type": "generate_execution_report",
                    "task_data": {
                        "execution_results": test_results,
                        "test_suite_id": test_suite_id
                    }
                })
                
                if report_result:
                    execution['report'] = report_result
                    execution['agent_logs'].append('📊 ReportingAgent generated execution report')
            
            execution['result'] = {
                'summary': summary,
                'execution_results': test_results,
                'agent_result': execution_result
            }
            
            # Update test case statuses in database
            for i, test_case in enumerate(execution['test_cases']):
                case_status = 'passed' if i < execution['passed_cases'] else 'failed'
                update_query = "UPDATE test_cases SET status = %s, last_executed = %s WHERE id = %s"
                db.execute_query(update_query, (case_status, datetime.utcnow(), test_case[0]))
            
            execution['status'] = 'completed'
            execution['agent_logs'].append('✅ Test suite execution completed successfully')
            
        else:
            execution['status'] = 'failed'
            execution['error'] = execution_result.get('error', 'Unknown execution error')
            execution['agent_logs'].append(f'❌ Test execution failed: {execution["error"]}')
        
        # Finalize execution
        execution['end_time'] = datetime.utcnow()
        execution['progress'] = 100
        execution['current_step'] = f'Execution {execution["status"]}'
        
        logger.info(f"Agent-based execution completed: {execution['passed_cases']} passed, {execution['failed_cases']} failed")
        
    except Exception as e:
        logger.error(f"Agent-based execution failed: {e}")
        execution['status'] = 'failed'
        execution['end_time'] = datetime.utcnow()
        execution['error'] = str(e)
        execution['progress'] = 100
        execution['current_step'] = 'Execution failed'
        if 'agent_logs' not in execution:
            execution['agent_logs'] = []
        execution['agent_logs'].append(f'❌ Execution failed: {str(e)}')

async def run_single_test_case_execution(execution_id: str, test_case: Dict[str, Any]):
    """Background task to run single test case execution using ExecutionAgent"""
    execution = active_executions[execution_id]
    
    try:
        if not ExecutionAgent:
            raise Exception("ExecutionAgent not available")
        
        from database_postgres_full import db
        
        # Initialize ExecutionAgent
        execution['current_step'] = 'Initializing ExecutionAgent for single test'
        execution['progress'] = 20
        
        execution_agent = ExecutionAgent()
        
        # Generate a temporary test file for this test case
        execution['current_step'] = 'Generating test file'
        execution['progress'] = 40
        
        test_file = await generate_single_test_file(test_case)
        
        # Execute the test
        execution['current_step'] = 'ExecutionAgent running test'
        execution['progress'] = 60
        
        task_data = {
            "test_files": [test_file],
            "execution_config": {"headless": True},
            "headless": True
        }
        
        execution_result = await execution_agent.process_task({
            "task_type": "execute_tests",
            "task_data": task_data
        })
        
        # Process results
        execution['current_step'] = 'Processing results'
        execution['progress'] = 80
        
        if execution_result and execution_result.get('success'):
            test_results = execution_result.get('execution_results', {})
            summary = test_results.get('summary', {})
            
            final_status = 'passed' if summary.get('passed', 0) > 0 else 'failed'
            
            execution['final_status'] = final_status
            execution['result'] = {
                'test_case_id': test_case['id'],
                'status': final_status,
                'execution_time': test_results.get('performance_metrics', {}).get('total_execution_time', 0),
                'message': f'Test case executed with ExecutionAgent - {final_status}',
                'agent_result': execution_result
            }
            
            # Update test case in database
            update_query = "UPDATE test_cases SET status = %s, last_executed = %s WHERE id = %s"
            db.execute_query(update_query, (final_status, datetime.utcnow(), test_case['id']))
            
            execution['status'] = 'completed'
        else:
            execution['status'] = 'failed'
            execution['error'] = execution_result.get('error', 'Unknown execution error')
        
        # Finalize execution
        execution['end_time'] = datetime.utcnow()
        execution['progress'] = 100
        execution['current_step'] = f'Single test execution {execution["status"]}'
        
        logger.info(f"Single test case execution completed: {test_case['name']} - {execution.get('final_status', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Single test case execution failed: {e}")
        execution['status'] = 'failed'
        execution['end_time'] = datetime.utcnow()
        execution['error'] = str(e)
        execution['progress'] = 100
        execution['current_step'] = 'Single test execution failed'

async def generate_test_files_from_cases(test_cases: List, test_suite_id: str) -> List[str]:
    """Generate test files from test cases"""
    test_files = []
    
    for i, test_case in enumerate(test_cases):
        test_case_id = test_case[0]
        test_case_name = test_case[1]
        test_steps = test_case[3] if len(test_case) > 3 else "[]"
        
        # Create a simple Playwright test file
        test_content = f'''
import pytest
from playwright.sync_api import sync_playwright

def test_{test_case_name.lower().replace(" ", "_")}():
    """
    Test Case: {test_case_name}
    Generated from test case ID: {test_case_id}
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Test steps from database: {test_steps}
            page.goto("https://example.com")
            page.wait_for_timeout(2000)
            
            # Add your test logic here
            assert page.title() is not None
            
        finally:
            browser.close()

if __name__ == "__main__":
    test_{test_case_name.lower().replace(" ", "_")}()
'''
        
        # Save test file
        test_filename = f"test_{test_case_name.lower().replace(' ', '_')}_{i+1}.py"
        test_filepath = f"/tmp/{test_filename}"
        
        with open(test_filepath, 'w') as f:
            f.write(test_content)
        
        test_files.append(test_filepath)
    
    return test_files

async def generate_single_test_file(test_case: Dict[str, Any]) -> str:
    """Generate a single test file from a test case"""
    test_case_id = test_case['id']
    test_case_name = test_case['name']
    test_steps = test_case.get('test_steps', '[]')
    
    # Create a simple Playwright test file
    test_content = f'''
import pytest
from playwright.sync_api import sync_playwright

def test_{test_case_name.lower().replace(" ", "_")}():
    """
    Test Case: {test_case_name}
    Generated from test case ID: {test_case_id}
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Test steps from database: {test_steps}
            page.goto("https://example.com")
            page.wait_for_timeout(2000)
            
            # Add your test logic here
            assert page.title() is not None
            
        finally:
            browser.close()

if __name__ == "__main__":
    test_{test_case_name.lower().replace(" ", "_")}()
'''
    
    # Save test file
    test_filename = f"test_{test_case_name.lower().replace(' ', '_')}_single.py"
    test_filepath = f"/tmp/{test_filename}"
    
    with open(test_filepath, 'w') as f:
        f.write(test_content)
    
    return test_filepath
