-- SQLite Database Schema for AI Test Automation Platform
-- This replaces the PostgreSQL schema with SQLite-compatible syntax

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    key_features TEXT,
    user_flows TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Test Suites table
CREATE TABLE IF NOT EXISTS test_suites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    total_test_cases INTEGER DEFAULT 0,
    passed_test_cases INTEGER DEFAULT 0,
    failed_test_cases INTEGER DEFAULT 0,
    duration_minutes INTEGER DEFAULT 0,
    last_run_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Test Cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_suite_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(100) NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'draft',
    expected_result TEXT,
    actual_result TEXT,
    execution_time_ms INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_suite_id) REFERENCES test_suites(id)
);

-- Test Steps table
CREATE TABLE IF NOT EXISTS test_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    action VARCHAR(255) NOT NULL,
    target_element VARCHAR(500),
    input_data TEXT,
    expected_outcome TEXT,
    actual_outcome TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    screenshot_path VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id)
);

-- Agent Processing Jobs table
CREATE TABLE IF NOT EXISTS agent_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    progress_percentage INTEGER DEFAULT 0,
    current_agent VARCHAR(100),
    agent_data TEXT, -- JSON data for agent state
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Agent Activities table (for real-time tracking)
CREATE TABLE IF NOT EXISTS agent_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress_percentage INTEGER DEFAULT 0,
    message TEXT,
    details TEXT, -- JSON data
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES agent_jobs(id)
);

-- Test Executions table
CREATE TABLE IF NOT EXISTS test_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_suite_id INTEGER NOT NULL,
    execution_type VARCHAR(50) DEFAULT 'manual',
    status VARCHAR(50) DEFAULT 'running',
    total_cases INTEGER DEFAULT 0,
    passed_cases INTEGER DEFAULT 0,
    failed_cases INTEGER DEFAULT 0,
    skipped_cases INTEGER DEFAULT 0,
    duration_seconds INTEGER DEFAULT 0,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_suite_id) REFERENCES test_suites(id)
);

-- Insert default admin user
INSERT OR IGNORE INTO users (email, password_hash, first_name, last_name, role) 
VALUES ('admin@demo.com', 'demo_hash', 'Admin', 'User', 'admin');

-- Insert sample applications for demo
INSERT OR IGNORE INTO applications (user_id, name, url, type, description, key_features, user_flows) 
VALUES 
(1, 'HRMS Demo', 'https://opensource-demo.orangehrmlive.com', 'HRMS', 'Human Resource Management System', 'Employee management, Leave management, Attendance tracking, Performance reviews', 'Employee onboarding, Leave application, Performance evaluation, Recruitment process'),
(1, 'E-commerce Demo', 'https://demo.opencart.com', 'E-commerce', 'Online Shopping Platform', 'Product catalog, Shopping cart, Payment processing, Order management', 'Product browsing, Add to cart, Checkout process, Order tracking'),
(1, 'Banking Demo', 'https://demo.testfire.net', 'Banking', 'Online Banking System', 'Account management, Fund transfers, Bill payments, Transaction history', 'Login authentication, Balance inquiry, Money transfer, Bill payment');

-- Insert sample test suites
INSERT OR IGNORE INTO test_suites (application_id, name, description, type, status, success_rate, total_test_cases, passed_test_cases, failed_test_cases, duration_minutes, last_run_at) 
VALUES 
(1, 'HRMS Login Flow Test', 'Comprehensive login and authentication testing', 'functional', 'completed', 95.0, 8, 8, 0, 15, datetime('now', '-2 hours')),
(1, 'Employee Management Test', 'Employee CRUD operations and data validation', 'functional', 'running', 87.0, 12, 10, 2, 25, datetime('now', '-30 minutes')),
(1, 'Leave Application Test', 'Leave request workflow and approval process', 'integration', 'failed', 78.0, 6, 5, 1, 18, datetime('now', '-1 hour'));
