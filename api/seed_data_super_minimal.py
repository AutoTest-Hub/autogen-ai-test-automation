"""
Super Minimal Seed Data for PostgreSQL Schema
=============================================

This script creates the absolute minimum seed data required for the platform
to function, using only the most basic columns and avoiding all potential
permission and constraint issues.
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
    """Get database connection with autocommit for individual operations"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True  # Avoid transaction issues
    return conn

def execute_query(conn, query, params=None):
    """Execute query and return results"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return []
    except Exception as e:
        logger.warning(f"Query failed: {e}")
        return []

def execute_command(conn, command, params=None):
    """Execute command (INSERT, UPDATE, DELETE) with individual error handling"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(command, params)
            return True
    except Exception as e:
        logger.warning(f"Command failed: {e}")
        return False

def create_super_minimal_seed_data():
    """Create super minimal seed data that works with any schema configuration"""
    
    conn = get_db_connection()
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    try:
        logger.info("🌱 Starting super minimal seed data creation...")
        
        # =====================================================
        # 1. SUBSCRIPTION PLANS (absolute minimum)
        # =====================================================
        logger.info("📋 Creating subscription plans...")
        
        plan_id = uuid4()
        success = execute_command(conn, """
            INSERT INTO subscription_plans (id, name, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (plan_id, 'Enterprise', 'Enterprise plan'))
        
        if success:
            logger.info("✅ Created subscription plan: Enterprise")
        else:
            # Try to get existing plan
            existing_plans = execute_query(conn, "SELECT id FROM subscription_plans LIMIT 1")
            if existing_plans:
                plan_id = existing_plans[0]['id']
                logger.info("✅ Using existing subscription plan")
            else:
                logger.error("❌ Could not create or find subscription plan")
                return False
        
        # =====================================================
        # 2. CUSTOMERS (absolute minimum)
        # =====================================================
        logger.info("🏢 Creating customers...")
        
        customer_id = uuid4()
        success = execute_command(conn, """
            INSERT INTO customers (id, subscription_plan_id, name, email, company_name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                subscription_plan_id = EXCLUDED.subscription_plan_id,
                name = EXCLUDED.name,
                company_name = EXCLUDED.company_name
        """, (customer_id, plan_id, 'Demo Customer', 'demo@example.com', 'Demo Corporation'))
        
        # Always get the actual customer_id from database
        existing_customers = execute_query(conn, "SELECT id FROM customers WHERE email = %s", ('demo@example.com',))
        if existing_customers:
            customer_id = existing_customers[0]['id']
            logger.info("✅ Customer verified with ID: " + str(customer_id))
        else:
            logger.error("❌ Could not find customer after creation")
            return False
        
        # =====================================================
        # 3. CUSTOMER USERS (absolute minimum)
        # =====================================================
        logger.info("👥 Creating customer users...")
        
        user_id = uuid4()
        password_hash = pwd_context.hash('demo123')
        
        success = execute_command(conn, """
            INSERT INTO customer_users (id, customer_id, email, password_hash, first_name, last_name, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id, email) DO UPDATE SET
                password_hash = EXCLUDED.password_hash,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                role = EXCLUDED.role
        """, (user_id, customer_id, 'demo', password_hash, 'Demo', 'User', 'admin'))
        
        # Always get the actual user_id from database
        existing_users = execute_query(conn, "SELECT id FROM customer_users WHERE customer_id = %s AND email = %s", (customer_id, 'demo'))
        if existing_users:
            user_id = existing_users[0]['id']
            logger.info("✅ User verified with ID: " + str(user_id))
        else:
            logger.error("❌ Could not find user after creation")
            return False
        
        # =====================================================
        # 4. APPLICATIONS (absolute minimum)
        # =====================================================
        logger.info("🖥️ Creating applications...")
        
        app_id = uuid4()
        success = execute_command(conn, """
            INSERT INTO applications (id, customer_id, name, description, url, application_type, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (app_id, customer_id, 'Demo Application', 'Demo application for testing', 'https://demo.example.com', 'web', user_id))
        
        if success:
            logger.info("✅ Created application: Demo Application")
        else:
            # Try to get existing application
            existing_apps = execute_query(conn, "SELECT id FROM applications WHERE customer_id = %s LIMIT 1", (customer_id,))
            if existing_apps:
                app_id = existing_apps[0]['id']
                logger.info("✅ Using existing application")
            else:
                logger.warning("⚠️  Could not create application, but continuing...")
                app_id = None
        
        # =====================================================
        # 5. TEST SUITES (only if application exists)
        # =====================================================
        if app_id:
            logger.info("🧪 Creating test suites...")
            
            # Try with minimal columns first
            suite_id = uuid4()
            success = execute_command(conn, """
                INSERT INTO test_suites (id, customer_id, application_id, name, description, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (suite_id, customer_id, app_id, 'Demo Test Suite', 'Demo test suite for testing', user_id))
            
            if success:
                logger.info("✅ Created test suite: Demo Test Suite")
            else:
                logger.warning("⚠️  Could not create test suite, but continuing...")
        
        # =====================================================
        # VERIFICATION
        # =====================================================
        logger.info("🔍 Verifying super minimal seed data...")
        
        # Check key data exists
        customers_count = execute_query(conn, "SELECT COUNT(*) as count FROM customers WHERE email = %s", ('demo@example.com',))
        users_count = execute_query(conn, "SELECT COUNT(*) as count FROM customer_users WHERE customer_id = %s", (customer_id,))
        
        if customers_count and customers_count[0]['count'] > 0:
            logger.info("✅ Demo customer exists")
        else:
            logger.error("❌ Demo customer missing")
            return False
            
        if users_count and users_count[0]['count'] > 0:
            logger.info("✅ Demo user exists")
        else:
            logger.error("❌ Demo user missing")
            return False
        
        logger.info("✅ Super minimal seed data creation completed successfully!")
        logger.info("📊 Created essential data:")
        logger.info("   - 1 subscription plan (Enterprise)")
        logger.info("   - 1 demo customer (demo@example.com)")
        logger.info("   - 1 demo user (demo/admin)")
        logger.info("   - 1 demo application (if permissions allow)")
        logger.info("   - 1 demo test suite (if permissions allow)")
        logger.info("")
        logger.info("🎯 Ready for login:")
        logger.info("   Username: demo")
        logger.info("   Password: demo123")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Super minimal seed data creation failed: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("🌱 Super Minimal Seed Data Generator")
    logger.info("=" * 50)
    
    if create_super_minimal_seed_data():
        logger.info("🎉 Super minimal seed data setup completed successfully!")
    else:
        logger.error("❌ Super minimal seed data setup failed!")
        sys.exit(1)
