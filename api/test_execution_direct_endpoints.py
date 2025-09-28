from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime
from enhanced_test_execution_service import enhanced_test_execution_service
from database_postgres_full import db

logger = logging.getLogger(__name__)

router = APIRouter()

# Temporary: Use a mock user for testing (will add proper auth later)
async def get_current_user():
    """Mock user for testing - will be replaced with proper auth"""
    return {
        "customer_id": "e6f663ec-c7cc-47b1-ab85-0a38d5df19af", 
        "id": "test-user",
        "username": "tester@demo.com"
    }

class TestCaseExecutionRequest(BaseModel):
    test_case_id: str

class TestSuiteExecutionRequest(BaseModel):
    test_suite_id: str
    environment: Optional[str] = "staging"
    browser: Optional[str] = "chrome"
    parallel: Optional[bool] = False

@router.post("/api/v1/test/execute-case-direct")
async def execute_test_case_direct(request: TestCaseExecutionRequest):
    """Execute a single test case - Direct endpoint with AI agent integration"""
    try:
        current_user = await get_current_user()
        result = await enhanced_test_execution_service.execute_test_case(
            test_case_id=request.test_case_id,
            customer_id=current_user['customer_id']
        )
        
        return {
            "status": "success",
            "execution_id": result['execution_id'],
            "message": result['message'],
            "ai_enhanced": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to execute test case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start test case execution"
        )

@router.post("/api/v1/test/executions-direct")
async def execute_test_suite_direct(request: TestSuiteExecutionRequest):
    """Execute all test cases in a test suite - Direct endpoint with AI agent integration"""
    try:
        current_user = await get_current_user()
        result = await enhanced_test_execution_service.execute_test_suite(
            test_suite_id=request.test_suite_id,
            customer_id=current_user['customer_id']
        )
        
        return {
            "status": "success",
            "data": {
                "execution_id": result['execution_id'],
                "test_suite_id": result['test_suite_id'],
                "total_test_cases": result['total_test_cases'],
                "message": result['message'],
                "ai_enhanced": True
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to execute test suite: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start test suite execution"
        )

@router.get("/api/v1/test/execution-status-direct/{execution_id}")
async def get_execution_status_direct(execution_id: str):
    """Get the status of a running test execution - Direct endpoint with enhanced status"""
    try:
        status_data = await enhanced_test_execution_service.get_execution_status(execution_id)
        
        # Format response for frontend compatibility
        if status_data.get('status') == 'not_found':
            return {
                "status": "error",
                "message": "Execution not found"
            }
        
        # Map internal status to frontend expected format
        frontend_status = status_data['status']
        if frontend_status == 'completed':
            # Check if it was successful or failed
            final_status = status_data.get('result', {}).get('final_status', 'completed')
            if final_status == 'failed':
                frontend_status = 'failed'
        
        response_data = {
            "status": "success" if frontend_status in ['completed', 'running'] else "error",
            "data": {
                "execution_id": execution_id,
                "status": frontend_status,
                "message": _get_status_message(status_data),
                "details": _get_status_details(status_data),
                "execution_time": _calculate_execution_time(status_data),
                "progress": status_data.get('progress', 0),
                "current_step": status_data.get('current_step', ''),
                "result": status_data.get('result', {}),
                "error": status_data.get('error'),
                "ai_enhanced": True,
                "agent_status": status_data.get('agent_status', 'AI agents not available'),
                "total_cases": status_data.get('total_cases', 1),
                "completed_cases": status_data.get('completed_cases', 0),
                "passed_cases": status_data.get('passed_cases', 0),
                "failed_cases": status_data.get('failed_cases', 0)
            }
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to get execution status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution status"
        )

@router.get("/api/v1/test-suites/{suite_id}/test-cases-direct")
async def get_test_cases_for_suite_direct(suite_id: str):
    """Get all test cases for a specific test suite - Direct endpoint"""
    try:
        current_user = await get_current_user()
        
        query = """
            SELECT tc.id, tc.name, tc.description, tc.status, tc.test_steps, 
                   tc.expected_result, tc.created_at, tc.updated_at
            FROM test_cases tc
            JOIN test_suites ts ON tc.test_suite_id = ts.id
            WHERE tc.test_suite_id = %s AND ts.customer_id = %s
            ORDER BY tc.created_at
        """
        
        test_cases = db.execute_query(query, (suite_id, current_user['customer_id']))
        
        # Convert to list of dictionaries
        if test_cases:
            columns = ['id', 'name', 'description', 'status', 'test_steps', 
                      'expected_result', 'created_at', 'updated_at']
            test_cases_list = []
            for case in test_cases:
                case_dict = dict(zip(columns, case))
                # Add default values for missing fields
                case_dict['last_executed'] = None
                case_dict['execution_result'] = None
                test_cases_list.append(case_dict)
        else:
            test_cases_list = []
        
        return {
            "status": "success",
            "data": test_cases_list,
            "total": len(test_cases_list),
            "ai_enhanced": True
        }
        
    except Exception as e:
        logger.error(f"Failed to get test cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test cases"
        )

@router.get("/api/v1/test/execution-history/{suite_id}")
async def get_execution_history_direct(suite_id: str, limit: int = 10):
    """Get execution history for a test suite"""
    try:
        current_user = await get_current_user()
        
        # This would typically query a test_executions table
        # For now, return mock data showing AI-enhanced execution history
        history = [
            {
                "execution_id": f"exec_{i}",
                "executed_at": datetime.now().isoformat(),
                "status": "completed" if i % 3 != 0 else "failed",
                "total_tests": 5,
                "passed_tests": 4 if i % 3 != 0 else 2,
                "failed_tests": 1 if i % 3 != 0 else 3,
                "execution_time": f"{30 + i * 5}s",
                "ai_enhanced": True,
                "agent_used": "ExecutionAgent + ReportingAgent"
            }
            for i in range(1, min(limit + 1, 11))
        ]
        
        return {
            "status": "success",
            "data": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get execution history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution history"
        )

def _get_status_message(status_data: Dict[str, Any]) -> str:
    """Generate a user-friendly status message"""
    status = status_data.get('status', 'unknown')
    
    if status == 'running':
        current_step = status_data.get('current_step', '')
        progress = status_data.get('progress', 0)
        agent_status = status_data.get('agent_status', '')
        
        if current_step:
            message = f"{current_step} ({progress}%)"
            if 'AI Agent' in agent_status:
                message += " [AI Enhanced]"
            return message
        return f"Execution in progress ({progress}%)"
    
    elif status == 'completed':
        result = status_data.get('result', {})
        if 'summary' in result:  # Test suite result
            summary = result['summary']
            total = summary.get('passed', 0) + summary.get('failed', 0)
            message = f"Completed: {summary.get('passed', 0)}/{total} tests passed"
            if result.get('agent_execution', False):
                message += " [AI Enhanced]"
            return message
        else:  # Single test case result
            final_status = result.get('final_status', 'completed')
            message = f"Test {final_status}"
            if result.get('agent_execution', False):
                message += " [AI Enhanced]"
            return message
    
    elif status == 'failed':
        error = status_data.get('error', 'Unknown error')
        return f"Execution failed: {error}"
    
    return status.capitalize()

def _get_status_details(status_data: Dict[str, Any]) -> str:
    """Generate detailed status information"""
    status = status_data.get('status', 'unknown')
    
    if status == 'completed':
        result = status_data.get('result', {})
        if 'summary' in result:  # Test suite result
            summary = result['summary']
            details = []
            if summary.get('passed', 0) > 0:
                details.append(f"{summary['passed']} passed")
            if summary.get('failed', 0) > 0:
                details.append(f"{summary['failed']} failed")
            if summary.get('skipped', 0) > 0:
                details.append(f"{summary['skipped']} skipped")
            
            base_details = ", ".join(details) if details else "All tests completed"
            
            # Add AI enhancement info
            if result.get('agent_execution', False):
                execution_method = result.get('execution_method', 'AI Enhanced')
                base_details += f" | Executed using {execution_method}"
            
            return base_details
        else:  # Single test case result
            steps = result.get('steps_executed', [])
            base_details = f"{len(steps)} steps executed"
            
            if result.get('agent_execution', False):
                execution_method = result.get('execution_method', 'AI Enhanced')
                base_details += f" | Executed using {execution_method}"
            
            return base_details
    
    elif status == 'running':
        completed = status_data.get('completed_cases', 0)
        total = status_data.get('total_cases', 1)
        agent_status = status_data.get('agent_status', '')
        
        if total > 1:
            base_details = f"Executing test {completed + 1} of {total}"
        else:
            base_details = "Test execution in progress"
        
        if agent_status and 'AI' in agent_status:
            base_details += f" | {agent_status}"
        
        return base_details
    
    return ""

def _calculate_execution_time(status_data: Dict[str, Any]) -> Optional[str]:
    """Calculate execution time if available"""
    start_time = status_data.get('start_time')
    end_time = status_data.get('end_time')
    
    if start_time and end_time:
        try:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            duration = end_time - start_time
            total_seconds = int(duration.total_seconds())
            
            if total_seconds < 60:
                return f"{total_seconds}s"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                return f"{minutes}m {seconds}s"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        except Exception as e:
            logger.error(f"Failed to calculate execution time: {e}")
    
    return None
