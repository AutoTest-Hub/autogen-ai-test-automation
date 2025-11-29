-- Missing Tables for AI Test Automation Platform
-- PostgreSQL Schema Completion

-- =====================================================
-- TEST MANAGEMENT TABLES
-- =====================================================

-- Test suites for organizing test collections
CREATE TABLE IF NOT EXISTS test_suites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) DEFAULT 'functional',
    status VARCHAR(50) DEFAULT 'draft',
    
    -- Test configuration
    configuration JSONB,
    test_data JSONB,
    expected_results JSONB,
    
    -- Execution metadata
    total_test_cases INTEGER DEFAULT 0,
    passed_test_cases INTEGER DEFAULT 0,
    failed_test_cases INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Security and compliance
    data_classification VARCHAR(50) DEFAULT 'internal',
    contains_pii BOOLEAN DEFAULT false,
    
    -- Audit fields
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES customer_users(id),
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_type CHECK (type IN ('functional', 'performance', 'security', 'accessibility', 'api')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'active', 'running', 'completed', 'failed', 'archived'))
);

-- Enable RLS on test_suites table
ALTER TABLE test_suites ENABLE ROW LEVEL SECURITY;

-- Individual test cases within test suites
CREATE TABLE IF NOT EXISTS test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite_id UUID NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Test case details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(50) DEFAULT 'functional',
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Test steps and data
    test_steps JSONB,
    test_data JSONB,
    expected_result TEXT,
    
    -- Execution results
    status VARCHAR(50) DEFAULT 'pending',
    actual_result TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,
    screenshot_path VARCHAR(500),
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'passed', 'failed', 'skipped', 'blocked'))
);

-- Enable RLS on test_cases table
ALTER TABLE test_cases ENABLE ROW LEVEL SECURITY;

-- Test executions for tracking test runs
CREATE TABLE IF NOT EXISTS test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    test_suite_id UUID REFERENCES test_suites(id) ON DELETE CASCADE,
    
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
    total_tests INTEGER DEFAULT 0,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    skipped_tests INTEGER DEFAULT 0,
    security_issues_found INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    duration_seconds INTEGER,
    
    -- Execution details
    execution_log JSONB,
    error_details JSONB,
    performance_metrics JSONB,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    triggered_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_execution_type CHECK (execution_type IN ('manual', 'scheduled', 'api', 'ci_cd')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout'))
);

-- Enable RLS on test_executions table
ALTER TABLE test_executions ENABLE ROW LEVEL SECURITY;

-- Agent jobs for tracking AI agent activities
CREATE TABLE IF NOT EXISTS agent_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    test_suite_id UUID REFERENCES test_suites(id) ON DELETE CASCADE,
    
    -- Job details
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    progress_percentage INTEGER DEFAULT 0,
    current_agent VARCHAR(100),
    
    -- Job configuration
    input_data JSONB,
    configuration JSONB,
    
    -- Results
    output_data JSONB,
    error_details JSONB,
    
    -- Timing
    estimated_completion_time TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_job_type CHECK (job_type IN ('test_creation', 'test_execution', 'analysis', 'optimization')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- Enable RLS on agent_jobs table
ALTER TABLE agent_jobs ENABLE ROW LEVEL SECURITY;

-- Agent job activities for detailed progress tracking
CREATE TABLE IF NOT EXISTS agent_job_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES agent_jobs(id) ON DELETE CASCADE,
    
    -- Activity details
    agent_name VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    progress_percentage INTEGER,
    message TEXT,
    
    -- Activity data
    input_data JSONB,
    output_data JSONB,
    metadata JSONB,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_activity_type CHECK (activity_type IN ('discovery', 'analysis', 'generation', 'validation', 'optimization')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped'))
);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES FOR NEW TABLES
-- =====================================================

-- Test suites isolation by customer
CREATE POLICY customer_test_suites_isolation ON test_suites
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Test cases isolation by customer
CREATE POLICY customer_test_cases_isolation ON test_cases
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Test executions isolation by customer
CREATE POLICY customer_test_executions_isolation ON test_executions
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Agent jobs isolation by customer
CREATE POLICY customer_agent_jobs_isolation ON agent_jobs
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Test suites indexes
CREATE INDEX IF NOT EXISTS idx_test_suites_customer_id ON test_suites(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_suites_application_id ON test_suites(application_id);
CREATE INDEX IF NOT EXISTS idx_test_suites_status ON test_suites(status);
CREATE INDEX IF NOT EXISTS idx_test_suites_created_at ON test_suites(created_at);

-- Test cases indexes
CREATE INDEX IF NOT EXISTS idx_test_cases_suite_id ON test_cases(test_suite_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_customer_id ON test_cases(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_status ON test_cases(status);

-- Test executions indexes
CREATE INDEX IF NOT EXISTS idx_test_executions_customer_id ON test_executions(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_executions_suite_id ON test_executions(test_suite_id);
CREATE INDEX IF NOT EXISTS idx_test_executions_status ON test_executions(status);
CREATE INDEX IF NOT EXISTS idx_test_executions_created_at ON test_executions(created_at);

-- Agent jobs indexes
CREATE INDEX IF NOT EXISTS idx_agent_jobs_customer_id ON agent_jobs(customer_id);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_application_id ON agent_jobs(application_id);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_status ON agent_jobs(status);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_created_at ON agent_jobs(created_at);

-- Agent activities indexes
CREATE INDEX IF NOT EXISTS idx_agent_activities_job_id ON agent_job_activities(job_id);
CREATE INDEX IF NOT EXISTS idx_agent_activities_created_at ON agent_job_activities(created_at);

-- =====================================================
-- SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample test suites (will be created by the application)
-- This is handled by the database_postgres.py initialization function

-- =====================================================
-- GRANTS FOR APPLICATION ROLES
-- =====================================================

-- Grant permissions to application roles
GRANT SELECT, INSERT, UPDATE, DELETE ON test_suites TO app_read_write;
GRANT SELECT ON test_suites TO app_read_only;

GRANT SELECT, INSERT, UPDATE, DELETE ON test_cases TO app_read_write;
GRANT SELECT ON test_cases TO app_read_only;

GRANT SELECT, INSERT, UPDATE, DELETE ON test_executions TO app_read_write;
GRANT SELECT ON test_executions TO app_read_only;

GRANT SELECT, INSERT, UPDATE, DELETE ON agent_jobs TO app_read_write;
GRANT SELECT ON agent_jobs TO app_read_only;

GRANT SELECT, INSERT, UPDATE, DELETE ON agent_job_activities TO app_read_write;
GRANT SELECT ON agent_job_activities TO app_read_only;

-- Grant sequence permissions
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_read_write;
