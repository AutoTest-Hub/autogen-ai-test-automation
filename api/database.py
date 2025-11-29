"""
Database connection and models for SQLite
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'test_automation.db')

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

# Global database manager instance
db = DatabaseManager()

class Application:
    @staticmethod
    def create(user_id: int, name: str, url: str, app_type: str, 
               description: str = None, key_features: str = None, 
               user_flows: str = None) -> int:
        """Create a new application"""
        query = """
        INSERT INTO applications (user_id, name, url, type, description, key_features, user_flows)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return db.execute_insert(query, (user_id, name, url, app_type, description, key_features, user_flows))
    
    @staticmethod
    def get_by_user(user_id: int) -> List[Dict]:
        """Get all applications for a user"""
        query = "SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC"
        return db.execute_query(query, (user_id,))
    
    @staticmethod
    def get_by_id(app_id: int) -> Optional[Dict]:
        """Get application by ID"""
        query = "SELECT * FROM applications WHERE id = ?"
        results = db.execute_query(query, (app_id,))
        return results[0] if results else None

class TestSuite:
    @staticmethod
    def create(application_id: int, name: str, description: str, test_type: str) -> int:
        """Create a new test suite"""
        query = """
        INSERT INTO test_suites (application_id, name, description, type, status)
        VALUES (?, ?, ?, ?, 'draft')
        """
        return db.execute_insert(query, (application_id, name, description, test_type))
    
    @staticmethod
    def get_by_application(application_id: int) -> List[Dict]:
        """Get all test suites for an application"""
        query = """
        SELECT ts.*, a.name as application_name 
        FROM test_suites ts 
        JOIN applications a ON ts.application_id = a.id 
        WHERE ts.application_id = ? 
        ORDER BY ts.created_at DESC
        """
        return db.execute_query(query, (application_id,))
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Get all test suites with application info"""
        query = """
        SELECT ts.*, a.name as application_name, a.url as application_url
        FROM test_suites ts 
        JOIN applications a ON ts.application_id = a.id 
        ORDER BY ts.created_at DESC
        """
        return db.execute_query(query)
    
    @staticmethod
    def update_status(suite_id: int, status: str, success_rate: float = None) -> int:
        """Update test suite status and success rate"""
        if success_rate is not None:
            query = "UPDATE test_suites SET status = ?, success_rate = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            return db.execute_update(query, (status, success_rate, suite_id))
        else:
            query = "UPDATE test_suites SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            return db.execute_update(query, (status, suite_id))

class AgentJob:
    @staticmethod
    def create(application_id: int, job_type: str) -> int:
        """Create a new agent job"""
        query = """
        INSERT INTO agent_jobs (application_id, job_type, status, current_agent, started_at)
        VALUES (?, ?, 'pending', 'Discovery Agent', CURRENT_TIMESTAMP)
        """
        return db.execute_insert(query, (application_id, job_type))
    
    @staticmethod
    def update_progress(job_id: int, current_agent: str, progress: int, status: str = 'running') -> int:
        """Update job progress"""
        query = """
        UPDATE agent_jobs 
        SET current_agent = ?, progress_percentage = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        return db.execute_update(query, (current_agent, progress, status, job_id))
    
    @staticmethod
    def complete_job(job_id: int, status: str = 'completed') -> int:
        """Mark job as completed"""
        query = """
        UPDATE agent_jobs 
        SET status = ?, progress_percentage = 100, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        return db.execute_update(query, (status, job_id))
    
    @staticmethod
    def get_by_id(job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        query = "SELECT * FROM agent_jobs WHERE id = ?"
        results = db.execute_query(query, (job_id,))
        return results[0] if results else None

class AgentActivity:
    @staticmethod
    def create(job_id: int, agent_name: str, activity_type: str, status: str, 
               progress: int, message: str = None, details: Dict = None) -> int:
        """Create a new agent activity"""
        details_json = json.dumps(details) if details else None
        query = """
        INSERT INTO agent_activities (job_id, agent_name, activity_type, status, progress_percentage, message, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return db.execute_insert(query, (job_id, agent_name, activity_type, status, progress, message, details_json))
    
    @staticmethod
    def get_by_job(job_id: int) -> List[Dict]:
        """Get all activities for a job"""
        query = """
        SELECT * FROM agent_activities 
        WHERE job_id = ? 
        ORDER BY timestamp DESC
        """
        return db.execute_query(query, (job_id,))
    
    @staticmethod
    def get_recent(limit: int = 10) -> List[Dict]:
        """Get recent agent activities"""
        query = """
        SELECT aa.*, aj.job_type, a.name as application_name
        FROM agent_activities aa
        JOIN agent_jobs aj ON aa.job_id = aj.id
        JOIN applications a ON aj.application_id = a.id
        ORDER BY aa.timestamp DESC
        LIMIT ?
        """
        return db.execute_query(query, (limit,))
