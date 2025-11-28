from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging
import jwt
from database_postgres_full import TestSuite, TestCase, db, CustomerUser

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    try:
        # Get user from database
        user_data = CustomerUser.get_by_id(user_id)
        if user_data is None:
            raise credentials_exception
        
        return user_data
    except Exception as e:
        logger.error(f"Database error during authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

router = APIRouter()

class TestStepModel(BaseModel):
    action: str
    target: str
    description: str
    value: Optional[str] = None

class TestCaseUpdateModel(BaseModel):
    name: str
    description: str
    status: Optional[str] = 'draft'
    steps: List[TestStepModel] = []

class TestSuiteUpdateModel(BaseModel):
    suite: Dict[str, Any]
    testCases: List[Dict[str, Any]]

@router.get("/api/v1/test-suites/{suite_id}/test-cases")
async def get_test_cases(
    suite_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get all test cases for a test suite"""
    try:
        # Verify the suite belongs to the user's customer
        suite_query = """
        SELECT id FROM test_suites 
        WHERE id = %s AND customer_id = %s
        """
        suite_result = db.execute_query(suite_query, (suite_id, current_user['customer_id']))
        
        if not suite_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test suite not found"
            )
        
        # Get test cases with steps
        query = """
        SELECT 
            id, name, description, test_type, priority, status,
            test_steps, test_data, expected_result,
            created_at, updated_at
        FROM test_cases 
        WHERE test_suite_id = %s AND customer_id = %s
        ORDER BY created_at ASC
        """
        
        test_cases = db.execute_query(query, (suite_id, current_user['customer_id']))
        
        # Format the response
        formatted_cases = []
        for case in test_cases:
            formatted_case = {
                'id': str(case['id']),
                'name': case['name'],
                'description': case['description'],
                'status': case['status'],
                'test_type': case['test_type'],
                'priority': case['priority'],
                'expected_result': case['expected_result'],
                'steps': case['test_steps'] or [
                    {'action': 'navigate', 'target': '', 'description': 'Navigate to application'},
                    {'action': 'click', 'target': '', 'description': 'Click element'},
                    {'action': 'verify', 'target': '', 'description': 'Verify result'}
                ],
                'created_at': case['created_at'].isoformat() if case['created_at'] else None,
                'updated_at': case['updated_at'].isoformat() if case['updated_at'] else None
            }
            formatted_cases.append(formatted_case)
        
        return {
            "status": "success",
            "data": formatted_cases
        }
        
    except Exception as e:
        logger.error(f"Failed to get test cases for suite {suite_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test cases"
        )

@router.put("/api/v1/test-suites/{suite_id}")
async def update_test_suite(
    suite_id: UUID,
    update_data: TestSuiteUpdateModel,
    current_user: dict = Depends(get_current_user)
):
    """Update a test suite and its test cases"""
    try:
        # Verify the suite belongs to the user's customer
        suite_query = """
        SELECT id FROM test_suites 
        WHERE id = %s AND customer_id = %s
        """
        suite_result = db.execute_query(suite_query, (suite_id, current_user['customer_id']))
        
        if not suite_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test suite not found"
            )
        
        # Update suite information
        suite_info = update_data.suite
        suite_update_query = """
        UPDATE test_suites 
        SET name = %s, description = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND customer_id = %s
        """
        db.execute_command(
            suite_update_query, 
            (suite_info['name'], suite_info['description'], suite_id, current_user['customer_id'])
        )
        
        # Update test cases
        for test_case in update_data.testCases:
            case_id = test_case.get('id')
            
            if case_id and not case_id.startswith('new-'):
                # Update existing test case
                update_query = """
                UPDATE test_cases 
                SET name = %s, description = %s, status = %s, 
                    test_steps = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND customer_id = %s
                """
                db.execute_command(
                    update_query,
                    (
                        test_case['name'],
                        test_case['description'], 
                        test_case.get('status', 'draft'),
                        test_case.get('steps', []),
                        case_id,
                        current_user['customer_id']
                    )
                )
            else:
                # Create new test case
                insert_query = """
                INSERT INTO test_cases 
                (test_suite_id, customer_id, name, description, status, test_steps)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_command(
                    insert_query,
                    (
                        suite_id,
                        current_user['customer_id'],
                        test_case['name'],
                        test_case['description'],
                        test_case.get('status', 'draft'),
                        test_case.get('steps', [])
                    )
                )
        
        return {
            "status": "success",
            "message": "Test suite updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update test suite {suite_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test suite"
        )

@router.put("/api/v1/test-cases/{case_id}")
async def update_test_case(
    case_id: UUID,
    case_data: TestCaseUpdateModel,
    current_user: dict = Depends(get_current_user)
):
    """Update a specific test case"""
    try:
        # Verify the test case belongs to the user's customer
        verify_query = """
        SELECT id FROM test_cases 
        WHERE id = %s AND customer_id = %s
        """
        result = db.execute_query(verify_query, (case_id, current_user['customer_id']))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        
        # Update the test case
        update_query = """
        UPDATE test_cases 
        SET name = %s, description = %s, status = %s, 
            test_steps = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND customer_id = %s
        """
        
        steps_json = [step.dict() for step in case_data.steps]
        
        db.execute_command(
            update_query,
            (
                case_data.name,
                case_data.description,
                case_data.status,
                steps_json,
                case_id,
                current_user['customer_id']
            )
        )
        
        return {
            "status": "success",
            "message": "Test case updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update test case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test case"
        )

@router.delete("/api/v1/test-cases/{case_id}")
async def delete_test_case(
    case_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete a test case"""
    try:
        # Verify the test case belongs to the user's customer
        verify_query = """
        SELECT id FROM test_cases 
        WHERE id = %s AND customer_id = %s
        """
        result = db.execute_query(verify_query, (case_id, current_user['customer_id']))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        
        # Delete the test case
        delete_query = """
        DELETE FROM test_cases 
        WHERE id = %s AND customer_id = %s
        """
        db.execute_command(delete_query, (case_id, current_user['customer_id']))
        
        return {
            "status": "success",
            "message": "Test case deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete test case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test case"
        )

@router.post("/api/v1/test-suites/{suite_id}/test-cases")
async def create_test_case(
    suite_id: UUID,
    case_data: TestCaseUpdateModel,
    current_user: dict = Depends(get_current_user)
):
    """Create a new test case in a test suite"""
    try:
        # Verify the suite belongs to the user's customer
        suite_query = """
        SELECT id FROM test_suites 
        WHERE id = %s AND customer_id = %s
        """
        suite_result = db.execute_query(suite_query, (suite_id, current_user['customer_id']))
        
        if not suite_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test suite not found"
            )
        
        # Create the test case
        insert_query = """
        INSERT INTO test_cases 
        (test_suite_id, customer_id, name, description, status, test_steps)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        steps_json = [step.dict() for step in case_data.steps]
        
        result = db.execute_query(
            insert_query,
            (
                suite_id,
                current_user['customer_id'],
                case_data.name,
                case_data.description,
                case_data.status,
                steps_json
            )
        )
        
        new_case_id = result[0]['id'] if result else None
        
        return {
            "status": "success",
            "message": "Test case created successfully",
            "data": {"id": str(new_case_id)}
        }
        
    except Exception as e:
        logger.error(f"Failed to create test case in suite {suite_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test case"
        )
