"""
Enhanced Database Models with SOC Compliance and Hybrid Deployment Support
AI Test Automation SaaS Platform
"""

import os
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass

from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, JSON, DECIMAL, Date, ForeignKey, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from sqlalchemy.pool import QueuePool
from cryptography.fernet import Fernet
import bcrypt

# Base configuration
Base = declarative_base()

class DeploymentMode(Enum):
    SAAS = "SaaS"
    ONPREM = "OnPrem"

class SecurityTier(Enum):
    STANDARD = "standard"
    ENHANCED = "enhanced"
    ENTERPRISE = "enterprise"

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class DatabaseConfig:
    """Database configuration for different deployment modes"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    deployment_mode: DeploymentMode = DeploymentMode.SAAS

class SecurityManager:
    """Handles encryption, hashing, and security operations"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())
        self.fernet = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

# =====================================================
# CORE SYSTEM TABLES
# =====================================================

class SystemSettings(Base):
    """System-wide configuration settings"""
    __tablename__ = 'system_settings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(JSONB, nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_system_settings_key', 'setting_key'),
    )

class EncryptionKeys(Base):
    """Encryption key management for customer data"""
    __tablename__ = 'encryption_keys'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=True)
    key_type = Column(String(50), nullable=False)
    key_algorithm = Column(String(50), default='AES-256-GCM')
    key_hash = Column(String(255), nullable=False)
    key_version = Column(Integer, default=1)
    status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    activated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    rotated_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    
    __table_args__ = (
        CheckConstraint("key_type IN ('customer_data', 'credentials', 'pii', 'application_data')", name='valid_key_type'),
        CheckConstraint("status IN ('active', 'rotated', 'expired', 'revoked')", name='valid_key_status'),
        Index('idx_encryption_keys_customer', 'customer_id'),
        Index('idx_encryption_keys_type_status', 'key_type', 'status'),
    )

# =====================================================
# SUBSCRIPTION AND CUSTOMER MANAGEMENT
# =====================================================

class SubscriptionPlans(Base):
    """Subscription plans for SaaS deployment"""
    __tablename__ = 'subscription_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price_monthly = Column(DECIMAL(10, 2))
    price_yearly = Column(DECIMAL(10, 2))
    api_calls_limit = Column(Integer)
    applications_limit = Column(Integer)
    concurrent_tests_limit = Column(Integer)
    features = Column(JSONB)
    security_tier = Column(String(50), default='standard')
    data_retention_days = Column(Integer, default=365)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    customers = relationship("Customers", back_populates="subscription_plan")
    
    __table_args__ = (
        CheckConstraint("security_tier IN ('standard', 'enhanced', 'enterprise')", name='valid_security_tier'),
        Index('idx_subscription_plans_active', 'is_active'),
    )

class Customers(Base):
    """Customer organizations"""
    __tablename__ = 'customers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    company_name = Column(String(255))
    industry = Column(String(100))
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey('subscription_plans.id'))
    subscription_status = Column(String(50), default='trial')
    subscription_start_date = Column(DateTime(timezone=True))
    subscription_end_date = Column(DateTime(timezone=True))
    api_calls_used = Column(Integer, default=0)
    api_calls_reset_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Security and compliance fields
    data_classification = Column(String(50), default='internal')
    encryption_key_id = Column(UUID(as_uuid=True), ForeignKey('encryption_keys.id'))
    compliance_requirements = Column(JSONB)
    data_retention_policy = Column(JSONB)
    security_settings = Column(JSONB)
    
    # Audit fields
    billing_info = Column(JSONB)
    settings = Column(JSONB)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    subscription_plan = relationship("SubscriptionPlans", back_populates="customers")
    users = relationship("CustomerUsers", back_populates="customer")
    applications = relationship("Applications", back_populates="customer")
    test_creation_requests = relationship("TestCreationRequests", back_populates="customer")
    test_executions = relationship("TestExecutions", back_populates="customer")
    
    __table_args__ = (
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='valid_email'),
        CheckConstraint("data_classification IN ('public', 'internal', 'confidential', 'restricted')", name='valid_data_classification'),
        Index('idx_customers_email', 'email'),
        Index('idx_customers_subscription_status', 'subscription_status'),
        Index('idx_customers_active', 'is_active', 'is_deleted'),
    )

class CustomerUsers(Base):
    """Users within customer organizations"""
    __tablename__ = 'customer_users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default='member')
    permissions = Column(JSONB)
    
    # Security fields
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))  # Encrypted TOTP secret
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())
    password_expires_at = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # Session management
    last_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(INET)
    current_session_id = Column(UUID(as_uuid=True))
    session_expires_at = Column(DateTime(timezone=True))
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    customer = relationship("Customers", back_populates="users")
    
    __table_args__ = (
        UniqueConstraint('customer_id', 'email', name='unique_customer_email'),
        CheckConstraint("role IN ('admin', 'member', 'viewer', 'api_only')", name='valid_role'),
        CheckConstraint("length(password_hash) > 0", name='password_not_empty'),
        Index('idx_customer_users_customer_id', 'customer_id'),
        Index('idx_customer_users_email', 'customer_id', 'email'),
        Index('idx_customer_users_active', 'is_active', 'is_deleted'),
    )

# =====================================================
# APPLICATION MANAGEMENT
# =====================================================

class Applications(Base):
    """Customer applications under test"""
    __tablename__ = 'applications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(500), nullable=False)
    application_type = Column(String(100))
    environment = Column(String(50), default='production')
    status = Column(String(50), default='active')
    
    # Security fields
    security_classification = Column(String(50), default='internal')
    requires_vpn = Column(Boolean, default=False)
    allowed_ip_ranges = Column(JSONB)
    ssl_verification = Column(Boolean, default=True)
    
    # Compliance and audit
    metadata = Column(JSONB)
    compliance_tags = Column(JSONB)
    data_sensitivity_level = Column(String(50), default='medium')
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    
    # Relationships
    customer = relationship("Customers", back_populates="applications")
    credentials = relationship("ApplicationCredentials", back_populates="application")
    test_creation_requests = relationship("TestCreationRequests", back_populates="application")
    test_executions = relationship("TestExecutions", back_populates="application")
    
    __table_args__ = (
        CheckConstraint("url ~* '^https?://'", name='valid_url'),
        CheckConstraint("environment IN ('development', 'staging', 'production')", name='valid_environment'),
        CheckConstraint("data_sensitivity_level IN ('low', 'medium', 'high', 'critical')", name='valid_sensitivity'),
        Index('idx_applications_customer_id', 'customer_id'),
        Index('idx_applications_type', 'application_type'),
        Index('idx_applications_active', 'is_deleted'),
    )

class ApplicationCredentials(Base):
    """Encrypted credentials for applications"""
    __tablename__ = 'application_credentials'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    credential_type = Column(String(50), nullable=False)
    username = Column(String(255))
    
    # Encrypted credential storage
    password_encrypted = Column(Text)
    additional_data_encrypted = Column(Text)
    encryption_key_id = Column(UUID(as_uuid=True), ForeignKey('encryption_keys.id'), nullable=False)
    
    # Security metadata
    credential_strength_score = Column(Integer)
    last_rotation_date = Column(DateTime(timezone=True))
    rotation_frequency_days = Column(Integer, default=90)
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    accessed_at = Column(DateTime(timezone=True))
    access_count = Column(Integer, default=0)
    
    # Relationships
    application = relationship("Applications", back_populates="credentials")
    
    __table_args__ = (
        CheckConstraint("credential_type IN ('login', 'api_key', 'oauth', 'certificate', 'ssh_key')", name='valid_credential_type'),
        Index('idx_application_credentials_app_id', 'application_id'),
        Index('idx_application_credentials_type', 'credential_type'),
    )

# =====================================================
# TEST CREATION AND EXECUTION
# =====================================================

class TestCreationRequests(Base):
    """Test creation requests with security context"""
    __tablename__ = 'test_creation_requests'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    creation_method = Column(String(50), nullable=False)
    input_data = Column(JSONB, nullable=False)
    configuration = Column(JSONB)
    
    # Security and compliance
    data_classification = Column(String(50), default='internal')
    contains_pii = Column(Boolean, default=False)
    compliance_requirements = Column(JSONB)
    
    # Processing status
    status = Column(String(50), default='pending')
    progress_percentage = Column(Integer, default=0)
    current_agent = Column(String(100))
    estimated_completion_time = Column(DateTime(timezone=True))
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customers", back_populates="test_creation_requests")
    application = relationship("Applications", back_populates="test_creation_requests")
    
    __table_args__ = (
        CheckConstraint("creation_method IN ('requirements', 'test_cases', 'url_metadata', 'browser_recording')", name='valid_creation_method'),
        Index('idx_test_creation_requests_customer', 'customer_id', 'status'),
        Index('idx_test_creation_requests_app', 'application_id'),
    )

class TestExecutions(Base):
    """Test executions with security controls"""
    __tablename__ = 'test_executions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    test_suite_id = Column(UUID(as_uuid=True))  # Reference to test_suites table
    
    # Execution context
    execution_type = Column(String(50), default='manual')
    environment = Column(String(50))
    browser = Column(String(50))
    device_type = Column(String(50))
    execution_config = Column(JSONB)
    
    # Security context
    executed_from_ip = Column(INET)
    security_scan_enabled = Column(Boolean, default=True)
    data_masking_enabled = Column(Boolean, default=True)
    
    # Results
    status = Column(String(50), default='pending')
    total_tests = Column(Integer)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    security_issues_found = Column(Integer, default=0)
    success_rate = Column(DECIMAL(5, 2))
    duration_seconds = Column(Integer)
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Audit
    triggered_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customers", back_populates="test_executions")
    application = relationship("Applications", back_populates="test_executions")
    
    __table_args__ = (
        Index('idx_test_executions_customer_created', 'customer_id', 'created_at'),
        Index('idx_test_executions_app', 'application_id'),
        Index('idx_test_executions_status', 'status'),
    )

# =====================================================
# AUDIT AND COMPLIANCE
# =====================================================

class AuditLogs(Base):
    """Comprehensive audit log for all operations"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    
    # Event details
    event_type = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    action = Column(String(100), nullable=False)
    
    # Request context
    ip_address = Column(INET)
    user_agent = Column(Text)
    session_id = Column(UUID(as_uuid=True))
    request_id = Column(UUID(as_uuid=True))
    
    # Event data
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    metadata = Column(JSONB)
    
    # Security classification
    sensitivity_level = Column(String(50), default='internal')
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Compliance
    retention_until = Column(DateTime(timezone=True))
    
    __table_args__ = (
        CheckConstraint("event_type IN ('authentication', 'authorization', 'data_access', 'data_modification', 'configuration_change', 'security_event', 'system_event')", name='valid_event_type'),
        Index('idx_audit_logs_customer_timestamp', 'customer_id', 'timestamp'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_event_type', 'event_type', 'timestamp'),
    )

class SecurityEvents(Base):
    """Security events for monitoring and alerting"""
    __tablename__ = 'security_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    
    # Event classification
    event_category = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    event_code = Column(String(50), nullable=False)
    
    # Event details
    description = Column(Text, nullable=False)
    source_ip = Column(INET)
    user_agent = Column(Text)
    additional_context = Column(JSONB)
    
    # Response
    auto_response_taken = Column(JSONB)
    manual_response_required = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    
    # Timing
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name='valid_severity'),
        Index('idx_security_events_customer_severity', 'customer_id', 'severity', 'detected_at'),
        Index('idx_security_events_category', 'event_category', 'detected_at'),
    )

class DataAccessLogs(Base):
    """Data access log for compliance"""
    __tablename__ = 'data_access_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('customer_users.id'))
    
    # Access details
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True))
    access_type = Column(String(50), nullable=False)
    query_hash = Column(String(255))
    
    # Context
    application_context = Column(String(100))
    ip_address = Column(INET)
    session_id = Column(UUID(as_uuid=True))
    
    # Data classification
    data_classification = Column(String(50))
    pii_accessed = Column(Boolean, default=False)
    sensitive_data_accessed = Column(Boolean, default=False)
    
    # Timing
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("access_type IN ('read', 'write', 'delete', 'export')", name='valid_access_type'),
        Index('idx_data_access_logs_customer_time', 'customer_id', 'accessed_at'),
        Index('idx_data_access_logs_pii', 'customer_id', 'pii_accessed'),
        Index('idx_data_access_logs_table', 'table_name', 'accessed_at'),
    )

# =====================================================
# DATABASE CONNECTION AND SESSION MANAGEMENT
# =====================================================

class DatabaseManager:
    """Manages database connections and sessions with security controls"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.security_manager = SecurityManager()
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup database engine with security configurations"""
        connection_string = (
            f"postgresql://{self.config.username}:{self.config.password}@"
            f"{self.config.host}:{self.config.port}/{self.config.database}"
            f"?sslmode={self.config.ssl_mode}"
        )
        
        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            echo=self.config.echo,
            # Security settings
            connect_args={
                "sslmode": self.config.ssl_mode,
                "application_name": f"ai_test_automation_{self.config.deployment_mode.value.lower()}",
                "options": "-c default_transaction_isolation=read_committed"
            }
        )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session with security context"""
        session = self.SessionLocal()
        return session
    
    def set_customer_context(self, session: Session, customer_id: uuid.UUID):
        """Set customer context for row-level security"""
        session.execute(f"SELECT set_config('app.current_customer_id', '{customer_id}', true)")
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables (use with caution)"""
        Base.metadata.drop_all(bind=self.engine)

# =====================================================
# REPOSITORY PATTERN FOR DATA ACCESS
# =====================================================

class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, session: Session, model_class):
        self.session = session
        self.model_class = model_class
    
    def create(self, **kwargs) -> Any:
        """Create new record"""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def get_by_id(self, id: uuid.UUID) -> Optional[Any]:
        """Get record by ID"""
        return self.session.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Any]:
        """Get all records with pagination"""
        return self.session.query(self.model_class).offset(offset).limit(limit).all()
    
    def update(self, id: uuid.UUID, **kwargs) -> Optional[Any]:
        """Update record by ID"""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(instance)
        return instance
    
    def delete(self, id: uuid.UUID) -> bool:
        """Soft delete record by ID"""
        instance = self.get_by_id(id)
        if instance:
            instance.is_deleted = True
            instance.deleted_at = datetime.utcnow()
            self.session.commit()
            return True
        return False

class CustomerRepository(BaseRepository):
    """Repository for customer operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Customers)
    
    def get_by_email(self, email: str) -> Optional[Customers]:
        """Get customer by email"""
        return self.session.query(Customers).filter(
            Customers.email == email,
            Customers.is_deleted == False
        ).first()
    
    def get_active_customers(self) -> List[Customers]:
        """Get all active customers"""
        return self.session.query(Customers).filter(
            Customers.is_active == True,
            Customers.is_deleted == False
        ).all()

class ApplicationRepository(BaseRepository):
    """Repository for application operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Applications)
    
    def get_by_customer(self, customer_id: uuid.UUID) -> List[Applications]:
        """Get applications by customer"""
        return self.session.query(Applications).filter(
            Applications.customer_id == customer_id,
            Applications.is_deleted == False
        ).all()
    
    def get_by_url(self, url: str) -> Optional[Applications]:
        """Get application by URL"""
        return self.session.query(Applications).filter(
            Applications.url == url,
            Applications.is_deleted == False
        ).first()

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_database_config_from_env(deployment_mode: DeploymentMode = DeploymentMode.SAAS) -> DatabaseConfig:
    """Get database configuration from environment variables"""
    return DatabaseConfig(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', '5432')),
        database=os.environ.get('DB_NAME', 'ai_test_automation'),
        username=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'password'),
        ssl_mode=os.environ.get('DB_SSL_MODE', 'require'),
        pool_size=int(os.environ.get('DB_POOL_SIZE', '20')),
        max_overflow=int(os.environ.get('DB_MAX_OVERFLOW', '30')),
        deployment_mode=deployment_mode
    )

def init_database(deployment_mode: DeploymentMode = DeploymentMode.SAAS) -> DatabaseManager:
    """Initialize database with proper configuration"""
    config = get_database_config_from_env(deployment_mode)
    db_manager = DatabaseManager(config)
    db_manager.create_tables()
    return db_manager

# Export main classes and functions
__all__ = [
    'Base', 'DatabaseManager', 'SecurityManager', 'DeploymentMode', 'SecurityTier', 'DataClassification',
    'SystemSettings', 'EncryptionKeys', 'SubscriptionPlans', 'Customers', 'CustomerUsers',
    'Applications', 'ApplicationCredentials', 'TestCreationRequests', 'TestExecutions',
    'AuditLogs', 'SecurityEvents', 'DataAccessLogs',
    'BaseRepository', 'CustomerRepository', 'ApplicationRepository',
    'get_database_config_from_env', 'init_database'
]
