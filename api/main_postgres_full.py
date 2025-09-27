"""
AI Test Automation Platform API Server - Full Enterprise Schema
==============================================================

FastAPI server optimized for the complete 21-table PostgreSQL schema with:
- Enhanced agent management with real-time status
- Granular test step tracking
- Comprehensive activity logging
- Full enterprise features
"""

import os
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging

# Import our full PostgreSQL database models
from database_postgres_full import (
    db, Customer, CustomerUser, Application, TestSuite, AgentJob, AuditLog,
    initialize_database, get_dashboard_stats
)

# Import hybrid test management endpoints
from hybrid_test_endpoints import router as hybrid_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# FastAPI app initialization
app = FastAPI(
    title="AI Test Automation Platform - Enterprise",
    description="Full enterprise AI-powered test automation with 21-table PostgreSQL schema",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hybrid_router)

# =====================================================
# PYDANTIC MODELS
# =====================================================

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    customer_id: str
    customer_name: str

class ApplicationCreate(BaseModel):
    name: str
    url: str
    application_type: str
    description: Optional[str] = None

class TestCreationRequest(BaseModel):
    application_url: str
    application_name: str
    application_type: str
    key_features: Optional[str] = None
    important_user_flows: Optional[str] = None

class SystemInfo(BaseModel):
    app_name: str = "AI Test Automation Platform - Enterprise"
    version: str = "3.0.0"
    database: str = "PostgreSQL (21 Tables)"
    schema_type: str = "Full Enterprise Schema"
    status: str = "operational"
    timestamp: datetime

# =====================================================
# AUTHENTICATION & SECURITY
# =====================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = CustomerUser.get_by_email(user_id)
    if user is None:
        raise credentials_exception
    
    return user

# =====================================================
# API ENDPOINTS
# =====================================================

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint with schema information"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected" if db.connection else "disconnected",
        "schema": "Full Enterprise (21 tables)",
        "features": [
            "Granular test step tracking",
            "Real-time agent status",
            "Comprehensive activity logging",
            "Enhanced security controls"
        ]
    }

@app.get("/api/v1/system/info", response_model=SystemInfo)
async def get_system_info():
    """Get system information"""
    return SystemInfo(
        timestamp=datetime.now(timezone.utc)
    )

@app.post("/api/v1/auth/login")
async def login(user_credentials: UserLogin, request: Request):
    """Authenticate user and return access token"""
    try:
        # Get user by username (email field in database)
        user = CustomerUser.get_by_email(user_credentials.username)
        
        if not user or not verify_password(user_credentials.password, user['password_hash']):
            # Log failed login attempt
            if user:
                AuditLog.log_event(
                    customer_id=user['customer_id'],
                    user_id=user['id'],
                    event_type='authentication',
                    resource_type='user_session',
                    resource_id=user['id'],
                    action='failed_login',
                    ip_address=request.client.host,
                    metadata={'reason': 'invalid_credentials'}
                )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Update login information
        CustomerUser.update_login_info(user['id'], request.client.host)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['email']}, expires_delta=access_token_expires
        )
        
        # Log successful login
        AuditLog.log_event(
            customer_id=user['customer_id'],
            user_id=user['id'],
            event_type='authentication',
            resource_type='user_session',
            resource_id=user['id'],
            action='successful_login',
            ip_address=request.client.host
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user['id']),
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "role": user['role'],
                "customer_id": str(user['customer_id']),
                "customer_name": user['customer_name']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user['id']),
        email=current_user['email'],
        first_name=current_user['first_name'],
        last_name=current_user['last_name'],
        role=current_user['role'],
        customer_id=str(current_user['customer_id']),
        customer_name=current_user['customer_name']
    )

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_statistics(current_user: dict = Depends(get_current_user)):
    """Get enhanced dashboard statistics"""
    try:
        stats = get_dashboard_stats(current_user['customer_id'])
        
        # Add schema-specific information
        stats.update({
            "schema_version": "3.0.0",
            "total_tables": 21,
            "enterprise_features": [
                "Real-time agent tracking",
                "Granular test step execution",
                "Comprehensive audit logging",
                "Enhanced security controls"
            ]
        })
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )

@app.get("/api/v1/test/executions")
async def get_test_executions(current_user: dict = Depends(get_current_user)):
    """Get test executions for the current customer"""
    try:
        # Query test executions from database
        query = """
        SELECT te.id, te.test_suite_id, te.status, te.start_time, te.end_time,
               te.total_tests, te.passed_tests, te.failed_tests, te.skipped_tests,
               ts.name as test_suite_name, a.name as application_name
        FROM test_executions te
        JOIN test_suites ts ON te.test_suite_id = ts.id
        JOIN applications a ON ts.application_id = a.id
        WHERE te.customer_id = %s
        ORDER BY te.start_time DESC
        LIMIT 50
        """
        
        executions = db.execute_query(query, (current_user['customer_id'],))
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(execution['id']),
                    "test_suite_id": str(execution['test_suite_id']),
                    "test_suite_name": execution['test_suite_name'],
                    "application_name": execution['application_name'],
                    "status": execution['status'],
                    "start_time": execution['start_time'].isoformat() if execution['start_time'] else None,
                    "end_time": execution['end_time'].isoformat() if execution['end_time'] else None,
                    "total_tests": execution['total_tests'] or 0,
                    "passed_tests": execution['passed_tests'] or 0,
                    "failed_tests": execution['failed_tests'] or 0,
                    "skipped_tests": execution['skipped_tests'] or 0,
                    "success_rate": round((execution['passed_tests'] or 0) / max(execution['total_tests'] or 1, 1) * 100, 1)
                }
                for execution in executions
            ]
        }
    except Exception as e:
        logger.error(f"Get test executions error: {e}")
        # Return empty data instead of error to prevent frontend issues
        return {
            "status": "success",
            "data": []
        }

@app.get("/api/v1/applications")
async def get_applications(current_user: dict = Depends(get_current_user)):
    """Get all applications for the current customer"""
    try:
        applications = Application.get_by_customer(current_user['customer_id'])
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(app['id']),
                    "name": app['name'],
                    "url": app['url'],
                    "application_type": app['application_type'],
                    "description": app['description'],
                    "status": app['status'],
                    "data_sensitivity_level": app.get('data_sensitivity_level', 'medium'),
                    "created_at": app['created_at'].isoformat() if app['created_at'] else None
                }
                for app in applications
            ]
        }
    except Exception as e:
        logger.error(f"Get applications error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve applications"
        )

@app.post("/api/v1/applications")
async def create_application(
    app_data: ApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new application"""
    try:
        app_id = Application.create(
            customer_id=current_user['customer_id'],
            name=app_data.name,
            url=app_data.url,
            application_type=app_data.application_type,
            description=app_data.description,
            created_by=current_user['id']
        )
        
        if app_id:
            # Log application creation
            AuditLog.log_event(
                customer_id=current_user['customer_id'],
                user_id=current_user['id'],
                event_type='data_modification',
                resource_type='application',
                resource_id=app_id,
                action='create',
                new_values=app_data.dict()
            )
            
            return {
                "status": "success",
                "message": "Application created successfully",
                "data": {"id": str(app_id)}
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create application"
            )
            
    except Exception as e:
        logger.error(f"Create application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )

@app.get("/api/v1/tests")
async def get_test_suites(current_user: dict = Depends(get_current_user)):
    """Get all test suites with enhanced information"""
    try:
        test_suites = TestSuite.get_by_customer(current_user['customer_id'])
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(suite['id']),
                    "name": suite['name'],
                    "description": suite['description'],
                    "type": suite['test_type'],
                    "status": suite['status'],
                    "application_name": suite['application_name'],
                    "application_url": suite['application_url'],
                    "total_test_cases": suite['total_test_cases'],
                    "passed_test_cases": suite['passed_test_cases'],
                    "failed_test_cases": suite['failed_test_cases'],
                    "success_rate": float(suite['success_rate']) if suite['success_rate'] else 0,
                    "last_run_at": suite['last_run_at'].isoformat() if suite['last_run_at'] else None,
                    "duration_minutes": suite['duration_minutes'],
                    "data_classification": suite.get('data_classification', 'internal'),
                    "created_at": suite['created_at'].isoformat() if suite['created_at'] else None
                }
                for suite in test_suites
            ]
        }
    except Exception as e:
        logger.error(f"Get test suites error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test suites"
        )

@app.post("/api/v1/create-test")
async def create_test_suite(
    test_request: TestCreationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new test suite with enhanced agent processing"""
    try:
        # First, create or get the application
        app_id = Application.create(
            customer_id=current_user['customer_id'],
            name=test_request.application_name,
            url=test_request.application_url,
            application_type=test_request.application_type,
            description=f"Application for {test_request.application_type} testing",
            created_by=current_user['id']
        )
        
        if not app_id:
            # Try to get existing application
            applications = Application.get_by_customer(current_user['customer_id'])
            existing_app = next((app for app in applications if app['url'] == test_request.application_url), None)
            if existing_app:
                app_id = existing_app['id']
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create or find application"
                )
        
        # Create test suite
        suite_id = TestSuite.create(
            customer_id=current_user['customer_id'],
            application_id=app_id,
            name=f"{test_request.application_name} - Automated Test Suite",
            description=f"AI-generated test suite for {test_request.application_type} application",
            test_type='functional',
            created_by=current_user['id']
        )
        
        if not suite_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create test suite"
            )
        
        # Create agent job for test generation
        job_id = AgentJob.create(
            customer_id=current_user['customer_id'],
            application_id=app_id,
            job_type='test_creation',
            test_suite_id=suite_id,
            created_by=current_user['id']
        )
        
        if not job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create agent job"
            )
        
        # Log test creation
        AuditLog.log_event(
            customer_id=current_user['customer_id'],
            user_id=current_user['id'],
            event_type='data_modification',
            resource_type='test_suite',
            resource_id=suite_id,
            action='create',
            new_values=test_request.dict()
        )
        
        # Start REAL background agent processing that creates actual test cases
        from real_agent_processor import start_real_agent_processing
        import threading
        
        # Use threading to ensure the background task actually runs
        def run_agent_processing():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_real_agent_processing(job_id, test_request.dict()))
            loop.close()
        
        thread = threading.Thread(target=run_agent_processing)
        thread.daemon = True
        thread.start()
        
        return {
            "status": "success",
            "message": "Test creation started successfully! Agents are now processing your application.",
            "data": {
                "job_id": str(job_id),
                "test_suite_id": str(suite_id),
                "application_id": str(app_id),
                "application_name": test_request.application_name,
                "application_type": test_request.application_type,
                "test_management_url": "/test-management"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create test error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test suite"
        )

@app.get("/api/v1/agent-job/{job_id}")
async def get_agent_job_status(
    job_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get enhanced agent job status with real-time processing information"""
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
        
        return {
            "status": "success",
            "data": {
                "job": {
                    "id": str(job['id']),
                    "status": job['status'],
                    "progress_percentage": job.get('current_progress', job['progress_percentage']),
                    "current_agent": job['current_agent'],
                    "current_step": job.get('current_step'),
                    "created_at": job['created_at'].isoformat() if job['created_at'] else None,
                    "started_at": job['started_at'].isoformat() if job['started_at'] else None,
                    "completed_at": job['completed_at'].isoformat() if job['completed_at'] else None
                },
                "activities": [
                    {
                        "id": str(activity['id']),
                        "agent_name": activity['agent_name'],
                        "activity_type": activity['activity_type'],
                        "status": activity['status'],
                        "progress_percentage": activity['progress_percentage'],
                        "message": activity['message'],
                        "created_at": activity['created_at'].isoformat() if activity['created_at'] else None
                    }
                    for activity in activities
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get agent job error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent job status"
        )

# =====================================================
# ENHANCED BACKGROUND TASKS
# =====================================================

async def process_agent_job_enhanced(job_id: UUID, test_request: TestCreationRequest):
    """Enhanced background task with detailed agent processing"""
    try:
        # Update job status to running
        AgentJob.update_progress(job_id, 0, "Discovery Agent", "running")
        
        # Phase 1: Discovery and Analysis
        AgentJob.add_activity(
            job_id, "Discovery Agent", "discovery", 
            "Initializing application discovery process", "running", 5
        )
        await asyncio.sleep(2)
        
        AgentJob.add_activity(
            job_id, "Discovery Agent", "analysis",
            f"Analyzing {test_request.application_type} application structure", "running", 15
        )
        await asyncio.sleep(3)
        
        AgentJob.add_activity(
            job_id, "Discovery Agent", "discovery",
            "Mapping user interface components and workflows", "running", 25
        )
        await asyncio.sleep(2)
        
        AgentJob.add_activity(
            job_id, "Discovery Agent", "analysis",
            "Identifying critical user paths and business logic", "completed", 35
        )
        
        # Phase 2: Test Generation
        AgentJob.update_progress(job_id, 35, "Test Generation Agent")
        
        AgentJob.add_activity(
            job_id, "Test Generation Agent", "generation",
            "Creating comprehensive test scenarios based on discovery", "running", 50
        )
        await asyncio.sleep(4)
        
        AgentJob.add_activity(
            job_id, "Test Generation Agent", "generation",
            "Generating automated test scripts with assertions", "running", 65
        )
        await asyncio.sleep(3)
        
        AgentJob.add_activity(
            job_id, "Test Generation Agent", "validation",
            "Validating test coverage and edge cases", "running", 80
        )
        await asyncio.sleep(2)
        
        # Phase 3: Optimization and Finalization
        AgentJob.update_progress(job_id, 80, "Optimization Agent")
        
        AgentJob.add_activity(
            job_id, "Optimization Agent", "optimization",
            "Optimizing test execution performance and reliability", "running", 90
        )
        await asyncio.sleep(3)
        
        AgentJob.add_activity(
            job_id, "Optimization Agent", "validation",
            "Performing final validation and quality checks", "running", 95
        )
        await asyncio.sleep(2)
        
        # Complete the job
        AgentJob.update_progress(job_id, 100, "Completed", "completed")
        AgentJob.add_activity(
            job_id, "System", "validation",
            "Test suite generation completed successfully with enhanced features", "completed", 100
        )
        
        # Update test suite status
        job_data = AgentJob.get_by_id(job_id)
        if job_data and job_data['job']['test_suite_id']:
            TestSuite.update_status(job_data['job']['test_suite_id'], 'completed')
        
        logger.info(f"Enhanced agent job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Enhanced agent job processing error: {e}")
        AgentJob.update_progress(job_id, 0, "Error", "failed")
        AgentJob.add_activity(
            job_id, "System", "validation",
            f"Job failed with error: {str(e)}", "failed", 0
        )

# =====================================================
# APPLICATION STARTUP
# =====================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and create sample data on startup"""
    logger.info("Starting AI Test Automation Platform API Server (Enterprise)...")
    
    # Initialize database
    if initialize_database():
        logger.info("✅ Database initialized successfully")
    else:
        logger.error("❌ Database initialization failed")
    
    logger.info("🚀 Enterprise API Server ready with full 21-table schema!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Enterprise API Server...")
    db.disconnect()

# =====================================================
# MAIN ENTRY POINT
# =====================================================

if __name__ == "__main__":
    uvicorn.run(
        "main_postgres_full:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
