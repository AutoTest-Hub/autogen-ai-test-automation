"""
Hybrid Test Management Endpoints
Provides API endpoints for duplicate detection and intelligent test management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging

from auth import get_current_user
from duplicate_detection_service import duplicate_detection_service
from database_postgres_full import TestCase, TestSuite, Application

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/hybrid", tags=["hybrid-test-management"])

class DuplicateCheckRequest(BaseModel):
    application_id: UUID
    test_name: Optional[str] = None
    test_description: str
    similarity_threshold: Optional[float] = 0.8

class TestUpdateRequest(BaseModel):
    test_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    test_steps: Optional[Dict] = None
    priority: Optional[str] = None

class CoverageAnalysisRequest(BaseModel):
    application_id: UUID
    test_description: str

@router.post("/check-duplicates", response_model=Dict[str, Any])
async def check_for_duplicates(
    request: DuplicateCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """Check for duplicate tests before creation"""
    try:
        # Verify application belongs to customer
        applications = Application.get_by_customer(current_user['customer_id'])
        app_exists = any(str(app['id']) == str(request.application_id) for app in applications)
        
        if not app_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Set custom similarity threshold if provided
        if request.similarity_threshold:
            duplicate_detection_service.similarity_threshold = request.similarity_threshold
        
        # Find potential duplicates
        duplicates = duplicate_detection_service.find_duplicate_tests(
            customer_id=current_user['customer_id'],
            application_id=request.application_id,
            new_test_description=request.test_description,
            new_test_name=request.test_name
        )
        
        # Analyze coverage gaps
        coverage_analysis = duplicate_detection_service.analyze_test_coverage_gaps(
            customer_id=current_user['customer_id'],
            application_id=request.application_id,
            new_test_description=request.test_description
        )
        
        # Generate recommendations for each duplicate
        recommendations = []
        for duplicate in duplicates:
            should_update, reason = duplicate_detection_service.should_update_existing_test(
                existing_test=duplicate,
                new_test_data={
                    'name': request.test_name,
                    'description': request.test_description
                }
            )
            
            recommendations.append({
                'test_id': duplicate['test_id'],
                'test_name': duplicate['name'],
                'similarity_score': duplicate['similarity_score'],
                'should_update': should_update,
                'update_reason': reason,
                'action_recommendation': 'update' if should_update else 'review'
            })
        
        return {
            "status": "success",
            "data": {
                "has_duplicates": len(duplicates) > 0,
                "duplicate_count": len(duplicates),
                "duplicates": duplicates,
                "recommendations": recommendations,
                "coverage_analysis": coverage_analysis,
                "overall_recommendation": _generate_overall_recommendation(duplicates, coverage_analysis)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Duplicate check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check for duplicates"
        )

@router.post("/analyze-coverage", response_model=Dict[str, Any])
async def analyze_test_coverage(
    request: CoverageAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze test coverage for a new test description"""
    try:
        # Verify application belongs to customer
        applications = Application.get_by_customer(current_user['customer_id'])
        app_exists = any(str(app['id']) == str(request.application_id) for app in applications)
        
        if not app_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        coverage_analysis = duplicate_detection_service.analyze_test_coverage_gaps(
            customer_id=current_user['customer_id'],
            application_id=request.application_id,
            new_test_description=request.test_description
        )
        
        return {
            "status": "success",
            "data": coverage_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Coverage analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze test coverage"
        )

@router.put("/update-test", response_model=Dict[str, Any])
async def update_existing_test(
    request: TestUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing test case with new information"""
    try:
        # Get existing test
        test_data = TestCase.get_by_id(request.test_id)
        if not test_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        
        # Verify test belongs to customer
        if str(test_data['customer_id']) != str(current_user['customer_id']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Prepare update data
        update_data = {}
        if request.name:
            update_data['name'] = request.name
        if request.description:
            update_data['description'] = request.description
        if request.test_steps:
            update_data['test_steps'] = request.test_steps
        if request.priority:
            update_data['priority'] = request.priority
        
        # Add metadata about the update
        update_data['updated_by'] = current_user['id']
        update_data['status'] = 'updated'
        
        # Update the test case
        success = TestCase.update(request.test_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update test case"
            )
        
        # Get updated test data
        updated_test = TestCase.get_by_id(request.test_id)
        
        return {
            "status": "success",
            "message": "Test case updated successfully",
            "data": {
                "test_id": str(request.test_id),
                "name": updated_test['name'],
                "description": updated_test['description'],
                "status": updated_test['status'],
                "updated_at": updated_test['updated_at'].isoformat() if updated_test['updated_at'] else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test case"
        )

@router.get("/application/{application_id}/test-summary", response_model=Dict[str, Any])
async def get_application_test_summary(
    application_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get a summary of existing tests for an application"""
    try:
        # Verify application belongs to customer
        applications = Application.get_by_customer(current_user['customer_id'])
        app_data = next((app for app in applications if str(app['id']) == str(application_id)), None)
        
        if not app_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Get existing tests
        existing_tests = TestCase.get_by_application(application_id)
        
        # Analyze test distribution
        test_types = {}
        status_distribution = {}
        keywords_frequency = {}
        
        for test in existing_tests:
            # Count test types
            test_type = test.get('test_type', 'unknown')
            test_types[test_type] = test_types.get(test_type, 0) + 1
            
            # Count status distribution
            status = test.get('status', 'unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Count keywords
            keywords = duplicate_detection_service.extract_keywords(
                f"{test.get('name', '')} {test.get('description', '')}"
            )
            for keyword in keywords:
                keywords_frequency[keyword] = keywords_frequency.get(keyword, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(keywords_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "status": "success",
            "data": {
                "application": {
                    "id": str(application_id),
                    "name": app_data['name'],
                    "url": app_data['url'],
                    "type": app_data.get('application_type', 'unknown')
                },
                "test_summary": {
                    "total_tests": len(existing_tests),
                    "test_types": test_types,
                    "status_distribution": status_distribution,
                    "top_keywords": [{"keyword": k, "count": v} for k, v in top_keywords],
                    "coverage_areas": list(keywords_frequency.keys())
                },
                "recent_tests": [
                    {
                        "id": str(test['id']),
                        "name": test['name'],
                        "status": test['status'],
                        "created_at": test['created_at'].isoformat() if test['created_at'] else None
                    }
                    for test in sorted(existing_tests, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get test summary"
        )

def _generate_overall_recommendation(duplicates: List[Dict], coverage_analysis: Dict) -> str:
    """Generate an overall recommendation based on duplicates and coverage analysis"""
    if not duplicates:
        if coverage_analysis.get('coverage_improvement', 0) > 0.5:
            return "No duplicates found and good coverage improvement. Safe to create new test."
        else:
            return "No duplicates found but limited new coverage. Consider if this test is necessary."
    
    high_similarity_count = len([d for d in duplicates if d['similarity_score'] > 0.9])
    
    if high_similarity_count > 0:
        return f"Found {high_similarity_count} very similar test(s). Strongly recommend updating existing tests instead of creating new ones."
    
    if len(duplicates) > 2:
        return f"Found {len(duplicates)} similar tests. Review existing tests and consider consolidation."
    
    if coverage_analysis.get('coverage_improvement', 0) > 0.3:
        return "Some duplicates found but test adds meaningful new coverage. Consider creating with modifications."
    
    return "Similar tests exist. Recommend reviewing and updating existing tests instead of creating new ones."
