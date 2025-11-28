-- =====================================================
-- AI Test Automation Platform - Complete Database Setup
-- Single file for local development and production
-- Includes all 21 tables, security, and sample data
-- =====================================================

-- Enable required extensions (skip if not available)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- SECURITY ROLES AND PERMISSIONS
-- =====================================================

-- Create application roles
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_read_only') THEN
        CREATE ROLE app_read_only;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_read_write') THEN
        CREATE ROLE app_read_write;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_admin') THEN
        CREATE ROLE app_admin;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'audit_reader') THEN
        CREATE ROLE audit_reader;
    END IF;
END
$$;

-- Grant app_user the necessary roles
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
        GRANT app_read_write TO app_user;
        GRANT app_admin TO app_user;
    END IF;
END
$$;

-- =====================================================
-- CORE TABLES (21 TABLES TOTAL)
-- =====================================================

-- 1. CUSTOMERS TABLE
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    subscription_status VARCHAR(20) DEFAULT 'active',
    max_test_suites INTEGER DEFAULT 10,
    max_concurrent_executions INTEGER DEFAULT 3,
    api_rate_limit INTEGER DEFAULT 1000,
    storage_limit_gb INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    billing_email VARCHAR(255),
    billing_address TEXT,
    tax_id VARCHAR(100),
    contract_start_date DATE,
    contract_end_date DATE,
    auto_renewal BOOLEAN DEFAULT true
);

-- 2. CUSTOMER_USERS TABLE
CREATE TABLE IF NOT EXISTS customer_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'member',
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    password_expires_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. APPLICATIONS TABLE
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500) NOT NULL,
    application_type VARCHAR(50) DEFAULT 'web',
    framework VARCHAR(100),
    authentication_method VARCHAR(50),
    environment VARCHAR(50) DEFAULT 'staging',
    health_check_url VARCHAR(500),
    api_base_url VARCHAR(500),
    documentation_url VARCHAR(500),
    repository_url VARCHAR(500),
    contact_email VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    tags JSONB DEFAULT '[]',
    configuration JSONB DEFAULT '{}'
);

-- 4. TEST_SUITES TABLE
CREATE TABLE IF NOT EXISTS test_suites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(50) NOT NULL DEFAULT 'functional',
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'running', 'completed', 'failed', 'archived')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    environment VARCHAR(50) DEFAULT 'staging',
    browser VARCHAR(50) DEFAULT 'chromium',
    viewport_width INTEGER DEFAULT 1920,
    viewport_height INTEGER DEFAULT 1080,
    timeout_seconds INTEGER DEFAULT 30,
    retry_count INTEGER DEFAULT 1,
    parallel_execution BOOLEAN DEFAULT false,
    schedule_cron VARCHAR(100),
    is_scheduled BOOLEAN DEFAULT false,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    tags JSONB DEFAULT '[]',
    configuration JSONB DEFAULT '{}'
);

-- 5. TEST_CASES TABLE
CREATE TABLE IF NOT EXISTS test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    test_suite_id UUID NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_steps JSONB DEFAULT '[]',
    expected_results JSONB DEFAULT '[]',
    test_data JSONB DEFAULT '{}',
    preconditions TEXT,
    postconditions TEXT,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'passed', 'failed', 'skipped', 'blocked')),
    execution_order INTEGER DEFAULT 0,
    timeout_seconds INTEGER DEFAULT 30,
    retry_count INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    tags JSONB DEFAULT '[]',
    -- File storage columns for hybrid architecture
    test_file_path VARCHAR(1000),
    config_file_path VARCHAR(1000),
    generated_from_intent TEXT,
    generation_model VARCHAR(50),
    code_confidence_score DECIMAL(3,2),
    file_checksum VARCHAR(64),
    file_size_bytes BIGINT,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    avg_execution_time_ms INTEGER DEFAULT 0,
    last_executed_at TIMESTAMP WITH TIME ZONE,
    file_created_at TIMESTAMP WITH TIME ZONE,
    file_updated_at TIMESTAMP WITH TIME ZONE
);

-- 6. TEST_EXECUTION_RESULTS TABLE
CREATE TABLE IF NOT EXISTS test_execution_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    execution_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'passed', 'failed', 'skipped', 'error', 'timeout')),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    error_message TEXT,
    error_stack_trace TEXT,
    screenshot_path VARCHAR(500),
    video_path VARCHAR(500),
    logs TEXT,
    browser_info JSONB DEFAULT '{}',
    environment_info JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_by UUID REFERENCES customer_users(id),
    retry_attempt INTEGER DEFAULT 0,
    assertion_results JSONB DEFAULT '[]',
    step_results JSONB DEFAULT '[]'
);

-- 7. AGENT_JOBS TABLE
CREATE TABLE IF NOT EXISTS agent_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    test_suite_id UUID REFERENCES test_suites(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    priority INTEGER DEFAULT 5,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    progress_percentage INTEGER DEFAULT 0,
    estimated_duration_seconds INTEGER,
    actual_duration_seconds INTEGER,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    assigned_worker VARCHAR(100),
    worker_metadata JSONB DEFAULT '{}'
);

-- 8. AGENT_ACTIVITIES TABLE
CREATE TABLE IF NOT EXISTS agent_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    agent_job_id UUID NOT NULL REFERENCES agent_jobs(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('discovery', 'generation', 'validation', 'execution', 'analysis', 'reporting')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    message TEXT,
    details JSONB DEFAULT '{}',
    progress_percentage INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sequence_order INTEGER DEFAULT 0,
    parent_activity_id UUID REFERENCES agent_activities(id),
    metadata JSONB DEFAULT '{}'
);

-- 9. TEMPLATES TABLE
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    content JSONB NOT NULL DEFAULT '{}',
    variables JSONB DEFAULT '[]',
    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    version VARCHAR(20) DEFAULT '1.0.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    tags JSONB DEFAULT '[]'
);

-- 10. INTEGRATIONS TABLE
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    integration_type VARCHAR(50) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}',
    credentials JSONB DEFAULT '{}',
    webhook_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    metadata JSONB DEFAULT '{}'
);

-- 11. NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    user_id UUID REFERENCES customer_users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'unread' CHECK (status IN ('unread', 'read', 'archived')),
    action_url VARCHAR(500),
    action_label VARCHAR(100),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    channels JSONB DEFAULT '["web"]'
);

-- 12. AUDIT_LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    user_id UUID REFERENCES customer_users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('authentication', 'authorization', 'data_access', 'data_modification', 'configuration_change', 'security_event', 'system_event')),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical'))
);

-- 13. API_KEYS TABLE
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES customer_users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(20) NOT NULL,
    permissions JSONB DEFAULT '[]',
    rate_limit INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_whitelist JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

-- 14. WEBHOOKS TABLE
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    events JSONB NOT NULL DEFAULT '[]',
    headers JSONB DEFAULT '{}',
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    retry_count INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    metadata JSONB DEFAULT '{}'
);

-- 15. WEBHOOK_DELIVERIES TABLE
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    response_headers JSONB,
    delivery_attempts INTEGER DEFAULT 1,
    delivered_at TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT,
    duration_ms INTEGER
);

-- 16. FEATURE_FLAGS TABLE
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_enabled BOOLEAN DEFAULT false,
    rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
    target_customers JSONB DEFAULT '[]',
    target_users JSONB DEFAULT '[]',
    conditions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    metadata JSONB DEFAULT '{}'
);

-- 17. SYSTEM_METRICS TABLE
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(20),
    dimensions JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    aggregation_period VARCHAR(20) DEFAULT 'instant',
    metadata JSONB DEFAULT '{}'
);

-- 18. BILLING_USAGE TABLE
CREATE TABLE IF NOT EXISTS billing_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    usage_type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,4) DEFAULT 0.0000,
    total_cost DECIMAL(10,2) DEFAULT 0.00,
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    resource_id UUID,
    resource_type VARCHAR(50)
);

-- 19. ENVIRONMENTS TABLE
CREATE TABLE IF NOT EXISTS environments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    base_url VARCHAR(500) NOT NULL,
    environment_type VARCHAR(50) DEFAULT 'staging' CHECK (environment_type IN ('development', 'staging', 'production', 'testing')),
    configuration JSONB DEFAULT '{}',
    credentials JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    health_check_url VARCHAR(500),
    deployment_info JSONB DEFAULT '{}'
);

-- 20. SCHEDULES TABLE
CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    test_suite_id UUID NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cron_expression VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT true,
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    run_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_minutes INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    notification_settings JSONB DEFAULT '{}',
    execution_settings JSONB DEFAULT '{}'
);

-- 21. SCHEDULE_EXECUTIONS TABLE
CREATE TABLE IF NOT EXISTS schedule_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
    execution_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('scheduled', 'running', 'completed', 'failed', 'cancelled', 'timeout')),
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    test_results JSONB DEFAULT '{}',
    error_message TEXT,
    retry_attempt INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Customer-based indexes
CREATE INDEX IF NOT EXISTS idx_customer_users_customer_id ON customer_users(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_users_email ON customer_users(email);
CREATE INDEX IF NOT EXISTS idx_applications_customer_id ON applications(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_suites_customer_id ON test_suites(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_customer_id ON test_cases(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_suite_id ON test_cases(test_suite_id);
CREATE INDEX IF NOT EXISTS idx_test_execution_results_customer_id ON test_execution_results(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_execution_results_case_id ON test_execution_results(test_case_id);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_customer_id ON agent_jobs(customer_id);
CREATE INDEX IF NOT EXISTS idx_agent_activities_customer_id ON agent_activities(customer_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_customer_id ON audit_logs(customer_id);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_test_suites_status ON test_suites(status);
CREATE INDEX IF NOT EXISTS idx_test_cases_status ON test_cases(status);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_status ON agent_jobs(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_test_execution_results_executed_at ON test_execution_results(executed_at);

-- File storage indexes
CREATE INDEX IF NOT EXISTS idx_test_cases_file_path ON test_cases(test_file_path) WHERE test_file_path IS NOT NULL;

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on customer-specific tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_suites ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_execution_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Customer isolation policies
CREATE POLICY customer_isolation ON customers
    FOR ALL TO app_read_write, app_read_only
    USING (id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY customer_users_isolation ON customer_users
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY applications_isolation ON applications
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY test_suites_isolation ON test_suites
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY test_cases_isolation ON test_cases
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY test_execution_results_isolation ON test_execution_results
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY agent_jobs_isolation ON agent_jobs
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY agent_activities_isolation ON agent_activities
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

CREATE POLICY audit_logs_isolation ON audit_logs
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('session.current_customer_id')::uuid);

-- =====================================================
-- AUDIT TRIGGER FUNCTIONS
-- =====================================================

-- Generic audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (
            customer_id,
            event_type,
            action,
            resource_type,
            resource_id,
            new_values,
            created_at
        ) VALUES (
            COALESCE(NEW.customer_id, current_setting('session.current_customer_id', true)::uuid),
            'data_modification',
            'INSERT',
            TG_TABLE_NAME,
            NEW.id,
            to_jsonb(NEW),
            NOW()
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (
            customer_id,
            event_type,
            action,
            resource_type,
            resource_id,
            old_values,
            new_values,
            created_at
        ) VALUES (
            COALESCE(NEW.customer_id, current_setting('session.current_customer_id', true)::uuid),
            'data_modification',
            'UPDATE',
            TG_TABLE_NAME,
            NEW.id,
            to_jsonb(OLD),
            to_jsonb(NEW),
            NOW()
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (
            customer_id,
            event_type,
            action,
            resource_type,
            resource_id,
            old_values,
            created_at
        ) VALUES (
            COALESCE(OLD.customer_id, current_setting('session.current_customer_id', true)::uuid),
            'data_modification',
            'DELETE',
            TG_TABLE_NAME,
            OLD.id,
            to_jsonb(OLD),
            NOW()
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit triggers for key tables
CREATE TRIGGER audit_test_suites_trigger
    AFTER INSERT OR UPDATE OR DELETE ON test_suites
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_test_cases_trigger
    AFTER INSERT OR UPDATE OR DELETE ON test_cases
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- =====================================================
-- SAMPLE DATA FOR DEVELOPMENT
-- =====================================================

-- Insert demo customer
INSERT INTO customers (
    id, name, company_name, email, subscription_plan, is_active
) VALUES (
    'e6f663ec-c7cc-47b1-ab85-0a38d5df19af',
    'Demo Customer',
    'Demo Company Inc.',
    'demo@example.com',
    'enterprise',
    true
) ON CONFLICT (id) DO NOTHING;

-- Insert demo users
INSERT INTO customer_users (
    id, customer_id, email, password_hash, first_name, last_name, role, is_active
) VALUES 
(
    '643e8c64-0314-4e3d-adcc-983d120e7ef5',
    'e6f663ec-c7cc-47b1-ab85-0a38d5df19af',
    'tester@demo.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJK9.K5jO', -- password: demo123
    'Demo',
    'Tester',
    'admin',
    true
),
(
    '3f467a89-3951-4708-bde3-03e536eefe9b',
    'e6f663ec-c7cc-47b1-ab85-0a38d5df19af',
    'demo',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJK9.K5jO', -- password: demo123
    'Demo',
    'User',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert demo applications
INSERT INTO applications (
    id, customer_id, name, description, url, application_type, created_by
) VALUES 
(
    'fcde4dae-5b3a-47a6-89a1-69f04a1e1073',
    'e6f663ec-c7cc-47b1-ab85-0a38d5df19af',
    'HRMS Demo',
    'Human Resource Management System Demo',
    'https://hrms-demo.example.com',
    'web',
    '643e8c64-0314-4e3d-adcc-983d120e7ef5'
),
(
    '1cf21994-e597-4eba-b464-8c6abd306ef3',
    'e6f663ec-c7cc-47b1-ab85-0a38d5df19af',
    'E-commerce Demo',
    'E-commerce Platform Demo',
    'https://ecommerce-demo.example.com',
    'web',
    '643e8c64-0314-4e3d-adcc-983d120e7ef5'
),
(
    '56915756-5f7d-4d8e-b9e3-417de8265d0a',
    'e6f663ec-c7cc-47b1-ab85-0a38d5df19af',
    'HRMS Demo Platform',
    'Advanced HRMS Demo Platform',
    'https://hrms-platform-demo.example.com',
    'web',
    '643e8c64-0314-4e3d-adcc-983d120e7ef5'
) ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- PERMISSIONS AND GRANTS
-- =====================================================

-- Grant permissions to application roles
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_read_write;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read_only;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_read_write, app_read_only;

-- Grant admin permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_admin;

-- Audit reader permissions
GRANT SELECT ON audit_logs TO audit_reader;

-- =====================================================
-- UTILITY VIEWS FOR REPORTING
-- =====================================================

-- Test suite summary view
CREATE OR REPLACE VIEW test_suite_summary AS
SELECT 
    ts.id,
    ts.name,
    ts.customer_id,
    ts.status,
    ts.test_type,
    a.name as application_name,
    COUNT(tc.id) as total_test_cases,
    COUNT(CASE WHEN tc.status = 'passed' THEN 1 END) as passed_cases,
    COUNT(CASE WHEN tc.status = 'failed' THEN 1 END) as failed_cases,
    ts.created_at,
    ts.updated_at
FROM test_suites ts
LEFT JOIN applications a ON ts.application_id = a.id
LEFT JOIN test_cases tc ON ts.id = tc.test_suite_id
GROUP BY ts.id, ts.name, ts.customer_id, ts.status, ts.test_type, a.name, ts.created_at, ts.updated_at;

-- Customer usage summary view
CREATE OR REPLACE VIEW customer_usage_summary AS
SELECT 
    c.id,
    c.name,
    c.company_name,
    COUNT(DISTINCT ts.id) as total_test_suites,
    COUNT(DISTINCT tc.id) as total_test_cases,
    COUNT(DISTINCT ter.id) as total_executions,
    c.max_test_suites,
    c.max_concurrent_executions,
    c.created_at
FROM customers c
LEFT JOIN test_suites ts ON c.id = ts.customer_id
LEFT JOIN test_cases tc ON ts.id = tc.test_suite_id
LEFT JOIN test_execution_results ter ON tc.id = ter.test_case_id
GROUP BY c.id, c.name, c.company_name, c.max_test_suites, c.max_concurrent_executions, c.created_at;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ AI Test Automation Platform database setup completed successfully!';
    RAISE NOTICE '📊 Created 21 tables with proper security and sample data';
    RAISE NOTICE '🔐 Row Level Security enabled for multi-tenant isolation';
    RAISE NOTICE '📝 Audit logging configured for compliance';
    RAISE NOTICE '👤 Demo user: demo / demo123';
    RAISE NOTICE '🏢 Demo customer: e6f663ec-c7cc-47b1-ab85-0a38d5df19af';
END
$$;
