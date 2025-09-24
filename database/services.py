"""
Database service layer for AI Test Automation SaaS Platform
Provides high-level database operations and business logic
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from .models import (
    Customer, CustomerUser, SubscriptionPlan, Application, ApplicationCredential,
    TestCreationRequest, AgentActivity, TestSuite, TestCase, TestExecution,
    TestResult, CustomerAnalytics, ApiUsageLog
)

class CustomerService:
    """Service for customer management operations"""
    
    @staticmethod
    def create_customer(db: Session, customer_data: Dict[str, Any]) -> Customer:
        """Create a new customer"""
        customer = Customer(**customer_data)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
        """Get customer by email"""
        return db.query(Customer).filter(Customer.email == email).first()
    
    @staticmethod
    def get_customer_by_id(db: Session, customer_id: uuid.UUID) -> Optional[Customer]:
        """Get customer by ID"""
        return db.query(Customer).filter(Customer.id == customer_id).first()
    
    @staticmethod
    def update_api_usage(db: Session, customer_id: uuid.UUID, calls_used: int = 1):
        """Update customer API usage"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.api_calls_used += calls_used
            db.commit()
    
    @staticmethod
    def get_customer_analytics(db: Session, customer_id: uuid.UUID, days: int = 30) -> List[CustomerAnalytics]:
        """Get customer analytics for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.query(CustomerAnalytics).filter(
            and_(
                CustomerAnalytics.customer_id == customer_id,
                CustomerAnalytics.metric_date >= start_date
            )
        ).order_by(CustomerAnalytics.metric_date).all()

class ApplicationService:
    """Service for application management operations"""
    
    @staticmethod
    def create_application(db: Session, application_data: Dict[str, Any]) -> Application:
        """Create a new application"""
        application = Application(**application_data)
        db.add(application)
        db.commit()
        db.refresh(application)
        return application
    
    @staticmethod
    def get_customer_applications(db: Session, customer_id: uuid.UUID) -> List[Application]:
        """Get all applications for a customer"""
        return db.query(Application).filter(
            Application.customer_id == customer_id
        ).order_by(desc(Application.created_at)).all()
    
    @staticmethod
    def get_application_by_id(db: Session, application_id: uuid.UUID) -> Optional[Application]:
        """Get application by ID"""
        return db.query(Application).filter(Application.id == application_id).first()
    
    @staticmethod
    def update_application_status(db: Session, application_id: uuid.UUID, status: str):
        """Update application status"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if application:
            application.status = status
            application.updated_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def add_application_credentials(db: Session, credential_data: Dict[str, Any]) -> ApplicationCredential:
        """Add credentials for an application"""
        credential = ApplicationCredential(**credential_data)
        db.add(credential)
        db.commit()
        db.refresh(credential)
        return credential

class TestCreationService:
    """Service for test creation operations"""
    
    @staticmethod
    def create_test_request(db: Session, request_data: Dict[str, Any]) -> TestCreationRequest:
        """Create a new test creation request"""
        request = TestCreationRequest(**request_data)
        db.add(request)
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def get_test_request_by_id(db: Session, request_id: uuid.UUID) -> Optional[TestCreationRequest]:
        """Get test creation request by ID"""
        return db.query(TestCreationRequest).filter(TestCreationRequest.id == request_id).first()
    
    @staticmethod
    def update_test_request_progress(db: Session, request_id: uuid.UUID, 
                                   progress: int, current_agent: str = None):
        """Update test creation request progress"""
        request = db.query(TestCreationRequest).filter(TestCreationRequest.id == request_id).first()
        if request:
            request.progress_percentage = progress
            if current_agent:
                request.current_agent = current_agent
            request.updated_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def add_agent_activity(db: Session, activity_data: Dict[str, Any]) -> AgentActivity:
        """Add agent activity log"""
        activity = AgentActivity(**activity_data)
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def get_agent_activities(db: Session, request_id: uuid.UUID) -> List[AgentActivity]:
        """Get all agent activities for a test creation request"""
        return db.query(AgentActivity).filter(
            AgentActivity.test_creation_request_id == request_id
        ).order_by(AgentActivity.timestamp).all()
    
    @staticmethod
    def create_test_suite(db: Session, suite_data: Dict[str, Any]) -> TestSuite:
        """Create a new test suite"""
        suite = TestSuite(**suite_data)
        db.add(suite)
        db.commit()
        db.refresh(suite)
        return suite
    
    @staticmethod
    def add_test_case(db: Session, case_data: Dict[str, Any]) -> TestCase:
        """Add a test case to a suite"""
        case = TestCase(**case_data)
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

class TestExecutionService:
    """Service for test execution operations"""
    
    @staticmethod
    def create_test_execution(db: Session, execution_data: Dict[str, Any]) -> TestExecution:
        """Create a new test execution"""
        execution = TestExecution(**execution_data)
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution
    
    @staticmethod
    def get_customer_executions(db: Session, customer_id: uuid.UUID, 
                              limit: int = 50) -> List[TestExecution]:
        """Get recent test executions for a customer"""
        return db.query(TestExecution).filter(
            TestExecution.customer_id == customer_id
        ).order_by(desc(TestExecution.created_at)).limit(limit).all()
    
    @staticmethod
    def update_execution_status(db: Session, execution_id: uuid.UUID, 
                              status: str, **kwargs):
        """Update test execution status and metrics"""
        execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
        if execution:
            execution.status = status
            for key, value in kwargs.items():
                if hasattr(execution, key):
                    setattr(execution, key, value)
            db.commit()
    
    @staticmethod
    def add_test_result(db: Session, result_data: Dict[str, Any]) -> TestResult:
        """Add a test result"""
        result = TestResult(**result_data)
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
    
    @staticmethod
    def get_execution_results(db: Session, execution_id: uuid.UUID) -> List[TestResult]:
        """Get all results for a test execution"""
        return db.query(TestResult).filter(
            TestResult.test_execution_id == execution_id
        ).order_by(TestResult.created_at).all()

class AnalyticsService:
    """Service for analytics and reporting operations"""
    
    @staticmethod
    def update_daily_analytics(db: Session, customer_id: uuid.UUID, date: datetime = None):
        """Update daily analytics for a customer"""
        if not date:
            date = datetime.utcnow().date()
        
        # Get or create analytics record for the date
        analytics = db.query(CustomerAnalytics).filter(
            and_(
                CustomerAnalytics.customer_id == customer_id,
                CustomerAnalytics.metric_date == date
            )
        ).first()
        
        if not analytics:
            analytics = CustomerAnalytics(
                customer_id=customer_id,
                metric_date=date
            )
            db.add(analytics)
        
        # Calculate metrics for the day
        executions = db.query(TestExecution).filter(
            and_(
                TestExecution.customer_id == customer_id,
                func.date(TestExecution.created_at) == date
            )
        ).all()
        
        analytics.total_executions = len(executions)
        analytics.total_tests_run = sum(e.total_tests or 0 for e in executions)
        analytics.total_tests_passed = sum(e.passed_tests or 0 for e in executions)
        analytics.total_tests_failed = sum(e.failed_tests or 0 for e in executions)
        analytics.total_duration_minutes = sum(e.duration_seconds or 0 for e in executions) // 60
        
        if analytics.total_tests_run > 0:
            analytics.average_success_rate = (analytics.total_tests_passed / analytics.total_tests_run) * 100
        
        # Count unique applications tested
        app_ids = set(e.application_id for e in executions if e.application_id)
        analytics.applications_tested = len(app_ids)
        
        # Get API usage for the day
        api_usage = db.query(func.count(ApiUsageLog.id)).filter(
            and_(
                ApiUsageLog.customer_id == customer_id,
                func.date(ApiUsageLog.created_at) == date
            )
        ).scalar()
        analytics.api_calls_used = api_usage or 0
        
        db.commit()
        return analytics
    
    @staticmethod
    def get_customer_dashboard_stats(db: Session, customer_id: uuid.UUID) -> Dict[str, Any]:
        """Get dashboard statistics for a customer"""
        # Get customer info
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {}
        
        # Get application count
        app_count = db.query(func.count(Application.id)).filter(
            Application.customer_id == customer_id
        ).scalar()
        
        # Get recent executions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_executions = db.query(TestExecution).filter(
            and_(
                TestExecution.customer_id == customer_id,
                TestExecution.created_at >= thirty_days_ago
            )
        ).all()
        
        total_tests = sum(e.total_tests or 0 for e in recent_executions)
        passed_tests = sum(e.passed_tests or 0 for e in recent_executions)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Get API usage percentage
        plan_limit = customer.subscription_plan.api_calls_limit if customer.subscription_plan else 1000
        usage_percentage = (customer.api_calls_used / plan_limit * 100) if plan_limit > 0 else 0
        
        return {
            'applications_count': app_count,
            'total_executions': len(recent_executions),
            'total_tests': total_tests,
            'success_rate': round(success_rate, 1),
            'api_calls_used': customer.api_calls_used,
            'api_calls_limit': plan_limit,
            'api_usage_percentage': round(usage_percentage, 1),
            'subscription_status': customer.subscription_status,
            'plan_name': customer.subscription_plan.name if customer.subscription_plan else 'Free'
        }
    
    @staticmethod
    def log_api_usage(db: Session, log_data: Dict[str, Any]):
        """Log API usage"""
        log = ApiUsageLog(**log_data)
        db.add(log)
        db.commit()

class RealtimeService:
    """Service for real-time operations and WebSocket support"""
    
    @staticmethod
    def get_active_test_requests(db: Session, customer_id: uuid.UUID) -> List[TestCreationRequest]:
        """Get active test creation requests for real-time monitoring"""
        return db.query(TestCreationRequest).filter(
            and_(
                TestCreationRequest.customer_id == customer_id,
                TestCreationRequest.status.in_(['pending', 'processing'])
            )
        ).all()
    
    @staticmethod
    def get_running_executions(db: Session, customer_id: uuid.UUID) -> List[TestExecution]:
        """Get running test executions for real-time monitoring"""
        return db.query(TestExecution).filter(
            and_(
                TestExecution.customer_id == customer_id,
                TestExecution.status.in_(['pending', 'running'])
            )
        ).all()
    
    @staticmethod
    def get_recent_agent_activities(db: Session, request_id: uuid.UUID, 
                                  since: datetime = None) -> List[AgentActivity]:
        """Get recent agent activities for real-time updates"""
        query = db.query(AgentActivity).filter(
            AgentActivity.test_creation_request_id == request_id
        )
        
        if since:
            query = query.filter(AgentActivity.timestamp > since)
        
        return query.order_by(desc(AgentActivity.timestamp)).limit(50).all()

# Utility functions for common operations
def get_customer_with_stats(db: Session, customer_id: uuid.UUID) -> Dict[str, Any]:
    """Get customer with comprehensive statistics"""
    customer = CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        return None
    
    stats = AnalyticsService.get_customer_dashboard_stats(db, customer_id)
    
    return {
        'customer': customer,
        'stats': stats
    }

def create_sample_data(db: Session):
    """Create sample data for development/testing"""
    # Create subscription plans
    starter_plan = SubscriptionPlan(
        name="Starter",
        description="Perfect for small teams",
        price_monthly=29.00,
        api_calls_limit=1000,
        applications_limit=3,
        concurrent_tests_limit=2,
        features=["basic_reporting", "email_support"]
    )
    db.add(starter_plan)
    db.commit()
    
    # Create sample customer
    customer = Customer(
        name="Demo Customer",
        email="demo@example.com",
        company_name="Demo Company",
        industry="Technology",
        subscription_plan_id=starter_plan.id,
        subscription_status="active"
    )
    db.add(customer)
    db.commit()
    
    # Create sample application
    application = Application(
        customer_id=customer.id,
        name="E-commerce Store",
        description="Main customer-facing store",
        url="https://demo.example.com",
        application_type="ecommerce"
    )
    db.add(application)
    db.commit()
    
    print("Sample data created successfully!")
