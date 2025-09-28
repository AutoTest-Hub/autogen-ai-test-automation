from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import asyncio
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for executions (in production, this would be in database)
active_executions = {}

class TestSuiteExecutionRequest(BaseModel):
    test_suite_id: str
    environment: Optional[str] = "staging"
    browser: Optional[str] = "chrome"
    parallel: Optional[bool] = False

class TestCaseExecutionRequest(BaseModel):
    test_case_id: str
    test_suite_id: Optional[str] = None

@router.get("/api/v1/test-suites/{suite_id}/test-cases")
async def get_test_cases_for_suite(suite_id: str):
    """Get all test cases for a specific test suite"""
    try:
        from database_postgres_full import db
        
        # Simplified query without customer_id filter for testing
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
            test_cases_list = [dict(zip(columns, case)) for case in test_cases]
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
    """Execute all test cases in a test suite"""
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
            'current_step': 'Initializing test execution',
            'test_cases': test_cases
        }
        
        # Store execution
        active_executions[execution_id] = execution_data
        
        # Start execution in background
        asyncio.create_task(run_test_suite_execution(execution_id))
        
        return {
            "status": "success",
            "data": {
                'execution_id': execution_id,
                'status': 'started',
                'test_suite_id': request.test_suite_id,
                'total_test_cases': len(test_cases),
                'message': f'Test suite "{suite_data["name"]}" execution started with {len(test_cases)} test cases'
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
                'error': execution.get('error', None)
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
    """Execute a single test case"""
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
            'current_step': 'Initializing test case execution'
        }
        
        # Store execution
        active_executions[execution_id] = execution_data
        
        # Start execution in background
        asyncio.create_task(run_test_case_execution(execution_id, test_case))
        
        return {
            "status": "success",
            "data": {
                'execution_id': execution_id,
                'status': 'started',
                'test_case_id': request.test_case_id,
                'message': f'Test case "{test_case["name"]}" execution started'
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to execute test case: {e}")
        return {
            "status": "error",
            "message": f"Failed to start test case execution: {str(e)}"
        }

async def run_test_suite_execution(execution_id: str):
    """Background task to run test suite execution"""
    execution = active_executions[execution_id]
    
    try:
        from database_postgres_full import db
        
        test_cases = execution['test_cases']
        total_cases = len(test_cases)
        
        execution['current_step'] = 'Setting up test environment'
        execution['progress'] = 10
        await asyncio.sleep(2)
        
        # Execute each test case
        for i, test_case in enumerate(test_cases):
            execution['current_step'] = f'Executing test case: {test_case[1]}'  # test_case[1] is name
            execution['progress'] = int(20 + (i / total_cases) * 70)
            
            # Simulate test execution
            await asyncio.sleep(3)
            
            # Simulate result (80% pass rate)
            import random
            case_status = 'passed' if random.random() > 0.2 else 'failed'
            
            if case_status == 'passed':
                execution['passed_cases'] += 1
            else:
                execution['failed_cases'] += 1
            
            execution['completed_cases'] += 1
            
            # Update test case status in database
            update_query = "UPDATE test_cases SET status = %s, last_executed = %s WHERE id = %s"
            db.execute_query(update_query, (case_status, datetime.utcnow(), test_case[0]))
        
        # Finalize execution
        execution['status'] = 'completed'
        execution['end_time'] = datetime.utcnow()
        execution['progress'] = 100
        execution['current_step'] = 'Test suite execution completed'
        execution['result'] = {
            'summary': {
                'passed': execution['passed_cases'],
                'failed': execution['failed_cases'],
                'total': total_cases
            }
        }
        
        # Update test suite statistics
        success_rate = (execution['passed_cases'] / total_cases) * 100
        update_suite_query = "UPDATE test_suites SET last_executed = %s WHERE id = %s"
        db.execute_query(update_suite_query, (datetime.utcnow(), execution['test_suite_id']))
        
        logger.info(f"Test suite execution completed: {execution['passed_cases']} passed, {execution['failed_cases']} failed")
        
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        execution['status'] = 'failed'
        execution['end_time'] = datetime.utcnow()
        execution['error'] = str(e)
        execution['progress'] = 100

async def run_test_case_execution(execution_id: str, test_case: Dict[str, Any]):
    """Background task to run test case execution"""
    execution = active_executions[execution_id]
    
    try:
        from database_postgres_full import db
        
        # Simulate test execution steps
        steps = [
            ('Setting up browser environment', 20),
            ('Navigating to application URL', 40),
            ('Executing test steps', 70),
            ('Validating results', 90),
            ('Generating report', 100)
        ]
        
        for step_name, progress in steps:
            execution['current_step'] = step_name
            execution['progress'] = progress
            await asyncio.sleep(2)
        
        # Simulate result (80% pass rate)
        import random
        final_status = 'passed' if random.random() > 0.2 else 'failed'
        
        # Update execution
        execution['status'] = 'completed'
        execution['end_time'] = datetime.utcnow()
        execution['final_status'] = final_status
        execution['result'] = {
            'test_case_id': test_case['id'],
            'status': final_status,
            'execution_time': 10000,  # milliseconds
            'message': f'Test case executed successfully' if final_status == 'passed' else 'Test case failed'
        }
        
        # Update test case in database
        update_query = "UPDATE test_cases SET status = %s, last_executed = %s WHERE id = %s"
        db.execute_query(update_query, (final_status, datetime.utcnow(), test_case['id']))
        
        logger.info(f"Test case execution completed: {test_case['name']} - {final_status}")
        
    except Exception as e:
        logger.error(f"Test case execution failed: {e}")
        execution['status'] = 'failed'
        execution['end_time'] = datetime.utcnow()
        execution['error'] = str(e)
        execution['progress'] = 100
