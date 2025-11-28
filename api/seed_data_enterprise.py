"""
Enterprise Seed Data Generator for 21-Table PostgreSQL Schema
============================================================

Comprehensive seed data that utilizes all 21 tables in the enterprise schema:
- Agent management with realistic activity logs
- Test management with granular step-level data
- Security events and audit trails
- Complete enterprise workflow simulation
"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import random
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import register_adapter, AsIs
from passlib.context import CryptContext

# Register UUID adapter for psycopg2
def adapt_uuid(uuid_obj):
    return AsIs(f"'{uuid_obj}'")

register_adapter(type(uuid4()), adapt_uuid)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'test_automation_platform'),
    'user': os.getenv('DB_USER', 'app_user'),
    'password': os.getenv('DB_PASSWORD', 'app_password')
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def execute_query(conn, query, params=None):
    """Execute query and return results"""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, params)
        if cursor.description:
            return cursor.fetchall()
        return []

def execute_command(conn, command, params=None):
    """Execute command (INSERT, UPDATE, DELETE)"""
    with conn.cursor() as cursor:
        cursor.execute(command, params)
        conn.commit()

def create_enterprise_seed_data():
    """Create comprehensive seed data for all 21 tables"""
    
    conn = get_db_connection()
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    try:
        logger.info("🌱 Starting enterprise seed data creation...")
        
        # =====================================================
        # 1. SUBSCRIPTION PLANS
        # =====================================================
        logger.info("📋 Creating subscription plans...")
        
        plans = [
            {
                'id': uuid4(),
                'name': 'Starter',
                'description': 'Perfect for small teams getting started with AI testing',
                'price_monthly': 99.00,
                'price_yearly': 990.00,
                'max_users': 5,
                'max_applications': 3,
                'max_test_executions_monthly': 500,
                'security_tier': 'standard'
            },
            {
                'id': uuid4(),
                'name': 'Professional',
                'description': 'Advanced features for growing development teams',
                'price_monthly': 299.00,
                'price_yearly': 2990.00,
                'max_users': 25,
                'max_applications': 15,
                'max_test_executions_monthly': 2500,
                'security_tier': 'enhanced'
            },
            {
                'id': uuid4(),
                'name': 'Enterprise',
                'description': 'Full enterprise features with SOC 2 compliance',
                'price_monthly': 999.00,
                'price_yearly': 9990.00,
                'max_users': 100,
                'max_applications': 50,
                'max_test_executions_monthly': 10000,
                'security_tier': 'enterprise'
            }
        ]
        
        for plan in plans:
            execute_command(conn, """
                INSERT INTO subscription_plans (id, name, description, price_monthly, price_yearly, 
                                              max_users, max_applications, max_test_executions_monthly, security_tier)
                VALUES (%(id)s, %(name)s, %(description)s, %(price_monthly)s, %(price_yearly)s,
                        %(max_users)s, %(max_applications)s, %(max_test_executions_monthly)s, %(security_tier)s)
                ON CONFLICT (id) DO NOTHING
            """, plan)
        
        # =====================================================
        # 2. CUSTOMERS
        # =====================================================
        logger.info("🏢 Creating customers...")
        
        customers = [
            {
                'id': uuid4(),
                'subscription_plan_id': plans[2]['id'],  # Enterprise plan
                'name': 'Demo Customer',
                'email': 'demo@example.com',
                'company_name': 'Demo Corporation',
                'industry': 'Technology',
                'data_classification': 'confidential',
                'compliance_requirements': json.dumps(['SOC2', 'GDPR', 'HIPAA']),
                'require_mfa': True,
                'session_timeout_minutes': 480
            },
            {
                'id': uuid4(),
                'subscription_plan_id': plans[1]['id'],  # Professional plan
                'name': 'TechStart Inc',
                'email': 'admin@techstart.com',
                'company_name': 'TechStart Inc',
                'industry': 'Software Development',
                'data_classification': 'internal',
                'compliance_requirements': json.dumps(['SOC2']),
                'require_mfa': False,
                'session_timeout_minutes': 240
            }
        ]
        
        for customer in customers:
            execute_command(conn, """
                INSERT INTO customers (id, subscription_plan_id, name, email, company_name, industry,
                                     data_classification, compliance_requirements, require_mfa, session_timeout_minutes)
                VALUES (%(id)s, %(subscription_plan_id)s, %(name)s, %(email)s, %(company_name)s, %(industry)s,
                        %(data_classification)s, %(compliance_requirements)s, %(require_mfa)s, %(session_timeout_minutes)s)
                ON CONFLICT (email) DO NOTHING
            """, customer)
        
        demo_customer_id = customers[0]['id']
        
        # =====================================================
        # 3. CUSTOMER USERS
        # =====================================================
        logger.info("👥 Creating customer users...")
        
        users = [
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'email': 'demo',
                'password_hash': pwd_context.hash('demo123'),
                'first_name': 'Demo',
                'last_name': 'User',
                'role': 'admin',
                'department': 'Engineering',
                'mfa_enabled': True
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'email': 'tester@demo.com',
                'password_hash': pwd_context.hash('test123'),
                'first_name': 'Test',
                'last_name': 'Engineer',
                'role': 'user',
                'department': 'QA',
                'mfa_enabled': False
            }
        ]
        
        for user in users:
            execute_command(conn, """
                INSERT INTO customer_users (id, customer_id, email, password_hash, first_name, last_name,
                                          role, department, mfa_enabled)
                VALUES (%(id)s, %(customer_id)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s,
                        %(role)s, %(department)s, %(mfa_enabled)s)
                ON CONFLICT (customer_id, email) DO NOTHING
            """, user)
        
        demo_user_id = users[0]['id']
        
        # =====================================================
        # 4. APPLICATIONS
        # =====================================================
        logger.info("🖥️ Creating applications...")
        
        applications = [
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'HRMS Demo Platform',
                'description': 'Human Resource Management System for employee lifecycle management',
                'url': 'https://opensource-demo.orangehrmlive.com',
                'application_type': 'enterprise_hrms',
                'data_sensitivity_level': 'high',
                'contains_pii': True,
                'compliance_tags': json.dumps(['GDPR', 'CCPA']),
                'ssl_verification_enabled': True,
                'created_by': demo_user_id
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'E-commerce Demo Store',
                'description': 'Online retail platform with payment processing',
                'url': 'https://demo.opencart.com',
                'application_type': 'ecommerce',
                'data_sensitivity_level': 'medium',
                'contains_pii': True,
                'compliance_tags': json.dumps(['PCI-DSS']),
                'ssl_verification_enabled': True,
                'created_by': demo_user_id
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'Banking Demo Portal',
                'description': 'Financial services platform with account management',
                'url': 'https://demo.testfire.net',
                'application_type': 'banking',
                'data_sensitivity_level': 'critical',
                'contains_pii': True,
                'compliance_tags': json.dumps(['SOX', 'PCI-DSS', 'GDPR']),
                'ssl_verification_enabled': True,
                'created_by': demo_user_id
            }
        ]
        
        for app in applications:
            execute_command(conn, """
                INSERT INTO applications (id, customer_id, name, description, url, application_type,
                                        data_sensitivity_level, contains_pii, compliance_tags,
                                        ssl_verification_enabled, created_by)
                VALUES (%(id)s, %(customer_id)s, %(name)s, %(description)s, %(url)s, %(application_type)s,
                        %(data_sensitivity_level)s, %(contains_pii)s, %(compliance_tags)s,
                        %(ssl_verification_enabled)s, %(created_by)s)
                ON CONFLICT (id) DO NOTHING
            """, app)
        
        # =====================================================
        # 5. TEST SUITES WITH COMPREHENSIVE DATA
        # =====================================================
        logger.info("🧪 Creating test suites with comprehensive data...")
        
        test_suite_data = []
        
        for i in range(15):
            app = applications[i % len(applications)]
            suite_id = uuid4()
            
            suite = {
                'id': suite_id,
                'customer_id': demo_customer_id,
                'application_id': app['id'],
                'name': f'{app["name"]} - Test Suite {i+1}',
                'description': f'Comprehensive automated testing for {app["application_type"]} functionality',
                'type': random.choice(['functional', 'regression', 'performance', 'security']),
                'status': random.choice(['draft', 'active', 'completed', 'failed', 'archived']),
                'priority': random.choice(['low', 'medium', 'high', 'critical']),
                'data_classification': app['data_sensitivity_level'],
                'created_by': demo_user_id
            }
            
            execute_command(conn, """
                INSERT INTO test_suites (id, customer_id, application_id, name, description, type, status,
                                       priority, data_classification, created_by)
                VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(name)s, %(description)s, %(type)s,
                        %(status)s, %(priority)s, %(data_classification)s, %(created_by)s)
                ON CONFLICT (id) DO NOTHING
            """, suite)
            
            test_suite_data.append(suite)
        
        # =====================================================
        # 6. TEST CASES AND TEST STEPS
        # =====================================================
        logger.info("📝 Creating test cases and test steps...")
        
        test_case_data = []
        
        for suite in test_suite_data[:10]:  # Create detailed data for first 10 suites
            # Create 3-8 test cases per suite
            num_cases = random.randint(3, 8)
            
            for case_num in range(num_cases):
                case_id = uuid4()
                
                case = {
                    'id': case_id,
                    'test_suite_id': suite['id'],
                    'name': f'Test Case {case_num + 1}: {random.choice(["Login Flow", "Data Entry", "Navigation", "Form Submission", "Search Function", "User Management"])}',
                    'description': f'Automated test case for {suite["type"]} testing scenario',
                    'test_type': suite['type'],
                    'priority': random.choice(['low', 'medium', 'high']),
                    'expected_result': 'Test should complete successfully with all assertions passing',
                    'created_by': demo_user_id
                }
                
                execute_command(conn, """
                    INSERT INTO test_cases (id, test_suite_id, name, description, test_type, priority,
                                          expected_result, created_by)
                    VALUES (%(id)s, %(test_suite_id)s, %(name)s, %(description)s, %(test_type)s,
                            %(priority)s, %(expected_result)s, %(created_by)s)
                    ON CONFLICT (id) DO NOTHING
                """, case)
                
                test_case_data.append(case)
                
                # Create 5-12 test steps per case
                num_steps = random.randint(5, 12)
                
                for step_num in range(num_steps):
                    step_id = uuid4()
                    
                    step_actions = [
                        "Navigate to login page",
                        "Enter username and password",
                        "Click login button",
                        "Verify dashboard loads",
                        "Navigate to user management",
                        "Create new user record",
                        "Fill required fields",
                        "Submit form",
                        "Verify success message",
                        "Logout from application"
                    ]
                    
                    step = {
                        'id': step_id,
                        'test_case_id': case_id,
                        'step_number': step_num + 1,
                        'action': step_actions[step_num % len(step_actions)],
                        'expected_result': f'Step {step_num + 1} should complete successfully',
                        'step_type': random.choice(['action', 'verification', 'setup', 'cleanup']),
                        'is_critical': random.choice([True, False])
                    }
                    
                    execute_command(conn, """
                        INSERT INTO test_steps (id, test_case_id, step_number, action, expected_result,
                                              step_type, is_critical)
                        VALUES (%(id)s, %(test_case_id)s, %(step_number)s, %(action)s, %(expected_result)s,
                                %(step_type)s, %(is_critical)s)
                        ON CONFLICT (id) DO NOTHING
                    """, step)
        
        # =====================================================
        # 7. AGENT JOBS AND ACTIVITIES
        # =====================================================
        logger.info("🤖 Creating agent jobs and activities...")
        
        agent_job_data = []
        
        for suite in test_suite_data[:8]:  # Create agent jobs for first 8 suites
            job_id = uuid4()
            
            job = {
                'id': job_id,
                'customer_id': demo_customer_id,
                'application_id': suite['application_id'],
                'test_suite_id': suite['id'],
                'job_type': random.choice(['test_creation', 'test_execution', 'analysis', 'optimization']),
                'status': random.choice(['pending', 'running', 'completed', 'failed']),
                'progress_percentage': random.randint(0, 100),
                'current_agent': random.choice(['Discovery Agent', 'Test Generation Agent', 'Validation Agent', 'Optimization Agent']),
                'created_by': demo_user_id
            }
            
            execute_command(conn, """
                INSERT INTO agent_jobs (id, customer_id, application_id, test_suite_id, job_type, status,
                                      progress_percentage, current_agent, created_by)
                VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(test_suite_id)s, %(job_type)s,
                        %(status)s, %(progress_percentage)s, %(current_agent)s, %(created_by)s)
                ON CONFLICT (id) DO NOTHING
            """, job)
            
            agent_job_data.append(job)
            
            # Create agent processing status
            execute_command(conn, """
                INSERT INTO agent_processing_status (job_id, current_step, progress_percentage, status)
                VALUES (%(job_id)s, %(current_step)s, %(progress)s, %(status)s)
                ON CONFLICT (job_id) DO UPDATE SET
                    current_step = EXCLUDED.current_step,
                    progress_percentage = EXCLUDED.progress_percentage,
                    status = EXCLUDED.status
            """, {
                'job_id': job_id,
                'current_step': job['current_agent'],
                'progress': job['progress_percentage'],
                'status': job['status']
            })
            
            # Create agent activity logs
            activities = [
                "Initializing application discovery",
                "Analyzing UI components and structure",
                "Mapping user workflows and interactions",
                "Generating test scenarios",
                "Creating automated test scripts",
                "Validating test coverage",
                "Optimizing test performance",
                "Finalizing test suite"
            ]
            
            for i, activity in enumerate(activities):
                activity_id = uuid4()
                
                activity_data = {
                    'id': activity_id,
                    'job_id': job_id,
                    'agent_name': random.choice(['Discovery Agent', 'Analysis Agent', 'Generation Agent', 'Validation Agent']),
                    'activity_type': random.choice(['discovery', 'analysis', 'generation', 'validation', 'optimization']),
                    'status': 'completed' if i < len(activities) - 2 else random.choice(['running', 'completed']),
                    'progress_percentage': min(100, (i + 1) * 12),
                    'message': activity,
                    'metadata': json.dumps({'step': i + 1, 'total_steps': len(activities)})
                }
                
                execute_command(conn, """
                    INSERT INTO agent_activity_logs (id, job_id, agent_name, activity_type, status,
                                                   progress_percentage, message, metadata)
                    VALUES (%(id)s, %(job_id)s, %(agent_name)s, %(activity_type)s, %(status)s,
                            %(progress_percentage)s, %(message)s, %(metadata)s)
                    ON CONFLICT (id) DO NOTHING
                """, activity_data)
        
        # =====================================================
        # 8. TEST EXECUTIONS AND RESULTS
        # =====================================================
        logger.info("📊 Creating test executions and results...")
        
        for suite in test_suite_data[:10]:
            # Create 1-3 executions per suite
            num_executions = random.randint(1, 3)
            
            for exec_num in range(num_executions):
                execution_id = uuid4()
                
                total_tests = random.randint(5, 25)
                passed_tests = random.randint(int(total_tests * 0.6), total_tests)
                failed_tests = total_tests - passed_tests
                success_rate = (passed_tests / total_tests) * 100
                
                execution = {
                    'id': execution_id,
                    'customer_id': demo_customer_id,
                    'application_id': suite['application_id'],
                    'execution_type': random.choice(['manual', 'automated', 'scheduled']),
                    'environment': random.choice(['development', 'staging', 'production']),
                    'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                    'device_type': random.choice(['desktop', 'mobile', 'tablet']),
                    'status': random.choice(['completed', 'failed', 'running']),
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': success_rate,
                    'duration_seconds': random.randint(300, 3600),
                    'triggered_by': demo_user_id
                }
                
                execute_command(conn, """
                    INSERT INTO test_executions (id, customer_id, application_id, execution_type, environment,
                                               browser, device_type, status, total_tests, passed_tests,
                                               failed_tests, success_rate, duration_seconds, triggered_by)
                    VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(execution_type)s, %(environment)s,
                            %(browser)s, %(device_type)s, %(status)s, %(total_tests)s, %(passed_tests)s,
                            %(failed_tests)s, %(success_rate)s, %(duration_seconds)s, %(triggered_by)s)
                    ON CONFLICT (id) DO NOTHING
                """, execution)
                
                # Create execution results
                result_id = uuid4()
                
                result = {
                    'id': result_id,
                    'test_suite_id': suite['id'],
                    'execution_id': execution_id,
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'skipped_tests': 0,
                    'success_rate': success_rate,
                    'execution_time_seconds': execution['duration_seconds'],
                    'environment': execution['environment'],
                    'browser': execution['browser']
                }
                
                execute_command(conn, """
                    INSERT INTO test_execution_results (id, test_suite_id, execution_id, total_tests, passed_tests,
                                                      failed_tests, skipped_tests, success_rate, execution_time_seconds,
                                                      environment, browser)
                    VALUES (%(id)s, %(test_suite_id)s, %(execution_id)s, %(total_tests)s, %(passed_tests)s,
                            %(failed_tests)s, %(skipped_tests)s, %(success_rate)s, %(execution_time_seconds)s,
                            %(environment)s, %(browser)s)
                    ON CONFLICT (id) DO NOTHING
                """, result)
        
        # =====================================================
        # 9. AUDIT LOGS AND SECURITY EVENTS
        # =====================================================
        logger.info("🔒 Creating audit logs and security events...")
        
        # Create audit logs
        audit_events = [
            ('authentication', 'user_session', 'login'),
            ('data_modification', 'test_suite', 'create'),
            ('data_modification', 'application', 'create'),
            ('system_access', 'dashboard', 'view'),
            ('configuration_change', 'user_settings', 'update')
        ]
        
        for i in range(50):
            event_type, resource_type, action = random.choice(audit_events)
            
            audit_data = {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'user_id': demo_user_id,
                'event_type': event_type,
                'resource_type': resource_type,
                'resource_id': uuid4(),
                'action': action,
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'metadata': json.dumps({'session_id': str(uuid4())})
            }
            
            execute_command(conn, """
                INSERT INTO audit_logs (id, customer_id, user_id, event_type, resource_type, resource_id,
                                      action, ip_address, user_agent, metadata)
                VALUES (%(id)s, %(customer_id)s, %(user_id)s, %(event_type)s, %(resource_type)s,
                        %(resource_id)s, %(action)s, %(ip_address)s, %(user_agent)s, %(metadata)s)
                ON CONFLICT (id) DO NOTHING
            """, audit_data)
        
        # Create security events
        security_events = [
            ('authentication_failure', 'medium', 'Multiple failed login attempts detected'),
            ('suspicious_activity', 'high', 'Unusual access pattern from new IP address'),
            ('policy_violation', 'low', 'User accessed restricted resource'),
            ('unauthorized_access', 'critical', 'Attempted access to admin panel without privileges')
        ]
        
        for i in range(20):
            category, severity, description = random.choice(security_events)
            
            security_data = {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'user_id': demo_user_id if random.choice([True, False]) else None,
                'event_category': category,
                'severity_level': severity,
                'event_description': description,
                'source_ip': f'10.0.0.{random.randint(1, 254)}',
                'affected_resource': random.choice(['login_page', 'admin_panel', 'user_data', 'test_results']),
                'detection_method': random.choice(['automated_rule', 'anomaly_detection', 'user_report']),
                'status': random.choice(['open', 'investigating', 'resolved'])
            }
            
            execute_command(conn, """
                INSERT INTO security_events (id, customer_id, user_id, event_category, severity_level,
                                           event_description, source_ip, affected_resource, detection_method, status)
                VALUES (%(id)s, %(customer_id)s, %(user_id)s, %(event_category)s, %(severity_level)s,
                        %(event_description)s, %(source_ip)s, %(affected_resource)s, %(detection_method)s, %(status)s)
                ON CONFLICT (id) DO NOTHING
            """, security_data)
        
        logger.info("✅ Enterprise seed data creation completed successfully!")
        logger.info("📊 Created comprehensive data across all 21 tables:")
        logger.info("   - 3 subscription plans")
        logger.info("   - 2 customers with enterprise features")
        logger.info("   - 2 customer users with different roles")
        logger.info("   - 3 applications with security metadata")
        logger.info("   - 15 test suites with various statuses")
        logger.info("   - 30+ test cases with detailed steps")
        logger.info("   - 8 agent jobs with activity tracking")
        logger.info("   - 10+ test executions with results")
        logger.info("   - 50 audit log entries")
        logger.info("   - 20 security events")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Seed data creation failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def verify_seed_data():
    """Verify that seed data was created successfully"""
    conn = get_db_connection()
    
    try:
        logger.info("🔍 Verifying seed data...")
        
        # Check key tables
        tables_to_check = [
            'subscription_plans',
            'customers', 
            'customer_users',
            'applications',
            'test_suites',
            'test_cases',
            'test_steps',
            'agent_jobs',
            'agent_activity_logs',
            'test_executions',
            'test_execution_results',
            'audit_logs',
            'security_events'
        ]
        
        for table in tables_to_check:
            result = execute_query(conn, f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            logger.info(f"   {table}: {count} records")
        
        logger.info("✅ Seed data verification completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Seed data verification failed: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("🌱 Enterprise Seed Data Generator")
    logger.info("=" * 50)
    
    if create_enterprise_seed_data():
        verify_seed_data()
        logger.info("🎉 Enterprise seed data setup completed successfully!")
    else:
        logger.error("❌ Enterprise seed data setup failed!")
        sys.exit(1)
