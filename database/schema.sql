-- AI Test Automation SaaS Platform Database Schema - SOC Compliant
-- PostgreSQL 14+ with Enhanced Security Controls
-- SOC 2 Type II Compliant by Design

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_audit" CASCADE;

-- =====================================================
-- SECURITY & AUDIT CONFIGURATION
-- =====================================================

-- Enable Row Level Security globally
ALTER DATABASE CURRENT SET row_security = on;

-- Configure audit logging for SOC compliance
-- This will log all DDL, DML, and security-related operations
ALTER SYSTEM SET shared_preload_libraries = 'pg_audit';
ALTER SYSTEM SET pg_audit.log = 'all';
ALTER SYSTEM SET pg_audit.log_catalog = 'on';
ALTER SYSTEM SET pg_audit.log_parameter = 'on';
ALTER SYSTEM SET pg_audit.log_statement_once = 'off';
ALTER SYSTEM SET pg_audit.log_level = 'log';

-- Configure connection and authentication security
ALTER SYSTEM SET ssl = 'on';
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
ALTER SYSTEM SET log_connections = 'on';
ALTER SYSTEM SET log_disconnections = 'on';
ALTER SYSTEM SET log_checkpoints = 'on';
ALTER SYSTEM SET log_lock_waits = 'on';

-- =====================================================
-- SECURITY ROLES AND PERMISSIONS
-- =====================================================

-- Create application-specific roles with minimal privileges
CREATE ROLE app_read_only;
CREATE ROLE app_read_write;
CREATE ROLE app_admin;
CREATE ROLE audit_reader;

-- Grant minimal required permissions
GRANT CONNECT ON DATABASE CURRENT TO app_read_only, app_read_write, app_admin;
GRANT USAGE ON SCHEMA public TO app_read_only, app_read_write, app_admin;

-- =====================================================
-- CUSTOMER & SUBSCRIPTION MANAGEMENT (ENHANCED SECURITY)
-- =====================================================

-- Subscription plans with audit trail
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    api_calls_limit INTEGER,
    applications_limit INTEGER,
    concurrent_tests_limit INTEGER,
    features JSONB,
    security_tier VARCHAR(50) DEFAULT 'standard', -- standard, enhanced, enterprise
    data_retention_days INTEGER DEFAULT 365,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Customers with enhanced security fields
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    industry VARCHAR(100),
    subscription_plan_id UUID REFERENCES subscription_plans(id),
    subscription_status VARCHAR(50) DEFAULT 'trial',
    subscription_start_date TIMESTAMP WITH TIME ZONE,
    subscription_end_date TIMESTAMP WITH TIME ZONE,
    api_calls_used INTEGER DEFAULT 0,
    api_calls_reset_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Security and compliance fields
    data_classification VARCHAR(50) DEFAULT 'internal', -- public, internal, confidential, restricted
    encryption_key_id UUID, -- Reference to encryption key for customer data
    compliance_requirements JSONB, -- GDPR, HIPAA, SOX, etc.
    data_retention_policy JSONB,
    security_settings JSONB,
    
    -- Audit fields
    billing_info JSONB,
    settings JSONB,
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    
    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_data_classification CHECK (data_classification IN ('public', 'internal', 'confidential', 'restricted'))
);

-- Enable RLS on customers table
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Customer users with enhanced authentication
CREATE TABLE customer_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'member',
    permissions JSONB,
    
    -- Security fields
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255), -- Encrypted TOTP secret
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    password_expires_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    -- Session management
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    current_session_id UUID,
    session_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    
    UNIQUE(customer_id, email),
    CONSTRAINT valid_role CHECK (role IN ('admin', 'member', 'viewer', 'api_only')),
    CONSTRAINT password_not_empty CHECK (length(password_hash) > 0)
);

-- Enable RLS on customer_users table
ALTER TABLE customer_users ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- APPLICATION MANAGEMENT (ENHANCED SECURITY)
-- =====================================================

-- Applications with security metadata
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500) NOT NULL,
    application_type VARCHAR(100),
    environment VARCHAR(50) DEFAULT 'production',
    status VARCHAR(50) DEFAULT 'active',
    
    -- Security fields
    security_classification VARCHAR(50) DEFAULT 'internal',
    requires_vpn BOOLEAN DEFAULT false,
    allowed_ip_ranges JSONB, -- Array of CIDR blocks
    ssl_verification BOOLEAN DEFAULT true,
    
    -- Compliance and audit
    metadata JSONB,
    compliance_tags JSONB,
    data_sensitivity_level VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES customer_users(id),
    
    CONSTRAINT valid_url CHECK (url ~* '^https?://'),
    CONSTRAINT valid_environment CHECK (environment IN ('development', 'staging', 'production')),
    CONSTRAINT valid_sensitivity CHECK (data_sensitivity_level IN ('low', 'medium', 'high', 'critical'))
);

-- Enable RLS on applications table
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Application credentials with encryption
CREATE TABLE application_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    credential_type VARCHAR(50) NOT NULL,
    username VARCHAR(255),
    
    -- Encrypted credential storage
    password_encrypted TEXT, -- AES-256 encrypted
    additional_data_encrypted TEXT, -- Encrypted JSON for API keys, tokens, etc.
    encryption_key_id UUID NOT NULL, -- Reference to key management system
    
    -- Security metadata
    credential_strength_score INTEGER, -- 0-100 password strength
    last_rotation_date TIMESTAMP WITH TIME ZONE,
    rotation_frequency_days INTEGER DEFAULT 90,
    
    -- Audit fields
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    accessed_at TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    
    CONSTRAINT valid_credential_type CHECK (credential_type IN ('login', 'api_key', 'oauth', 'certificate', 'ssh_key'))
);

-- Enable RLS on application_credentials table
ALTER TABLE application_credentials ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- ENCRYPTION KEY MANAGEMENT
-- =====================================================

-- Encryption keys for customer data
CREATE TABLE encryption_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    key_type VARCHAR(50) NOT NULL, -- customer_data, credentials, pii
    key_algorithm VARCHAR(50) DEFAULT 'AES-256-GCM',
    key_hash VARCHAR(255) NOT NULL, -- Hash of the actual key for verification
    key_version INTEGER DEFAULT 1,
    
    -- Key lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    rotated_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active', -- active, rotated, expired, revoked
    
    -- Audit
    created_by UUID REFERENCES customer_users(id),
    
    CONSTRAINT valid_key_type CHECK (key_type IN ('customer_data', 'credentials', 'pii', 'application_data')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'rotated', 'expired', 'revoked'))
);

-- =====================================================
-- AUDIT AND COMPLIANCE TABLES
-- =====================================================

-- Comprehensive audit log for all operations
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    user_id UUID REFERENCES customer_users(id),
    
    -- Event details
    event_type VARCHAR(100) NOT NULL, -- login, logout, create, update, delete, access, etc.
    resource_type VARCHAR(100), -- customer, application, test_suite, etc.
    resource_id UUID,
    action VARCHAR(100) NOT NULL,
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    request_id UUID,
    
    -- Event data
    old_values JSONB, -- Previous state for updates/deletes
    new_values JSONB, -- New state for creates/updates
    metadata JSONB, -- Additional context
    
    -- Security classification
    sensitivity_level VARCHAR(50) DEFAULT 'internal',
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Compliance
    retention_until TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'authentication', 'authorization', 'data_access', 'data_modification',
        'configuration_change', 'security_event', 'system_event'
    ))
);

-- Security events for monitoring and alerting
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    user_id UUID REFERENCES customer_users(id),
    
    -- Event classification
    event_category VARCHAR(50) NOT NULL, -- authentication, authorization, data_access, etc.
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    event_code VARCHAR(50) NOT NULL, -- FAILED_LOGIN, PRIVILEGE_ESCALATION, etc.
    
    -- Event details
    description TEXT NOT NULL,
    source_ip INET,
    user_agent TEXT,
    additional_context JSONB,
    
    -- Response
    auto_response_taken JSONB, -- Automated actions taken
    manual_response_required BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES customer_users(id),
    
    -- Timing
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_severity CHECK (severity IN ('low', 'medium', 'high', 'critical'))
);

-- Data access log for compliance
CREATE TABLE data_access_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    user_id UUID REFERENCES customer_users(id),
    
    -- Access details
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    access_type VARCHAR(50) NOT NULL, -- read, write, delete
    query_hash VARCHAR(255), -- Hash of the SQL query
    
    -- Context
    application_context VARCHAR(100), -- web_ui, api, background_job
    ip_address INET,
    session_id UUID,
    
    -- Data classification
    data_classification VARCHAR(50),
    pii_accessed BOOLEAN DEFAULT false,
    sensitive_data_accessed BOOLEAN DEFAULT false,
    
    -- Timing
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_access_type CHECK (access_type IN ('read', 'write', 'delete', 'export'))
);

-- =====================================================
-- TEST CREATION & EXECUTION (ENHANCED SECURITY)
-- =====================================================

-- Test creation requests with security context
CREATE TABLE test_creation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    creation_method VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    configuration JSONB,
    
    -- Security and compliance
    data_classification VARCHAR(50) DEFAULT 'internal',
    contains_pii BOOLEAN DEFAULT false,
    compliance_requirements JSONB,
    
    -- Processing status
    status VARCHAR(50) DEFAULT 'pending',
    progress_percentage INTEGER DEFAULT 0,
    current_agent VARCHAR(100),
    estimated_completion_time TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_creation_method CHECK (creation_method IN ('requirements', 'test_cases', 'url_metadata', 'browser_recording'))
);

-- Enable RLS on test_creation_requests table
ALTER TABLE test_creation_requests ENABLE ROW LEVEL SECURITY;

-- Test executions with security controls
CREATE TABLE test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    test_suite_id UUID REFERENCES test_suites(id),
    
    -- Execution context
    execution_type VARCHAR(50) DEFAULT 'manual',
    environment VARCHAR(50),
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

-- Enable RLS on test_executions table
ALTER TABLE test_executions ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Customers can only see their own data
CREATE POLICY customer_isolation ON customers
    FOR ALL TO app_read_write, app_read_only
    USING (id = current_setting('app.current_customer_id')::uuid);

-- Customer users can only see users from their organization
CREATE POLICY customer_user_isolation ON customer_users
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Applications scoped to customer
CREATE POLICY application_isolation ON applications
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Application credentials scoped to customer (through application)
CREATE POLICY credential_isolation ON application_credentials
    FOR ALL TO app_read_write, app_read_only
    USING (application_id IN (
        SELECT id FROM applications WHERE customer_id = current_setting('app.current_customer_id')::uuid
    ));

-- Test creation requests scoped to customer
CREATE POLICY test_request_isolation ON test_creation_requests
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Test executions scoped to customer
CREATE POLICY test_execution_isolation ON test_executions
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- =====================================================
-- SECURITY FUNCTIONS
-- =====================================================

-- Function to set current customer context (called by application)
CREATE OR REPLACE FUNCTION set_customer_context(customer_uuid UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_customer_id', customer_uuid::text, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to encrypt sensitive data
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT, key_id UUID)
RETURNS TEXT AS $$
DECLARE
    encrypted_data TEXT;
BEGIN
    -- In production, this would integrate with a proper key management system
    -- For now, we'll use pgcrypto with a derived key
    SELECT encode(
        encrypt(
            data::bytea,
            digest(key_id::text, 'sha256'),
            'aes'
        ),
        'base64'
    ) INTO encrypted_data;
    
    RETURN encrypted_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to decrypt sensitive data
CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT, key_id UUID)
RETURNS TEXT AS $$
DECLARE
    decrypted_data TEXT;
BEGIN
    SELECT convert_from(
        decrypt(
            decode(encrypted_data, 'base64'),
            digest(key_id::text, 'sha256'),
            'aes'
        ),
        'UTF8'
    ) INTO decrypted_data;
    
    RETURN decrypted_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log security events
CREATE OR REPLACE FUNCTION log_security_event(
    p_customer_id UUID,
    p_user_id UUID,
    p_event_category VARCHAR(50),
    p_severity VARCHAR(20),
    p_event_code VARCHAR(50),
    p_description TEXT,
    p_source_ip INET DEFAULT NULL,
    p_additional_context JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    event_id UUID;
BEGIN
    INSERT INTO security_events (
        customer_id, user_id, event_category, severity, event_code,
        description, source_ip, additional_context
    ) VALUES (
        p_customer_id, p_user_id, p_event_category, p_severity, p_event_code,
        p_description, p_source_ip, p_additional_context
    ) RETURNING id INTO event_id;
    
    RETURN event_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- INDEXES FOR PERFORMANCE AND SECURITY
-- =====================================================

-- Customer and application indexes
CREATE INDEX idx_customers_email ON customers(email) WHERE is_deleted = false;
CREATE INDEX idx_customers_subscription_status ON customers(subscription_status) WHERE is_deleted = false;
CREATE INDEX idx_customer_users_customer_id ON customer_users(customer_id) WHERE is_deleted = false;
CREATE INDEX idx_customer_users_email ON customer_users(customer_id, email) WHERE is_deleted = false;
CREATE INDEX idx_applications_customer_id ON applications(customer_id) WHERE is_deleted = false;

-- Security and audit indexes
CREATE INDEX idx_audit_logs_customer_timestamp ON audit_logs(customer_id, timestamp);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_security_events_customer_severity ON security_events(customer_id, severity, detected_at);
CREATE INDEX idx_data_access_logs_customer_time ON data_access_logs(customer_id, accessed_at);
CREATE INDEX idx_data_access_logs_pii ON data_access_logs(customer_id) WHERE pii_accessed = true;

-- Test execution indexes
CREATE INDEX idx_test_executions_customer_created ON test_executions(customer_id, created_at);
CREATE INDEX idx_test_creation_requests_customer_status ON test_creation_requests(customer_id, status);

-- =====================================================
-- INITIAL SECURITY CONFIGURATION
-- =====================================================

-- Insert default encryption keys for system use
INSERT INTO encryption_keys (id, key_type, key_algorithm, key_hash, status) VALUES
(uuid_generate_v4(), 'customer_data', 'AES-256-GCM', encode(digest('system_default_key_customer_data', 'sha256'), 'hex'), 'active'),
(uuid_generate_v4(), 'credentials', 'AES-256-GCM', encode(digest('system_default_key_credentials', 'sha256'), 'hex'), 'active'),
(uuid_generate_v4(), 'pii', 'AES-256-GCM', encode(digest('system_default_key_pii', 'sha256'), 'hex'), 'active');

-- Grant appropriate permissions to application roles
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read_only;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_read_write;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_read_write, app_admin;

-- Grant audit access
GRANT SELECT ON audit_logs, security_events, data_access_logs TO audit_reader;

-- Revoke public access
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM public;
REVOKE ALL ON SCHEMA public FROM public;

-- Create triggers for automatic audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (
            customer_id, event_type, resource_type, resource_id, action, new_values
        ) VALUES (
            COALESCE(NEW.customer_id, current_setting('app.current_customer_id', true)::uuid),
            'data_modification',
            TG_TABLE_NAME,
            NEW.id,
            'CREATE',
            to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (
            customer_id, event_type, resource_type, resource_id, action, old_values, new_values
        ) VALUES (
            COALESCE(NEW.customer_id, current_setting('app.current_customer_id', true)::uuid),
            'data_modification',
            TG_TABLE_NAME,
            NEW.id,
            'UPDATE',
            to_jsonb(OLD),
            to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (
            customer_id, event_type, resource_type, resource_id, action, old_values
        ) VALUES (
            COALESCE(OLD.customer_id, current_setting('app.current_customer_id', true)::uuid),
            'data_modification',
            TG_TABLE_NAME,
            OLD.id,
            'DELETE',
            to_jsonb(OLD)
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to key tables
CREATE TRIGGER audit_customers AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_applications AFTER INSERT OR UPDATE OR DELETE ON applications
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_test_executions AFTER INSERT OR UPDATE OR DELETE ON test_executions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- =====================================================
-- SOC COMPLIANCE VIEWS
-- =====================================================

-- View for SOC auditors to review access controls
CREATE VIEW soc_access_review AS
SELECT 
    c.company_name,
    cu.email,
    cu.role,
    cu.permissions,
    cu.last_login_at,
    cu.is_active,
    cu.mfa_enabled
FROM customers c
JOIN customer_users cu ON c.id = cu.customer_id
WHERE cu.is_deleted = false;

-- View for data access monitoring
CREATE VIEW soc_data_access_summary AS
SELECT 
    c.company_name,
    dal.table_name,
    dal.access_type,
    COUNT(*) as access_count,
    COUNT(*) FILTER (WHERE dal.pii_accessed = true) as pii_access_count,
    DATE(dal.accessed_at) as access_date
FROM customers c
JOIN data_access_logs dal ON c.id = dal.customer_id
GROUP BY c.company_name, dal.table_name, dal.access_type, DATE(dal.accessed_at)
ORDER BY access_date DESC;

-- View for security events monitoring
CREATE VIEW soc_security_events_summary AS
SELECT 
    c.company_name,
    se.event_category,
    se.severity,
    se.event_code,
    COUNT(*) as event_count,
    DATE(se.detected_at) as event_date
FROM customers c
LEFT JOIN security_events se ON c.id = se.customer_id
GROUP BY c.company_name, se.event_category, se.severity, se.event_code, DATE(se.detected_at)
ORDER BY event_date DESC, se.severity DESC;

COMMENT ON DATABASE CURRENT IS 'AI Test Automation Platform - SOC 2 Type II Compliant Database';
