import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from database_postgres_full import TestCase, TestSuite, db

logger = logging.getLogger(__name__)

class TestExecutionService:
    """Service for executing test cases and test suites"""
    
    def __init__(self):
        self.active_executions = {}  # Track running executions
    
    async def execute_test_case(self, test_case_id: str, customer_id: str) -> Dict[str, Any]:
        """Execute a single test case"""
        try:
            # Get test case details
            test_case = TestCase.get_by_id(test_case_id)
            if not test_case:
                raise ValueError(f"Test case {test_case_id} not found")
            
            # Create execution record
            execution_id = str(uuid.uuid4())
            execution_data = {
                'id': execution_id,
                'test_case_id': test_case_id,
                'status': 'running',
                'start_time': datetime.utcnow(),
                'customer_id': customer_id
            }
            
            # Store execution in memory (in production, this would be in database)
            self.active_executions[execution_id] = execution_data
            
            # Start execution in background
            asyncio.create_task(self._run_test_case(execution_id, test_case))
            
            return {
                'execution_id': execution_id,
                'status': 'started',
                'test_case_id': test_case_id,
                'message': f'Test case "{test_case["name"]}" execution started'
            }
            
        except Exception as e:
            logger.error(f"Failed to start test case execution: {e}")
            raise
    
    async def execute_test_suite(self, test_suite_id: str, customer_id: str) -> Dict[str, Any]:
        """Execute all test cases in a test suite"""
        try:
            # Get test suite and its test cases
            test_suite = TestSuite.get_by_id(test_suite_id)
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
                'test_cases': test_cases
            }
            
            # Store execution in memory
            self.active_executions[execution_id] = execution_data
            
            # Start suite execution in background
            asyncio.create_task(self._run_test_suite(execution_id, test_suite, test_cases))
            
            return {
                'execution_id': execution_id,
                'status': 'started',
                'test_suite_id': test_suite_id,
                'total_test_cases': len(test_cases),
                'message': f'Test suite "{test_suite["name"]}" execution started with {len(test_cases)} test cases'
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
            'error': execution.get('error', None)
        }
    
    async def _run_test_case(self, execution_id: str, test_case: Dict[str, Any]):
        """Run a single test case (background task)"""
        execution = self.active_executions[execution_id]
        
        try:
            # Update status
            execution['current_step'] = 'Initializing test environment'
            execution['progress'] = 10
            
            # Simulate test execution steps
            steps = [
                ('Setting up browser environment', 20),
                ('Navigating to application URL', 30),
                ('Executing test steps', 60),
                ('Validating results', 80),
                ('Generating report', 90),
                ('Cleaning up', 100)
            ]
            
            test_result = {
                'test_case_id': test_case['id'],
                'test_case_name': test_case['name'],
                'steps_executed': [],
                'screenshots': [],
                'logs': []
            }
            
            for step_name, progress in steps:
                execution['current_step'] = step_name
                execution['progress'] = progress
                
                # Simulate step execution time
                await asyncio.sleep(2)
                
                # Simulate step result
                step_result = {
                    'step': step_name,
                    'status': 'passed',
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': f'Successfully completed {step_name.lower()}'
                }
                
                test_result['steps_executed'].append(step_result)
                test_result['logs'].append(f"[{datetime.utcnow().isoformat()}] {step_name} - PASSED")
            
            # Determine final result (simulate 80% pass rate)
            import random
            final_status = 'passed' if random.random() > 0.2 else 'failed'
            
            if final_status == 'failed':
                test_result['error'] = 'Simulated test failure for demonstration'
                test_result['logs'].append(f"[{datetime.utcnow().isoformat()}] Test failed: Element not found")
            
            # Update execution with final result
            execution['status'] = 'completed'
            execution['end_time'] = datetime.utcnow()
            execution['result'] = test_result
            execution['final_status'] = final_status
            execution['progress'] = 100
            
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
            
            logger.info(f"Test case {test_case['id']} execution completed with status: {final_status}")
            
        except Exception as e:
            logger.error(f"Test case execution failed: {e}")
            execution['status'] = 'failed'
            execution['end_time'] = datetime.utcnow()
            execution['error'] = str(e)
            execution['progress'] = 100
    
    async def _run_test_suite(self, execution_id: str, test_suite: Dict[str, Any], test_cases: List[Dict[str, Any]]):
        """Run all test cases in a test suite (background task)"""
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
                }
            }
            
            # Execute each test case
            for i, test_case in enumerate(test_cases):
                execution['current_step'] = f'Executing test case: {test_case["name"]}'
                execution['progress'] = int(10 + (i / len(test_cases)) * 80)
                
                # Simulate test case execution
                await asyncio.sleep(3)
                
                # Simulate result (80% pass rate)
                import random
                case_status = 'passed' if random.random() > 0.2 else 'failed'
                
                case_result = {
                    'test_case_id': test_case['id'],
                    'name': test_case['name'],
                    'status': case_status,
                    'execution_time': random.randint(1000, 5000),  # milliseconds
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                if case_status == 'failed':
                    case_result['error'] = f'Simulated failure in test case: {test_case["name"]}'
                
                suite_result['executed_cases'].append(case_result)
                suite_result['summary'][case_status] += 1
                
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
                    case_status,
                    datetime.utcnow(),
                    test_case['id']
                ))
            
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
            
            logger.info(f"Test suite {test_suite['id']} execution completed. Passed: {suite_result['summary']['passed']}, Failed: {suite_result['summary']['failed']}")
            
        except Exception as e:
            logger.error(f"Test suite execution failed: {e}")
            execution['status'] = 'failed'
            execution['end_time'] = datetime.utcnow()
            execution['error'] = str(e)
            execution['progress'] = 100

# Global instance
test_execution_service = TestExecutionService()
