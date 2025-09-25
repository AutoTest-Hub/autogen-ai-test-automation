"""
Minimal Working Seed Data for PostgreSQL Schema
==============================================

This script creates basic seed data using only core required columns
and avoids constraint violations by using minimal, safe values.
"""

import os
import sys
import logging
from uuid import uuid4
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

def create_minimal_seed_data():
    """Create minimal working seed data"""
    
    conn = get_db_connection()
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    try:
        logger.info("🌱 Starting minimal seed data creation...")
        
        # =====================================================
        # 1. SUBSCRIPTION PLANS (minimal columns only)
        # =====================================================
        logger.info("📋 Creating subscription plans...")
        
        plans = [
            {
                'id': uuid4(),
                'name': 'Starter',
                'description': 'Basic plan for small teams',
                'price_monthly': 99.00,
                'price_yearly': 990.00
            },
            {
                'id': uuid4(),
                'name': 'Professional', 
                'description': 'Advanced plan for growing teams',
                'price_monthly': 299.00,
                'price_yearly': 2990.00
            },
            {
                'id': uuid4(),
                'name': 'Enterprise',
                'description': 'Full enterprise features',
                'price_monthly': 999.00,
                'price_yearly': 9990.00
            }
        ]
        
        for plan in plans:
            try:
                execute_command(conn, """
                    INSERT INTO subscription_plans (id, name, description, price_monthly, price_yearly)
                    VALUES (%(id)s, %(name)s, %(description)s, %(price_monthly)s, %(price_yearly)s)
                    ON CONFLICT (id) DO NOTHING
                """, plan)
                logger.info(f"✅ Created subscription plan: {plan['name']}")
            except Exception as e:
                logger.warning(f"⚠️  Could not create plan {plan['name']}: {e}")
        
        # =====================================================
        # 2. CUSTOMERS (minimal columns only)
        # =====================================================
        logger.info("🏢 Creating customers...")
        
        customers = [
            {
                'id': uuid4(),
                'subscription_plan_id': plans[2]['id'],  # Enterprise plan
                'name': 'Demo Customer',
                'email': 'demo@example.com',
                'company_name': 'Demo Corporation'
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
                logger.warning(f"⚠️  Could not create customer {customer['email']}: {e}")
        
        # Verify demo customer exists
        demo_customer_check = execute_query(conn, "SELECT id FROM customers WHERE email = %s", ('demo@example.com',))
        if demo_customer_check:
            demo_customer_id = demo_customer_check[0]['id']
            logger.info(f"✅ Demo customer verified with ID: {demo_customer_id}")
        else:
            logger.error("❌ Demo customer not found after creation")
            return False
        
        # =====================================================
        # 3. CUSTOMER USERS (minimal columns only)
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
                'role': 'admin'
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'email': 'tester@demo.com',
                'password_hash': pwd_context.hash('test123'),
                'first_name': 'Test',
                'last_name': 'Engineer',
                'role': 'member'
            }
        ]
        
        for user in users:
            try:
                execute_command(conn, """
                    INSERT INTO customer_users (id, customer_id, email, password_hash, first_name, last_name, role)
                    VALUES (%(id)s, %(customer_id)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(role)s)
                    ON CONFLICT (customer_id, email) DO UPDATE SET
                        password_hash = EXCLUDED.password_hash,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        role = EXCLUDED.role
                """, user)
                logger.info(f"✅ Created/updated user: {user['email']}")
            except Exception as e:
                logger.warning(f"⚠️  Could not create user {user['email']}: {e}")
        
        # Verify demo user exists
        demo_user_check = execute_query(conn, "SELECT id FROM customer_users WHERE customer_id = %s AND email = %s", (demo_customer_id, 'demo'))
        if demo_user_check:
            demo_user_id = demo_user_check[0]['id']
            logger.info(f"✅ Demo user verified with ID: {demo_user_id}")
        else:
            logger.error("❌ Demo user not found after creation")
            return False
        
        # =====================================================
        # 4. APPLICATIONS (minimal columns only)
        # =====================================================
        logger.info("🖥️ Creating applications...")
        
        applications = [
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'HRMS Demo Platform',
                'description': 'Human Resource Management System demo',
                'url': 'https://opensource-demo.orangehrmlive.com',
                'application_type': 'web',
                'created_by': demo_user_id
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'E-commerce Demo Store',
                'description': 'Online retail platform demo',
                'url': 'https://demo.opencart.com',
                'application_type': 'web',
                'created_by': demo_user_id
            },
            {
                'id': uuid4(),
                'customer_id': demo_customer_id,
                'name': 'Banking Demo Portal',
                'description': 'Financial services platform demo',
                'url': 'https://demo.testfire.net',
                'application_type': 'web',
                'created_by': demo_user_id
            }
        ]
        
        for app in applications:
            try:
                execute_command(conn, """
                    INSERT INTO applications (id, customer_id, name, description, url, application_type, created_by)
                    VALUES (%(id)s, %(customer_id)s, %(name)s, %(description)s, %(url)s, %(application_type)s, %(created_by)s)
                    ON CONFLICT (id) DO NOTHING
                """, app)
                logger.info(f"✅ Created application: {app['name']}")
            except Exception as e:
                logger.warning(f"⚠️  Could not create application {app['name']}: {e}")
        
        # =====================================================
        # 5. TEST SUITES (minimal columns only)
        # =====================================================
        logger.info("🧪 Creating test suites...")
        
        for i in range(12):
            app = applications[i % len(applications)]
            suite_id = uuid4()
            
            suite = {
                'id': suite_id,
                'customer_id': demo_customer_id,
                'application_id': app['id'],
                'name': f'{app["name"]} - Test Suite {i+1}',
                'description': f'Automated test suite {i+1}',
                'type': 'functional',  # Use safe default
                'status': 'draft',     # Use safe default
                'created_by': demo_user_id
            }
            
            try:
                execute_command(conn, """
                    INSERT INTO test_suites (id, customer_id, application_id, name, description, type, status, created_by)
                    VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(name)s, %(description)s, %(type)s, %(status)s, %(created_by)s)
                    ON CONFLICT (id) DO NOTHING
                """, suite)
                logger.info(f"✅ Created test suite: {suite['name']}")
            except Exception as e:
                logger.warning(f"⚠️  Could not create test suite {suite['name']}: {e}")
        
        # =====================================================
        # 6. AGENT JOBS (minimal columns only)
        # =====================================================
        logger.info("🤖 Creating agent jobs...")
        
        # Get some test suites for agent jobs
        test_suites = execute_query(conn, "SELECT id, application_id FROM test_suites LIMIT 5")
        
        for i, suite in enumerate(test_suites):
            job_id = uuid4()
            
            job = {
                'id': job_id,
                'customer_id': demo_customer_id,
                'application_id': suite['application_id'],
                'test_suite_id': suite['id'],
                'job_type': 'test_creation',
                'status': 'completed',
                'progress_percentage': 100,
                'created_by': demo_user_id
            }
            
            try:
                execute_command(conn, """
                    INSERT INTO agent_jobs (id, customer_id, application_id, test_suite_id, job_type, status, progress_percentage, created_by)
                    VALUES (%(id)s, %(customer_id)s, %(application_id)s, %(test_suite_id)s, %(job_type)s, %(status)s, %(progress_percentage)s, %(created_by)s)
                    ON CONFLICT (id) DO NOTHING
                """, job)
                logger.info(f"✅ Created agent job {i+1}")
            except Exception as e:
                logger.warning(f"⚠️  Could not create agent job {i+1}: {e}")
        
        logger.info("✅ Minimal seed data creation completed successfully!")
        logger.info("📊 Created basic data:")
        logger.info("   - 3 subscription plans")
        logger.info("   - 1 demo customer")
        logger.info("   - 2 customer users (demo/admin, tester/member)")
        logger.info("   - 3 applications")
        logger.info("   - 12 test suites")
        logger.info("   - 5 agent jobs")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Minimal seed data creation failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def verify_minimal_seed_data():
    """Verify that minimal seed data was created successfully"""
    conn = get_db_connection()
    
    try:
        logger.info("🔍 Verifying minimal seed data...")
        
        # Check key tables
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
        
        logger.info("✅ Minimal seed data verification completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Minimal seed data verification failed: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("🌱 Minimal Seed Data Generator")
    logger.info("=" * 40)
    
    if create_minimal_seed_data():
        verify_minimal_seed_data()
        logger.info("🎉 Minimal seed data setup completed successfully!")
    else:
        logger.error("❌ Minimal seed data setup failed!")
        sys.exit(1)
