-- PostgreSQL 14+ Schema - Fixed Version (No Problematic Triggers)
-- SOC 2 Type II Compliant by Design

-- Enable required extensions (ignore errors if not available)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- SECURITY ROLES AND PERMISSIONS
-- =====================================================

-- Create application-specific roles with minimal privileges
DO $$ BEGIN
    CREATE ROLE app_read_only;
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE ROLE app_read_write;
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE ROLE app_admin;
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- Grant minimal required permissions
GRANT CONNECT ON DATABASE CURRENT TO app_read_only, app_read_write, app_admin;
GRANT USAGE ON SCHEMA public TO app_read_only, app_read_write, app_admin;

-- =====================================================
-- CUSTOMER & SUBSCRIPTION MANAGEMENT
-- =====================================================

-- Subscription plans with enhanced security metadata
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    max_users INTEGER DEFAULT 10,
    max_applications INTEGER DEFAULT 5,
    max_test_executions_monthly INTEGER DEFAULT 1000,
    
    -- Security and compliance features
    security_tier VARCHAR(50) DEFAULT 'standard',
    compliance_features JSONB DEFAULT '{}',
    audit_retention_days INTEGER DEFAULT 90,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customer organizations with enhanced security controls
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_plan_id UUID REFERENCES subscription_plans(id),
    
    -- Basic information
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    industry VARCHAR(100),
    
    -- Security and compliance
    data_classification VARCHAR(50) DEFAULT 'internal',
    compliance_requirements JSONB DEFAULT '[]',
    encryption_key_id UUID,
    
    -- Subscription and billing
    subscription_status VARCHAR(50) DEFAULT 'active',
    billing_email VARCHAR(255),
    
    -- Security metadata
    allowed_ip_ranges INET[],
    require_mfa BOOLEAN DEFAULT false,
    session_timeout_minutes INTEGER DEFAULT 480,
    
    -- Audit fields
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_data_classification CHECK (data_classification IN ('public', 'internal', 'confidential', 'restricted')),
    CONSTRAINT valid_subscription_status CHECK (subscription_status IN ('active', 'suspended', 'cancelled', 'trial'))
);

-- Customer users with enhanced authentication
CREATE TABLE IF NOT EXISTS customer_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Authentication
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    department VARCHAR(100),
    
    -- Security settings
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Session management
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    current_session_id VARCHAR(255),
    
    -- Audit fields
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_role CHECK (role IN ('admin', 'user', 'viewer', 'auditor')),
    UNIQUE(customer_id, email)
);

-- =====================================================
-- APPLICATION MANAGEMENT WITH SECURITY
-- =====================================================

-- Applications with enhanced security metadata
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Basic information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500) NOT NULL,
    application_type VARCHAR(100) NOT NULL,
    
    -- Security classification
    data_sensitivity_level VARCHAR(50) DEFAULT 'medium',
    contains_pii BOOLEAN DEFAULT false,
    compliance_tags JSONB DEFAULT '[]',
    
    -- Access controls
    allowed_ip_ranges INET[],
    requires_vpn BOOLEAN DEFAULT false,
    ssl_verification_enabled BOOLEAN DEFAULT true,
    
    -- Configuration
    configuration JSONB DEFAULT '{}',
    environment VARCHAR(50) DEFAULT 'production',
    
    -- Status and metadata
    status VARCHAR(50) DEFAULT 'active',
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_sensitivity CHECK (data_sensitivity_level IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'maintenance', 'archived'))
);

-- Application credentials with encryption
CREATE TABLE IF NOT EXISTS application_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Credential information
    credential_type VARCHAR(50) NOT NULL,
    username VARCHAR(255),
    encrypted_password TEXT,
    api_key_encrypted TEXT,
    
    -- Security metadata
    encryption_key_id UUID,
    last_rotated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rotation_frequency_days INTEGER DEFAULT 90,
    
    -- Access control
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_credential_type CHECK (credential_type IN ('basic_auth', 'api_key', 'oauth', 'certificate'))
);

-- =====================================================
-- ENCRYPTION AND SECURITY MANAGEMENT
-- =====================================================

-- Encryption keys management
CREATE TABLE IF NOT EXISTS encryption_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Key information
    key_name VARCHAR(255) NOT NULL,
    key_type VARCHAR(50) NOT NULL,
    encrypted_key_data TEXT NOT NULL,
    key_version INTEGER DEFAULT 1,
    
    -- Key lifecycle
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    rotated_at TIMESTAMP WITH TIME ZONE,
    
    -- Security metadata
    algorithm VARCHAR(50) DEFAULT 'AES-256',
    key_usage JSONB DEFAULT '[]',
    
    CONSTRAINT valid_key_type CHECK (key_type IN ('data_encryption', 'credential_encryption', 'signing')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'expired', 'compromised'))
);

-- =====================================================
-- AUDIT AND COMPLIANCE LOGGING
-- =====================================================

-- Comprehensive audit logs for SOC 2 compliance
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    user_id UUID REFERENCES customer_users(id),
    
    -- Event information
    event_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    action VARCHAR(50) NOT NULL,
    
    -- Event details
    old_values JSONB,
    new_values JSONB,
    metadata JSONB DEFAULT '{}',
    
    -- Context information
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_event_type CHECK (event_type IN ('authentication', 'authorization', 'data_modification', 'system_access', 'configuration_change')),
    CONSTRAINT valid_action CHECK (action IN ('create', 'read', 'update', 'delete', 'login', 'logout', 'failed_login', 'permission_change'))
);

-- Security events for monitoring and alerting
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    user_id UUID REFERENCES customer_users(id),
    
    -- Event classification
    event_category VARCHAR(50) NOT NULL,
    severity_level VARCHAR(20) NOT NULL,
    event_description TEXT NOT NULL,
    
    -- Technical details
    source_ip INET,
    affected_resource VARCHAR(255),
    detection_method VARCHAR(100),
    
    -- Response and resolution
    status VARCHAR(50) DEFAULT 'open',
    assigned_to UUID REFERENCES customer_users(id),
    resolution_notes TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Timing
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_category CHECK (event_category IN ('authentication_failure', 'unauthorized_access', 'data_breach', 'suspicious_activity', 'policy_violation')),
    CONSTRAINT valid_severity CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_status CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive'))
);

-- Data access logs for compliance tracking
CREATE TABLE IF NOT EXISTS data_access_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    user_id UUID NOT NULL REFERENCES customer_users(id),
    
    -- Access details
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    access_type VARCHAR(50) NOT NULL,
    data_classification VARCHAR(50),
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    
    -- Results
    access_granted BOOLEAN NOT NULL,
    denial_reason TEXT,
    
    -- Timing
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_access_type CHECK (access_type IN ('read', 'write', 'delete', 'export', 'print'))
);

-- =====================================================
-- TEST MANAGEMENT TABLES
-- =====================================================

-- Test creation requests tracking
CREATE TABLE IF NOT EXISTS test_creation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Request details
    application_url VARCHAR(500) NOT NULL,
    application_name VARCHAR(255) NOT NULL,
    application_type VARCHAR(100) NOT NULL,
    key_features TEXT,
    important_user_flows TEXT,
    
    -- Processing status
    status VARCHAR(50) DEFAULT 'pending',
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    generated_test_suite_id UUID,
    error_message TEXT,
    
    -- Audit
    requested_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

-- Test executions with enhanced security context
CREATE TABLE IF NOT EXISTS test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    
    -- Execution context
    execution_type VARCHAR(50) DEFAULT 'manual',
    environment VARCHAR(50) DEFAULT 'production',
    browser VARCHAR(50),
    device_type VARCHAR(50),
    execution_config JSONB,
    
    -- Security context
    executed_from_ip INET,
    security_scan_enabled BOOLEAN DEFAULT true,
    data_masking_enabled BOOLEAN DEFAULT true,
    
    -- Results
    status VARCHAR(50) DEFAULT 'pending',
    total_tests INTEGER,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    skipped_tests INTEGER DEFAULT 0,
    security_issues_found INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    duration_seconds INTEGER,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    triggered_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Customer and user indexes
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customer_users_customer_id ON customer_users(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_users_email ON customer_users(customer_id, email);

-- Application indexes
CREATE INDEX IF NOT EXISTS idx_applications_customer_id ON applications(customer_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

-- Audit and security indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_customer_id ON audit_logs(customer_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_security_events_customer_id ON security_events(customer_id);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity_level);

-- Test execution indexes
CREATE INDEX IF NOT EXISTS idx_test_executions_customer_id ON test_executions(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_executions_application_id ON test_executions(application_id);

-- =====================================================
-- GRANTS FOR APPLICATION ROLES
-- =====================================================

-- Grant permissions to application roles
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_read_write;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read_only;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_read_write;
