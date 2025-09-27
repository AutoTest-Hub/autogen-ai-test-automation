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
    
    def connect(self, customer_id: str = None):
        """Establish database connection with optional customer context"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            
            # Set customer context for RLS if provided
            if customer_id:
                with self.connection.cursor() as cursor:
                    # Set customer context for RLS (using session variable)
                    cursor.execute("SET session.current_customer_id = %s", (customer_id,))
                logger.info(f"✅ Connected to PostgreSQL database with customer context: {customer_id}")
            else:
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
        try:
            logger.info(f"🔍 Getting applications for customer_id: {customer_id}")
            
            # Set customer context for RLS
            with db.connection.cursor() as cursor:
                cursor.execute("SET session.current_customer_id = %s", (str(customer_id),))
                cursor.execute("SET app.current_customer_id = %s", (str(customer_id),))
            
            query = """
            SELECT * FROM applications 
            WHERE customer_id = %s AND status = 'active'
            ORDER BY created_at DESC
            """
            result = db.execute_query(query, (customer_id,))
            logger.info(f"✅ Found {len(result)} applications for customer {customer_id}")
            return result
        except Exception as e:
            logger.error(f"❌ Error getting applications for customer {customer_id}: {e}")
            return []

class TestSuite:
    """Enhanced test suite management with full schema support"""
    
    @staticmethod
    def create(customer_id: UUID, application_id: UUID, name: str, description: str = None,
               test_type: str = 'functional', created_by: UUID = None) -> Optional[UUID]:
        """Create a new test suite"""
        suite_id = uuid4()
        query = """
        INSERT INTO test_suites (id, customer_id, application_id, name, description, test_type, status, created_by) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        try:
            result = db.execute_query(query, (
                suite_id, customer_id, application_id, name, description, test_type, 'draft', created_by
            ))
            return result[0]['id'] if result else None
        except Exception as e:
            logger.error(f"Failed to create test suite: {e}")
            return None
    
    @staticmethod
    def get_by_customer(customer_id: UUID) -> List[Dict]:
        """Get all test suites for a customer with application details"""
        try:
            logger.info(f"🔍 Getting test suites for customer_id: {customer_id}")
            
            # Set customer context for RLS
            with db.connection.cursor() as cursor:
                cursor.execute("SET session.current_customer_id = %s", (str(customer_id),))
            
            query = """
            SELECT 
                ts.*,
                a.name as application_name,
                a.url as application_url,
                0 as total_test_cases,
                0 as passed_test_cases,
                0 as failed_test_cases,
                0 as success_rate,
                NULL as last_run_at,
                0 as duration_minutes
            FROM test_suites ts
            JOIN applications a ON ts.application_id = a.id
            WHERE ts.customer_id = %s AND ts.is_deleted = false
            ORDER BY ts.created_at DESC
            """
            result = db.execute_query(query, (customer_id,))
            logger.info(f"🔍 Query returned {len(result) if result else 0} test suites")
            return result
        except Exception as e:
            logger.error(f"Failed to get test suites for customer {customer_id}: {e}")
            return []
    
    @staticmethod
    def update_status(suite_id: UUID, status: str):
        """Update test suite status"""
        query = "UPDATE test_suites SET status = %s WHERE id = %s"
        return db.execute_command(query, (status, suite_id))

class TestCase:
    """Test case management with file storage support"""
    
    @staticmethod
    def save_with_file_path(test_case_data: Dict) -> Optional[UUID]:
        """Save test case metadata with file path information"""
        test_case_id = test_case_data.get('id', uuid4())
        
        try:
            # Ensure database connection with customer context
            if not db.connection or db.connection.closed:
                db.connect(customer_id=str(test_case_data['customer_id']))
            else:
                # Set customer context for existing connection
                with db.connection.cursor() as cursor:
                    cursor.execute("SET session.current_customer_id = %s", (str(test_case_data['customer_id']),))
            
            query = """
            INSERT INTO test_cases (
                id, customer_id, test_suite_id, name, description, 
                test_file_path, config_file_path, generated_from_intent,
                generation_model, file_size_bytes, file_checksum,
                code_confidence_score, status, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            result = db.execute_query(query, (
                test_case_id,
                test_case_data['customer_id'],
                test_case_data['test_suite_id'],
                test_case_data['name'],
                test_case_data.get('description', ''),
                test_case_data.get('test_file_path'),
                test_case_data.get('config_file_path'),
                test_case_data.get('generated_from_intent'),
                test_case_data.get('generation_model', 'gpt-4'),
                test_case_data.get('file_size_bytes', 0),
                test_case_data.get('file_checksum'),
                test_case_data.get('code_confidence_score', 0.85),
                test_case_data.get('status', 'generated'),
                test_case_data.get('created_by')
            ))
            
            logger.info(f"✅ Saved test case metadata: {test_case_data['name']} → {test_case_data.get('test_file_path')}")
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to save test case metadata: {e}")
            logger.error(f"   Customer ID: {test_case_data.get('customer_id')}")
            logger.error(f"   Test Suite ID: {test_case_data.get('test_suite_id')}")
            return None
    
    @staticmethod
    def get_by_suite(suite_id: UUID) -> List[Dict]:
        """Get all test cases for a test suite"""
        query = """
        SELECT 
            id, name, description, test_file_path, config_file_path,
            generated_from_intent, generation_model, file_size_bytes,
            code_confidence_score, status, created_at, updated_at
        FROM test_cases 
        WHERE test_suite_id = %s AND is_deleted = false
        ORDER BY created_at ASC
        """
        return db.execute_query(query, (suite_id,))
    
    @staticmethod
    def update_file_path(test_case_id: UUID, file_path: str, file_size: int = None, checksum: str = None):
        """Update test case file path and metadata"""
        query = """
        UPDATE test_cases 
        SET test_file_path = %s, file_size_bytes = %s, file_checksum = %s, updated_at = NOW()
        WHERE id = %s
        """
        return db.execute_command(query, (file_path, file_size, checksum, test_case_id))
    
    @staticmethod
    def get_by_customer(customer_id: UUID) -> List[Dict]:
        """Get all test cases for a customer with suite information"""
        query = """
        SELECT 
            tc.id, tc.name, tc.description, tc.test_file_path,
            tc.generation_model, tc.code_confidence_score, tc.status,
            tc.created_at, ts.name as suite_name, a.name as application_name
        FROM test_cases tc
        JOIN test_suites ts ON tc.test_suite_id = ts.id
        JOIN applications a ON ts.application_id = a.id
        WHERE tc.customer_id = %s AND tc.is_deleted = false
        ORDER BY tc.created_at DESC
        """
        return db.execute_query(query, (customer_id,))

class TestExecutionResult:
    """Test execution results with file artifact tracking"""
    
    @staticmethod
    def save_execution_result(execution_data: Dict) -> Optional[UUID]:
        """Save test execution result with artifact paths"""
        execution_id = execution_data.get('id', uuid4())
        
        query = """
        INSERT INTO test_execution_results (
            id, test_case_id, execution_id, executed_by, execution_environment,
            browser, device_type, status, started_at, completed_at,
            duration_seconds, error_message, screenshot_path, video_path,
            logs_path, report_path, performance_metrics
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        try:
            result = db.execute_query(query, (
                execution_id,
                execution_data['test_case_id'],
                execution_data.get('execution_id'),
                execution_data.get('executed_by'),
                execution_data.get('execution_environment', 'local'),
                execution_data.get('browser', 'chromium'),
                execution_data.get('device_type', 'desktop'),
                execution_data['status'],
                execution_data.get('started_at'),
                execution_data.get('completed_at'),
                execution_data.get('duration_seconds'),
                execution_data.get('error_message'),
                execution_data.get('screenshot_path'),
                execution_data.get('video_path'),
                execution_data.get('logs_path'),
                execution_data.get('report_path'),
                json.dumps(execution_data.get('performance_metrics', {}))
            ))
            
            logger.info(f"✅ Saved execution result: {execution_data['status']} for test case {execution_data['test_case_id']}")
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to save execution result: {e}")
            return None
    
    @staticmethod
    def get_by_test_case(test_case_id: UUID, limit: int = 10) -> List[Dict]:
        """Get execution results for a test case"""
        query = """
        SELECT * FROM test_execution_results
        WHERE test_case_id = %s
        ORDER BY completed_at DESC
        LIMIT %s
        """
        return db.execute_query(query, (test_case_id, limit))

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
        """Get agent job with activities"""
        job_query = """
        SELECT * FROM agent_jobs
        WHERE id = %s
        """
        
        activities_query = """
        SELECT * FROM agent_job_activities
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
        return db.execute_command(job_query, (progress, current_agent, status, job_id))
    
    @staticmethod
    def add_activity(job_id: UUID, agent_name: str, activity_type: str, 
                    message: str, status: str = 'completed', progress: int = None):
        """Add agent activity log"""
        activity_id = uuid4()
        query = """
        INSERT INTO agent_job_activities (
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
        AVG(CASE WHEN ter.status = 'passed' THEN 100.0 ELSE 0.0 END) as avg_success_rate,
        COUNT(*) as total_results
    FROM test_execution_results ter
    JOIN test_cases tc ON ter.test_case_id = tc.id
    JOIN test_suites ts ON tc.test_suite_id = ts.id
    WHERE ts.customer_id = %s AND ter.executed_at > NOW() - INTERVAL '30 days'
    """
    success_result = db.execute_query(success_query, (customer_id,))
    if success_result and success_result[0]['total_results']:
        stats['avg_success_rate'] = float(success_result[0]['avg_success_rate'] or 0)
    else:
        stats['avg_success_rate'] = 0
    
    return stats

def initialize_database() -> bool:
    """Initialize database with comprehensive enterprise seed data"""
    try:
        if not db.connect():
            return False
        
        # Check if schema exists (verify we have the actual schema tables)
        tables_query = """
        SELECT COUNT(*) as table_count 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name IN (
            'customers', 'customer_users', 'applications', 'test_suites', 'test_cases',
            'agent_jobs', 'agent_job_activities', 'test_executions', 'audit_logs', 
            'security_events', 'subscription_plans', 'application_credentials'
        )
        """
        result = db.execute_query(tables_query)
        if not result or result[0]['table_count'] < 8:
            logger.warning("⚠️  Incomplete database schema found. Please run the complete schema files first.")
            logger.info("Expected core tables: customers, customer_users, applications, test_suites,")
            logger.info("                     agent_jobs, test_executions, audit_logs, security_events")
            return False
        
        logger.info(f"✅ Database schema verified ({result[0]['table_count']} core tables found)")
        
        # Check if comprehensive seed data already exists
        demo_customer = Customer.get_by_email('demo@example.com')
        if demo_customer:
            # Check if we have comprehensive data (not just basic)
            suites_query = "SELECT COUNT(*) as count FROM test_suites WHERE customer_id = %s"
            suites_result = db.execute_query(suites_query, (demo_customer['id'],))
            
            if suites_result and suites_result[0]['count'] >= 10:
                logger.info("✅ Comprehensive seed data already exists")
                return True
            else:
                logger.info("⚠️  Basic seed data found, but upgrading to comprehensive enterprise data...")
        
        # Try comprehensive enterprise seed data first, then fall back to minimal
        try:
            logger.info("🌱 Attempting comprehensive enterprise seed data...")
            
            # Import and run the corrected seed data creation
            from seed_data_corrected import create_corrected_seed_data
            
            if create_corrected_seed_data():
                logger.info("✅ Comprehensive enterprise seed data created successfully")
                return True
            else:
                logger.warning("⚠️  Comprehensive seed data failed, trying minimal approach...")
                
        except Exception as e:
            logger.warning(f"⚠️  Comprehensive seed data failed: {e}")
            logger.info("Trying minimal seed data approach...")
        
        # Fall back to minimal seed data
        try:
            from seed_data_minimal import create_minimal_seed_data
            
            if create_minimal_seed_data():
                logger.info("✅ Minimal seed data created successfully")
                logger.info("📊 Basic data includes:")
                logger.info("   - Subscription plans")
                logger.info("   - Demo customer and users")
                logger.info("   - Sample applications")
                logger.info("   - Test suites and agent jobs")
                return True
            else:
                logger.error("❌ Minimal seed data creation failed")
                return create_basic_seed_data()
                
        except Exception as e:
            logger.warning(f"⚠️  Minimal seed data failed: {e}")
            logger.info("Falling back to basic seed data creation...")
            return create_basic_seed_data()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def create_basic_seed_data() -> bool:
    """Create basic seed data as fallback"""
    try:
        logger.info("📦 Creating basic seed data...")
        
        # Create demo customer and user (basic version)
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
        
        logger.info("✅ Basic seed data creation completed")
        return True
        
    except Exception as e:
        logger.error(f"Basic seed data creation failed: {e}")
        return False
