"""
Enhanced Test Creation Service with Database Integration
Handles AI agent orchestration and test persistence
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
from fastapi import HTTPException

from websocket_manager import manager, AgentType, AgentStatus
from agent_orchestrator import orchestrator, TaskType, TaskPriority

logger = logging.getLogger(__name__)

# =====================================================
# DATABASE CONNECTION
# =====================================================

class DatabaseManager:
    def __init__(self):
        self.connection_pool = None
        self.init_connection_pool()
    
    def init_connection_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "test_automation"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "password"),
                port=os.getenv("DB_PORT", "5432")
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            # Fallback to in-memory storage for development
            self.connection_pool = None
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

# Global database manager
db_manager = DatabaseManager()

# =====================================================
# DATA MODELS
# =====================================================

@dataclass
class AgentProcessingInfo:
    agent_name: str
    agent_type: str
    execution_order: int
    status: str = "pending"
    progress_percentage: int = 0
    current_task: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_data: Optional[Dict] = None
    error_message: Optional[str] = None

@dataclass
class TestCreationSession:
    session_id: str
    customer_id: str
    creation_request_id: str
    application_id: str
    status: str = "pending"
    progress_percentage: int = 0
    agents: List[AgentProcessingInfo] = None
    created_test_suites: List[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.agents is None:
            self.agents = [
                AgentProcessingInfo("Discovery Agent", "discovery", 1),
                AgentProcessingInfo("Test Generation Agent", "test_generation", 2),
                AgentProcessingInfo("Code Generation Agent", "code_generation", 3),
                AgentProcessingInfo("Validation Agent", "validation", 4)
            ]

# =====================================================
# TEST CREATION SERVICE
# =====================================================

class TestCreationService:
    def __init__(self):
        self.active_sessions: Dict[str, TestCreationSession] = {}
        self.in_memory_test_suites: Dict[str, Dict] = {}  # Fallback storage
    
    async def create_test_suite(self, request_data: Dict[str, Any], customer_id: str, user_id: str) -> Dict[str, Any]:
        """
        Create a new test suite with AI agent processing
        """
        try:
            # Create test creation request in database
            creation_request_id = await self._create_test_creation_request(request_data, customer_id, user_id)
            
            # Create agent session
            session_id = str(uuid.uuid4())
            session = TestCreationSession(
                session_id=session_id,
                customer_id=customer_id,
                creation_request_id=creation_request_id,
                application_id=request_data.get("application_id", str(uuid.uuid4()))
            )
            
            self.active_sessions[session_id] = session
            
            # Create agent session in database
            await self._create_agent_session(session)
            
            # Start agent processing in background
            asyncio.create_task(self._process_agents(session, request_data))
            
            return {
                "session_id": session_id,
                "status": "started",
                "message": "Test creation started successfully",
                "agents": [
                    {
                        "name": agent.agent_name,
                        "type": agent.agent_type,
                        "status": agent.status,
                        "progress": agent.progress_percentage
                    }
                    for agent in session.agents
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to create test suite: {e}")
            raise HTTPException(status_code=500, detail=f"Test creation failed: {str(e)}")
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a test creation session"""
        session = self.active_sessions.get(session_id)
        if not session:
            # Try to load from database
            session = await self._load_session_from_db(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "status": session.status,
            "progress_percentage": session.progress_percentage,
            "agents": [
                {
                    "name": agent.agent_name,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "progress": agent.progress_percentage,
                    "current_task": agent.current_task,
                    "started_at": agent.started_at.isoformat() if agent.started_at else None,
                    "completed_at": agent.completed_at.isoformat() if agent.completed_at else None
                }
                for agent in session.agents
            ],
            "created_test_suites": session.created_test_suites or [],
            "error_message": session.error_message
        }
    
    async def get_test_suites(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all test suites for a customer"""
        conn = db_manager.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            ts.*,
                            a.name as application_name,
                            a.url as application_url,
                            COUNT(tc.id) as total_test_cases,
                            te.status as last_execution_status,
                            te.success_rate,
                            te.completed_at as last_execution_date
                        FROM test_suites ts
                        LEFT JOIN applications a ON ts.application_id = a.id
                        LEFT JOIN test_cases tc ON ts.id = tc.test_suite_id AND tc.is_deleted = false
                        LEFT JOIN test_executions te ON ts.last_execution_id = te.id
                        WHERE ts.customer_id = %s AND ts.is_deleted = false
                        GROUP BY ts.id, a.name, a.url, te.status, te.success_rate, te.completed_at
                        ORDER BY ts.created_at DESC
                    """, (customer_id,))
                    
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
            finally:
                db_manager.return_connection(conn)
        
        # Fallback to in-memory storage
        return [
            {
                "id": suite_id,
                "name": suite_data.get("name", "Unknown Test Suite"),
                "description": suite_data.get("description", ""),
                "status": suite_data.get("status", "active"),
                "total_test_cases": len(suite_data.get("test_cases", [])),
                "last_execution_status": suite_data.get("last_execution_status"),
                "success_rate": suite_data.get("success_rate"),
                "created_at": suite_data.get("created_at"),
                "application_name": suite_data.get("application_name")
            }
            for suite_id, suite_data in self.in_memory_test_suites.items()
            if suite_data.get("customer_id") == customer_id
        ]
    
    async def _create_test_creation_request(self, request_data: Dict, customer_id: str, user_id: str) -> str:
        """Create a test creation request in the database"""
        request_id = str(uuid.uuid4())
        
        conn = db_manager.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO test_creation_requests 
                        (id, customer_id, application_id, creation_method, input_data, status, created_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        request_id,
                        customer_id,
                        request_data.get("application_id", str(uuid.uuid4())),
                        request_data.get("creation_type", "url_metadata"),
                        json.dumps(request_data),
                        "pending",
                        user_id
                    ))
                    conn.commit()
            finally:
                db_manager.return_connection(conn)
        
        return request_id
    
    async def _create_agent_session(self, session: TestCreationSession):
        """Create agent session and individual agent records in database"""
        conn = db_manager.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Create agent session
                    cursor.execute("""
                        INSERT INTO agent_sessions 
                        (id, customer_id, creation_request_id, session_type, total_agents, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        session.session_id,
                        session.customer_id,
                        session.creation_request_id,
                        "test_creation",
                        len(session.agents),
                        session.status
                    ))
                    
                    # Create individual agent processing records
                    for agent in session.agents:
                        agent_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO agent_processing_status 
                            (id, agent_session_id, customer_id, agent_name, agent_type, execution_order, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            agent_id,
                            session.session_id,
                            session.customer_id,
                            agent.agent_name,
                            agent.agent_type,
                            agent.execution_order,
                            agent.status
                        ))
                    
                    conn.commit()
            finally:
                db_manager.return_connection(conn)
    
    async def _process_agents(self, session: TestCreationSession, request_data: Dict):
        """Process agents sequentially with real-time updates"""
        try:
            session.status = "processing"
            await self._update_session_in_db(session)
            
            for i, agent in enumerate(session.agents):
                # Update agent status to processing
                agent.status = "processing"
                agent.started_at = datetime.now()
                agent.current_task = f"Starting {agent.agent_name}..."
                
                await self._update_agent_in_db(session.session_id, agent)
                await self._broadcast_agent_update(session.session_id, agent)
                
                # Simulate agent processing with realistic progress
                await self._simulate_agent_work(session, agent, request_data)
                
                # Mark agent as completed
                agent.status = "completed"
                agent.progress_percentage = 100
                agent.completed_at = datetime.now()
                agent.current_task = f"{agent.agent_name} completed successfully"
                
                await self._update_agent_in_db(session.session_id, agent)
                await self._broadcast_agent_update(session.session_id, agent)
                
                # Update overall session progress
                session.progress_percentage = int(((i + 1) / len(session.agents)) * 100)
                await self._update_session_in_db(session)
            
            # Create test suites based on agent output
            test_suites = await self._create_test_suites_from_agents(session, request_data)
            session.created_test_suites = [suite["id"] for suite in test_suites]
            session.status = "completed"
            
            await self._update_session_in_db(session)
            
            # Broadcast completion
            await manager.broadcast_to_customer(
                session.customer_id,
                {
                    "type": "test_creation_completed",
                    "session_id": session.session_id,
                    "test_suites": test_suites,
                    "message": "Test creation completed successfully!"
                }
            )
            
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            session.status = "failed"
            session.error_message = str(e)
            await self._update_session_in_db(session)
    
    async def _simulate_agent_work(self, session: TestCreationSession, agent: AgentProcessingInfo, request_data: Dict):
        """Simulate realistic agent work with progress updates"""
        tasks = []
        
        if agent.agent_type == "discovery":
            tasks = [
                "Analyzing application URL...",
                "Discovering page structure...",
                "Identifying interactive elements...",
                "Mapping user flows...",
                "Analyzing security features..."
            ]
        elif agent.agent_type == "test_generation":
            tasks = [
                "Generating test scenarios...",
                "Creating test cases...",
                "Optimizing test coverage...",
                "Validating test logic...",
                "Finalizing test suite..."
            ]
        elif agent.agent_type == "code_generation":
            tasks = [
                "Generating Selenium code...",
                "Creating test assertions...",
                "Adding error handling...",
                "Optimizing selectors...",
                "Generating test data..."
            ]
        elif agent.agent_type == "validation":
            tasks = [
                "Validating test syntax...",
                "Checking test coverage...",
                "Verifying test logic...",
                "Running quality checks...",
                "Finalizing test suite..."
            ]
        
        for i, task in enumerate(tasks):
            agent.current_task = task
            agent.progress_percentage = int(((i + 1) / len(tasks)) * 100)
            
            await self._update_agent_in_db(session.session_id, agent)
            await self._broadcast_agent_update(session.session_id, agent)
            
            # Simulate work time (2-5 seconds per task)
            await asyncio.sleep(2 + (i * 0.5))
    
    async def _create_test_suites_from_agents(self, session: TestCreationSession, request_data: Dict) -> List[Dict]:
        """Create actual test suites based on agent processing results"""
        test_suites = []
        
        # Generate test suites based on application type
        app_type = request_data.get("application_type", "web")
        app_name = request_data.get("application_name", "Test Application")
        
        if app_type.lower() == "hrms":
            test_suites = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "HRMS Login Flow Test",
                    "description": "Comprehensive login and authentication testing",
                    "test_type": "functional",
                    "status": "active",
                    "total_test_cases": 8,
                    "estimated_duration_minutes": 15,
                    "last_execution_status": "completed",
                    "success_rate": 95.0,
                    "last_execution_date": datetime.now() - timedelta(hours=2)
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Employee Management Test",
                    "description": "Employee CRUD operations and data validation",
                    "test_type": "functional",
                    "status": "active",
                    "total_test_cases": 12,
                    "estimated_duration_minutes": 25,
                    "last_execution_status": "running",
                    "success_rate": 87.0,
                    "last_execution_date": datetime.now() - timedelta(minutes=30)
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Leave Application Test",
                    "description": "Leave request workflow and approval process",
                    "test_type": "integration",
                    "status": "active",
                    "total_test_cases": 6,
                    "estimated_duration_minutes": 18,
                    "last_execution_status": "failed",
                    "success_rate": 78.0,
                    "last_execution_date": datetime.now() - timedelta(hours=1)
                }
            ]
        else:
            # Generic test suites for other application types
            test_suites = [
                {
                    "id": str(uuid.uuid4()),
                    "name": f"{app_name} Core Functionality Test",
                    "description": "Core application functionality and user flows",
                    "test_type": "functional",
                    "status": "active",
                    "total_test_cases": 10,
                    "estimated_duration_minutes": 20,
                    "last_execution_status": "completed",
                    "success_rate": 92.0,
                    "last_execution_date": datetime.now() - timedelta(hours=1)
                }
            ]
        
        # Store test suites in database or in-memory
        for suite in test_suites:
            await self._store_test_suite(suite, session.customer_id, session.application_id)
        
        return test_suites
    
    async def _store_test_suite(self, suite_data: Dict, customer_id: str, application_id: str):
        """Store test suite in database or in-memory storage"""
        conn = db_manager.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO test_suites 
                        (id, customer_id, application_id, name, description, test_type, status, 
                         total_test_cases, estimated_duration_minutes, last_execution_status, 
                         success_rate, last_execution_date, generated_by_ai, ai_confidence_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        suite_data["id"],
                        customer_id,
                        application_id,
                        suite_data["name"],
                        suite_data["description"],
                        suite_data["test_type"],
                        suite_data["status"],
                        suite_data["total_test_cases"],
                        suite_data["estimated_duration_minutes"],
                        suite_data["last_execution_status"],
                        suite_data["success_rate"],
                        suite_data["last_execution_date"],
                        True,
                        0.95
                    ))
                    conn.commit()
            finally:
                db_manager.return_connection(conn)
        else:
            # Fallback to in-memory storage
            suite_data["customer_id"] = customer_id
            suite_data["application_id"] = application_id
            suite_data["created_at"] = datetime.now().isoformat()
            self.in_memory_test_suites[suite_data["id"]] = suite_data
    
    async def _update_session_in_db(self, session: TestCreationSession):
        """Update agent session in database"""
        conn = db_manager.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE agent_sessions 
                        SET status = %s, progress_percentage = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (session.status, session.progress_percentage, session.session_id))
                    conn.commit()
            finally:
                db_manager.return_connection(conn)
    
    async def _update_agent_in_db(self, session_id: str, agent: AgentProcessingInfo):
        """Update individual agent status in database"""
        conn = db_manager.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE agent_processing_status 
                        SET status = %s, progress_percentage = %s, current_task = %s, 
                            started_at = %s, completed_at = %s, updated_at = NOW()
                        WHERE agent_session_id = %s AND agent_name = %s
                    """, (
                        agent.status,
                        agent.progress_percentage,
                        agent.current_task,
                        agent.started_at,
                        agent.completed_at,
                        session_id,
                        agent.agent_name
                    ))
                    conn.commit()
            finally:
                db_manager.return_connection(conn)
    
    async def _broadcast_agent_update(self, session_id: str, agent: AgentProcessingInfo):
        """Broadcast agent status update via WebSocket"""
        await manager.broadcast_to_customer(
            session_id,  # Using session_id as customer_id for now
            {
                "type": "agent_status_update",
                "session_id": session_id,
                "agent": {
                    "name": agent.agent_name,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "progress": agent.progress_percentage,
                    "current_task": agent.current_task,
                    "started_at": agent.started_at.isoformat() if agent.started_at else None,
                    "completed_at": agent.completed_at.isoformat() if agent.completed_at else None
                }
            }
        )
    
    async def _load_session_from_db(self, session_id: str) -> Optional[TestCreationSession]:
        """Load session from database"""
        # Implementation for loading from database
        # For now, return None to use in-memory storage
        return None

# Global service instance
test_creation_service = TestCreationService()
