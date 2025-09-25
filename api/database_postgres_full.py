"""
PostgreSQL Database Models - Full Enterprise Schema (21 Tables)
==============================================================

Updated to work with the complete enterprise schema including:
- 21 tables with full agent and test management
- Granular test step tracking
- Comprehensive agent activity logging
- Real-time processing status
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import register_adapter, AsIs
import json

# Register UUID adapter for psycopg2
def adapt_uuid(uuid_obj):
    return AsIs(f"'{uuid_obj}'")

register_adapter(UUID, adapt_uuid)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """PostgreSQL database manager for full enterprise schema"""
    
    def __init__(self):
        self.connection = None
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'test_automation_platform'),
            'user': os.getenv('DB_USER', 'app_user'),
            'password': os.getenv('DB_PASSWORD', 'app_password')
        }
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a query and return results"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                return []
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """Execute a command (INSERT, UPDATE, DELETE)"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(command, params)
                return True
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False

# Global database instance
db = DatabaseManager()

class Customer:
    """Customer management with full enterprise features"""
    
    @staticmethod
    def create(name: str, email: str, company_name: str = None) -> Optional[UUID]:
        """Create a new customer"""
        customer_id = uuid4()
        query = """
        INSERT INTO customers (id, name, email, company_name, subscription_status)
        VALUES (%s, %s, %s, %s, 'active')
        RETURNING id
        """
        try:
            result = db.execute_query(query, (customer_id, name, email, company_name))
            return result[0]['id'] if result else None
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """Get customer by email"""
        query = """
        SELECT c.*, sp.name as subscription_plan_name
        FROM customers c
        LEFT JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
        WHERE c.email = %s AND c.is_active = true
        """
        result = db.execute_query(query, (email,))
        return result[0] if result else None

class CustomerUser:
    """Enhanced user management with full authentication features"""
    
    @staticmethod
    def create(customer_id: UUID, email: str, password_hash: str, 
               first_name: str = None, last_name: str = None, role: str = 'user') -> Optional[UUID]:
        """Create a new customer user"""
        user_id = uuid4()
        query = """
        INSERT INTO customer_users (
            id, customer_id, email, password_hash, first_name, last_name, role
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        try:
            result = db.execute_query(query, (user_id, customer_id, email, password_hash, 
                                            first_name, last_name, role))
            return result[0]['id'] if result else None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """Get user by email with customer information"""
        query = """
        SELECT cu.*, c.name as customer_name, c.company_name
        FROM customer_users cu
        JOIN customers c ON cu.customer_id = c.id
        WHERE cu.email = %s AND cu.is_active = true AND c.is_active = true
        """
        result = db.execute_query(query, (email,))
        return result[0] if result else None
    
    @staticmethod
    def update_login_info(user_id: UUID, ip_address: str):
        """Update user login information"""
        query = """
        UPDATE customer_users 
        SET last_login_at = NOW(), last_login_ip = %s
        WHERE id = %s
        """
        return db.execute_command(query, (ip_address, user_id))

class Application:
    """Application management with enhanced security features"""
    
    @staticmethod
    def create(customer_id: UUID, name: str, url: str, application_type: str,
               description: str = None, created_by: UUID = None) -> Optional[UUID]:
        """Create a new application"""
        app_id = uuid4()
        query = """
        INSERT INTO applications (
            id, customer_id, name, url, application_type, description, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        try:
            result = db.execute_query(query, (app_id, customer_id, name, url, 
                                            application_type, description, created_by))
            return result[0]['id'] if result else None
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            return None
    
    @staticmethod
    def get_by_customer(customer_id: UUID) -> List[Dict]:
        """Get all applications for a customer"""
        query = """
        SELECT * FROM applications 
        WHERE customer_id = %s AND status = 'active'
        ORDER BY created_at DESC
        """
        return db.execute_query(query, (customer_id,))

class TestSuite:
    """Enhanced test suite management with full schema support"""
    
    @staticmethod
    def create(customer_id: UUID, application_id: UUID, name: str, description: str = None,
               test_type: str = 'functional', created_by: UUID = None) -> Optional[UUID]:
        """Create a new test suite"""
        suite_id = uuid4()
        query = """
        INSERT INTO test_suites (
            id, customer_id, application_id, name, description, type, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        try:
            result = db.execute_query(query, (suite_id, customer_id, application_id, 
                                            name, description, test_type, created_by))
            return result[0]['id'] if result else None
        except Exception as e:
            logger.error(f"Failed to create test suite: {e}")
            return None
    
    @staticmethod
    def get_by_customer(customer_id: UUID) -> List[Dict]:
        """Get all test suites for a customer with application details"""
        query = """
        SELECT 
            ts.*,
            a.name as application_name,
            a.url as application_url,
            COALESCE(ter.total_tests, 0) as total_test_cases,
            COALESCE(ter.passed_tests, 0) as passed_test_cases,
            COALESCE(ter.failed_tests, 0) as failed_test_cases,
            COALESCE(ter.success_rate, 0) as success_rate,
            ter.completed_at as last_run_at,
            EXTRACT(EPOCH FROM (ter.completed_at - ter.started_at))/60 as duration_minutes
        FROM test_suites ts
        JOIN applications a ON ts.application_id = a.id
        LEFT JOIN LATERAL (
            SELECT * FROM test_execution_results ter2
            WHERE ter2.test_suite_id = ts.id
            ORDER BY ter2.completed_at DESC
            LIMIT 1
        ) ter ON true
        WHERE ts.customer_id = %s AND ts.is_deleted = false
        ORDER BY ts.created_at DESC
        """
        return db.execute_query(query, (customer_id,))
    
    @staticmethod
    def update_status(suite_id: UUID, status: str):
        """Update test suite status"""
        query = "UPDATE test_suites SET status = %s WHERE id = %s"
        return db.execute_command(query, (status, suite_id))

class AgentJob:
    """Enhanced agent job management with full activity tracking"""
    
    @staticmethod
    def create(customer_id: UUID, application_id: UUID, job_type: str,
               test_suite_id: UUID = None, created_by: UUID = None) -> Optional[UUID]:
        """Create a new agent job"""
        job_id = uuid4()
        query = """
        INSERT INTO agent_jobs (
            id, customer_id, application_id, test_suite_id, job_type, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        try:
            result = db.execute_query(query, (job_id, customer_id, application_id, 
                                            test_suite_id, job_type, created_by))
            return result[0]['id'] if result else None
        except Exception as e:
            logger.error(f"Failed to create agent job: {e}")
            return None
    
    @staticmethod
    def get_by_id(job_id: UUID) -> Optional[Dict]:
        """Get agent job with activities and processing status"""
        job_query = """
        SELECT aj.*, aps.current_step, aps.progress_percentage as current_progress
        FROM agent_jobs aj
        LEFT JOIN agent_processing_status aps ON aj.id = aps.job_id
        WHERE aj.id = %s
        """
        
        activities_query = """
        SELECT * FROM agent_activity_logs
        WHERE job_id = %s
        ORDER BY created_at ASC
        """
        
        job_result = db.execute_query(job_query, (job_id,))
        activities_result = db.execute_query(activities_query, (job_id,))
        
        if job_result:
            return {
                'job': job_result[0],
                'activities': activities_result
            }
        return None
    
    @staticmethod
    def update_progress(job_id: UUID, progress: int, current_agent: str = None, status: str = None):
        """Update agent job progress"""
        # Update main job
        job_query = """
        UPDATE agent_jobs 
        SET progress_percentage = %s, current_agent = %s, status = COALESCE(%s, status),
            updated_at = NOW()
        WHERE id = %s
        """
        db.execute_command(job_query, (progress, current_agent, status, job_id))
        
        # Update processing status
        status_query = """
        INSERT INTO agent_processing_status (job_id, current_step, progress_percentage)
        VALUES (%s, %s, %s)
        ON CONFLICT (job_id) DO UPDATE SET
            current_step = EXCLUDED.current_step,
            progress_percentage = EXCLUDED.progress_percentage,
            updated_at = NOW()
        """
        return db.execute_command(status_query, (job_id, current_agent, progress))
    
    @staticmethod
    def add_activity(job_id: UUID, agent_name: str, activity_type: str, 
                    message: str, status: str = 'completed', progress: int = None):
        """Add agent activity log"""
        activity_id = uuid4()
        query = """
        INSERT INTO agent_activity_logs (
            id, job_id, agent_name, activity_type, status, progress_percentage, message
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return db.execute_command(query, (activity_id, job_id, agent_name, 
                                        activity_type, status, progress, message))

class AuditLog:
    """Comprehensive audit logging for SOC 2 compliance"""
    
    @staticmethod
    def log_event(customer_id: UUID, user_id: UUID = None, event_type: str = 'system_access',
                  resource_type: str = 'system', resource_id: UUID = None, action: str = 'access',
                  ip_address: str = None, metadata: Dict = None, old_values: Dict = None, 
                  new_values: Dict = None):
        """Log an audit event"""
        log_id = uuid4()
        query = """
        INSERT INTO audit_logs (
            id, customer_id, user_id, event_type, resource_type, resource_id, 
            action, ip_address, metadata, old_values, new_values
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return db.execute_command(query, (
            log_id, customer_id, user_id, event_type, resource_type, resource_id,
            action, ip_address, json.dumps(metadata or {}), 
            json.dumps(old_values or {}), json.dumps(new_values or {})
        ))

def get_dashboard_stats(customer_id: UUID) -> Dict:
    """Get comprehensive dashboard statistics"""
    stats = {}
    
    # Test suites count
    suites_query = """
    SELECT 
        COUNT(*) as total_suites,
        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_suites,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_suites
    FROM test_suites 
    WHERE customer_id = %s AND is_deleted = false
    """
    suites_result = db.execute_query(suites_query, (customer_id,))
    if suites_result:
        stats.update(suites_result[0])
    
    # Applications count
    apps_query = "SELECT COUNT(*) as total_applications FROM applications WHERE customer_id = %s"
    apps_result = db.execute_query(apps_query, (customer_id,))
    if apps_result:
        stats.update(apps_result[0])
    
    # Recent executions
    executions_query = """
    SELECT COUNT(*) as recent_executions
    FROM test_executions 
    WHERE customer_id = %s AND created_at > NOW() - INTERVAL '30 days'
    """
    exec_result = db.execute_query(executions_query, (customer_id,))
    if exec_result:
        stats.update(exec_result[0])
    
    # Success rate
    success_query = """
    SELECT 
        AVG(success_rate) as avg_success_rate,
        COUNT(*) as total_results
    FROM test_execution_results ter
    JOIN test_suites ts ON ter.test_suite_id = ts.id
    WHERE ts.customer_id = %s AND ter.completed_at > NOW() - INTERVAL '30 days'
    """
    success_result = db.execute_query(success_query, (customer_id,))
    if success_result and success_result[0]['total_results']:
        stats['avg_success_rate'] = float(success_result[0]['avg_success_rate'] or 0)
    else:
        stats['avg_success_rate'] = 0
    
    return stats

def initialize_database() -> bool:
    """Initialize database with sample data"""
    try:
        if not db.connect():
            return False
        
        # Check if schema exists
        tables_query = """
        SELECT COUNT(*) as table_count 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name IN ('customers', 'customer_users')
        """
        result = db.execute_query(tables_query)
        if not result or result[0]['table_count'] < 2:
            logger.warning("⚠️  Database schema not found. Please run the schema.sql file first.")
            logger.info("Run: sudo -u postgres psql -d test_automation_platform -f /path/to/schema.sql")
            return False
        
        logger.info("✅ Database schema verified")
        
        # Check if demo customer exists
        demo_customer = Customer.get_by_email('demo@example.com')
        if demo_customer:
            logger.info("✅ Demo customer already exists")
            return True
        
        # Create demo customer and user
        from passlib.context import CryptContext
        
        customer_id = Customer.create(
            name='Demo Customer',
            email='demo@example.com',
            company_name='Demo Company'
        )
        
        if customer_id:
            pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
            password_hash = pwd_context.hash('demo123')
            
            user_id = CustomerUser.create(
                customer_id=customer_id,
                email='demo',
                password_hash=password_hash,
                first_name='Demo',
                last_name='User',
                role='admin'
            )
            
            if user_id:
                # Create sample applications
                app1_id = Application.create(
                    customer_id=customer_id,
                    name='HRMS Demo',
                    url='https://opensource-demo.orangehrmlive.com',
                    application_type='enterprise_hrms',
                    description='Human Resource Management System Demo',
                    created_by=user_id
                )
                
                app2_id = Application.create(
                    customer_id=customer_id,
                    name='E-commerce Demo',
                    url='https://demo.opencart.com',
                    application_type='ecommerce',
                    description='E-commerce Platform Demo',
                    created_by=user_id
                )
                
                if app1_id and app2_id:
                    # Create sample test suites
                    for i in range(12):
                        suite_name = f'Test Suite {i+1}'
                        app_id = app1_id if i % 2 == 0 else app2_id
                        
                        suite_id = TestSuite.create(
                            customer_id=customer_id,
                            application_id=app_id,
                            name=suite_name,
                            description=f'Automated test suite {i+1}',
                            test_type='functional',
                            created_by=user_id
                        )
                        
                        if suite_id and i < 8:  # Update some suites with different statuses
                            if i < 4:
                                TestSuite.update_status(suite_id, 'completed')
                            elif i < 6:
                                TestSuite.update_status(suite_id, 'running')
                            else:
                                TestSuite.update_status(suite_id, 'failed')
        
        logger.info("✅ Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
