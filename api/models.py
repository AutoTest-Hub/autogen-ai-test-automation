"""
API Data Models and Schemas
===========================

Pydantic models for request/response validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class ExecutionStatus(str, Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    DISCOVERING = "discovering"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    EXECUTING = "executing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class ApplicationType(str, Enum):
    ECOMMERCE = "ecommerce"
    ENTERPRISE_HRMS = "enterprise_hrms"
    FINANCIAL_BANKING = "financial_banking"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    CUSTOM = "custom"

class TestPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Base Models
class BaseResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    is_active: bool = True
    api_quota: int = 100
    api_usage: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

# Test Configuration Models
class TestScenario(BaseModel):
    name: str
    description: str
    priority: TestPriority = TestPriority.MEDIUM
    steps: List[str]
    test_data: Optional[Dict[str, Any]] = None
    expected_elements: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None

class TestEnvironment(BaseModel):
    headless: bool = True
    timeout: int = Field(30000, ge=5000, le=300000)  # 5s to 5min
    viewport: Optional[Dict[str, int]] = None
    user_agent: Optional[str] = None
    locale: str = "en-US"

class RequirementsConfig(BaseModel):
    app_name: str = Field(..., min_length=1, max_length=100)
    base_url: str = Field(..., regex=r'^https?://.+')
    application_type: ApplicationType
    description: Optional[str] = None
    priority_areas: List[str] = Field(default_factory=list)
    test_scenarios: Dict[str, TestScenario] = Field(default_factory=dict)
    test_environment: TestEnvironment = Field(default_factory=TestEnvironment)
    business_rules: Optional[Dict[str, Any]] = None
    security_requirements: Optional[Dict[str, Any]] = None
    performance_requirements: Optional[Dict[str, Any]] = None
    integration_points: Optional[List[str]] = None

    @validator('base_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

# Test Execution Models
class TestExecutionRequest(BaseModel):
    url: str = Field(..., regex=r'^https?://.+')
    name: str = Field(..., min_length=1, max_length=100)
    headless: bool = True
    requirements_config: Optional[RequirementsConfig] = None
    custom_config: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    tags: Optional[List[str]] = None

    @validator('name')
    def validate_name(cls, v):
        # Remove special characters and spaces
        import re
        return re.sub(r'[^a-zA-Z0-9_-]', '_', v)

class TestExecutionResponse(BaseModel):
    execution_id: str
    status: ExecutionStatus
    message: str
    estimated_duration: int  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExecutionProgress(BaseModel):
    phase: str
    progress: float = Field(..., ge=0.0, le=1.0)
    message: str
    details: Optional[Dict[str, Any]] = None

class TestExecutionStatus(BaseModel):
    execution_id: str
    status: ExecutionStatus
    progress: ExecutionProgress
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    user: str
    request: TestExecutionRequest
    results_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Test Results Models
class TestFile(BaseModel):
    name: str
    path: str
    type: str  # test, page_object, configuration
    framework: str
    test_count: Optional[int] = None
    elements_used: Optional[int] = None

class DiscoveryResults(BaseModel):
    total_elements: int
    interactive_elements: int
    forms: int
    navigation_elements: int
    content_elements: int
    elements_by_type: Dict[str, int]
    page_structure: Dict[str, Any]

class ExecutionResults(BaseModel):
    total_tests: int
    passed: int
    failed: int
    skipped: int
    success_rate: float
    execution_time: float
    test_results: List[Dict[str, Any]]
    screenshots: List[str]
    logs: List[str]

class QualityMetrics(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=10.0)
    coverage_score: float = Field(..., ge=0.0, le=1.0)
    maintainability_score: float = Field(..., ge=0.0, le=1.0)
    reliability_score: float = Field(..., ge=0.0, le=1.0)
    performance_score: float = Field(..., ge=0.0, le=1.0)

class TestExecutionResults(BaseModel):
    execution_id: str
    summary: Dict[str, Any]
    generated_files: List[TestFile]
    discovery_results: DiscoveryResults
    execution_results: ExecutionResults
    quality_metrics: QualityMetrics
    reports: Dict[str, str]  # report_type -> file_path
    created_at: datetime
    completed_at: datetime

# Analytics Models
class ExecutionStats(BaseModel):
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration: float
    success_rate: float
    most_common_app_types: List[Dict[str, Any]]
    execution_trends: List[Dict[str, Any]]

class UserStats(BaseModel):
    total_users: int
    active_users: int
    api_usage_stats: Dict[str, Any]
    quota_utilization: Dict[str, Any]

# Webhook Models
class WebhookEvent(BaseModel):
    event_type: str  # execution.started, execution.completed, execution.failed
    execution_id: str
    timestamp: datetime
    data: Dict[str, Any]

# Template Models
class RequirementsTemplate(BaseModel):
    name: str
    display_name: str
    description: str
    application_type: ApplicationType
    template_config: RequirementsConfig
    created_at: datetime
    updated_at: datetime

# Validation Models
class ValidationResult(BaseModel):
    valid: bool
    score: float = Field(..., ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class URLValidation(BaseModel):
    url: str
    accessible: bool
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    detected_technologies: List[str] = Field(default_factory=list)
    application_type_suggestion: Optional[ApplicationType] = None

# Batch Operations
class BatchExecutionRequest(BaseModel):
    executions: List[TestExecutionRequest] = Field(..., max_items=10)
    parallel: bool = False

class BatchExecutionResponse(BaseModel):
    batch_id: str
    executions: List[TestExecutionResponse]
    status: str

# Export Models
class ExportRequest(BaseModel):
    execution_ids: List[str]
    format: str = Field("json", regex=r'^(json|csv|xlsx|pdf)$')
    include_files: bool = False

class ExportResponse(BaseModel):
    export_id: str
    download_url: str
    expires_at: datetime
