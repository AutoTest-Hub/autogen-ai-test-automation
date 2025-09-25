"""
Corrected Enterprise Seed Data Generator for Actual 21-Table Schema
==================================================================

This script creates comprehensive seed data that matches the actual PostgreSQL schema
structure with correct column names and relationships.
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

def create_corrected_seed_data():
    """Create comprehensive seed data matching actual schema"""
    
    conn = get_db_connection()
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    try:
        logger.info("🌱 Starting corrected enterprise seed data creation...")
        
        # Note: Working with existing RLS policies - data will be created with proper ownership
        
        # =====================================================
        # 1. SUBSCRIPTION PLANS (using actual columns)
        # =====================================================
        logger.info("📋 Creating subscription plans...")
        
        plans = [
            {
                'id': uuid4(),
                'name': 'Starter',
                'description': 'Perfect for small teams getting started with AI testing',
                'price_monthly': 99.00,
                'price_yearly': 990.00,
                'api_calls_limit': 5000,
                'applications_limit': 3,
                'concurrent_tests_limit': 2,
                'features': json.dumps(['basic_testing', 'email_support']),
                'security_tier': 'standard'
            },
            {
                'id': uuid4(),
                'name': 'Professional',
                'description': 'Advanced features for growing development teams',
                'price_monthly': 299.00,
                'price_yearly': 2990.00,
                'api_calls_limit': 25000,
                'applications_limit': 15,
                'concurrent_tests_limit': 10,
                'features': json.dumps(['advanced_testing', 'priority_support', 'analytics']),
                'security_tier': 'enhanced'
            },
            {
                'id': uuid4(),
                'name': 'Enterprise',
                'description': 'Full enterprise features with SOC 2 compliance',
                'price_monthly': 999.00,
                'price_yearly': 9990.00,
                'api_calls_limit': 100000,
                'applications_limit': 50,
                'concurrent_tests_limit': 50,
                'features': json.dumps(['enterprise_testing', 'dedicated_support', 'soc2_compliance', 'custom_integrations']),
                'security_tier': 'enterprise'
            }
        ]
        
        for plan in plans:
            execute_command(conn, """
                INSERT INTO subscription_plans (id, name, description, price_monthly, price_yearly, 
                                              api_calls_limit, applications_limit, concurrent_tests_limit, 
                                              features, security_tier)
                VALUES (%(id)s, %(name)s, %(description)s, %(price_monthly)s, %(price_yearly)s,
                        %(api_calls_limit)s, %(applications_limit)s, %(concurrent_tests_limit)s,
                        %(features)s, %(security_tier)s)
                ON CONFLICT (id) DO NOTHING
            """, plan)
        
        # =====================================================
        # 2. CUSTOMERS (check actual columns first)
        # =====================================================
        logger.info("🏢 Creating customers...")
        
        # Check what columns exist in customers table
        customer_columns = execute_query(conn, """
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'customers' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        logger.info(f"Customer table columns: {[col['column_name'] for col in customer_columns]}")
        
        # Create customers with only existing columns
        customers = [
            {
                'id': uuid4(),
                'subscription_plan_id': plans[2]['id'],  # Enterprise plan
                'name': 'Demo Customer',
                'email': 'demo@example.com',
                'company_name': 'Demo Corporation'
            },
            {
                'id': uuid4(),
                'subscription_plan_id': plans[1]['id'],  # Professional plan
                'name': 'TechStart Inc',
                'email': 'admin@techstart.com',
                'company_name': 'TechStart Inc'
            }
        ]
        
        for customer in customers:
            try:
                execute_command(conn, """
                    INSERT INTO customers (id, subscription_plan_id, name, email, company_name)
                    VALUES (%(id)s, %(subscription_plan_id)s, %(name)s, %(email)s, %(company_name)s)
                    ON CONFLICT (email) DO UPDATE SET
                        subscription_plan_id = EXCLUDED.subscription_plan_id,
                        name = EXCLUDED.name,
                        company_name = EXCLUDED.company_name
                """, customer)
                logger.info(f"✅ Created/updated customer: {customer['email']}")
            except Exception as e:
                logger.error(f"❌ Failed to create customer {customer['email']}: {e}")
                raise
        
        # Verify demo customer exists
        demo_customer_check = execute_query(conn, "SELECT id FROM customers WHERE email = %s", ('demo@example.com',))
        if demo_customer_check:
            demo_customer_id = demo_customer_check[0]['id']
            logger.info(f"✅ Demo customer verified with ID: {demo_customer_id}")
        else:
            logger.error("❌ Demo customer not found after creation")
            raise Exception("Demo customer creation failed")
        
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
                'role': 'admin'  # Valid role: admin, member, viewer, api_only
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'email': 'tester@demo.com',
                'password_hash': pwd_context.hash('test123'),
                'first_name': 'Test',
                'last_name': 'Engineer',
                'role': 'member'  # Changed from 'user' to 'member' (valid role)
            }
        ]
        
        for user in users:
            execute_command(conn, """
                INSERT INTO customer_users (id, customer_id, email, password_hash, first_name, last_name, role)
                VALUES (%(id)s, %(customer_id)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(role)s)
                ON CONFLICT (customer_id, email) DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    role = EXCLUDED.role
            """, user)
        
        # Verify demo user exists and get actual ID
        demo_user_check = execute_query(conn, "SELECT id FROM customer_users WHERE customer_id = %s AND email = %s", (demo_customer_id, 'demo'))
        if demo_user_check:
            demo_user_id = demo_user_check[0]['id']
            logger.info(f"✅ Demo user verified with ID: {demo_user_id}")
        else:
            logger.error("❌ Demo user not found after creation")
            raise Exception("Demo user creation failed")
        
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
                'created_by': demo_user_id
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'E-commerce Demo Store',
                'description': 'Online retail platform with payment processing',
                'url': 'https://demo.opencart.com',
                'application_type': 'ecommerce',
                'created_by': demo_user_id
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'Banking Demo Portal',
                'description': 'Financial services platform with account management',
                'url': 'https://demo.testfire.net',
                'application_type': 'banking',
                'created_by': demo_user_id
            }
        ]
        
        for app in applications:
            execute_command(conn, """
                INSERT INTO applications (id, customer_id, name, description, url, application_type, created_by)
                VALUES (%(id)s, %(customer_id)s, %(name)s, %(description)s, %(url)s, %(application_type)s, %(created_by)s)
                ON CONFLICT (id) DO NOTHING
            """, app)
        
        # =====================================================
        # 5. TEST SUITES
        # =====================================================
        logger.info("🧪 Creating test suites...")
        
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
                'type': random.choice(['functional', 'performance', 'security', 'accessibility', 'api']),
                'status': random.choice(['draft', 'active', 'completed', 'failed']),
                'created_by': demo_user_id
            }
            
            execute_command(conn, """
                INSERT INTO test_suites (id, customer_id, application_id, name, description, type, status, created_by)
                VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(name)s, %(description)s, %(type)s, %(status)s, %(created_by)s)
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
                    'expected_result': 'Test should complete successfully with all assertions passing',
                    'created_by': demo_user_id
                }
                
                execute_command(conn, """
                    INSERT INTO test_cases (id, test_suite_id, name, description, expected_result, created_by)
                    VALUES (%(id)s, %(test_suite_id)s, %(name)s, %(description)s, %(expected_result)s, %(created_by)s)
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
                        'expected_result': f'Step {step_num + 1} should complete successfully'
                    }
                    
                    execute_command(conn, """
                        INSERT INTO test_steps (id, test_case_id, step_number, action, expected_result)
                        VALUES (%(id)s, %(test_case_id)s, %(step_number)s, %(action)s, %(expected_result)s)
                        ON CONFLICT (id) DO NOTHING
                    """, step)
        
        # =====================================================
        # 7. AGENT JOBS AND ACTIVITIES
        # =====================================================
        logger.info("🤖 Creating agent jobs and activities...")
        
        for suite in test_suite_data[:8]:  # Create agent jobs for first 8 suites
            job_id = uuid4()
            
            job = {
                'id': job_id,
                'customer_id': demo_customer_id,
                'application_id': suite['application_id'],
                'test_suite_id': suite['id'],
                'job_type': random.choice(['test_creation', 'test_execution', 'analysis']),
                'status': random.choice(['pending', 'running', 'completed', 'failed']),
                'progress_percentage': random.randint(0, 100),
                'created_by': demo_user_id
            }
            
            execute_command(conn, """
                INSERT INTO agent_jobs (id, customer_id, application_id, test_suite_id, job_type, status, progress_percentage, created_by)
                VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(test_suite_id)s, %(job_type)s, %(status)s, %(progress_percentage)s, %(created_by)s)
                ON CONFLICT (id) DO NOTHING
            """, job)
            
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
                    'activity_type': random.choice(['discovery', 'analysis', 'generation', 'validation']),
                    'status': 'completed' if i < len(activities) - 2 else random.choice(['running', 'completed']),
                    'progress_percentage': min(100, (i + 1) * 12),
                    'message': activity
                }
                
                execute_command(conn, """
                    INSERT INTO agent_activity_logs (id, job_id, agent_name, activity_type, status, progress_percentage, message)
                    VALUES (%(id)s, %(job_id)s, %(agent_name)s, %(activity_type)s, %(status)s, %(progress_percentage)s, %(message)s)
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
                    'status': random.choice(['completed', 'failed', 'running']),
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': success_rate,
                    'duration_seconds': random.randint(300, 3600),
                    'triggered_by': demo_user_id
                }
                
                execute_command(conn, """
                    INSERT INTO test_executions (id, customer_id, application_id, status, total_tests, passed_tests, failed_tests, success_rate, duration_seconds, triggered_by)
                    VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(status)s, %(total_tests)s, %(passed_tests)s, %(failed_tests)s, %(success_rate)s, %(duration_seconds)s, %(triggered_by)s)
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
                    'success_rate': success_rate,
                    'execution_time_seconds': execution['duration_seconds']
                }
                
                execute_command(conn, """
                    INSERT INTO test_execution_results (id, test_suite_id, execution_id, total_tests, passed_tests, failed_tests, success_rate, execution_time_seconds)
                    VALUES (%(id)s, %(test_suite_id)s, %(execution_id)s, %(total_tests)s, %(passed_tests)s, %(failed_tests)s, %(success_rate)s, %(execution_time_seconds)s)
                    ON CONFLICT (id) DO NOTHING
                """, result)
        
        # =====================================================
        # 9. AUDIT LOGS
        # =====================================================
        logger.info("🔒 Creating audit logs...")
        
        # Create audit logs
        for i in range(30):
            audit_data = {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'user_id': demo_user_id,
                'event_type': random.choice(['authentication', 'data_modification', 'system_access']),
                'resource_type': random.choice(['user_session', 'test_suite', 'application']),
                'resource_id': uuid4(),
                'action': random.choice(['login', 'create', 'update', 'view']),
                'ip_address': f'192.168.1.{random.randint(1, 254)}'
            }
            
            execute_command(conn, """
                INSERT INTO audit_logs (id, customer_id, user_id, event_type, resource_type, resource_id, action, ip_address)
                VALUES (%(id)s, %(customer_id)s, %(user_id)s, %(event_type)s, %(resource_type)s, %(resource_id)s, %(action)s, %(ip_address)s)
                ON CONFLICT (id) DO NOTHING
            """, audit_data)
        
        # Seed data creation completed with RLS policies intact
        
        logger.info("✅ Corrected enterprise seed data creation completed successfully!")
        logger.info("📊 Created comprehensive data across all available tables:")
        logger.info("   - 3 subscription plans with actual column structure")
        logger.info("   - 2 customers with enterprise features")
        logger.info("   - 2 customer users with different roles")
        logger.info("   - 3 applications with detailed information")
        logger.info("   - 15 test suites with various statuses")
        logger.info("   - 30+ test cases with detailed steps")
        logger.info("   - 8 agent jobs with activity tracking")
        logger.info("   - 10+ test executions with results")
        logger.info("   - 30 audit log entries")
        
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
        
        # Check key tables that we know exist
        tables_to_check = [
            'subscription_plans',
            'customers', 
            'customer_users',
            'applications',
            'test_suites',
            'agent_jobs'
        ]
        
        for table in tables_to_check:
            try:
                result = execute_query(conn, f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count'] if result else 0
                logger.info(f"   {table}: {count} records")
            except Exception as e:
                logger.warning(f"   {table}: Could not check ({e})")
        
        logger.info("✅ Seed data verification completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Seed data verification failed: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("🌱 Corrected Enterprise Seed Data Generator")
    logger.info("=" * 50)
    
    if create_corrected_seed_data():
        verify_seed_data()
        logger.info("🎉 Corrected enterprise seed data setup completed successfully!")
    else:
        logger.error("❌ Corrected enterprise seed data setup failed!")
        sys.exit(1)
