"""
Requirements Validation Endpoints for AI Test Automation Platform
Handles requirements.json file validation and processing
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import Dict, Any, List
import json
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

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/api/v1/requirements/validate")
async def validate_requirements(
    requirements_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Validate requirements.json structure and content"""
    try:
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        
        # Check required fields
        required_fields = ["testSuiteName", "description"]
        for field in required_fields:
            if field not in requirements_data:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["valid"] = False
        
        # Validate test categories structure
        test_categories = requirements_data.get("testCategories", [])
        if not test_categories:
            validation_result["warnings"].append("No test categories found")
        else:
            total_tests = 0
            categories_count = len(test_categories)
            
            for i, category in enumerate(test_categories):
                if "category" not in category:
                    validation_result["errors"].append(f"Category {i+1} missing 'category' field")
                    validation_result["valid"] = False
                
                tests = category.get("tests", [])
                total_tests += len(tests)
                
                for j, test in enumerate(tests):
                    if "name" not in test:
                        validation_result["errors"].append(f"Test {j+1} in category '{category.get('category', 'Unknown')}' missing 'name' field")
                        validation_result["valid"] = False
            
            validation_result["summary"] = {
                "total_categories": categories_count,
                "total_tests": total_tests,
                "estimated_duration": f"{total_tests * 2}-{total_tests * 5} minutes"
            }
        
        # Check application info
        app_info = requirements_data.get("applicationInfo")
        if app_info:
            if "name" not in app_info:
                validation_result["warnings"].append("Application info missing 'name' field")
            if "type" not in app_info:
                validation_result["warnings"].append("Application info missing 'type' field")
        else:
            validation_result["warnings"].append("No application info provided")
        
        return {
            "status": "success",
            "data": validation_result
        }
        
    except Exception as e:
        logger.error(f"Requirements validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate requirements"
        )

@router.post("/api/v1/requirements/upload")
async def upload_requirements_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and validate requirements.json file"""
    try:
        # Check file type
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a JSON file"
            )
        
        # Read and parse file content
        content = await file.read()
        try:
            requirements_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON format: {str(e)}"
            )
        
        # Validate the requirements
        validation_result = await validate_requirements(requirements_data, current_user)
        
        return {
            "status": "success",
            "message": "Requirements file uploaded and validated successfully",
            "data": {
                "filename": file.filename,
                "requirements_data": requirements_data,
                "validation": validation_result["data"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Requirements upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload requirements file"
        )

@router.get("/api/v1/requirements/templates")
async def get_requirements_templates(
    current_user: dict = Depends(get_current_user)
):
    """Get available requirements.json templates"""
    try:
        templates = [
            {
                "name": "E-commerce Platform",
                "description": "Comprehensive test suite for e-commerce applications",
                "categories": ["Authentication", "Product Catalog", "Shopping Cart", "Checkout", "Order Management"],
                "estimated_tests": 25
            },
            {
                "name": "Banking Application",
                "description": "Test suite for banking and financial applications",
                "categories": ["Authentication", "Account Management", "Transactions", "Security", "Reporting"],
                "estimated_tests": 20
            },
            {
                "name": "HRMS Platform",
                "description": "Test suite for Human Resource Management Systems",
                "categories": ["Employee Management", "Leave Management", "Payroll", "Performance", "Reporting"],
                "estimated_tests": 18
            },
            {
                "name": "Healthcare System",
                "description": "Test suite for healthcare management applications",
                "categories": ["Patient Management", "Appointments", "Medical Records", "Billing", "Compliance"],
                "estimated_tests": 22
            }
        ]
        
        return {
            "status": "success",
            "data": templates
        }
        
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirements templates"
        )
