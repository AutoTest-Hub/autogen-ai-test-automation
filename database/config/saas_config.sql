-- SaaS Deployment Configuration
-- Multi-tenant PostgreSQL configuration for cloud deployment

-- =====================================================
-- SAAS-SPECIFIC CONFIGURATION
-- =====================================================

-- Set deployment mode
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('deployment_mode', '"SaaS"', 'Deployment mode: SaaS or OnPrem', true),
('multi_tenant', 'true', 'Enable multi-tenant features', false),
('billing_enabled', 'true', 'Enable billing and subscription management', false),
('user_registration_enabled', 'true', 'Allow new user registration', true),
('max_customers', '10000', 'Maximum number of customers', false),
('default_trial_days', '14', 'Default trial period in days', true);

-- SaaS-specific subscription plans
INSERT INTO subscription_plans (name, description, price_monthly, price_yearly, api_calls_limit, applications_limit, concurrent_tests_limit, features, security_tier) VALUES
('Starter', 'Perfect for small teams getting started with AI test automation', 49.00, 490.00, 2500, 5, 3, 
 '["basic_reporting", "email_support", "standard_agents", "web_dashboard"]', 'standard'),

('Professional', 'For growing teams with advanced testing needs', 149.00, 1490.00, 10000, 20, 10, 
 '["advanced_reporting", "priority_support", "enhanced_agents", "api_access", "custom_integrations", "advanced_analytics"]', 'enhanced'),

('Enterprise', 'For large organizations with comprehensive requirements', 399.00, 3990.00, 50000, 100, 50, 
 '["enterprise_reporting", "dedicated_support", "premium_agents", "sso", "advanced_security", "custom_branding", "audit_logs", "compliance_tools"]', 'enterprise'),

('Enterprise Plus', 'For enterprise customers with unlimited scale', 999.00, 9990.00, 250000, 500, 200, 
 '["unlimited_reporting", "24x7_support", "premium_agents", "sso", "advanced_security", "custom_branding", "audit_logs", "compliance_tools", "dedicated_infrastructure", "custom_development"]', 'enterprise');

-- SaaS-specific system settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('stripe_enabled', 'true', 'Enable Stripe payment processing', false),
('webhook_notifications_enabled', 'true', 'Enable webhook notifications for integrations', false),
('analytics_tracking_enabled', 'true', 'Enable usage analytics and tracking', false),
('marketing_emails_enabled', 'true', 'Enable marketing email communications', false),
('support_chat_enabled', 'true', 'Enable in-app support chat', true),
('feature_announcements_enabled', 'true', 'Enable feature announcement notifications', true),
('usage_alerts_enabled', 'true', 'Enable usage limit alerts', true),
('auto_scaling_enabled', 'true', 'Enable automatic resource scaling', false),
('cdn_enabled', 'true', 'Enable CDN for static assets', false),
('backup_retention_days', '90', 'Backup retention period in days', false);

-- SaaS security configuration
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('session_timeout_minutes', '480', 'Session timeout in minutes (8 hours)', false),
('password_min_length', '8', 'Minimum password length', true),
('password_require_special_chars', 'true', 'Require special characters in passwords', true),
('mfa_required_for_admins', 'true', 'Require MFA for admin users', false),
('login_attempt_limit', '5', 'Maximum failed login attempts before lockout', false),
('lockout_duration_minutes', '30', 'Account lockout duration in minutes', false),
('ip_whitelist_enabled', 'false', 'Enable IP address whitelisting', false),
('audit_log_retention_days', '2555', 'Audit log retention period (7 years)', false);

-- SaaS rate limiting configuration
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('api_rate_limit_per_minute', '1000', 'API calls per minute per customer', false),
('api_rate_limit_per_hour', '10000', 'API calls per hour per customer', false),
('api_rate_limit_per_day', '100000', 'API calls per day per customer', false),
('concurrent_test_limit_enforcement', 'true', 'Enforce concurrent test execution limits', false),
('resource_usage_monitoring', 'true', 'Monitor and limit resource usage per customer', false);

-- Create SaaS-specific database roles
CREATE ROLE saas_billing_service;
CREATE ROLE saas_analytics_service;
CREATE ROLE saas_notification_service;

-- Grant permissions for SaaS services
GRANT SELECT, INSERT, UPDATE ON customers, subscription_plans TO saas_billing_service;
GRANT SELECT ON customer_analytics, api_usage_logs TO saas_analytics_service;
GRANT SELECT ON customers, customer_users, security_events TO saas_notification_service;

-- SaaS monitoring and alerting configuration
CREATE TABLE saas_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_unit VARCHAR(50),
    dimensions JSONB, -- customer_id, plan_type, etc.
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_saas_metrics_name_time (metric_name, timestamp),
    INDEX idx_saas_metrics_dimensions (dimensions)
);

-- SaaS billing and usage tracking
CREATE TABLE billing_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    event_type VARCHAR(50) NOT NULL, -- subscription_created, payment_succeeded, etc.
    amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    stripe_event_id VARCHAR(255),
    metadata JSONB,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_billing_events_customer (customer_id, processed_at),
    INDEX idx_billing_events_type (event_type, processed_at)
);

-- SaaS feature usage tracking
CREATE TABLE feature_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    feature_name VARCHAR(100) NOT NULL,
    usage_count INTEGER DEFAULT 1,
    usage_date DATE DEFAULT CURRENT_DATE,
    metadata JSONB,
    
    UNIQUE(customer_id, feature_name, usage_date),
    INDEX idx_feature_usage_customer_date (customer_id, usage_date),
    INDEX idx_feature_usage_feature (feature_name, usage_date)
);

-- SaaS notification preferences
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    user_id UUID REFERENCES customer_users(id),
    notification_type VARCHAR(50) NOT NULL, -- email, sms, webhook, in_app
    channel VARCHAR(50) NOT NULL, -- marketing, security, billing, product
    enabled BOOLEAN DEFAULT true,
    frequency VARCHAR(50) DEFAULT 'immediate', -- immediate, daily, weekly, monthly
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(customer_id, user_id, notification_type, channel),
    INDEX idx_notification_prefs_customer (customer_id)
);

-- SaaS webhook configurations
CREATE TABLE webhook_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    url VARCHAR(500) NOT NULL,
    events JSONB NOT NULL, -- Array of event types to send
    secret VARCHAR(255) NOT NULL, -- For webhook signature verification
    is_active BOOLEAN DEFAULT true,
    last_success_at TIMESTAMP WITH TIME ZONE,
    last_failure_at TIMESTAMP WITH TIME ZONE,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_webhook_endpoints_customer (customer_id),
    CONSTRAINT valid_webhook_url CHECK (url ~* '^https://')
);

-- SaaS integration configurations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    integration_type VARCHAR(50) NOT NULL, -- github, jira, slack, teams, etc.
    configuration JSONB NOT NULL,
    credentials_encrypted TEXT, -- Encrypted OAuth tokens, API keys, etc.
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) DEFAULT 'pending', -- pending, success, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_integrations_customer (customer_id),
    INDEX idx_integrations_type (integration_type)
);

-- SaaS support tickets
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    user_id UUID REFERENCES customer_users(id),
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, waiting, resolved, closed
    category VARCHAR(50), -- technical, billing, feature_request, bug_report
    assigned_to VARCHAR(100), -- Support team member
    resolution TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_support_tickets_customer (customer_id, status),
    INDEX idx_support_tickets_status (status, priority, created_at)
);

-- SaaS performance monitoring
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(50) NOT NULL, -- response_time, throughput, error_rate, etc.
    service_name VARCHAR(100) NOT NULL, -- api, web_ui, agents, database
    value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- ms, requests/sec, percentage, etc.
    dimensions JSONB, -- endpoint, customer_tier, region, etc.
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_performance_metrics_type_time (metric_type, timestamp),
    INDEX idx_performance_metrics_service (service_name, timestamp)
);

-- Enable RLS for SaaS-specific tables
ALTER TABLE billing_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_endpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;

-- RLS policies for SaaS tables
CREATE POLICY billing_events_isolation ON billing_events
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

CREATE POLICY feature_usage_isolation ON feature_usage
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

CREATE POLICY notification_preferences_isolation ON notification_preferences
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

CREATE POLICY webhook_endpoints_isolation ON webhook_endpoints
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

CREATE POLICY integrations_isolation ON integrations
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

CREATE POLICY support_tickets_isolation ON support_tickets
    FOR ALL TO app_read_write, app_read_only
    USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- SaaS-specific functions
CREATE OR REPLACE FUNCTION get_customer_usage_summary(p_customer_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'api_calls_used', c.api_calls_used,
        'api_calls_limit', sp.api_calls_limit,
        'applications_count', (SELECT COUNT(*) FROM applications WHERE customer_id = p_customer_id),
        'applications_limit', sp.applications_limit,
        'current_executions', (SELECT COUNT(*) FROM test_executions WHERE customer_id = p_customer_id AND status IN ('pending', 'running')),
        'concurrent_tests_limit', sp.concurrent_tests_limit,
        'subscription_status', c.subscription_status,
        'plan_name', sp.name
    ) INTO result
    FROM customers c
    LEFT JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
    WHERE c.id = p_customer_id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION check_usage_limits(p_customer_id UUID, p_resource_type VARCHAR(50))
RETURNS BOOLEAN AS $$
DECLARE
    usage_summary JSONB;
    current_count INTEGER;
    limit_count INTEGER;
BEGIN
    SELECT get_customer_usage_summary(p_customer_id) INTO usage_summary;
    
    CASE p_resource_type
        WHEN 'api_calls' THEN
            current_count := (usage_summary->>'api_calls_used')::INTEGER;
            limit_count := (usage_summary->>'api_calls_limit')::INTEGER;
        WHEN 'applications' THEN
            current_count := (usage_summary->>'applications_count')::INTEGER;
            limit_count := (usage_summary->>'applications_limit')::INTEGER;
        WHEN 'concurrent_tests' THEN
            current_count := (usage_summary->>'current_executions')::INTEGER;
            limit_count := (usage_summary->>'concurrent_tests_limit')::INTEGER;
        ELSE
            RETURN false;
    END CASE;
    
    RETURN current_count < limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- SaaS monitoring views
CREATE VIEW saas_customer_health AS
SELECT 
    c.id,
    c.company_name,
    c.subscription_status,
    sp.name as plan_name,
    c.api_calls_used,
    sp.api_calls_limit,
    ROUND((c.api_calls_used::DECIMAL / sp.api_calls_limit * 100), 2) as api_usage_percentage,
    (SELECT COUNT(*) FROM applications WHERE customer_id = c.id) as applications_count,
    sp.applications_limit,
    (SELECT COUNT(*) FROM test_executions WHERE customer_id = c.id AND created_at >= NOW() - INTERVAL '30 days') as executions_last_30_days,
    c.created_at as customer_since
FROM customers c
LEFT JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
WHERE c.is_active = true AND c.is_deleted = false;

CREATE VIEW saas_revenue_metrics AS
SELECT 
    DATE_TRUNC('month', c.subscription_start_date) as month,
    COUNT(*) as new_customers,
    SUM(sp.price_monthly) as monthly_recurring_revenue,
    AVG(sp.price_monthly) as average_revenue_per_user
FROM customers c
JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
WHERE c.subscription_status = 'active'
GROUP BY DATE_TRUNC('month', c.subscription_start_date)
ORDER BY month;

-- Grant permissions for SaaS views
GRANT SELECT ON saas_customer_health, saas_revenue_metrics TO saas_analytics_service;

COMMENT ON SCHEMA public IS 'AI Test Automation Platform - SaaS Multi-Tenant Configuration';
