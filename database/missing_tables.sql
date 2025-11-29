-- Missing Tables for AI Test Automation Platform
-- These tables are essential for test storage and agent processing

-- =====================================================
-- TEST SUITES AND TEST CASES
-- =====================================================

-- Test suites - Collections of related tests
CREATE TABLE test_suites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    creation_request_id UUID REFERENCES test_creation_requests(id),
    
    -- Basic information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(100), -- functional, regression, smoke, integration
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
    
    -- Test suite metadata
    total_test_cases INTEGER DEFAULT 0,
    estimated_duration_minutes INTEGER,
    complexity_score INTEGER, -- 1-10 scale
    
    -- Status and execution
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, archived, deprecated
    last_execution_id UUID,
    last_execution_status VARCHAR(50),
    last_execution_date TIMESTAMP WITH TIME ZONE,
    success_rate DECIMAL(5,2),
    
    -- AI generation metadata
    generated_by_ai BOOLEAN DEFAULT true,
    ai_confidence_score DECIMAL(3,2), -- 0.00-1.00
    generation_method VARCHAR(100), -- requirements_based, url_analysis, recording_based
    source_requirements TEXT,
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES customer_users(id),
    
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'active', 'archived', 'deprecated')),
    CONSTRAINT valid_complexity CHECK (complexity_score BETWEEN 1 AND 10)
);

-- Enable RLS on test_suites table
ALTER TABLE test_suites ENABLE ROW LEVEL SECURITY;

-- Test cases - Individual test scenarios
CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite_id UUID NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Basic information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_objective TEXT,
    preconditions TEXT,
    expected_result TEXT,
    
    -- Test case details
    test_data JSONB, -- Input data, test parameters
    execution_order INTEGER DEFAULT 1,
    is_critical BOOLEAN DEFAULT false,
    estimated_duration_seconds INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, deprecated
    last_execution_status VARCHAR(50), -- passed, failed, skipped, error
    last_execution_date TIMESTAMP WITH TIME ZONE,
    
    -- AI generation metadata
    generated_by_ai BOOLEAN DEFAULT true,
    ai_confidence_score DECIMAL(3,2),
    generation_prompt TEXT,
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    updated_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT valid_test_case_status CHECK (status IN ('active', 'inactive', 'deprecated')),
    CONSTRAINT valid_execution_status CHECK (last_execution_status IN ('passed', 'failed', 'skipped', 'error'))
);

-- Enable RLS on test_cases table
ALTER TABLE test_cases ENABLE ROW LEVEL SECURITY;

-- Test steps - Detailed steps within test cases
CREATE TABLE test_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Step details
    step_number INTEGER NOT NULL,
    action_type VARCHAR(100) NOT NULL, -- click, type, navigate, verify, wait
    description TEXT NOT NULL,
    
    -- Action parameters
    selector VARCHAR(500), -- CSS selector, XPath, etc.
    input_data TEXT,
    expected_value TEXT,
    timeout_seconds INTEGER DEFAULT 30,
    
    -- Step metadata
    is_optional BOOLEAN DEFAULT false,
    retry_count INTEGER DEFAULT 0,
    screenshot_on_failure BOOLEAN DEFAULT true,
    
    -- Execution results
    last_execution_status VARCHAR(50), -- passed, failed, skipped
    last_execution_duration_ms INTEGER,
    last_error_message TEXT,
    
    -- AI generation
    generated_by_ai BOOLEAN DEFAULT true,
    ai_confidence_score DECIMAL(3,2),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_action_type CHECK (action_type IN (
        'click', 'type', 'navigate', 'verify', 'wait', 'scroll', 'select', 'upload', 'download'
    )),
    CONSTRAINT valid_step_status CHECK (last_execution_status IN ('passed', 'failed', 'skipped'))
);

-- Enable RLS on test_steps table
ALTER TABLE test_steps ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- AGENT PROCESSING AND STATUS TRACKING
-- =====================================================

-- Agent processing sessions - Track AI agent workflows
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    creation_request_id UUID NOT NULL REFERENCES test_creation_requests(id) ON DELETE CASCADE,
    
    -- Session metadata
    session_type VARCHAR(100) DEFAULT 'test_creation', -- test_creation, test_execution, analysis
    total_agents INTEGER DEFAULT 4,
    current_agent_index INTEGER DEFAULT 0,
    
    -- Overall status
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed, cancelled
    progress_percentage INTEGER DEFAULT 0,
    estimated_completion_time TIMESTAMP WITH TIME ZONE,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Results
    final_output JSONB,
    error_message TEXT,
    
    -- Audit fields
    created_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_session_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

-- Enable RLS on agent_sessions table
ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;

-- Individual agent processing status
CREATE TABLE agent_processing_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_session_id UUID NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Agent details
    agent_name VARCHAR(100) NOT NULL, -- Discovery Agent, Test Generation Agent, etc.
    agent_type VARCHAR(100) NOT NULL, -- discovery, test_generation, code_generation, validation
    execution_order INTEGER NOT NULL,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed, skipped
    progress_percentage INTEGER DEFAULT 0,
    current_task VARCHAR(255),
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Results and output
    output_data JSONB,
    error_message TEXT,
    confidence_score DECIMAL(3,2),
    
    -- Dependencies
    depends_on_agent_id UUID REFERENCES agent_processing_status(id),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_agent_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'skipped')),
    CONSTRAINT valid_agent_type CHECK (agent_type IN ('discovery', 'test_generation', 'code_generation', 'validation'))
);

-- Enable RLS on agent_processing_status table
ALTER TABLE agent_processing_status ENABLE ROW LEVEL SECURITY;

-- Agent activity logs for real-time updates
CREATE TABLE agent_activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_processing_id UUID NOT NULL REFERENCES agent_processing_status(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Activity details
    activity_type VARCHAR(100) NOT NULL, -- started, progress_update, completed, error, info
    message TEXT NOT NULL,
    details JSONB,
    
    -- Progress tracking
    progress_percentage INTEGER,
    estimated_time_remaining_seconds INTEGER,
    
    -- Timing
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_activity_type CHECK (activity_type IN ('started', 'progress_update', 'completed', 'error', 'info'))
);

-- Enable RLS on agent_activity_logs table
ALTER TABLE agent_activity_logs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- TEST EXECUTION RESULTS
-- =====================================================

-- Test execution results - Detailed results for each test case
CREATE TABLE test_execution_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_execution_id UUID NOT NULL REFERENCES test_executions(id) ON DELETE CASCADE,
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Execution details
    execution_order INTEGER,
    status VARCHAR(50) NOT NULL, -- passed, failed, skipped, error
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Results
    error_message TEXT,
    screenshot_path VARCHAR(500),
    video_path VARCHAR(500),
    logs JSONB,
    
    -- Metrics
    assertions_total INTEGER DEFAULT 0,
    assertions_passed INTEGER DEFAULT 0,
    assertions_failed INTEGER DEFAULT 0,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_result_status CHECK (status IN ('passed', 'failed', 'skipped', 'error'))
);

-- Enable RLS on test_execution_results table
ALTER TABLE test_execution_results ENABLE ROW LEVEL SECURITY;

-- Test step execution results
CREATE TABLE test_step_execution_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_execution_result_id UUID NOT NULL REFERENCES test_execution_results(id) ON DELETE CASCADE,
    test_step_id UUID NOT NULL REFERENCES test_steps(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Execution details
    step_number INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- passed, failed, skipped
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Results
    actual_value TEXT,
    expected_value TEXT,
    error_message TEXT,
    screenshot_path VARCHAR(500),
    
    -- Retry information
    retry_attempt INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 0,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_step_result_status CHECK (status IN ('passed', 'failed', 'skipped'))
);

-- Enable RLS on test_step_execution_results table
ALTER TABLE test_step_execution_results ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Test suite indexes
CREATE INDEX idx_test_suites_customer_id ON test_suites(customer_id) WHERE is_deleted = false;
CREATE INDEX idx_test_suites_application_id ON test_suites(application_id) WHERE is_deleted = false;
CREATE INDEX idx_test_suites_status ON test_suites(status) WHERE is_deleted = false;
CREATE INDEX idx_test_suites_created_at ON test_suites(created_at);

-- Test case indexes
CREATE INDEX idx_test_cases_suite_id ON test_cases(test_suite_id) WHERE is_deleted = false;
CREATE INDEX idx_test_cases_customer_id ON test_cases(customer_id) WHERE is_deleted = false;
CREATE INDEX idx_test_cases_execution_order ON test_cases(test_suite_id, execution_order);

-- Test step indexes
CREATE INDEX idx_test_steps_case_id ON test_steps(test_case_id);
CREATE INDEX idx_test_steps_step_number ON test_steps(test_case_id, step_number);

-- Agent processing indexes
CREATE INDEX idx_agent_sessions_customer_id ON agent_sessions(customer_id);
CREATE INDEX idx_agent_sessions_request_id ON agent_sessions(creation_request_id);
CREATE INDEX idx_agent_sessions_status ON agent_sessions(status);
CREATE INDEX idx_agent_processing_session_id ON agent_processing_status(agent_session_id);
CREATE INDEX idx_agent_processing_status ON agent_processing_status(status);
CREATE INDEX idx_agent_activity_logs_processing_id ON agent_activity_logs(agent_processing_id);
CREATE INDEX idx_agent_activity_logs_timestamp ON agent_activity_logs(timestamp);

-- Execution result indexes
CREATE INDEX idx_test_execution_results_execution_id ON test_execution_results(test_execution_id);
CREATE INDEX idx_test_execution_results_case_id ON test_execution_results(test_case_id);
CREATE INDEX idx_test_step_results_execution_result_id ON test_step_execution_results(test_execution_result_id);
CREATE INDEX idx_test_step_results_step_id ON test_step_execution_results(test_step_id);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Test suites isolation
CREATE POLICY test_suites_isolation ON test_suites
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Test cases isolation
CREATE POLICY test_cases_isolation ON test_cases
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Test steps isolation
CREATE POLICY test_steps_isolation ON test_steps
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Agent sessions isolation
CREATE POLICY agent_sessions_isolation ON agent_sessions
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Agent processing isolation
CREATE POLICY agent_processing_isolation ON agent_processing_status
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Agent activity logs isolation
CREATE POLICY agent_activity_logs_isolation ON agent_activity_logs
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Test execution results isolation
CREATE POLICY test_execution_results_isolation ON test_execution_results
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Test step execution results isolation
CREATE POLICY test_step_execution_results_isolation ON test_step_execution_results
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Update test suite statistics when test cases change
CREATE OR REPLACE FUNCTION update_test_suite_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE test_suites 
    SET 
        total_test_cases = (
            SELECT COUNT(*) 
            FROM test_cases 
            WHERE test_suite_id = COALESCE(NEW.test_suite_id, OLD.test_suite_id)
            AND is_deleted = false
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.test_suite_id, OLD.test_suite_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_test_suite_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON test_cases
    FOR EACH ROW EXECUTE FUNCTION update_test_suite_stats();

-- Update agent session progress based on individual agent progress
CREATE OR REPLACE FUNCTION update_agent_session_progress()
RETURNS TRIGGER AS $$
DECLARE
    avg_progress INTEGER;
    session_status VARCHAR(50);
BEGIN
    -- Calculate average progress of all agents in the session
    SELECT 
        COALESCE(AVG(progress_percentage), 0)::INTEGER,
        CASE 
            WHEN COUNT(*) FILTER (WHERE status = 'failed') > 0 THEN 'failed'
            WHEN COUNT(*) FILTER (WHERE status = 'completed') = COUNT(*) THEN 'completed'
            WHEN COUNT(*) FILTER (WHERE status IN ('processing', 'completed')) > 0 THEN 'processing'
            ELSE 'pending'
        END
    INTO avg_progress, session_status
    FROM agent_processing_status 
    WHERE agent_session_id = NEW.agent_session_id;
    
    -- Update the agent session
    UPDATE agent_sessions 
    SET 
        progress_percentage = avg_progress,
        status = session_status,
        current_agent_index = (
            SELECT COALESCE(MAX(execution_order), 0)
            FROM agent_processing_status 
            WHERE agent_session_id = NEW.agent_session_id 
            AND status IN ('processing', 'completed')
        ),
        completed_at = CASE WHEN session_status = 'completed' THEN NOW() ELSE completed_at END,
        updated_at = NOW()
    WHERE id = NEW.agent_session_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agent_session_progress_trigger
    AFTER INSERT OR UPDATE ON agent_processing_status
    FOR EACH ROW EXECUTE FUNCTION update_agent_session_progress();

-- Apply audit triggers to new tables
CREATE TRIGGER audit_test_suites AFTER INSERT OR UPDATE OR DELETE ON test_suites
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_test_cases AFTER INSERT OR UPDATE OR DELETE ON test_cases
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_agent_sessions AFTER INSERT OR UPDATE OR DELETE ON agent_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

COMMENT ON TABLE test_suites IS 'AI-generated test suites with comprehensive metadata and tracking';
COMMENT ON TABLE test_cases IS 'Individual test cases within test suites';
COMMENT ON TABLE test_steps IS 'Detailed steps for test case execution';
COMMENT ON TABLE agent_sessions IS 'AI agent processing sessions for test creation';
COMMENT ON TABLE agent_processing_status IS 'Individual agent status within processing sessions';
COMMENT ON TABLE agent_activity_logs IS 'Real-time activity logs for agent processing';
