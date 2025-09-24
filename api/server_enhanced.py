"""
Enhanced API Server with Real-Time Agent Activity Dashboard
AI Test Automation SaaS Platform with WebSocket Support
"""

import os
import uuid
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Security, Request, Response, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Import WebSocket and orchestration components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from websocket_manager import manager, AgentType, AgentStatus
from websocket_endpoints import router as websocket_router, create_agent_activity, simulate_agent_work
from agent_orchestrator import orchestrator, TaskType, TaskPriority
from auth import authenticate_user, create_access_token, get_current_user, check_quota_middleware

# =====================================================
# CONFIGURATION AND SETUP
# =====================================================

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Deployment configuration
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "SaaS")
API_VERSION = "v1"
API_TITLE = f"AI Test Automation Platform - {DEPLOYMENT_MODE} Edition"

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# =====================================================
# PYDANTIC MODELS
# =====================================================

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]
    expires_in: int

class TestExecutionRequest(BaseModel):
    url: str = Field(..., description="Application URL to test")
    test_name: str = Field(..., description="Name for the test execution")
    headless: bool = Field(True, description="Run tests in headless mode")
    requirements_file: Optional[str] = Field(None, description="Requirements file to use")
    test_type: str = Field("comprehensive", description="Type of test to run")

class TestCreationRequest(BaseModel):
    creation_type: str = Field(..., description="Type of test creation: requirements, test_cases, or url_metadata")
    application_url: str = Field(..., description="URL of the application to test")
    application_name: str = Field(..., description="Name of the application")
    application_type: str = Field(..., description="Type of application (e-commerce, banking, etc.)")
    
    # For requirements-based creation
    requirements_text: Optional[str] = Field(None, description="Business requirements text")
    requirements_file: Optional[str] = Field(None, description="Requirements file path")
    
    # For test cases-based creation
    test_cases: Optional[List[Dict[str, Any]]] = Field(None, description="Manual test cases to convert")
    
    # For URL + metadata creation
    key_features: Optional[List[str]] = Field(None, description="Key features to test")
    user_flows: Optional[List[str]] = Field(None, description="Important user flows")
    
    # Common options
    priority: str = Field("normal", description="Task priority: low, normal, high, urgent")
    generate_performance_tests: bool = Field(False, description="Include performance tests")
    generate_cross_browser_tests: bool = Field(False, description="Include cross-browser tests")

class ApplicationRequest(BaseModel):
    name: str = Field(..., description="Application name")
    url: str = Field(..., description="Application URL")
    description: str = Field(..., description="Application description")
    application_type: str = Field(..., description="Type of application")
    testing_goals: str = Field(..., description="What you want to test")
    credentials: Optional[Dict[str, str]] = Field(None, description="Test credentials")

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    current_step: str
    activities: List[Dict[str, Any]]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# =====================================================
# APPLICATION SETUP
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"Starting {API_TITLE}")
    logger.info(f"Deployment Mode: {DEPLOYMENT_MODE}")
    
    # Start background tasks
    cleanup_task = asyncio.create_task(cleanup_background_task())
    
    yield
    
    # Cleanup
    cleanup_task.cancel()
    logger.info("Application shutdown complete")

async def cleanup_background_task():
    """Background task for cleanup operations"""
    while True:
        try:
            # Clean up old activities
            manager.cleanup_old_activities(hours=24)
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying

# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description="AI-powered test automation platform with real-time agent monitoring",
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if DEPLOYMENT_MODE == "SaaS" else None,
    redoc_url="/redoc" if DEPLOYMENT_MODE == "SaaS" else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if DEPLOYMENT_MODE == "OnPrem":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.company.local"]
    )

# Include WebSocket router
app.include_router(websocket_router, prefix="/api/v1")

# =====================================================
# AUTHENTICATION ENDPOINTS
# =====================================================

@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return access token"""
    try:
        user = authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "api_calls_limit": user["api_calls_limit"],
                "api_calls_used": user["api_calls_used"],
                "subscription_plan": user["subscription_plan"]
            },
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "api_calls_limit": current_user["api_calls_limit"],
        "api_calls_used": current_user["api_calls_used"],
        "subscription_plan": current_user["subscription_plan"],
        "deployment_mode": DEPLOYMENT_MODE
    }

# =====================================================
# APPLICATION MANAGEMENT ENDPOINTS
# =====================================================

@app.post("/api/v1/applications")
async def create_application(
    request: ApplicationRequest,
    current_user: Dict[str, Any] = Depends(check_quota_middleware)
):
    """Create a new application for testing"""
    try:
        application_id = str(uuid.uuid4())
        
        # Store application (in production, this would go to database)
        application_data = {
            "id": application_id,
            "user_id": current_user["id"],
            "name": request.name,
            "url": request.url,
            "description": request.description,
            "application_type": request.application_type,
            "testing_goals": request.testing_goals,
            "credentials": request.credentials,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        logger.info(f"Created application {application_id} for user {current_user['id']}")
        
        return {
            "application_id": application_id,
            "message": "Application created successfully",
            "application": application_data
        }
        
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )

@app.get("/api/v1/applications")
async def get_user_applications(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all applications for the current user"""
    try:
        # In production, this would query the database
        # For demo, return sample applications
        applications = [
            {
                "id": "app_1",
                "name": "E-commerce Demo",
                "url": "https://demo.automationexercise.com",
                "application_type": "ecommerce",
                "status": "active",
                "tests_count": 15,
                "last_test_run": "2024-01-15T10:30:00Z",
                "success_rate": 92
            },
            {
                "id": "app_2", 
                "name": "Banking Portal",
                "url": "https://demo.testfire.net",
                "application_type": "banking",
                "status": "active",
                "tests_count": 8,
                "last_test_run": "2024-01-14T15:45:00Z",
                "success_rate": 88
            }
        ]
        
        return {"applications": applications}
        
    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applications"
        )

# =====================================================
# TEST CREATION ENDPOINTS WITH REAL-TIME MONITORING
# =====================================================

@app.post("/api/v1/test/create", response_model=Dict[str, Any])
async def create_test_with_agents(
    request: TestCreationRequest,
    current_user: Dict[str, Any] = Depends(check_quota_middleware)
):
    """Create tests using AI agents with real-time monitoring"""
    try:
        # Determine task type based on creation type
        task_type_mapping = {
            "requirements": TaskType.GENERATE_TESTS_FROM_REQUIREMENTS,
            "test_cases": TaskType.GENERATE_TESTS_FROM_CASES,
            "url_metadata": TaskType.GENERATE_TESTS_FROM_URL
        }
        
        task_type = task_type_mapping.get(request.creation_type)
        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid creation type: {request.creation_type}"
            )
        
        # Determine priority
        priority_mapping = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT
        }
        priority = priority_mapping.get(request.priority, TaskPriority.NORMAL)
        
        # Prepare task data
        task_data = {
            "creation_type": request.creation_type,
            "application_url": request.application_url,
            "application_name": request.application_name,
            "application_type": request.application_type,
            "requirements_text": request.requirements_text,
            "requirements_file": request.requirements_file,
            "test_cases": request.test_cases,
            "key_features": request.key_features,
            "user_flows": request.user_flows,
            "generate_performance_tests": request.generate_performance_tests,
            "generate_cross_browser_tests": request.generate_cross_browser_tests
        }
        
        # Submit task to orchestrator
        task_id = await orchestrator.submit_task(
            task_type=task_type,
            user_id=current_user["id"],
            data=task_data,
            priority=priority
        )
        
        logger.info(f"Test creation task {task_id} submitted for user {current_user['id']}")
        
        return {
            "task_id": task_id,
            "message": "Test creation started. Connect to WebSocket for real-time updates.",
            "websocket_url": f"/api/v1/ws/agent-activity/{current_user['id']}",
            "status": "submitted"
        }
        
    except Exception as e:
        logger.error(f"Error creating test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test: {str(e)}"
        )

@app.get("/api/v1/test/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the status of a test creation task"""
    try:
        task = orchestrator.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        if task.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get activities for this task
        activities = manager.get_task_activities(task_id)
        
        # Calculate overall progress
        if activities:
            total_progress = sum(activity.progress for activity in activities)
            avg_progress = int(total_progress / len(activities))
        else:
            avg_progress = 0
        
        # Get current step from active activities
        current_step = ""
        for activity in activities:
            if activity.status not in [AgentStatus.COMPLETED, AgentStatus.ERROR]:
                current_step = activity.current_step
                break
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task.status,
            progress=avg_progress,
            current_step=current_step,
            activities=[activity.to_dict() for activity in activities],
            result=task.result,
            error=task.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task status"
        )

# =====================================================
# TEST EXECUTION ENDPOINTS
# =====================================================

class TestExecutionRequest(BaseModel):
    test_id: str = Field(..., description="ID of the test to execute")
    execution_name: str = Field(..., description="Name for this execution")
    environment: str = Field("production", description="Environment to run tests against")
    browser: str = Field("chrome", description="Browser to use for execution")
    headless: bool = Field(True, description="Run tests in headless mode")
    parallel: bool = Field(False, description="Run tests in parallel")
    max_workers: int = Field(1, description="Maximum number of parallel workers")
    timeout: int = Field(300, description="Test timeout in seconds")
    retry_failed: bool = Field(True, description="Retry failed tests")
    max_retries: int = Field(2, description="Maximum number of retries")

class TestExecutionResponse(BaseModel):
    execution_id: str
    status: str
    message: str
    websocket_url: str
    estimated_duration: int

@app.post("/api/v1/test/execute", response_model=TestExecutionResponse)
async def execute_test(
    request: TestExecutionRequest,
    current_user: Dict[str, Any] = Depends(check_quota_middleware)
):
    """Execute a previously created test"""
    try:
        execution_id = str(uuid.uuid4())
        
        # Validate test exists (in production, check database)
        # For demo, we'll simulate test execution
        
        # Create execution task
        task_data = {
            "test_id": request.test_id,
            "execution_name": request.execution_name,
            "environment": request.environment,
            "browser": request.browser,
            "headless": request.headless,
            "parallel": request.parallel,
            "max_workers": request.max_workers,
            "timeout": request.timeout,
            "retry_failed": request.retry_failed,
            "max_retries": request.max_retries,
            "execution_id": execution_id
        }
        
        # Submit execution task to orchestrator
        task_id = await orchestrator.submit_task(
            task_type=TaskType.EXECUTE_TESTS,
            user_id=current_user["id"],
            data=task_data,
            priority=TaskPriority.NORMAL
        )
        
        logger.info(f"Test execution {execution_id} started for user {current_user['id']}")
        
        return TestExecutionResponse(
            execution_id=execution_id,
            status="started",
            message="Test execution started. Connect to WebSocket for real-time updates.",
            websocket_url=f"/api/v1/ws/agent-activity/{current_user['id']}",
            estimated_duration=300  # 5 minutes estimate
        )
        
    except Exception as e:
        logger.error(f"Error executing test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test execution failed: {str(e)}"
        )

@app.get("/api/v1/test/execution/{execution_id}")
async def get_execution_status(
    execution_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the status of a test execution"""
    try:
        # In production, this would query the database
        # For demo, return mock execution status
        execution_status = {
            "execution_id": execution_id,
            "status": "running",
            "progress": 65,
            "current_test": "Login functionality test",
            "tests_completed": 13,
            "tests_total": 20,
            "tests_passed": 11,
            "tests_failed": 2,
            "start_time": "2024-09-24T10:30:00Z",
            "estimated_completion": "2024-09-24T10:35:00Z",
            "environment": "production",
            "browser": "chrome",
            "logs": [
                {"timestamp": "2024-09-24T10:30:00Z", "level": "info", "message": "Starting test execution"},
                {"timestamp": "2024-09-24T10:30:15Z", "level": "info", "message": "Login test passed"},
                {"timestamp": "2024-09-24T10:30:30Z", "level": "warning", "message": "Slow response detected"},
                {"timestamp": "2024-09-24T10:30:45Z", "level": "error", "message": "Element not found: #submit-button"}
            ]
        }
        
        return execution_status
        
    except Exception as e:
        logger.error(f"Error getting execution status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get execution status"
        )

@app.post("/api/v1/test/execution/{execution_id}/stop")
async def stop_execution(
    execution_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Stop a running test execution"""
    try:
        # In production, this would stop the actual execution
        logger.info(f"Stopping execution {execution_id} for user {current_user['id']}")
        
        return {
            "execution_id": execution_id,
            "status": "stopped",
            "message": "Test execution stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Error stopping execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop execution"
        )

@app.get("/api/v1/test/execution/{execution_id}/results")
async def get_execution_results(
    execution_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed results of a test execution"""
    try:
        # In production, this would query the database for actual results
        results = {
            "execution_id": execution_id,
            "status": "completed",
            "summary": {
                "total_tests": 20,
                "passed": 18,
                "failed": 2,
                "skipped": 0,
                "success_rate": 90.0,
                "duration": 285,
                "start_time": "2024-09-24T10:30:00Z",
                "end_time": "2024-09-24T10:34:45Z"
            },
            "test_results": [
                {
                    "test_name": "User Login",
                    "status": "passed",
                    "duration": 12.5,
                    "assertions": 5,
                    "screenshots": ["login_success.png"],
                    "logs": ["Login form filled successfully", "Authentication successful"]
                },
                {
                    "test_name": "Product Search",
                    "status": "passed", 
                    "duration": 8.3,
                    "assertions": 3,
                    "screenshots": ["search_results.png"],
                    "logs": ["Search query executed", "Results displayed correctly"]
                },
                {
                    "test_name": "Checkout Process",
                    "status": "failed",
                    "duration": 15.2,
                    "assertions": 7,
                    "error": "Element not found: #payment-submit",
                    "screenshots": ["checkout_error.png"],
                    "logs": ["Cart items loaded", "Payment form displayed", "Error: Submit button not found"]
                }
            ],
            "artifacts": {
                "screenshots": ["login_success.png", "search_results.png", "checkout_error.png"],
                "videos": ["execution_recording.mp4"],
                "reports": ["detailed_report.html", "junit_results.xml"],
                "logs": ["execution.log", "browser.log"]
            },
            "performance": {
                "avg_response_time": 1.2,
                "max_response_time": 3.8,
                "min_response_time": 0.3,
                "page_load_times": [2.1, 1.8, 2.5, 1.9]
            }
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting execution results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get execution results"
        )

# =====================================================
# LEGACY TEST EXECUTION ENDPOINT (BACKWARD COMPATIBILITY)
# =====================================================

@app.post("/api/v1/test/execute-legacy")
async def execute_test_legacy(
    request: TestExecutionRequest,
    current_user: Dict[str, Any] = Depends(check_quota_middleware)
):
    """Legacy test execution endpoint for backward compatibility"""
    try:
        # Convert to new test creation format
        creation_request = TestCreationRequest(
            creation_type="url_metadata",
            application_url=request.url,
            application_name=request.test_name,
            application_type="web_application",
            key_features=["login", "navigation", "forms"],
            user_flows=["user_registration", "user_login", "main_workflow"]
        )
        
        # Use the new test creation endpoint
        return await create_test_with_agents(creation_request, current_user)
        
    except Exception as e:
        logger.error(f"Error in legacy test execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test execution failed: {str(e)}"
        )

# =====================================================
# DEMO AND TESTING ENDPOINTS
# =====================================================

@app.post("/api/v1/demo/simulate-agent-work")
async def simulate_agent_work_demo(
    agent_type: str,
    user_id: str,
    steps: List[str],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Demo endpoint to simulate agent work for testing"""
    try:
        # Create a demo activity
        agent_type_enum = AgentType(agent_type)
        activity = await create_agent_activity(
            agent_type=agent_type_enum,
            task_id=f"demo_task_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            total_steps=len(steps),
            metadata={"demo": True}
        )
        
        # Start simulation in background
        asyncio.create_task(simulate_agent_work(activity.id, steps, delay_between_steps=2.0))
        
        return {
            "activity_id": activity.id,
            "message": "Agent simulation started",
            "websocket_url": f"/api/v1/ws/agent-activity/{user_id}"
        }
        
    except Exception as e:
        logger.error(f"Error in agent simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )

# =====================================================
# SYSTEM STATUS AND HEALTH ENDPOINTS
# =====================================================

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "deployment_mode": DEPLOYMENT_MODE,
        "version": API_VERSION,
        "active_connections": len(manager.active_connections),
        "active_tasks": len(orchestrator.running_tasks)
    }

@app.get("/api/v1/system/info")
async def system_info():
    """Get system information for deployment configuration (public endpoint)"""
    try:
        # Define features based on deployment mode
        if DEPLOYMENT_MODE == "SaaS":
            features_enabled = {
                "billing": True,
                "userRegistration": True,
                "multiTenant": True,
                "subscriptionPlans": True,
                "publicSignup": True,
                "marketingPages": True,
                "usageAnalytics": True,
                "cloudIntegrations": True,
                "autoScaling": True,
                "globalCDN": True,
                "real_time_monitoring": True,
                "multi_modal_creation": True,
                "agent_orchestration": True,
                "advanced_analytics": True,
                "ldap_integration": False,
                "custom_branding": False
            }
            branding = {
                "name": "AI Test Automation Platform",
                "edition": "SaaS Edition",
                "logo_url": "/logo.png",
                "primary_color": "#3b82f6",
                "secondary_color": "#1e40af"
            }
        else:  # OnPrem
            features_enabled = {
                "billing": False,
                "userRegistration": False,
                "multiTenant": False,
                "subscriptionPlans": False,
                "publicSignup": False,
                "marketingPages": False,
                "usageAnalytics": True,
                "cloudIntegrations": False,
                "autoScaling": False,
                "globalCDN": False,
                "ldapIntegration": True,
                "customBranding": True,
                "airGappedMode": True,
                "enterpriseSecurity": True,
                "auditCompliance": True,
                "customReports": True,
                "real_time_monitoring": True,
                "multi_modal_creation": True,
                "agent_orchestration": True,
                "advanced_analytics": True
            }
            branding = {
                "name": "Enterprise Test Automation",
                "edition": "OnPrem Edition",
                "logo_url": "/logo-enterprise.png",
                "primary_color": "#059669",
                "secondary_color": "#047857"
            }
        
        return {
            "deployment_mode": DEPLOYMENT_MODE,
            "version": "1.0.0",
            "features": features_enabled,
            "branding": branding
        }
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system info"
        )

@app.get("/api/v1/system/status")
async def system_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get system status and statistics"""
    try:
        total_activities = sum(len(activities) for activities in manager.activities.values())
        active_activities = sum(
            1 for activities in manager.activities.values()
            for activity in activities
            if activity.status not in [AgentStatus.COMPLETED, AgentStatus.ERROR]
        )
        
        return {
            "deployment_mode": DEPLOYMENT_MODE,
            "system_health": "healthy",
            "statistics": {
                "connected_users": len(manager.active_connections),
                "total_activities": total_activities,
                "active_activities": active_activities,
                "running_tasks": len(orchestrator.running_tasks),
                "queued_tasks": len(orchestrator.task_queue)
            },
            "agent_types": [agent_type.value for agent_type in AgentType],
            "supported_task_types": [task_type.value for task_type in TaskType]
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system status"
        )

# =====================================================
# REQUIREMENTS TEMPLATES ENDPOINT
# =====================================================

@app.get("/api/v1/requirements/templates")
async def get_requirements_templates(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get available requirements templates"""
    try:
        templates = [
            {
                "id": "ecommerce",
                "name": "E-commerce Template",
                "description": "Comprehensive testing for e-commerce applications",
                "file": "requirements_ecommerce.json",
                "application_types": ["ecommerce", "retail", "marketplace"]
            },
            {
                "id": "banking",
                "name": "Banking Template", 
                "description": "Security-focused testing for banking applications",
                "file": "requirements_banking.json",
                "application_types": ["banking", "fintech", "financial"]
            },
            {
                "id": "hrms",
                "name": "HRMS Template",
                "description": "Employee management system testing",
                "file": "requirements_hrms.json", 
                "application_types": ["hrms", "hr", "employee_management"]
            }
        ]
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch templates"
        )

@app.get("/api/v1/requirements/template/{template_name}")
async def get_requirements_template(
    template_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific requirements template"""
    try:
        # Map template names to files
        template_files = {
            "ecommerce": "requirements_ecommerce.json",
            "banking": "requirements_banking.json", 
            "hrms": "requirements_hrms.json"
        }
        
        if template_name not in template_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_name}' not found"
            )
        
        # Load template file
        template_file = template_files[template_name]
        template_path = os.path.join(os.path.dirname(__file__), "..", template_file)
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            return template_data
        else:
            # Return a basic template structure if file doesn't exist
            return {
                "name": template_name.title(),
                "description": f"Template for {template_name} applications",
                "requirements": [
                    "User authentication and authorization",
                    "Data validation and error handling",
                    "Security and compliance checks",
                    "Performance and scalability testing"
                ]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template {template_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch template"
        )

@app.get("/api/v1/test/executions")
async def get_test_executions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get test execution history"""
    try:
        # Return mock data for now - in production this would come from database
        executions = [
            {
                "id": "exec_001",
                "test_name": "E-commerce Checkout Flow",
                "application_url": "https://demo-store.example.com",
                "status": "completed",
                "created_at": "2024-09-24T10:30:00Z",
                "completed_at": "2024-09-24T10:45:00Z",
                "duration": 900,
                "tests_passed": 24,
                "tests_failed": 1,
                "success_rate": 96.0
            },
            {
                "id": "exec_002", 
                "test_name": "User Registration Flow",
                "application_url": "https://demo-app.example.com",
                "status": "running",
                "created_at": "2024-09-24T11:00:00Z",
                "completed_at": None,
                "duration": None,
                "tests_passed": 12,
                "tests_failed": 0,
                "success_rate": 100.0
            }
        ]
        
        return {"executions": executions}
        
    except Exception as e:
        logger.error(f"Error fetching test executions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch test executions"
        )

# =====================================================
# MAIN APPLICATION ENTRY POINT
# =====================================================

if __name__ == "__main__":
    uvicorn.run(
        "server_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
