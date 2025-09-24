-- AI Test Automation SaaS Platform Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- CUSTOMER & SUBSCRIPTION MANAGEMENT
-- =====================================================

-- Subscription plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    api_calls_limit INTEGER,
    applications_limit INTEGER,
    concurrent_tests_limit INTEGER,
    features JSONB, -- Array of feature flags
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customers/Organizations
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    industry VARCHAR(100),
    subscription_plan_id UUID REFERENCES subscription_plans(id),
    subscription_status VARCHAR(50) DEFAULT 'trial', -- trial, active, suspended, cancelled
    subscription_start_date TIMESTAMP WITH TIME ZONE,
    subscription_end_date TIMESTAMP WITH TIME ZONE,
    api_calls_used INTEGER DEFAULT 0,
    api_calls_reset_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    billing_info JSONB,
    settings JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customer users (team members)
CREATE TABLE customer_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'member', -- admin, member, viewer
    permissions JSONB,
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(customer_id, email)
);

-- =====================================================
-- APPLICATION MANAGEMENT
-- =====================================================

-- Customer applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500) NOT NULL,
    application_type VARCHAR(100), -- ecommerce, banking, healthcare, etc.
    environment VARCHAR(50) DEFAULT 'production', -- production, staging, development
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, analyzing
    metadata JSONB, -- Custom fields, tags, etc.
    created_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Application credentials (encrypted)
CREATE TABLE application_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    credential_type VARCHAR(50) NOT NULL, -- login, api_key, oauth, etc.
    username VARCHAR(255),
    password_encrypted TEXT, -- Encrypted password
    additional_data JSONB, -- API keys, tokens, etc. (encrypted)
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Application discovery results
CREATE TABLE application_discoveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    discovery_type VARCHAR(50), -- initial, scheduled, manual
    elements_found INTEGER,
    pages_analyzed INTEGER,
    user_flows_identified INTEGER,
    technologies_detected JSONB,
    security_findings JSONB,
    performance_metrics JSONB,
    discovery_data JSONB, -- Full discovery results
    status VARCHAR(50) DEFAULT 'completed', -- running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TEST CREATION & MANAGEMENT
-- =====================================================

-- Test creation requests
CREATE TABLE test_creation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    creation_method VARCHAR(50) NOT NULL, -- requirements, test_cases, url_metadata, browser_recording
    input_data JSONB NOT NULL, -- Requirements, test cases, or metadata
    configuration JSONB, -- Priority, coverage, test types, etc.
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    progress_percentage INTEGER DEFAULT 0,
    current_agent VARCHAR(100),
    estimated_completion_time TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Agent activities and logs
CREATE TABLE agent_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_creation_request_id UUID REFERENCES test_creation_requests(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL, -- discovery, requirements, test_generation, code_generation, validation
    activity_type VARCHAR(50) NOT NULL, -- started, progress, completed, failed, info
    message TEXT,
    progress_percentage INTEGER,
    metadata JSONB, -- Agent-specific data
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated test suites
CREATE TABLE test_suites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_creation_request_id UUID REFERENCES test_creation_requests(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(100), -- functional, ui, integration, performance, security
    priority VARCHAR(50), -- low, medium, high, critical
    coverage_level VARCHAR(50), -- basic, comprehensive, exhaustive
    estimated_duration_minutes INTEGER,
    test_scenarios_count INTEGER,
    automation_code TEXT, -- Generated test code
    configuration JSONB, -- Test configuration and settings
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, archived
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual test cases within suites
CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite_id UUID NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_steps JSONB, -- Array of test steps
    expected_results JSONB,
    test_data JSONB, -- Test data and parameters
    tags JSONB, -- Array of tags for categorization
    automation_code TEXT, -- Individual test case code
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TEST EXECUTION & RESULTS
-- =====================================================

-- Test execution sessions
CREATE TABLE test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    test_suite_id UUID REFERENCES test_suites(id),
    execution_type VARCHAR(50) DEFAULT 'manual', -- manual, scheduled, ci_cd, api
    environment VARCHAR(50), -- production, staging, development
    browser VARCHAR(50), -- chrome, firefox, safari, edge
    device_type VARCHAR(50), -- desktop, mobile, tablet
    execution_config JSONB, -- Execution parameters
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    total_tests INTEGER,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    skipped_tests INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    duration_seconds INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    triggered_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual test case results
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_execution_id UUID NOT NULL REFERENCES test_executions(id) ON DELETE CASCADE,
    test_case_id UUID REFERENCES test_cases(id),
    test_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- passed, failed, skipped, error
    duration_seconds DECIMAL(10,3),
    error_message TEXT,
    stack_trace TEXT,
    screenshots JSONB, -- Array of screenshot URLs
    logs JSONB, -- Execution logs
    performance_metrics JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test execution artifacts (screenshots, videos, reports)
CREATE TABLE test_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_execution_id UUID REFERENCES test_executions(id) ON DELETE CASCADE,
    test_result_id UUID REFERENCES test_results(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL, -- screenshot, video, report, log
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- REPORTING & ANALYTICS
-- =====================================================

-- Test reports
CREATE TABLE test_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id),
    test_execution_id UUID REFERENCES test_executions(id),
    report_type VARCHAR(50) NOT NULL, -- html, json, pdf, junit
    report_name VARCHAR(255),
    report_data JSONB, -- Report content
    file_path VARCHAR(500), -- Path to generated report file
    is_public BOOLEAN DEFAULT false,
    public_url VARCHAR(500), -- Public sharing URL
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customer analytics and metrics
CREATE TABLE customer_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    total_executions INTEGER DEFAULT 0,
    total_tests_run INTEGER DEFAULT 0,
    total_tests_passed INTEGER DEFAULT 0,
    total_tests_failed INTEGER DEFAULT 0,
    average_success_rate DECIMAL(5,2),
    total_duration_minutes INTEGER DEFAULT 0,
    api_calls_used INTEGER DEFAULT 0,
    applications_tested INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(customer_id, metric_date)
);

-- =====================================================
-- SYSTEM CONFIGURATION
-- =====================================================

-- AI agent configurations
CREATE TABLE agent_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(100) NOT NULL,
    agent_version VARCHAR(50),
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System settings and feature flags
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB,
    description TEXT,
    is_public BOOLEAN DEFAULT false, -- Can be accessed by customers
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage tracking
CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    user_id UUID REFERENCES customer_users(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Customer and application indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_subscription_status ON customers(subscription_status);
CREATE INDEX idx_customer_users_customer_id ON customer_users(customer_id);
CREATE INDEX idx_applications_customer_id ON applications(customer_id);
CREATE INDEX idx_applications_status ON applications(status);

-- Test creation and execution indexes
CREATE INDEX idx_test_creation_requests_customer_id ON test_creation_requests(customer_id);
CREATE INDEX idx_test_creation_requests_status ON test_creation_requests(status);
CREATE INDEX idx_test_executions_customer_id ON test_executions(customer_id);
CREATE INDEX idx_test_executions_application_id ON test_executions(application_id);
CREATE INDEX idx_test_executions_status ON test_executions(status);
CREATE INDEX idx_test_executions_created_at ON test_executions(created_at);

-- Agent activity indexes
CREATE INDEX idx_agent_activities_request_id ON agent_activities(test_creation_request_id);
CREATE INDEX idx_agent_activities_agent_name ON agent_activities(agent_name);
CREATE INDEX idx_agent_activities_timestamp ON agent_activities(timestamp);

-- Analytics indexes
CREATE INDEX idx_customer_analytics_customer_date ON customer_analytics(customer_id, metric_date);
CREATE INDEX idx_api_usage_logs_customer_id ON api_usage_logs(customer_id);
CREATE INDEX idx_api_usage_logs_created_at ON api_usage_logs(created_at);

-- =====================================================
-- SAMPLE DATA FOR DEVELOPMENT
-- =====================================================

-- Insert default subscription plans
INSERT INTO subscription_plans (name, description, price_monthly, price_yearly, api_calls_limit, applications_limit, concurrent_tests_limit, features) VALUES
('Starter', 'Perfect for small teams getting started', 29.00, 290.00, 1000, 3, 2, '["basic_reporting", "email_support"]'),
('Professional', 'For growing teams with advanced needs', 99.00, 990.00, 5000, 10, 5, '["advanced_reporting", "priority_support", "custom_integrations"]'),
('Enterprise', 'For large organizations with custom requirements', 299.00, 2990.00, 25000, 50, 20, '["enterprise_reporting", "dedicated_support", "custom_integrations", "sso", "advanced_security"]');

-- Insert system settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('max_test_duration_minutes', '60', 'Maximum allowed test execution duration', false),
('default_browser', '"chrome"', 'Default browser for test execution', true),
('supported_browsers', '["chrome", "firefox", "safari", "edge"]', 'List of supported browsers', true),
('ai_model_version', '"gpt-4"', 'Current AI model version for test generation', false);

-- Insert default agent configurations
INSERT INTO agent_configurations (agent_name, agent_version, configuration) VALUES
('discovery_agent', '1.0.0', '{"timeout_seconds": 300, "max_pages": 50, "depth_limit": 3}'),
('requirements_agent', '1.0.0', '{"max_scenarios": 100, "include_edge_cases": true}'),
('test_generation_agent', '1.0.0', '{"code_style": "playwright", "include_assertions": true}'),
('validation_agent', '1.0.0', '{"quality_threshold": 0.8, "coverage_threshold": 0.9}');
