-- AI Test Automation Platform - Complete Database Export
-- Generated for external access and replication
-- =====================================================

-- This file contains the complete database schema and sample data
-- from the AI Test Automation Platform

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- CORE TABLES WITH COMPLETE SCHEMA
-- =====================================================

-- 1. CUSTOMERS TABLE
CREATE TABLE customers (
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
CREATE TABLE customer_users (
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
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500),
    environment VARCHAR(50) DEFAULT 'staging',
    application_type VARCHAR(50) DEFAULT 'web',
    technology_stack JSONB DEFAULT '{}',
    authentication_method VARCHAR(100),
    base_url VARCHAR(500),
    api_documentation_url VARCHAR(500),
    repository_url VARCHAR(500),
    deployment_status VARCHAR(50) DEFAULT 'active',
    health_check_url VARCHAR(500),
    monitoring_enabled BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    tags JSONB DEFAULT '[]',
    configuration JSONB DEFAULT '{}'
);

-- 4. TEST_SUITES TABLE
CREATE TABLE test_suites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(50) DEFAULT 'functional',
    priority VARCHAR(20) DEFAULT 'medium',
    environment VARCHAR(50) DEFAULT 'staging',
    browser VARCHAR(50) DEFAULT 'chrome',
    parallel_execution BOOLEAN DEFAULT false,
    max_parallel_tests INTEGER DEFAULT 1,
    timeout_minutes INTEGER DEFAULT 30,
    retry_count INTEGER DEFAULT 0,
    schedule_cron VARCHAR(100),
    is_scheduled BOOLEAN DEFAULT false,
    tags JSONB DEFAULT '[]',
    configuration JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'draft',
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    last_executed_at TIMESTAMP WITH TIME ZONE,
    last_execution_status VARCHAR(50),
    success_rate DECIMAL(5,2) DEFAULT 0.00
);

-- 5. TEST_CASES TABLE
CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite_id UUID NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_steps JSONB NOT NULL DEFAULT '[]',
    expected_result TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    test_type VARCHAR(50) DEFAULT 'functional',
    tags JSONB DEFAULT '[]',
    preconditions TEXT,
    test_data JSONB DEFAULT '{}',
    environment_requirements JSONB DEFAULT '{}',
    estimated_duration_minutes INTEGER DEFAULT 5,
    automation_status VARCHAR(50) DEFAULT 'manual',
    test_script_path VARCHAR(500),
    test_script_language VARCHAR(50),
    status VARCHAR(20) DEFAULT 'draft',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    last_executed_at TIMESTAMP WITH TIME ZONE,
    last_execution_status VARCHAR(50),
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0
);

-- 6. TEST_STEPS TABLE
CREATE TABLE test_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    element_selector VARCHAR(500),
    input_data TEXT,
    expected_result TEXT,
    screenshot_required BOOLEAN DEFAULT false,
    wait_time_seconds INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    is_conditional BOOLEAN DEFAULT false,
    condition_expression TEXT,
    error_handling VARCHAR(100) DEFAULT 'fail',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(test_case_id, step_number)
);

-- 7. TEST_EXECUTIONS TABLE
CREATE TABLE test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite_id UUID REFERENCES test_suites(id) ON DELETE CASCADE,
    test_case_id UUID REFERENCES test_cases(id) ON DELETE CASCADE,
    execution_type VARCHAR(50) DEFAULT 'manual',
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    environment VARCHAR(50),
    browser VARCHAR(50),
    browser_version VARCHAR(50),
    os VARCHAR(50),
    resolution VARCHAR(20),
    executed_by UUID REFERENCES customer_users(id),
    agent_id VARCHAR(100),
    execution_config JSONB DEFAULT '{}',
    error_message TEXT,
    stack_trace TEXT,
    screenshots JSONB DEFAULT '[]',
    logs JSONB DEFAULT '[]',
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. TEST_RESULTS TABLE
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES test_executions(id) ON DELETE CASCADE,
    test_step_id UUID REFERENCES test_steps(id),
    step_number INTEGER,
    status VARCHAR(50) NOT NULL,
    actual_result TEXT,
    expected_result TEXT,
    error_message TEXT,
    screenshot_path VARCHAR(500),
    execution_time_ms INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    element_found BOOLEAN,
    element_selector VARCHAR(500),
    page_url VARCHAR(1000),
    page_title VARCHAR(500),
    additional_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. REQUIREMENTS TABLE
CREATE TABLE requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    requirement_type VARCHAR(50) DEFAULT 'functional',
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'draft',
    acceptance_criteria JSONB DEFAULT '[]',
    business_rules JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    source_document VARCHAR(500),
    stakeholder VARCHAR(255),
    estimated_effort_hours INTEGER,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    approved_by UUID REFERENCES customer_users(id),
    approved_at TIMESTAMP WITH TIME ZONE
);

-- 10. REQUIREMENT_TEST_MAPPING TABLE
CREATE TABLE requirement_test_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    coverage_type VARCHAR(50) DEFAULT 'full',
    mapping_confidence DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES customer_users(id),
    UNIQUE(requirement_id, test_case_id)
);

-- Continue with remaining tables...
-- (Additional tables would be included here for complete schema)

-- =====================================================
-- SAMPLE DATA INSERTS
-- =====================================================

-- Insert sample customer
INSERT INTO customers (id, name, company_name, email, phone, subscription_plan) VALUES 
('e6f663ec-c7cc-47b1-ab85-0a38d5df19af', 'Demo Customer', 'Demo Corp', 'demo@example.com', '+1-555-0123', 'enterprise')
ON CONFLICT (id) DO NOTHING;

-- Insert sample user
INSERT INTO customer_users (id, customer_id, email, password_hash, first_name, last_name, role) VALUES 
('f7a774fd-d8dd-48c2-bc86-1b49e6e8e8bf', 'e6f663ec-c7cc-47b1-ab85-0a38d5df19af', 'tester@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlDO', 'Test', 'User', 'admin')
ON CONFLICT (id) DO NOTHING;

-- Insert sample application
INSERT INTO applications (id, customer_id, name, description, url, environment) VALUES 
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'e6f663ec-c7cc-47b1-ab85-0a38d5df19af', 'Demo E-commerce App', 'Sample e-commerce application for testing', 'https://demo-ecommerce.example.com', 'staging')
ON CONFLICT (id) DO NOTHING;

-- Insert sample test suite
INSERT INTO test_suites (id, customer_id, application_id, name, description, test_type) VALUES 
('b2c3d4e5-f6a7-8901-bcde-f23456789012', 'e6f663ec-c7cc-47b1-ab85-0a38d5df19af', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'User Authentication Tests', 'Comprehensive tests for user login, registration, and authentication flows', 'functional')
ON CONFLICT (id) DO NOTHING;

-- Insert sample test cases with detailed steps
INSERT INTO test_cases (id, test_suite_id, name, description, test_steps, expected_result) VALUES 
('c3d4e5f6-a7b8-9012-cdef-345678901234', 'b2c3d4e5-f6a7-8901-bcde-f23456789012', 'Valid User Login', 'Test successful login with valid credentials', 
'[
  {"step": 1, "action": "navigate", "description": "Navigate to login page", "target": "/login"},
  {"step": 2, "action": "input", "description": "Enter valid username", "target": "#username", "value": "testuser@example.com"},
  {"step": 3, "action": "input", "description": "Enter valid password", "target": "#password", "value": "SecurePass123!"},
  {"step": 4, "action": "click", "description": "Click login button", "target": "#login-btn"},
  {"step": 5, "action": "verify", "description": "Verify successful login", "target": ".dashboard", "expected": "Dashboard page is displayed"}
]', 'User should be successfully logged in and redirected to dashboard'),

('d4e5f6a7-b8c9-0123-defa-456789012345', 'b2c3d4e5-f6a7-8901-bcde-f23456789012', 'Invalid Password Login', 'Test login failure with invalid password', 
'[
  {"step": 1, "action": "navigate", "description": "Navigate to login page", "target": "/login"},
  {"step": 2, "action": "input", "description": "Enter valid username", "target": "#username", "value": "testuser@example.com"},
  {"step": 3, "action": "input", "description": "Enter invalid password", "target": "#password", "value": "WrongPassword"},
  {"step": 4, "action": "click", "description": "Click login button", "target": "#login-btn"},
  {"step": 5, "action": "verify", "description": "Verify error message", "target": ".error-message", "expected": "Invalid credentials error is displayed"}
]', 'Login should fail with appropriate error message')
ON CONFLICT (id) DO NOTHING;

-- Insert sample requirements
INSERT INTO requirements (id, customer_id, application_id, name, description, requirement_type, acceptance_criteria) VALUES 
('e5f6a7b8-c9d0-1234-efab-567890123456', 'e6f663ec-c7cc-47b1-ab85-0a38d5df19af', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'User Authentication System', 'Users must be able to securely log in and out of the system', 'functional',
'[
  {"criteria": "Users can log in with valid email and password"},
  {"criteria": "Invalid login attempts show appropriate error messages"},
  {"criteria": "Users can log out successfully"},
  {"criteria": "Session management works correctly"},
  {"criteria": "Password requirements are enforced"}
]')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customer_users_customer_id ON customer_users(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_users_email ON customer_users(email);
CREATE INDEX IF NOT EXISTS idx_applications_customer_id ON applications(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_suites_customer_id ON test_suites(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_suites_application_id ON test_suites(application_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_test_suite_id ON test_cases(test_suite_id);
CREATE INDEX IF NOT EXISTS idx_test_steps_test_case_id ON test_steps(test_case_id);
CREATE INDEX IF NOT EXISTS idx_test_executions_test_suite_id ON test_executions(test_suite_id);
CREATE INDEX IF NOT EXISTS idx_test_executions_test_case_id ON test_executions(test_case_id);
CREATE INDEX IF NOT EXISTS idx_test_results_execution_id ON test_results(execution_id);
CREATE INDEX IF NOT EXISTS idx_requirements_customer_id ON requirements(customer_id);
CREATE INDEX IF NOT EXISTS idx_requirement_test_mapping_requirement_id ON requirement_test_mapping(requirement_id);
CREATE INDEX IF NOT EXISTS idx_requirement_test_mapping_test_case_id ON requirement_test_mapping(test_case_id);

-- =====================================================
-- CONSTRAINTS AND TRIGGERS
-- =====================================================

-- Update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to relevant tables
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_users_updated_at BEFORE UPDATE ON customer_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_test_suites_updated_at BEFORE UPDATE ON test_suites FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_test_cases_updated_at BEFORE UPDATE ON test_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- CONNECTION INFORMATION
-- =====================================================

-- Database: test_automation_db
-- Host: localhost
-- Port: 5432
-- Username: postgres
-- Password: postgres (for development only)

-- To connect from external tools:
-- psql -h localhost -U postgres -d test_automation_db
-- Connection string: postgresql://postgres:postgres@localhost:5432/test_automation_db
