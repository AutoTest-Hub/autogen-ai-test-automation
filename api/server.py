"""
Enhanced API Server with SOC Compliance, Tenant Isolation, and Deployment Awareness
AI Test Automation SaaS Platform
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
from fastapi import FastAPI, HTTPException, Depends, Security, Request, Response, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext
import redis
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Import our secure database models
from database.models_secure import (
    DatabaseManager, SecurityManager, DeploymentMode,
    Customers, CustomerUsers, Applications, TestCreationRequests, TestExecutions,
    AuditLogs, SecurityEvents, DataAccessLogs,
    CustomerRepository, ApplicationRepository,
    get_database_config_from_env, init_database
)

# Import our enhanced agents
from agents.enhanced_discovery_agent import EnhancedDiscoveryAgent
from agents.integrated_test_generator import IntegratedTestGenerator
from agents.self_healing_agent import SelfHealingAgent
from agents.prioritization_agent import PrioritizationAgent
from agents.cross_browser_agent import CrossBrowserAgent
from agents.performance_agent import PerformanceAgent

# =====================================================
# CONFIGURATION AND SETUP
# =====================================================

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Deployment configuration
DEPLOYMENT_MODE = DeploymentMode(os.environ.get('DEPLOYMENT_MODE', 'SaaS'))
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# Initialize components
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
db_manager = init_database(DEPLOYMENT_MODE)
security_manager = SecurityManager()

# Redis for caching and rate limiting
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Rate limiting will be disabled.")
    redis_client = None

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# =====================================================
# PYDANTIC MODELS
# =====================================================

class UserLogin(BaseModel):
    email: str = Field(..., regex=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    password: str = Field(..., min_length=8)

class UserCreate(BaseModel):
    email: str = Field(..., regex=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)

class ApplicationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    url: str = Field(..., regex=r'^https?://.+')
    application_type: Optional[str] = Field(None, max_length=100)
    environment: str = Field('production', regex=r'^(development|staging|production)$')
    security_classification: str = Field('internal', regex=r'^(public|internal|confidential|restricted)$')
    data_sensitivity_level: str = Field('medium', regex=r'^(low|medium|high|critical)$')

class TestCreationRequest(BaseModel):
    application_id: uuid.UUID
    creation_method: str = Field(..., regex=r'^(requirements|test_cases|url_metadata|browser_recording)$')
    input_data: Dict[str, Any]
    configuration: Optional[Dict[str, Any]] = None
    data_classification: str = Field('internal', regex=r'^(public|internal|confidential|restricted)$')
    contains_pii: bool = False
    compliance_requirements: Optional[List[str]] = None

class TestExecutionRequest(BaseModel):
    application_id: uuid.UUID
    test_suite_id: Optional[uuid.UUID] = None
    execution_type: str = Field('manual', regex=r'^(manual|scheduled|api|webhook)$')
    environment: Optional[str] = Field(None, regex=r'^(development|staging|production)$')
    browser: Optional[str] = Field('chrome', regex=r'^(chrome|firefox|safari|edge)$')
    device_type: Optional[str] = Field('desktop', regex=r'^(desktop|mobile|tablet)$')
    execution_config: Optional[Dict[str, Any]] = None

class SecurityEventCreate(BaseModel):
    event_category: str = Field(..., regex=r'^(authentication|authorization|data_access|configuration_change|security_violation)$')
    severity: str = Field(..., regex=r'^(low|medium|high|critical)$')
    event_code: str = Field(..., max_length=50)
    description: str = Field(..., min_length=1)
    additional_context: Optional[Dict[str, Any]] = None

# =====================================================
# AUTHENTICATION AND AUTHORIZATION
# =====================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        customer_id: str = payload.get("customer_id")
        
        if user_id is None or customer_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        return {
            "user_id": uuid.UUID(user_id),
            "customer_id": uuid.UUID(customer_id),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def get_current_user(token_data: dict = Depends(verify_token), session: Session = Depends(lambda: db_manager.get_session())):
    """Get current authenticated user"""
    try:
        user = session.query(CustomerUsers).filter(
            CustomerUsers.id == token_data["user_id"],
            CustomerUsers.is_active == True,
            CustomerUsers.is_deleted == False
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Set customer context for RLS
        db_manager.set_customer_context(session, token_data["customer_id"])
        
        return user
    finally:
        session.close()

def check_permissions(required_permission: str):
    """Decorator to check user permissions"""
    def permission_checker(current_user: CustomerUsers = Depends(get_current_user)):
        user_permissions = current_user.permissions or {}
        if not user_permissions.get(required_permission, False) and current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return permission_checker

# =====================================================
# RATE LIMITING AND SECURITY MIDDLEWARE
# =====================================================

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    if redis_client is None:
        response = await call_next(request)
        return response
    
    # Get client IP
    client_ip = request.client.host
    
    # Get customer ID from token if available
    customer_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            customer_id = payload.get("customer_id")
        except:
            pass
    
    # Rate limiting key
    rate_limit_key = f"rate_limit:{customer_id or client_ip}:{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
    
    try:
        current_requests = redis_client.incr(rate_limit_key)
        if current_requests == 1:
            redis_client.expire(rate_limit_key, 60)  # 1 minute window
        
        # Check rate limits (adjust based on subscription plan)
        max_requests = 1000  # Default limit per minute
        if current_requests > max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
    except Exception as e:
        logger.warning(f"Rate limiting error: {e}")
    
    response = await call_next(request)
    return response

async def security_headers_middleware(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

async def audit_middleware(request: Request, call_next):
    """Audit logging middleware"""
    start_time = datetime.utcnow()
    
    # Get request info
    client_ip = request.client.host
    user_agent = request.headers.get("User-Agent", "")
    request_id = str(uuid.uuid4())
    
    # Add request ID to headers
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Log to audit system (async)
    asyncio.create_task(log_audit_event(
        event_type="api_request",
        resource_type="api_endpoint",
        action=f"{request.method} {request.url.path}",
        metadata={
            "request_id": request_id,
            "ip_address": client_ip,
            "user_agent": user_agent,
            "status_code": response.status_code,
            "duration_seconds": duration
        }
    ))
    
    # Update metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    request_duration.observe(duration)
    
    return response

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

async def log_audit_event(event_type: str, resource_type: str, action: str, 
                         customer_id: Optional[uuid.UUID] = None, 
                         user_id: Optional[uuid.UUID] = None,
                         metadata: Optional[Dict[str, Any]] = None):
    """Log audit event asynchronously"""
    try:
        session = db_manager.get_session()
        audit_log = AuditLogs(
            customer_id=customer_id,
            user_id=user_id,
            event_type=event_type,
            resource_type=resource_type,
            action=action,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        session.add(audit_log)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")

async def log_security_event(event_category: str, severity: str, event_code: str, 
                           description: str, customer_id: Optional[uuid.UUID] = None,
                           user_id: Optional[uuid.UUID] = None,
                           additional_context: Optional[Dict[str, Any]] = None):
    """Log security event asynchronously"""
    try:
        session = db_manager.get_session()
        security_event = SecurityEvents(
            customer_id=customer_id,
            user_id=user_id,
            event_category=event_category,
            severity=severity,
            event_code=event_code,
            description=description,
            additional_context=additional_context,
            detected_at=datetime.utcnow()
        )
        session.add(security_event)
        session.commit()
        session.close()
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

def check_ip_whitelist(request: Request) -> bool:
    """Check if IP is whitelisted (for OnPrem deployments)"""
    if DEPLOYMENT_MODE != DeploymentMode.ONPREM:
        return True
    
    # Implementation would check against IP whitelist table
    # For now, return True
    return True

# =====================================================
# FASTAPI APPLICATION SETUP
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info(f"Starting AI Test Automation API Server - {DEPLOYMENT_MODE.value} mode")
    
    # Initialize AI agents
    app.state.discovery_agent = EnhancedDiscoveryAgent()
    app.state.test_generator = IntegratedTestGenerator()
    app.state.self_healing_agent = SelfHealingAgent()
    app.state.prioritization_agent = PrioritizationAgent()
    app.state.cross_browser_agent = CrossBrowserAgent()
    app.state.performance_agent = PerformanceAgent()
    
    logger.info("AI agents initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Test Automation API Server")

# Create FastAPI app
app = FastAPI(
    title="AI Test Automation Platform API",
    description="Enterprise-grade AI-powered test automation platform with SOC 2 compliance",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(audit_middleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for production
if DEPLOYMENT_MODE == DeploymentMode.SAAS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.yourdomain.com", "localhost", "127.0.0.1"]
    )

# =====================================================
# API ENDPOINTS
# =====================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "deployment_mode": DEPLOYMENT_MODE.value,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# =====================================================
# AUTHENTICATION ENDPOINTS
# =====================================================

@app.post("/auth/login")
async def login(user_login: UserLogin, request: Request, background_tasks: BackgroundTasks):
    """User login endpoint"""
    session = db_manager.get_session()
    
    try:
        # Check IP whitelist for OnPrem
        if not check_ip_whitelist(request):
            raise HTTPException(status_code=403, detail="IP address not whitelisted")
        
        # Find user
        user = session.query(CustomerUsers).filter(
            CustomerUsers.email == user_login.email,
            CustomerUsers.is_active == True,
            CustomerUsers.is_deleted == False
        ).first()
        
        if not user or not pwd_context.verify(user_login.password, user.password_hash):
            # Log failed login attempt
            background_tasks.add_task(
                log_security_event,
                event_category="authentication",
                severity="medium",
                event_code="FAILED_LOGIN",
                description=f"Failed login attempt for email: {user_login.email}",
                additional_context={"ip_address": str(request.client.host)}
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(status_code=423, detail="Account is locked")
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = request.client.host
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "customer_id": str(user.customer_id),
                "email": user.email,
                "role": user.role
            },
            expires_delta=access_token_expires
        )
        
        session.commit()
        
        # Log successful login
        background_tasks.add_task(
            log_audit_event,
            event_type="authentication",
            resource_type="user_session",
            action="LOGIN_SUCCESS",
            customer_id=user.customer_id,
            user_id=user.id,
            metadata={"ip_address": str(request.client.host)}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
        }
        
    finally:
        session.close()

@app.post("/auth/register")
async def register(user_create: UserCreate, request: Request, background_tasks: BackgroundTasks):
    """User registration endpoint (SaaS only)"""
    if DEPLOYMENT_MODE == DeploymentMode.ONPREM:
        raise HTTPException(status_code=403, detail="Registration disabled in OnPrem mode")
    
    session = db_manager.get_session()
    
    try:
        # Check if user already exists
        existing_user = session.query(CustomerUsers).filter(
            CustomerUsers.email == user_create.email
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")
        
        # Create customer first
        customer = Customers(
            name=user_create.company_name or f"{user_create.first_name} {user_create.last_name}",
            email=user_create.email,
            company_name=user_create.company_name,
            industry=user_create.industry,
            subscription_status='trial'
        )
        session.add(customer)
        session.flush()  # Get customer ID
        
        # Create user
        hashed_password = pwd_context.hash(user_create.password)
        user = CustomerUsers(
            customer_id=customer.id,
            email=user_create.email,
            password_hash=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            role='admin'  # First user is admin
        )
        session.add(user)
        session.commit()
        
        # Log registration
        background_tasks.add_task(
            log_audit_event,
            event_type="authentication",
            resource_type="customer",
            action="REGISTRATION_SUCCESS",
            customer_id=customer.id,
            user_id=user.id,
            metadata={"ip_address": str(request.client.host)}
        )
        
        return {"message": "Registration successful", "customer_id": str(customer.id)}
        
    finally:
        session.close()

# =====================================================
# APPLICATION MANAGEMENT ENDPOINTS
# =====================================================

@app.post("/applications")
async def create_application(
    app_create: ApplicationCreate,
    current_user: CustomerUsers = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create new application"""
    session = db_manager.get_session()
    
    try:
        db_manager.set_customer_context(session, current_user.customer_id)
        
        application = Applications(
            customer_id=current_user.customer_id,
            name=app_create.name,
            description=app_create.description,
            url=app_create.url,
            application_type=app_create.application_type,
            environment=app_create.environment,
            security_classification=app_create.security_classification,
            data_sensitivity_level=app_create.data_sensitivity_level,
            created_by=current_user.id
        )
        
        session.add(application)
        session.commit()
        session.refresh(application)
        
        # Log application creation
        background_tasks.add_task(
            log_audit_event,
            event_type="data_modification",
            resource_type="application",
            action="CREATE",
            customer_id=current_user.customer_id,
            user_id=current_user.id,
            metadata={"application_id": str(application.id), "url": app_create.url}
        )
        
        return {
            "id": str(application.id),
            "name": application.name,
            "url": application.url,
            "status": "created"
        }
        
    finally:
        session.close()

@app.get("/applications")
async def get_applications(current_user: CustomerUsers = Depends(get_current_user)):
    """Get customer applications"""
    session = db_manager.get_session()
    
    try:
        db_manager.set_customer_context(session, current_user.customer_id)
        app_repo = ApplicationRepository(session)
        applications = app_repo.get_by_customer(current_user.customer_id)
        
        return [
            {
                "id": str(app.id),
                "name": app.name,
                "description": app.description,
                "url": app.url,
                "application_type": app.application_type,
                "environment": app.environment,
                "status": app.status,
                "created_at": app.created_at.isoformat()
            }
            for app in applications
        ]
        
    finally:
        session.close()

# =====================================================
# TEST CREATION ENDPOINTS
# =====================================================

@app.post("/test/create")
async def create_test(
    test_request: TestCreationRequest,
    current_user: CustomerUsers = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create test using AI agents"""
    session = db_manager.get_session()
    
    try:
        db_manager.set_customer_context(session, current_user.customer_id)
        
        # Verify application belongs to customer
        application = session.query(Applications).filter(
            Applications.id == test_request.application_id,
            Applications.customer_id == current_user.customer_id,
            Applications.is_deleted == False
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Create test creation request
        creation_request = TestCreationRequests(
            customer_id=current_user.customer_id,
            application_id=test_request.application_id,
            creation_method=test_request.creation_method,
            input_data=test_request.input_data,
            configuration=test_request.configuration,
            data_classification=test_request.data_classification,
            contains_pii=test_request.contains_pii,
            compliance_requirements=test_request.compliance_requirements,
            created_by=current_user.id
        )
        
        session.add(creation_request)
        session.commit()
        session.refresh(creation_request)
        
        # Start async test creation process
        background_tasks.add_task(
            process_test_creation,
            str(creation_request.id),
            str(current_user.customer_id)
        )
        
        return {
            "request_id": str(creation_request.id),
            "status": "processing",
            "estimated_completion": "5-10 minutes"
        }
        
    finally:
        session.close()

async def process_test_creation(request_id: str, customer_id: str):
    """Process test creation request using AI agents"""
    session = db_manager.get_session()
    
    try:
        db_manager.set_customer_context(session, uuid.UUID(customer_id))
        
        # Get the request
        request = session.query(TestCreationRequests).filter(
            TestCreationRequests.id == uuid.UUID(request_id)
        ).first()
        
        if not request:
            return
        
        # Update status
        request.status = 'processing'
        request.current_agent = 'Enhanced Discovery Agent'
        request.progress_percentage = 10
        session.commit()
        
        # Use AI agents to process the request
        # This is a simplified version - in production, this would be more complex
        
        # Discovery phase
        discovery_agent = app.state.discovery_agent
        discovery_results = await discovery_agent.analyze_application(request.input_data.get('url'))
        
        request.current_agent = 'Integrated Test Generator'
        request.progress_percentage = 50
        session.commit()
        
        # Test generation phase
        test_generator = app.state.test_generator
        test_results = await test_generator.generate_comprehensive_tests(
            request.input_data,
            discovery_results
        )
        
        request.current_agent = 'Quality Assurance'
        request.progress_percentage = 90
        session.commit()
        
        # Final processing
        request.status = 'completed'
        request.progress_percentage = 100
        request.current_agent = None
        session.commit()
        
        # Log completion
        await log_audit_event(
            event_type="data_modification",
            resource_type="test_creation_request",
            action="COMPLETED",
            customer_id=uuid.UUID(customer_id),
            metadata={"request_id": request_id, "tests_generated": len(test_results.get('tests', []))}
        )
        
    except Exception as e:
        logger.error(f"Test creation failed for request {request_id}: {e}")
        request.status = 'failed'
        session.commit()
    finally:
        session.close()

@app.get("/test/requests/{request_id}")
async def get_test_request_status(
    request_id: uuid.UUID,
    current_user: CustomerUsers = Depends(get_current_user)
):
    """Get test creation request status"""
    session = db_manager.get_session()
    
    try:
        db_manager.set_customer_context(session, current_user.customer_id)
        
        request = session.query(TestCreationRequests).filter(
            TestCreationRequests.id == request_id,
            TestCreationRequests.customer_id == current_user.customer_id
        ).first()
        
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        return {
            "id": str(request.id),
            "status": request.status,
            "progress_percentage": request.progress_percentage,
            "current_agent": request.current_agent,
            "created_at": request.created_at.isoformat(),
            "estimated_completion_time": request.estimated_completion_time.isoformat() if request.estimated_completion_time else None
        }
        
    finally:
        session.close()

# =====================================================
# SECURITY AND MONITORING ENDPOINTS
# =====================================================

@app.post("/security/events")
async def create_security_event(
    event: SecurityEventCreate,
    current_user: CustomerUsers = Depends(check_permissions("security_admin"))
):
    """Create security event (admin only)"""
    await log_security_event(
        event_category=event.event_category,
        severity=event.severity,
        event_code=event.event_code,
        description=event.description,
        customer_id=current_user.customer_id,
        user_id=current_user.id,
        additional_context=event.additional_context
    )
    
    return {"message": "Security event logged"}

@app.get("/audit/logs")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    current_user: CustomerUsers = Depends(check_permissions("audit_viewer"))
):
    """Get audit logs (admin only)"""
    session = db_manager.get_session()
    
    try:
        db_manager.set_customer_context(session, current_user.customer_id)
        
        logs = session.query(AuditLogs).filter(
            AuditLogs.customer_id == current_user.customer_id
        ).order_by(AuditLogs.timestamp.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                "id": str(log.id),
                "event_type": log.event_type,
                "resource_type": log.resource_type,
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),
                "metadata": log.metadata
            }
            for log in logs
        ]
        
    finally:
        session.close()

# =====================================================
# DEPLOYMENT-SPECIFIC ENDPOINTS
# =====================================================

@app.get("/system/info")
async def get_system_info(current_user: CustomerUsers = Depends(check_permissions("system_admin"))):
    """Get system information (admin only)"""
    return {
        "deployment_mode": DEPLOYMENT_MODE.value,
        "version": "1.0.0",
        "features_enabled": {
            "multi_tenant": DEPLOYMENT_MODE == DeploymentMode.SAAS,
            "billing": DEPLOYMENT_MODE == DeploymentMode.SAAS,
            "user_registration": DEPLOYMENT_MODE == DeploymentMode.SAAS,
            "ldap_integration": DEPLOYMENT_MODE == DeploymentMode.ONPREM,
            "custom_branding": DEPLOYMENT_MODE == DeploymentMode.ONPREM
        }
    }

if DEPLOYMENT_MODE == DeploymentMode.ONPREM:
    @app.get("/system/license")
    async def get_license_info(current_user: CustomerUsers = Depends(check_permissions("system_admin"))):
        """Get license information (OnPrem only)"""
        # Implementation would check license status
        return {
            "license_type": "enterprise",
            "expires_at": "2025-12-31",
            "features": ["unlimited_users", "unlimited_applications", "premium_support"]
        }

# =====================================================
# MAIN APPLICATION ENTRY POINT
# =====================================================

if __name__ == "__main__":
    uvicorn.run(
        "server_secure:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True
    )
