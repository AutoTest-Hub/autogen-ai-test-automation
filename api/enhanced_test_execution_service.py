import asyncio
import json
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_postgres_full import db
from test_suite_helper import TestSuiteHelper, TestCaseHelper

# Global flag for agent availability
AGENTS_AVAILABLE = False

# Import agents
try:
    from agents.execution_agent import ExecutionAgent
    from agents.reporting_agent import ReportingAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import agents: {e}")
    AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedTestExecutionService:
    """Enhanced service for executing test cases and test suites with AI agent integration"""
    
    def __init__(self):
        self.active_executions = {}  # Track running executions
        self.execution_agent = None
        self.reporting_agent = None
        
        # Initialize agents if available
        global AGENTS_AVAILABLE
        if AGENTS_AVAILABLE:
            try:
                self.execution_agent = ExecutionAgent()
                self.reporting_agent = ReportingAgent()
                logger.info("AI agents initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize AI agents: {e}")
                AGENTS_AVAILABLE = False
    
    async def execute_test_case(self, test_case_id: str, customer_id: str) -> Dict[str, Any]:
        """Execute a single test case with AI agent integration"""
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
            
            # Start execution in background
            asyncio.create_task(self._run_test_case_with_agent(execution_id, test_case))
            
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
        """Execute all test cases in a test suite with AI agent integration"""
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
            asyncio.create_task(self._run_test_suite_with_agent(execution_id, test_suite, test_cases))
            
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
            'error': execution.get('error', None),
            'agent_status': execution.get('agent_status', 'Not using AI agents')
        }
    
    async def _run_test_case_with_agent(self, execution_id: str, test_case: Dict[str, Any]):
        """Run a single test case using AI agents if available"""
        execution = self.active_executions[execution_id]
        
        try:
            # Update status
            execution['current_step'] = 'Initializing test execution'
            execution['progress'] = 10
            
            if AGENTS_AVAILABLE and self.execution_agent:
                # Use AI ExecutionAgent for intelligent test execution
                execution['agent_status'] = 'Using AI ExecutionAgent'
                execution['current_step'] = 'AI Agent analyzing test case'
                execution['progress'] = 20
                
                # Prepare task data for the agent
                task_data = {
                    "task_type": "execute_tests",
                    "test_case": test_case,
                    "execution_config": {
                        "headless": True,
                        "timeout": 30,
                        "retry_count": 1
                    }
                }
                
                # Execute using AI agent
                execution['current_step'] = 'AI Agent executing test'
                execution['progress'] = 40
                
                agent_result = await self.execution_agent.process_task(task_data)
                
                # Process agent results
                execution['progress'] = 80
                execution['current_step'] = 'Processing AI agent results'
                
                # Generate report using ReportingAgent if available
                if self.reporting_agent:
                    execution['current_step'] = 'AI Agent generating report'
                    execution['progress'] = 90
                    
                    report_task = {
                        "type": "execution_report",
                        "execution_data": agent_result,
                        "test_case": test_case
                    }
                    
                    report_result = await self.reporting_agent.process_task(report_task)
                    agent_result['report'] = report_result
                
                # Determine final status based on agent results
                final_status = 'passed' if agent_result.get('success', False) else 'failed'
                
                test_result = {
                    'test_case_id': test_case['id'],
                    'test_case_name': test_case['name'],
                    'agent_execution': True,
                    'agent_result': agent_result,
                    'execution_method': 'AI ExecutionAgent',
                    'final_status': final_status
                }
                
            else:
                # Fallback to simulated execution
                execution['agent_status'] = 'AI agents not available - using simulation'
                test_result = await self._simulate_test_execution(test_case, execution)
                final_status = test_result.get('final_status', 'passed')
            
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
    
    async def _run_test_suite_with_agent(self, execution_id: str, test_suite: Dict[str, Any], test_cases: List[Dict[str, Any]]):
        """Run all test cases in a test suite using AI agents if available"""
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
                'agent_execution': AGENTS_AVAILABLE and self.execution_agent is not None
            }
            
            if AGENTS_AVAILABLE and self.execution_agent:
                # Use AI ExecutionAgent for intelligent suite execution
                execution['agent_status'] = 'Using AI ExecutionAgent for suite'
                execution['current_step'] = 'AI Agent analyzing test suite'
                execution['progress'] = 10
                
                # Prepare task data for the agent
                task_data = {
                    "task_type": "execute_suite",
                    "test_suite": test_suite,
                    "test_cases": test_cases,
                    "execution_config": {
                        "headless": True,
                        "parallel": False,
                        "timeout": 60
                    }
                }
                
                # Execute using AI agent
                execution['current_step'] = 'AI Agent executing test suite'
                execution['progress'] = 30
                
                agent_result = await self.execution_agent.process_task(task_data)
                
                # Process agent results
                execution['progress'] = 70
                execution['current_step'] = 'Processing AI agent results'
                
                # Update suite result with agent data
                if agent_result.get('success', False):
                    suite_result['agent_result'] = agent_result
                    suite_result['execution_method'] = 'AI ExecutionAgent'
                    
                    # Extract results from agent execution
                    agent_summary = agent_result.get('summary', {})
                    suite_result['summary']['passed'] = agent_summary.get('tests_passed', 0)
                    suite_result['summary']['failed'] = agent_summary.get('tests_failed', 0)
                    
                    # Update execution counters
                    execution['passed_cases'] = suite_result['summary']['passed']
                    execution['failed_cases'] = suite_result['summary']['failed']
                    execution['completed_cases'] = len(test_cases)
                
                # Generate comprehensive report using ReportingAgent
                if self.reporting_agent:
                    execution['current_step'] = 'AI Agent generating comprehensive report'
                    execution['progress'] = 85
                    
                    report_task = {
                        "type": "execution_report",
                        "execution_data": agent_result,
                        "test_suite": test_suite,
                        "test_cases": test_cases
                    }
                    
                    report_result = await self.reporting_agent.process_task(report_task)
                    suite_result['comprehensive_report'] = report_result
                
            else:
                # Fallback to simulated execution for each test case
                execution['agent_status'] = 'AI agents not available - using simulation'
                
                for i, test_case in enumerate(test_cases):
                    execution['current_step'] = f'Simulating test case: {test_case["name"]}'
                    execution['progress'] = int(10 + (i / len(test_cases)) * 80)
                    
                    # Simulate test case execution
                    await asyncio.sleep(2)
                    
                    case_result = await self._simulate_test_case_execution(test_case)
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
    
    async def _simulate_test_execution(self, test_case: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate test execution when AI agents are not available"""
        # Simulate test execution steps
        steps = [
            ('Setting up test environment', 20),
            ('Navigating to application', 30),
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
            'logs': [],
            'agent_execution': False,
            'execution_method': 'Simulation'
        }
        
        for step_name, progress in steps:
            execution['current_step'] = step_name
            execution['progress'] = progress
            
            # Simulate step execution time
            await asyncio.sleep(1)
            
            # Simulate step result
            step_result = {
                'step': step_name,
                'status': 'passed',
                'timestamp': datetime.utcnow().isoformat(),
                'details': f'Successfully completed {step_name.lower()}'
            }
            
            test_result['steps_executed'].append(step_result)
            test_result['logs'].append(f"[{datetime.utcnow().isoformat()}] {step_name} - PASSED")
        
        # Determine final result (simulate 85% pass rate)
        import random
        final_status = 'passed' if random.random() > 0.15 else 'failed'
        
        if final_status == 'failed':
            test_result['error'] = 'Simulated test failure for demonstration'
            test_result['logs'].append(f"[{datetime.utcnow().isoformat()}] Test failed: Simulated failure")
        
        test_result['final_status'] = final_status
        return test_result
    
    async def _simulate_test_case_execution(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate individual test case execution"""
        import random
        
        # Simulate execution time
        await asyncio.sleep(random.uniform(1, 3))
        
        # Simulate result (85% pass rate)
        case_status = 'passed' if random.random() > 0.15 else 'failed'
        
        case_result = {
            'test_case_id': test_case['id'],
            'name': test_case['name'],
            'status': case_status,
            'execution_time': random.randint(1000, 5000),  # milliseconds
            'timestamp': datetime.utcnow().isoformat(),
            'agent_execution': False,
            'execution_method': 'Simulation'
        }
        
        if case_status == 'failed':
            case_result['error'] = f'Simulated failure in test case: {test_case["name"]}'
        
        return case_result

# Global instance
enhanced_test_execution_service = EnhancedTestExecutionService()
