"""
Agent Job Status Endpoints for AI Test Automation Platform
Provides real-time status tracking for test creation jobs
"""

from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from typing import Dict, Any
import logging

# Import dependencies
# Import dependencies - avoid circular import
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

from database_postgres_full import AgentJob, TestSuite

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/v1/agent-jobs/{job_id}/status")
async def get_agent_job_status(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get agent job status with real-time progress information"""
    try:
        job_data = AgentJob.get_by_id(job_id)
        
        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent job not found"
            )
        
        job = job_data['job']
        activities = job_data['activities']
        
        # Verify job belongs to current customer
        if str(job['customer_id']) != str(current_user['customer_id']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Map activities to phases for frontend
        phases = []
        phase_names = ["Discovery Agent", "Generation Agent", "Code Agent", "Validation Agent"]
        
        for phase_name in phase_names:
            phase_activities = [a for a in activities if a['agent_name'] == phase_name]
            if phase_activities:
                latest_activity = max(phase_activities, key=lambda x: x['created_at'])
                phases.append({
                    "name": phase_name,
                    "status": latest_activity['status'],
                    "progress": latest_activity['progress_percentage'],
                    "message": latest_activity['message']
                })
            else:
                phases.append({
                    "name": phase_name,
                    "status": "pending",
                    "progress": 0,
                    "message": f"Waiting to start {phase_name.lower()}"
                })
        
        return {
            "status": "success",
            "data": {
                "status": job['status'],
                "progress_percentage": job.get('current_progress', job['progress_percentage']),
                "current_agent": job['current_agent'],
                "phases": phases,
                "created_at": job['created_at'].isoformat() if job['created_at'] else None,
                "started_at": job['started_at'].isoformat() if job['started_at'] else None,
                "completed_at": job['completed_at'].isoformat() if job['completed_at'] else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get agent job status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent job status"
        )

@router.get("/api/v1/agent-jobs/{job_id}/tests")
async def get_agent_job_tests(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get tests created by the agent job"""
    try:
        job_data = AgentJob.get_by_id(job_id)
        
        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent job not found"
            )
        
        job = job_data['job']
        
        # Verify job belongs to current customer
        if str(job['customer_id']) != str(current_user['customer_id']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get test suite and its test cases
        test_suite_id = job.get('test_suite_id')
        if not test_suite_id:
            return {
                "status": "success",
                "data": []
            }
        
        # For now, return mock test data since we don't have test cases table
        # In a real implementation, this would query the test_cases table
        mock_tests = [
            {
                "name": "User Login Flow Test",
                "description": "Validates user authentication and login process",
                "type": "Functional",
                "file_path": f"/tests/test_suite_{test_suite_id}/login_test.py",
                "confidence_score": 95
            },
            {
                "name": "Navigation Menu Test",
                "description": "Tests main navigation functionality and accessibility",
                "type": "UI",
                "file_path": f"/tests/test_suite_{test_suite_id}/navigation_test.py",
                "confidence_score": 88
            },
            {
                "name": "Form Validation Test",
                "description": "Validates form input handling and error messages",
                "type": "Functional",
                "file_path": f"/tests/test_suite_{test_suite_id}/form_validation_test.py",
                "confidence_score": 92
            }
        ]
        
        return {
            "status": "success",
            "data": mock_tests
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get agent job tests error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent job tests"
        )
