"""
Database models for AI Test Automation SaaS Platform
Using SQLAlchemy ORM with PostgreSQL
"""

from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, DECIMAL, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from datetime import datetime
import uuid
import os

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/ai_test_automation')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =====================================================
# CUSTOMER & SUBSCRIPTION MODELS
# =====================================================

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price_monthly = Column(DECIMAL(10, 2))
    price_yearly = Column(DECIMAL(10, 2))
    api_calls_limit = Column(Integer)
    applications_limit = Column(Integer)
    concurrent_tests_limit = Column(Integer)
    features = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customers = relationship("Customer", back_populates="subscription_plan")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    company_name = Column(String(255))
    industry = Column(String(100))
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey('subscription_plans.id'))
    subscription_status = Column(String(50), default='trial')
    subscription_start_date = Column(DateTime)
    subscription_end_date = Column(DateTime)
    api_calls_used = Column(Integer, default=0)
    api_calls_reset_date = Column(DateTime, default=datetime.utcnow)
    billing_info = Column(JSONB)
    settings = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription_plan = relationship("SubscriptionPlan", back_populates="customers")
    users = relationship("CustomerUser", back_populates="customer")
    applications = relationship("Application", back_populates="customer")
    test_creation_requests = relationship("TestCreationRequest", back_populates="customer")
    test_executions = relationship("TestExecution", back_populates="customer")

class CustomerUser(Base):
    __tablename__ = "customer_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default='member')
    permissions = Column(JSONB)
    last_login_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="users")

# =====================================================
# APPLICATION MODELS
# =====================================================

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(500), nullable=False)
    application_type = Column(String(100))
    environment = Column(String(50), default='production')
    status = Column(String(50), default='active')
    metadata = Column(JSONB)
    created_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="applications")
    credentials = relationship("ApplicationCredential", back_populates="application")
    discoveries = relationship("ApplicationDiscovery", back_populates="application")
    test_creation_requests = relationship("TestCreationRequest", back_populates="application")
    test_suites = relationship("TestSuite", back_populates="application")

class ApplicationCredential(Base):
    __tablename__ = "application_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    credential_type = Column(String(50), nullable=False)
    username = Column(String(255))
    password_encrypted = Column(Text)
    additional_data = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="credentials")

class ApplicationDiscovery(Base):
    __tablename__ = "application_discoveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    discovery_type = Column(String(50))
    elements_found = Column(Integer)
    pages_analyzed = Column(Integer)
    user_flows_identified = Column(Integer)
    technologies_detected = Column(JSONB)
    security_findings = Column(JSONB)
    performance_metrics = Column(JSONB)
    discovery_data = Column(JSONB)
    status = Column(String(50), default='completed')
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="discoveries")

# =====================================================
# TEST CREATION MODELS
# =====================================================

class TestCreationRequest(Base):
    __tablename__ = "test_creation_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    creation_method = Column(String(50), nullable=False)
    input_data = Column(JSONB, nullable=False)
    configuration = Column(JSONB)
    status = Column(String(50), default='pending')
    progress_percentage = Column(Integer, default=0)
    current_agent = Column(String(100))
    estimated_completion_time = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="test_creation_requests")
    application = relationship("Application", back_populates="test_creation_requests")
    agent_activities = relationship("AgentActivity", back_populates="test_creation_request")
    test_suites = relationship("TestSuite", back_populates="test_creation_request")

class AgentActivity(Base):
    __tablename__ = "agent_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_creation_request_id = Column(UUID(as_uuid=True), ForeignKey('test_creation_requests.id'))
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)
    activity_type = Column(String(50), nullable=False)
    message = Column(Text)
    progress_percentage = Column(Integer)
    metadata = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_creation_request = relationship("TestCreationRequest", back_populates="agent_activities")

class TestSuite(Base):
    __tablename__ = "test_suites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_creation_request_id = Column(UUID(as_uuid=True), ForeignKey('test_creation_requests.id'))
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    test_type = Column(String(100))
    priority = Column(String(50))
    coverage_level = Column(String(50))
    estimated_duration_minutes = Column(Integer)
    test_scenarios_count = Column(Integer)
    automation_code = Column(Text)
    configuration = Column(JSONB)
    status = Column(String(50), default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_creation_request = relationship("TestCreationRequest", back_populates="test_suites")
    application = relationship("Application", back_populates="test_suites")
    test_cases = relationship("TestCase", back_populates="test_suite")

class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_suite_id = Column(UUID(as_uuid=True), ForeignKey('test_suites.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    test_steps = Column(JSONB)
    expected_results = Column(JSONB)
    test_data = Column(JSONB)
    tags = Column(JSONB)
    automation_code = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_suite = relationship("TestSuite", back_populates="test_cases")

# =====================================================
# TEST EXECUTION MODELS
# =====================================================

class TestExecution(Base):
    __tablename__ = "test_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    test_suite_id = Column(UUID(as_uuid=True), ForeignKey('test_suites.id'))
    execution_type = Column(String(50), default='manual')
    environment = Column(String(50))
    browser = Column(String(50))
    device_type = Column(String(50))
    execution_config = Column(JSONB)
    status = Column(String(50), default='pending')
    total_tests = Column(Integer)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    success_rate = Column(DECIMAL(5, 2))
    duration_seconds = Column(Integer)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="test_executions")
    test_results = relationship("TestResult", back_populates="test_execution")

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_execution_id = Column(UUID(as_uuid=True), ForeignKey('test_executions.id'), nullable=False)
    test_case_id = Column(UUID(as_uuid=True), ForeignKey('test_cases.id'))
    test_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    duration_seconds = Column(DECIMAL(10, 3))
    error_message = Column(Text)
    stack_trace = Column(Text)
    screenshots = Column(JSONB)
    logs = Column(JSONB)
    performance_metrics = Column(JSONB)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_execution = relationship("TestExecution", back_populates="test_results")

# =====================================================
# ANALYTICS MODELS
# =====================================================

class CustomerAnalytics(Base):
    __tablename__ = "customer_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    metric_date = Column(DateTime, nullable=False)
    total_executions = Column(Integer, default=0)
    total_tests_run = Column(Integer, default=0)
    total_tests_passed = Column(Integer, default=0)
    total_tests_failed = Column(Integer, default=0)
    average_success_rate = Column(DECIMAL(5, 2))
    total_duration_minutes = Column(Integer, default=0)
    api_calls_used = Column(Integer, default=0)
    applications_tested = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables"""
    Base.metadata.drop_all(bind=engine)

# Database initialization
if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")
