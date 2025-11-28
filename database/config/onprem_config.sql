-- On-Premise Deployment Configuration
-- Single-tenant PostgreSQL configuration for enterprise deployment

-- =====================================================
-- ON-PREMISE SPECIFIC CONFIGURATION
-- =====================================================

-- Set deployment mode
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('deployment_mode', '"OnPrem"', 'Deployment mode: SaaS or OnPrem', true),
('multi_tenant', 'false', 'Disable multi-tenant features', false),
('billing_enabled', 'false', 'Disable billing and subscription management', false),
('user_registration_enabled', 'false', 'Disable new user registration (admin-managed)', false),
('license_enforcement_enabled', 'true', 'Enable license key enforcement', false),
('max_users', '1000', 'Maximum number of users (license-dependent)', false),
('enterprise_features_enabled', 'true', 'Enable all enterprise features', false);

-- On-Premise license configuration
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('license_type', '"enterprise"', 'License type: starter, professional, enterprise, unlimited', false),
('license_expiry_date', '"2025-12-31"', 'License expiration date', false),
('licensed_users', '1000', 'Number of licensed users', false),
('licensed_applications', '500', 'Number of licensed applications', false),
('licensed_api_calls_per_month', '1000000', 'Licensed API calls per month', false),
('support_level', '"enterprise"', 'Support level: basic, professional, enterprise', false),
('custom_branding_enabled', 'true', 'Enable custom branding and white-labeling', false);

-- On-Premise security configuration (enhanced for enterprise)
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('session_timeout_minutes', '240', 'Session timeout in minutes (4 hours)', false),
('password_min_length', '12', 'Minimum password length (enterprise standard)', true),
('password_complexity_required', 'true', 'Require complex passwords', true),
('mfa_required_for_all_users', 'true', 'Require MFA for all users', false),
('login_attempt_limit', '3', 'Maximum failed login attempts before lockout', false),
('lockout_duration_minutes', '60', 'Account lockout duration in minutes', false),
('ip_whitelist_enabled', 'true', 'Enable IP address whitelisting', false),
('audit_log_retention_days', '2555', 'Audit log retention period (7 years)', false),
('encryption_at_rest_enabled', 'true', 'Enable database encryption at rest', false),
('tls_version_minimum', '"1.3"', 'Minimum TLS version required', false);

-- On-Premise integration settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('ldap_integration_enabled', 'false', 'Enable LDAP/Active Directory integration', false),
('saml_sso_enabled', 'false', 'Enable SAML SSO integration', false),
('oauth_providers_enabled', 'false', 'Enable OAuth provider integration', false),
('api_rate_limiting_enabled', 'true', 'Enable API rate limiting', false),
('webhook_notifications_enabled', 'true', 'Enable webhook notifications', false),
('email_notifications_enabled', 'true', 'Enable email notifications', false),
('slack_integration_enabled', 'false', 'Enable Slack integration', false),
('teams_integration_enabled', 'false', 'Enable Microsoft Teams integration', false);

-- Create default enterprise customer for On-Premise deployment
DO $$
DECLARE
    enterprise_customer_id UUID;
    admin_user_id UUID;
    enterprise_plan_id UUID;
BEGIN
    -- Create enterprise subscription plan
    INSERT INTO subscription_plans (
        id, name, description, price_monthly, price_yearly, 
        api_calls_limit, applications_limit, concurrent_tests_limit, 
        features, security_tier
    ) VALUES (
        uuid_generate_v4(), 'Enterprise On-Premise', 
        'Full enterprise features for on-premise deployment',
        0.00, 0.00, 1000000, 1000, 100,
        '["unlimited_reporting", "24x7_support", "premium_agents", "sso", "advanced_security", "custom_branding", "audit_logs", "compliance_tools", "ldap_integration", "api_access", "webhook_support"]',
        'enterprise'
    ) RETURNING id INTO enterprise_plan_id;

    -- Create default enterprise customer
    INSERT INTO customers (
        id, name, email, company_name, industry,
        subscription_plan_id, subscription_status,
        data_classification, compliance_requirements,
        security_settings, is_active
    ) VALUES (
        uuid_generate_v4(), 'Enterprise Customer', 
        'admin@company.local', 'Enterprise Organization', 'Technology',
        enterprise_plan_id, 'active',
        'confidential', 
        '["SOC2", "ISO27001", "GDPR", "HIPAA"]',
        '{"mfa_required": true, "ip_whitelist_enabled": true, "audit_logging": "comprehensive"}',
        true
    ) RETURNING id INTO enterprise_customer_id;

    -- Create default admin user
    INSERT INTO customer_users (
        id, customer_id, email, password_hash, 
        first_name, last_name, role, 
        mfa_enabled, is_active
    ) VALUES (
        uuid_generate_v4(), enterprise_customer_id, 
        'admin@company.local', 
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', -- Default: 'admin123'
        'System', 'Administrator', 'admin',
        true, true
    ) RETURNING id INTO admin_user_id;

    -- Store the default customer ID for application use
    INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
    ('default_customer_id', '"' || enterprise_customer_id || '"', 'Default customer ID for On-Premise deployment', false);

    -- Log the setup
    INSERT INTO audit_logs (
        customer_id, event_type, resource_type, action, 
        new_values, metadata
    ) VALUES (
        enterprise_customer_id, 'system_event', 'deployment', 'ONPREM_SETUP',
        jsonb_build_object(
            'customer_id', enterprise_customer_id,
            'admin_user_id', admin_user_id,
            'plan_id', enterprise_plan_id
        ),
        jsonb_build_object(
            'deployment_type', 'OnPrem',
            'setup_timestamp', NOW(),
            'version', '1.0.0'
        )
    );
END $$;

-- On-Premise specific tables

-- License management
CREATE TABLE license_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_key VARCHAR(500) NOT NULL UNIQUE,
    license_type VARCHAR(50) NOT NULL, -- starter, professional, enterprise, unlimited
    issued_to VARCHAR(255) NOT NULL,
    issued_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    max_users INTEGER,
    max_applications INTEGER,
    max_api_calls_per_month INTEGER,
    features JSONB,
    is_active BOOLEAN DEFAULT true,
    activated_at TIMESTAMP WITH TIME ZONE,
    last_validated_at TIMESTAMP WITH TIME ZONE,
    validation_count INTEGER DEFAULT 0,
    
    CONSTRAINT valid_license_type CHECK (license_type IN ('starter', 'professional', 'enterprise', 'unlimited'))
);

-- LDAP/Active Directory configuration
CREATE TABLE ldap_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_url VARCHAR(500) NOT NULL,
    bind_dn VARCHAR(500),
    bind_password_encrypted TEXT,
    user_search_base VARCHAR(500) NOT NULL,
    user_search_filter VARCHAR(500) DEFAULT '(uid={username})',
    group_search_base VARCHAR(500),
    group_search_filter VARCHAR(500) DEFAULT '(member={user_dn})',
    attribute_mapping JSONB, -- Map LDAP attributes to user fields
    ssl_enabled BOOLEAN DEFAULT true,
    ssl_verify BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_server_url CHECK (server_url ~* '^ldaps?://')
);

-- SAML SSO configuration
CREATE TABLE saml_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id VARCHAR(500) NOT NULL,
    sso_url VARCHAR(500) NOT NULL,
    slo_url VARCHAR(500),
    x509_certificate TEXT NOT NULL,
    attribute_mapping JSONB, -- Map SAML attributes to user fields
    sign_requests BOOLEAN DEFAULT true,
    encrypt_assertions BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_sso_url CHECK (sso_url ~* '^https://')
);

-- Custom branding configuration
CREATE TABLE branding_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255),
    logo_url VARCHAR(500),
    favicon_url VARCHAR(500),
    primary_color VARCHAR(7), -- Hex color code
    secondary_color VARCHAR(7),
    accent_color VARCHAR(7),
    custom_css TEXT,
    footer_text TEXT,
    support_email VARCHAR(255),
    support_url VARCHAR(500),
    terms_url VARCHAR(500),
    privacy_url VARCHAR(500),
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_color_format CHECK (
        (primary_color IS NULL OR primary_color ~* '^#[0-9A-Fa-f]{6}$') AND
        (secondary_color IS NULL OR secondary_color ~* '^#[0-9A-Fa-f]{6}$') AND
        (accent_color IS NULL OR accent_color ~* '^#[0-9A-Fa-f]{6}$')
    )
);

-- IP whitelist for enhanced security
CREATE TABLE ip_whitelist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ip_address INET NOT NULL,
    ip_range CIDR,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES customer_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT ip_or_range_required CHECK (
        (ip_address IS NOT NULL AND ip_range IS NULL) OR
        (ip_address IS NULL AND ip_range IS NOT NULL)
    )
);

-- System maintenance and updates
CREATE TABLE system_maintenance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    maintenance_type VARCHAR(50) NOT NULL, -- update, backup, security_patch, etc.
    description TEXT NOT NULL,
    scheduled_start TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_end TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed, failed
    impact_level VARCHAR(20) DEFAULT 'low', -- low, medium, high
    affected_services JSONB,
    maintenance_notes TEXT,
    performed_by VARCHAR(255),
    
    CONSTRAINT valid_maintenance_type CHECK (maintenance_type IN ('update', 'backup', 'security_patch', 'configuration_change', 'hardware_maintenance')),
    CONSTRAINT valid_status CHECK (status IN ('scheduled', 'in_progress', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_impact_level CHECK (impact_level IN ('low', 'medium', 'high'))
);

-- On-Premise specific functions

-- Function to validate license
CREATE OR REPLACE FUNCTION validate_license()
RETURNS BOOLEAN AS $$
DECLARE
    license_record RECORD;
    current_users INTEGER;
    current_applications INTEGER;
BEGIN
    -- Get active license
    SELECT * INTO license_record 
    FROM license_info 
    WHERE is_active = true 
    AND expiry_date >= CURRENT_DATE 
    LIMIT 1;
    
    IF NOT FOUND THEN
        RETURN false;
    END IF;
    
    -- Check user limit
    SELECT COUNT(*) INTO current_users 
    FROM customer_users 
    WHERE is_active = true AND is_deleted = false;
    
    IF current_users > license_record.max_users THEN
        RETURN false;
    END IF;
    
    -- Check application limit
    SELECT COUNT(*) INTO current_applications 
    FROM applications 
    WHERE is_deleted = false;
    
    IF current_applications > license_record.max_applications THEN
        RETURN false;
    END IF;
    
    -- Update validation timestamp
    UPDATE license_info 
    SET last_validated_at = NOW(), validation_count = validation_count + 1
    WHERE id = license_record.id;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get system status
CREATE OR REPLACE FUNCTION get_system_status()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    license_valid BOOLEAN;
    total_users INTEGER;
    total_applications INTEGER;
    total_executions_today INTEGER;
BEGIN
    -- Validate license
    SELECT validate_license() INTO license_valid;
    
    -- Get usage statistics
    SELECT COUNT(*) INTO total_users FROM customer_users WHERE is_active = true;
    SELECT COUNT(*) INTO total_applications FROM applications WHERE is_deleted = false;
    SELECT COUNT(*) INTO total_executions_today FROM test_executions WHERE DATE(created_at) = CURRENT_DATE;
    
    -- Build result
    SELECT jsonb_build_object(
        'license_valid', license_valid,
        'deployment_mode', 'OnPrem',
        'total_users', total_users,
        'total_applications', total_applications,
        'executions_today', total_executions_today,
        'database_size', pg_size_pretty(pg_database_size(current_database())),
        'uptime', EXTRACT(EPOCH FROM (NOW() - pg_postmaster_start_time())),
        'last_backup', (SELECT MAX(created_at) FROM audit_logs WHERE event_type = 'system_event' AND action = 'BACKUP_COMPLETED'),
        'maintenance_mode', COALESCE((SELECT setting_value::boolean FROM system_settings WHERE setting_key = 'maintenance_mode'), false)
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check IP whitelist
CREATE OR REPLACE FUNCTION is_ip_whitelisted(check_ip INET)
RETURNS BOOLEAN AS $$
DECLARE
    whitelist_enabled BOOLEAN;
    ip_allowed BOOLEAN := false;
BEGIN
    -- Check if IP whitelisting is enabled
    SELECT COALESCE((SELECT setting_value::boolean FROM system_settings WHERE setting_key = 'ip_whitelist_enabled'), false)
    INTO whitelist_enabled;
    
    IF NOT whitelist_enabled THEN
        RETURN true;
    END IF;
    
    -- Check if IP is in whitelist
    SELECT EXISTS(
        SELECT 1 FROM ip_whitelist 
        WHERE is_active = true 
        AND (
            ip_address = check_ip OR 
            (ip_range IS NOT NULL AND check_ip << ip_range)
        )
    ) INTO ip_allowed;
    
    RETURN ip_allowed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- On-Premise monitoring views
CREATE VIEW onprem_system_health AS
SELECT 
    'license' as component,
    CASE WHEN validate_license() THEN 'healthy' ELSE 'critical' END as status,
    jsonb_build_object(
        'valid', validate_license(),
        'expires', (SELECT expiry_date FROM license_info WHERE is_active = true LIMIT 1)
    ) as details
UNION ALL
SELECT 
    'database' as component,
    'healthy' as status,
    jsonb_build_object(
        'size', pg_size_pretty(pg_database_size(current_database())),
        'connections', (SELECT count(*) FROM pg_stat_activity),
        'uptime_hours', ROUND(EXTRACT(EPOCH FROM (NOW() - pg_postmaster_start_time())) / 3600, 2)
    ) as details
UNION ALL
SELECT 
    'users' as component,
    CASE WHEN COUNT(*) > 0 THEN 'healthy' ELSE 'warning' END as status,
    jsonb_build_object(
        'total_users', COUNT(*),
        'active_users', COUNT(*) FILTER (WHERE last_login_at > NOW() - INTERVAL '30 days')
    ) as details
FROM customer_users WHERE is_active = true;

CREATE VIEW onprem_usage_summary AS
SELECT 
    DATE(created_at) as usage_date,
    COUNT(*) as total_executions,
    COUNT(DISTINCT customer_id) as active_customers,
    COUNT(DISTINCT application_id) as applications_tested,
    AVG(duration_seconds) as avg_duration_seconds,
    SUM(total_tests) as total_tests_run,
    SUM(passed_tests) as total_tests_passed
FROM test_executions
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY usage_date DESC;

-- Insert default branding configuration
INSERT INTO branding_configuration (
    company_name, primary_color, secondary_color, accent_color,
    footer_text, support_email, is_active
) VALUES (
    'AI Test Automation Platform',
    '#2563eb', '#1e40af', '#3b82f6',
    'Powered by AI Test Automation Platform',
    'support@company.local',
    true
);

-- Create default IP whitelist entries (localhost and private networks)
INSERT INTO ip_whitelist (ip_range, description, is_active) VALUES
('127.0.0.0/8', 'Localhost', true),
('10.0.0.0/8', 'Private Network Class A', true),
('172.16.0.0/12', 'Private Network Class B', true),
('192.168.0.0/16', 'Private Network Class C', true);

COMMENT ON SCHEMA public IS 'AI Test Automation Platform - On-Premise Single-Tenant Configuration';
