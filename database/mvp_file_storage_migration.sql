-- MVP File Storage Migration
-- Add file storage support to existing test_cases table
-- Maintains backward compatibility with existing data

-- Add file storage columns to test_cases table
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS test_file_path VARCHAR(1000);
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS config_file_path VARCHAR(1000);
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS generated_from_intent TEXT;
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS generation_model VARCHAR(50) DEFAULT 'gpt-4';
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS generation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS code_confidence_score DECIMAL(3,2) DEFAULT 0.85;
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS file_size_bytes BIGINT;
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS file_checksum VARCHAR(64);
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS success_rate DECIMAL(5,2) DEFAULT 0.00;
ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS avg_execution_time_ms INTEGER;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_test_cases_file_path ON test_cases(test_file_path);
CREATE INDEX IF NOT EXISTS idx_test_cases_generation_timestamp ON test_cases(generation_timestamp);
CREATE INDEX IF NOT EXISTS idx_test_cases_success_rate ON test_cases(success_rate);

-- Add comments for documentation
COMMENT ON COLUMN test_cases.test_file_path IS 'Path to the actual Playwright test file (local path or cloud storage URL)';
COMMENT ON COLUMN test_cases.config_file_path IS 'Path to test configuration file (conftest.py, etc.)';
COMMENT ON COLUMN test_cases.generated_from_intent IS 'Original natural language intent used to generate this test';
COMMENT ON COLUMN test_cases.generation_model IS 'AI model used to generate the test code (gpt-4, claude-3, etc.)';
COMMENT ON COLUMN test_cases.code_confidence_score IS 'AI confidence score for generated code (0.00 to 1.00)';
COMMENT ON COLUMN test_cases.file_checksum IS 'SHA-256 checksum of the test file for integrity verification';
COMMENT ON COLUMN test_cases.success_rate IS 'Success rate over last 10 executions (0.00 to 100.00)';

-- Create test execution results table for detailed execution tracking
CREATE TABLE IF NOT EXISTS test_execution_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    execution_id UUID,
    
    -- Execution metadata
    executed_by UUID REFERENCES customer_users(id),
    execution_environment VARCHAR(100),
    browser VARCHAR(50),
    device_type VARCHAR(50),
    
    -- Results
    status VARCHAR(50) NOT NULL CHECK (status IN ('passed', 'failed', 'skipped', 'error')),
    duration_ms INTEGER,
    error_message TEXT,
    stack_trace TEXT,
    
    -- Artifacts (file paths)
    screenshot_path VARCHAR(1000),
    video_path VARCHAR(1000),
    logs_path VARCHAR(1000),
    report_path VARCHAR(1000),
    
    -- Audit fields
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for test execution results
CREATE INDEX IF NOT EXISTS idx_test_execution_results_test_case_id ON test_execution_results(test_case_id);
CREATE INDEX IF NOT EXISTS idx_test_execution_results_status ON test_execution_results(status);
CREATE INDEX IF NOT EXISTS idx_test_execution_results_executed_at ON test_execution_results(executed_at);

-- Enable RLS on test execution results
ALTER TABLE test_execution_results ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for test execution results
CREATE POLICY customer_test_execution_results_isolation ON test_execution_results
    FOR ALL TO app_read_write, app_read_only
    USING (
        test_case_id IN (
            SELECT id FROM test_cases 
            WHERE customer_id::text = current_setting('app.current_customer_id', true)
        )
    );

-- Grant permissions on new table
GRANT SELECT ON test_execution_results TO app_read_only;
GRANT SELECT, INSERT, UPDATE, DELETE ON test_execution_results TO app_read_write;

-- Create function to update test case success rate
CREATE OR REPLACE FUNCTION update_test_case_success_rate(p_test_case_id UUID)
RETURNS VOID AS $$
DECLARE
    v_total_executions INTEGER;
    v_passed_executions INTEGER;
    v_success_rate DECIMAL(5,2);
BEGIN
    -- Get execution counts from last 10 executions
    SELECT COUNT(*) INTO v_total_executions
    FROM (
        SELECT id FROM test_execution_results 
        WHERE test_case_id = p_test_case_id 
        ORDER BY executed_at DESC 
        LIMIT 10
    ) recent_executions;
    
    IF v_total_executions > 0 THEN
        SELECT COUNT(*) INTO v_passed_executions
        FROM (
            SELECT id FROM test_execution_results 
            WHERE test_case_id = p_test_case_id 
            AND status = 'passed'
            ORDER BY executed_at DESC 
            LIMIT 10
        ) recent_passed;
        
        v_success_rate := (v_passed_executions::DECIMAL / v_total_executions::DECIMAL) * 100;
        
        UPDATE test_cases 
        SET success_rate = v_success_rate,
            updated_at = NOW()
        WHERE id = p_test_case_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create function to update test suite statistics
CREATE OR REPLACE FUNCTION update_test_suite_statistics(p_test_suite_id UUID)
RETURNS VOID AS $$
DECLARE
    v_total_tests INTEGER;
    v_passed_tests INTEGER;
    v_failed_tests INTEGER;
    v_overall_success_rate DECIMAL(5,2);
BEGIN
    -- Count total test cases in suite
    SELECT COUNT(*) INTO v_total_tests
    FROM test_cases 
    WHERE test_suite_id = p_test_suite_id;
    
    -- Count recent execution results
    SELECT 
        COUNT(CASE WHEN ter.status = 'passed' THEN 1 END),
        COUNT(CASE WHEN ter.status = 'failed' THEN 1 END)
    INTO v_passed_tests, v_failed_tests
    FROM test_cases tc
    LEFT JOIN LATERAL (
        SELECT status 
        FROM test_execution_results ter 
        WHERE ter.test_case_id = tc.id 
        ORDER BY ter.executed_at DESC 
        LIMIT 1
    ) ter ON true
    WHERE tc.test_suite_id = p_test_suite_id;
    
    -- Calculate overall success rate
    IF v_total_tests > 0 THEN
        v_overall_success_rate := (v_passed_tests::DECIMAL / v_total_tests::DECIMAL) * 100;
    ELSE
        v_overall_success_rate := 0;
    END IF;
    
    -- Update test suite
    UPDATE test_suites 
    SET total_test_cases = v_total_tests,
        passed_test_cases = v_passed_tests,
        failed_test_cases = v_failed_tests,
        success_rate = v_overall_success_rate,
        updated_at = NOW()
    WHERE id = p_test_suite_id;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update success rates
CREATE OR REPLACE FUNCTION trigger_update_success_rates()
RETURNS TRIGGER AS $$
BEGIN
    -- Update test case success rate
    PERFORM update_test_case_success_rate(NEW.test_case_id);
    
    -- Update test suite statistics
    PERFORM update_test_suite_statistics(
        (SELECT test_suite_id FROM test_cases WHERE id = NEW.test_case_id)
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on test execution results
DROP TRIGGER IF EXISTS trigger_test_execution_success_rate ON test_execution_results;
CREATE TRIGGER trigger_test_execution_success_rate
    AFTER INSERT ON test_execution_results
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_success_rates();

-- Add audit logging for file operations
INSERT INTO audit_logs (
    customer_id, 
    user_id, 
    event_type, 
    action, 
    resource_type, 
    resource_id, 
    details, 
    ip_address
) VALUES (
    '00000000-0000-0000-0000-000000000000'::UUID,
    '00000000-0000-0000-0000-000000000000'::UUID,
    'data_modification',
    'schema_migration',
    'database',
    'test_cases',
    '{"migration": "mvp_file_storage", "columns_added": ["test_file_path", "config_file_path", "generated_from_intent", "generation_model", "generation_timestamp", "code_confidence_score", "file_size_bytes", "file_checksum", "last_modified", "success_rate", "avg_execution_time_ms"], "tables_created": ["test_execution_results"]}',
    '127.0.0.1'
);

-- Verify migration
DO $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns 
    WHERE table_name = 'test_cases' 
    AND column_name IN ('test_file_path', 'config_file_path', 'generated_from_intent');
    
    IF column_count = 3 THEN
        RAISE NOTICE '✅ MVP file storage migration completed successfully';
        RAISE NOTICE '📁 Added file storage columns to test_cases table';
        RAISE NOTICE '📊 Created test_execution_results table for detailed tracking';
        RAISE NOTICE '🔄 Added automatic success rate calculation triggers';
    ELSE
        RAISE EXCEPTION '❌ Migration failed - expected columns not found';
    END IF;
END $$;
