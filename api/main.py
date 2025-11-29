"""
AI Test Automation SaaS Platform - REST API
===========================================

Production-ready FastAPI service for the enhanced three-tier test automation system.
Provides RESTful endpoints for programmatic access, authentication, and integration.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import uuid
import json
import os
from datetime import datetime, timedelta
import logging
from pathlib import Path
import jwt
from passlib.context import CryptContext

# Import our enhanced system components
import sys
sys.path.append('..')
from proper_multi_agent_workflow import ProperMultiAgentWorkflow
from agents.enhanced_discovery_agent import create_enhanced_discovery_agent
from agents.integrated_test_generator import create_integrated_test_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Test Automation SaaS Platform",
    description="Production-ready API for intelligent test automation generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory storage (replace with database in production)
users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "is_active": True,
        "api_quota": 1000,
        "api_usage": 0
    }
}

test_executions = {}
execution_results = {}

# Pydantic models
class User(BaseModel):
    username: str
    email: str
    is_active: bool = True
    api_quota: int = 100
    api_usage: int = 0

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TestExecutionRequest(BaseModel):
    url: str = Field(..., description="Target application URL")
    name: str = Field(..., description="Test execution name")
    headless: bool = Field(True, description="Run browser in headless mode")
    requirements_file: Optional[str] = Field(None, description="Custom requirements file")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional configuration")

class TestExecutionResponse(BaseModel):
    execution_id: str
    status: str
    message: str
    estimated_duration: int  # seconds

class TestExecutionStatus(BaseModel):
    execution_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 to 1.0
    current_phase: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class RequirementsTemplate(BaseModel):
    app_name: str
    base_url: str
    application_type: str
    description: str
    priority_areas: List[str]
    test_scenarios: Dict[str, Any]
    test_environment: Dict[str, Any]

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

async def check_api_quota(user: dict):
    if user["api_usage"] >= user["api_quota"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="API quota exceeded"
        )

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Test Automation SaaS Platform API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/auth/register", response_model=Dict[str, str])
async def register_user(user: UserCreate):
    """Register a new user"""
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_active": True,
        "api_quota": 100,
        "api_usage": 0
    }
    
    return {"message": "User registered successfully"}

@app.post("/auth/login", response_model=Token)
async def login_user(user: UserLogin):
    """Authenticate user and return access token"""
    db_user = users_db.get(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return User(**current_user)

@app.post("/test/execute", response_model=TestExecutionResponse)
async def execute_test(
    request: TestExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Execute test automation workflow"""
    await check_api_quota(current_user)
    
    # Generate unique execution ID
    execution_id = str(uuid.uuid4())
    
    # Initialize execution status
    test_executions[execution_id] = TestExecutionStatus(
        execution_id=execution_id,
        status="pending",
        progress=0.0,
        current_phase="Initializing",
        start_time=datetime.utcnow()
    )
    
    # Start background task
    background_tasks.add_task(
        run_test_workflow,
        execution_id,
        request,
        current_user["username"]
    )
    
    # Update API usage
    users_db[current_user["username"]]["api_usage"] += 1
    
    return TestExecutionResponse(
        execution_id=execution_id,
        status="pending",
        message="Test execution started",
        estimated_duration=300  # 5 minutes estimate
    )

@app.get("/test/status/{execution_id}", response_model=TestExecutionStatus)
async def get_test_status(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get test execution status"""
    if execution_id not in test_executions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    return test_executions[execution_id]

@app.get("/test/results/{execution_id}")
async def get_test_results(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed test execution results"""
    if execution_id not in execution_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found"
        )
    
    return execution_results[execution_id]

@app.get("/test/executions", response_model=List[TestExecutionStatus])
async def list_test_executions(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """List user's test executions"""
    # In production, filter by user
    executions = list(test_executions.values())[offset:offset+limit]
    return executions

@app.get("/requirements/templates", response_model=List[str])
async def list_requirements_templates():
    """List available requirements templates"""
    templates = []
    for file in Path("..").glob("requirements_*.json"):
        templates.append(file.stem)
    return templates

@app.get("/requirements/template/{template_name}", response_model=RequirementsTemplate)
async def get_requirements_template(template_name: str):
    """Get a specific requirements template"""
    template_file = Path(f"../requirements_{template_name}.json")
    if not template_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    with open(template_file, 'r') as f:
        template_data = json.load(f)
    
    return RequirementsTemplate(**template_data)

@app.post("/requirements/validate")
async def validate_requirements(
    requirements: RequirementsTemplate,
    current_user: dict = Depends(get_current_user)
):
    """Validate requirements configuration"""
    # Perform validation logic
    validation_results = {
        "valid": True,
        "warnings": [],
        "errors": []
    }
    
    # Basic validation
    if not requirements.base_url.startswith(('http://', 'https://')):
        validation_results["errors"].append("Invalid URL format")
        validation_results["valid"] = False
    
    if len(requirements.test_scenarios) == 0:
        validation_results["warnings"].append("No test scenarios defined")
    
    return validation_results

# Background task functions
async def run_test_workflow(execution_id: str, request: TestExecutionRequest, username: str):
    """Background task to run the test workflow"""
    try:
        # Update status
        test_executions[execution_id].status = "running"
        test_executions[execution_id].current_phase = "Initializing workflow"
        test_executions[execution_id].progress = 0.1
        
        # Initialize workflow
        workflow = ProperMultiAgentWorkflow()
        
        # Update progress
        test_executions[execution_id].current_phase = "Running test generation"
        test_executions[execution_id].progress = 0.3
        
        # Execute workflow
        results = await workflow.run(
            url=request.url,
            name=request.name,
            headless=request.headless
        )
        
        # Update progress
        test_executions[execution_id].progress = 0.9
        test_executions[execution_id].current_phase = "Finalizing results"
        
        # Store results
        execution_results[execution_id] = results
        
        # Complete execution
        test_executions[execution_id].status = "completed"
        test_executions[execution_id].progress = 1.0
        test_executions[execution_id].current_phase = "Completed"
        test_executions[execution_id].end_time = datetime.utcnow()
        test_executions[execution_id].results = {
            "summary": {
                "total_tests": results.get("created_tests", {}).get("total_tests", 0),
                "execution_time": results.get("execution_results", {}).get("execution_time", 0),
                "success_rate": results.get("execution_results", {}).get("success_rate", 0)
            }
        }
        
        logger.info(f"Test execution {execution_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Test execution {execution_id} failed: {str(e)}")
        test_executions[execution_id].status = "failed"
        test_executions[execution_id].error = str(e)
        test_executions[execution_id].end_time = datetime.utcnow()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
