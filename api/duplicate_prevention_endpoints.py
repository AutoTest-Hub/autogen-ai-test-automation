"""
Duplicate Prevention Endpoints for AI Test Automation Platform
Provides API endpoints for duplicate detection and smart updates
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

# Import dependencies
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user - local implementation to avoid circular import"""
    from database_postgres_full import CustomerUser
    
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
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = CustomerUser.get_by_email(user_id)
    if user is None:
        raise credentials_exception
    
    return user

from duplicate_prevention_service import DuplicatePreventionService

logger = logging.getLogger(__name__)

router = APIRouter()

class DuplicateCheckRequest(BaseModel):
    application_id: str
    test_name: str
    test_description: str
    requirements_data: Optional[Dict[str, Any]] = None

class UpdateStrategyRequest(BaseModel):
    existing_suite_id: str
    new_requirements: Optional[Dict[str, Any]] = None

@router.post("/api/v1/tests/check-duplicates")
async def check_for_duplicates(
    request: DuplicateCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """Check for potential duplicate test suites before creation"""
    try:
        result = DuplicatePreventionService.check_for_duplicates(
            customer_id=current_user['customer_id'],
            application_id=request.application_id,
            test_name=request.test_name,
            test_description=request.test_description,
            requirements_data=request.requirements_data
        )
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Duplicate check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check for duplicates"
        )

@router.post("/api/v1/tests/update-strategy")
async def get_update_strategy(
    request: UpdateStrategyRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get recommended strategy for updating an existing test suite"""
    try:
        result = DuplicatePreventionService.suggest_update_strategy(
            existing_suite_id=request.existing_suite_id,
            new_requirements=request.new_requirements
        )
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Update strategy error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to determine update strategy"
        )

@router.get("/api/v1/tests/recent/{application_id}")
async def get_recent_test_suites(
    application_id: str,
    hours: int = 24,
    current_user: dict = Depends(get_current_user)
):
    """Get recently created test suites for an application"""
    try:
        from duplicate_prevention_service import DuplicatePreventionService
        
        recent_suites = DuplicatePreventionService._find_recent_suites(
            customer_id=current_user['customer_id'],
            application_id=application_id,
            hours=hours
        )
        
        return {
            "status": "success",
            "data": {
                "recent_suites": recent_suites,
                "count": len(recent_suites),
                "timeframe_hours": hours
            }
        }
        
    except Exception as e:
        logger.error(f"Recent suites error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent test suites"
        )

@router.put("/api/v1/tests/{suite_id}/update")
async def update_existing_test_suite(
    suite_id: str,
    request: DuplicateCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing test suite with new configuration"""
    try:
        from database_postgres_full import TestSuite
        
        # Verify the suite belongs to the current customer
        existing_suites = DuplicatePreventionService._get_existing_suites(
            current_user['customer_id'], request.application_id
        )
        
        target_suite = next((s for s in existing_suites if str(s['id']) == suite_id), None)
        if not target_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test suite not found or access denied"
            )
        
        # Check if suite can be updated
        if target_suite['status'] == 'running':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot update a test suite that is currently running"
            )
        
        # Update the test suite
        update_result = TestSuite.update(
            suite_id=suite_id,
            name=request.test_name,
            description=request.test_description,
            updated_by=current_user['id']
        )
        
        if not update_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update test suite"
            )
        
        return {
            "status": "success",
            "message": "Test suite updated successfully",
            "data": {
                "suite_id": suite_id,
                "updated_name": request.test_name,
                "updated_description": request.test_description
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update test suite error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test suite"
        )
