from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID
import logging
from test_execution_service import test_execution_service

logger = logging.getLogger(__name__)

# Temporary: Use a mock user for testing (will add proper auth later)
async def get_current_user():
    """Mock user for testing - will be replaced with proper auth"""
    return {
        "customer_id": "e6f663ec-c7cc-47b1-ab85-0a38d5df19af", 
        "id": "test-user",
        "username": "tester@demo.com"
    }

router = APIRouter()

class TestCaseExecutionRequest(BaseModel):
    test_case_id: str
    test_suite_id: Optional[str] = None

class TestSuiteExecutionRequest(BaseModel):
    test_suite_id: str
    environment: Optional[str] = "staging"
    browser: Optional[str] = "chrome"
    parallel: Optional[bool] = False

@router.post("/api/v1/test/execute-case")
async def execute_test_case(
    request: TestCaseExecutionRequest
):
    """Execute a single test case"""
    try:
        current_user = await get_current_user()
        result = await test_execution_service.execute_test_case(
            test_case_id=request.test_case_id,
            customer_id=current_user['customer_id']
        )
        
        return {
            "status": "success",
            "data": result
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

@router.post("/api/v1/test/executions")
async def execute_test_suite(
    request: TestSuiteExecutionRequest
):
    """Execute all test cases in a test suite"""
    try:
        current_user = await get_current_user()
        result = await test_execution_service.execute_test_suite(
            test_suite_id=request.test_suite_id,
            customer_id=current_user['customer_id']
        )
        
        return {
            "status": "success",
            "data": result
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

@router.get("/api/v1/test/execution/{execution_id}/status")
async def get_execution_status(
    execution_id: str
):
    """Get the status of a running test execution"""
    try:
        status_data = await test_execution_service.get_execution_status(execution_id)
        
        return {
            "status": "success",
            "data": status_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get execution status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve execution status"
        )

@router.get("/api/v1/test-suites/{suite_id}/test-cases")
async def get_test_cases_for_suite(
    suite_id: str
):
    """Get all test cases for a specific test suite"""
    try:
        from database_postgres_full import db
        current_user = await get_current_user()
        
        query = """
            SELECT tc.id, tc.name, tc.description, tc.status, tc.test_steps, 
                   tc.expected_result, tc.created_at, tc.updated_at, tc.last_executed,
                   tc.execution_result
            FROM test_cases tc
            JOIN test_suites ts ON tc.test_suite_id = ts.id
            WHERE tc.test_suite_id = %s AND ts.customer_id = %s
            ORDER BY tc.created_at
        """
        
        test_cases = db.execute_query(query, (suite_id, current_user['customer_id']))
        
        # Convert to list of dictionaries
        if test_cases:
            columns = ['id', 'name', 'description', 'status', 'test_steps', 
                      'expected_result', 'created_at', 'updated_at', 'last_executed', 'execution_result']
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test cases"
        )
