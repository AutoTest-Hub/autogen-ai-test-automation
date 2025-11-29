"""
Helper functions for TestSuite and TestCase operations
"""
from typing import Dict, Any, Optional
from database_postgres_full import db
import logging

logger = logging.getLogger(__name__)

class TestSuiteHelper:
    """Helper class for TestSuite operations"""
    
    @staticmethod
    def get_by_id(suite_id: str) -> Optional[Dict[str, Any]]:
        """Get test suite by ID"""
        try:
            query = """
                SELECT ts.*, a.name as application_name, a.url as application_url
                FROM test_suites ts
                JOIN applications a ON ts.application_id = a.id
                WHERE ts.id = %s AND ts.is_deleted = false
            """
            result = db.execute_query(query, (suite_id,))
            
            if result and len(result) > 0:
                # Convert tuple to dictionary
                columns = ['id', 'customer_id', 'application_id', 'name', 'description', 
                          'test_type', 'status', 'created_by', 'created_at', 'updated_at', 
                          'is_deleted', 'application_name', 'application_url']
                return dict(zip(columns, result[0]))
            return None
            
        except Exception as e:
            logger.error(f"Failed to get test suite {suite_id}: {e}")
            return None

class TestCaseHelper:
    """Helper class for TestCase operations"""
    
    @staticmethod
    def get_by_id(case_id: str) -> Optional[Dict[str, Any]]:
        """Get test case by ID"""
        try:
            query = """
                SELECT tc.*, ts.name as suite_name
                FROM test_cases tc
                JOIN test_suites ts ON tc.test_suite_id = ts.id
                WHERE tc.id = %s
            """
            result = db.execute_query(query, (case_id,))
            
            if result and len(result) > 0:
                # Convert tuple to dictionary
                columns = ['id', 'test_suite_id', 'name', 'description', 'test_steps', 
                          'expected_result', 'status', 'created_at', 'updated_at', 'suite_name']
                return dict(zip(columns, result[0]))
            return None
            
        except Exception as e:
            logger.error(f"Failed to get test case {case_id}: {e}")
            return None
