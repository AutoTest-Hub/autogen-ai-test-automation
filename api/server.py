#!/usr/bin/env python3
"""
Standalone API Server for AI Test Automation SaaS Platform
==========================================================

Production-ready REST API server that integrates with the enhanced three-tier system.
Run with: python server.py
"""

import asyncio
import json
import os
import sys
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Simple HTTP server implementation
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (replace with database in production)
users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@testautomation.ai",
        "password": "admin123",  # In production, use hashed passwords
        "api_quota": 1000,
        "api_usage": 0,
        "created_at": datetime.utcnow().isoformat()
    },
    "demo": {
        "username": "demo",
        "email": "demo@testautomation.ai", 
        "password": "demo123",
        "api_quota": 50,
        "api_usage": 0,
        "created_at": datetime.utcnow().isoformat()
    }
}

test_executions = {}
execution_results = {}
active_tokens = {}

class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the API endpoints"""
    
    def _send_response(self, status_code: int, data: dict, headers: dict = None):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        
        self.end_headers()
        
        response = json.dumps(data, indent=2, default=str)
        self.wfile.write(response.encode())
    
    def _get_request_data(self) -> dict:
        """Parse JSON request data"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                return json.loads(post_data.decode())
            return {}
        except Exception as e:
            logger.error(f"Error parsing request data: {e}")
            return {}
    
    def _authenticate(self) -> Optional[dict]:
        """Simple authentication check"""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            return active_tokens.get(token)
        return None
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._send_response(200, {"message": "OK"})
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        try:
            if path == '/':
                self._handle_root()
            elif path == '/health':
                self._handle_health()
            elif path == '/auth/me':
                self._handle_auth_me()
            elif path.startswith('/test/status/'):
                execution_id = path.split('/')[-1]
                self._handle_test_status(execution_id)
            elif path.startswith('/test/results/'):
                execution_id = path.split('/')[-1]
                self._handle_test_results(execution_id)
            elif path == '/test/executions':
                self._handle_list_executions()
            elif path == '/requirements/templates':
                self._handle_list_templates()
            elif path.startswith('/requirements/template/'):
                template_name = path.split('/')[-1]
                self._handle_get_template(template_name)
            else:
                self._send_response(404, {"error": "Endpoint not found"})
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self._send_response(500, {"error": "Internal server error"})
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        data = self._get_request_data()
        
        try:
            if path == '/auth/register':
                self._handle_register(data)
            elif path == '/auth/login':
                self._handle_login(data)
            elif path == '/test/execute':
                self._handle_test_execute(data)
            elif path == '/requirements/validate':
                self._handle_validate_requirements(data)
            else:
                self._send_response(404, {"error": "Endpoint not found"})
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self._send_response(500, {"error": "Internal server error"})
    
    def _handle_root(self):
        """Root endpoint"""
        self._send_response(200, {
            "message": "AI Test Automation SaaS Platform API",
            "version": "1.0.0",
            "status": "operational",
            "endpoints": {
                "authentication": ["/auth/register", "/auth/login", "/auth/me"],
                "test_execution": ["/test/execute", "/test/status/{id}", "/test/results/{id}"],
                "requirements": ["/requirements/templates", "/requirements/template/{name}"],
                "health": ["/health"]
            },
            "documentation": "Visit /docs for API documentation"
        })
    
    def _handle_health(self):
        """Health check endpoint"""
        # Check if enhanced system is available
        try:
            from proper_multi_agent_workflow import ProperMultiAgentWorkflow
            workflow = ProperMultiAgentWorkflow()
            enhanced_status = "✅ Enhanced three-tier system operational"
            requirements_status = "✅ Requirements configuration loaded" if workflow.requirements_config else "⚠️ No requirements loaded"
        except Exception as e:
            enhanced_status = f"❌ Enhanced system error: {str(e)}"
            requirements_status = "❌ Requirements system unavailable"
        
        self._send_response(200, {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "system_status": {
                "enhanced_workflow": enhanced_status,
                "requirements_config": requirements_status,
                "api_server": "✅ API server operational",
                "authentication": "✅ Authentication system ready"
            }
        })
    
    def _handle_register(self, data: dict):
        """User registration"""
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            self._send_response(400, {"error": "Missing required fields"})
            return
        
        if username in users_db:
            self._send_response(400, {"error": "Username already exists"})
            return
        
        users_db[username] = {
            "username": username,
            "email": email,
            "password": password,  # In production, hash this
            "api_quota": 100,
            "api_usage": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._send_response(201, {"message": "User registered successfully"})
    
    def _handle_login(self, data: dict):
        """User authentication"""
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            self._send_response(400, {"error": "Missing username or password"})
            return
        
        user = users_db.get(username)
        if not user or user['password'] != password:
            self._send_response(401, {"error": "Invalid credentials"})
            return
        
        # Generate simple token
        token = str(uuid.uuid4())
        active_tokens[token] = user
        
        self._send_response(200, {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "username": user["username"],
                "email": user["email"],
                "api_quota": user["api_quota"],
                "api_usage": user["api_usage"]
            }
        })
    
    def _handle_auth_me(self):
        """Get current user info"""
        user = self._authenticate()
        if not user:
            self._send_response(401, {"error": "Authentication required"})
            return
        
        self._send_response(200, {
            "username": user["username"],
            "email": user["email"],
            "api_quota": user["api_quota"],
            "api_usage": user["api_usage"],
            "created_at": user["created_at"]
        })
    
    def _handle_test_execute(self, data: dict):
        """Execute test automation workflow"""
        user = self._authenticate()
        if not user:
            self._send_response(401, {"error": "Authentication required"})
            return
        
        if user["api_usage"] >= user["api_quota"]:
            self._send_response(429, {"error": "API quota exceeded"})
            return
        
        url = data.get('url')
        name = data.get('name')
        headless = data.get('headless', True)
        
        if not all([url, name]):
            self._send_response(400, {"error": "Missing required fields: url, name"})
            return
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Initialize execution status
        test_executions[execution_id] = {
            "execution_id": execution_id,
            "status": "pending",
            "progress": 0.0,
            "current_phase": "Initializing",
            "start_time": datetime.utcnow().isoformat(),
            "user": user["username"],
            "request": data
        }
        
        # Update user API usage
        users_db[user["username"]]["api_usage"] += 1
        
        # Start background execution
        threading.Thread(
            target=self._run_test_workflow,
            args=(execution_id, url, name, headless, user["username"]),
            daemon=True
        ).start()
        
        self._send_response(202, {
            "execution_id": execution_id,
            "status": "pending",
            "message": "Test execution started",
            "estimated_duration": 300
        })
    
    def _run_test_workflow(self, execution_id: str, url: str, name: str, headless: bool, username: str):
        """Background task to run test workflow"""
        try:
            # Update status
            test_executions[execution_id]["status"] = "running"
            test_executions[execution_id]["current_phase"] = "Starting workflow"
            test_executions[execution_id]["progress"] = 0.1
            
            # Change to the correct directory
            os.chdir(Path(__file__).parent.parent)
            
            # Run the workflow script
            cmd = [
                "bash", "run_proper_multi_agent_workflow.sh",
                "--url", url,
                "--name", name
            ]
            if not headless:
                cmd.append("--no-headless")
            
            # Update progress
            test_executions[execution_id]["current_phase"] = "Executing test generation"
            test_executions[execution_id]["progress"] = 0.3
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Update progress
            test_executions[execution_id]["progress"] = 0.9
            test_executions[execution_id]["current_phase"] = "Finalizing results"
            
            # Parse results
            if result.returncode == 0:
                # Success
                test_executions[execution_id]["status"] = "completed"
                test_executions[execution_id]["progress"] = 1.0
                test_executions[execution_id]["current_phase"] = "Completed"
                test_executions[execution_id]["end_time"] = datetime.utcnow().isoformat()
                
                # Store results
                execution_results[execution_id] = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "summary": self._parse_workflow_output(result.stdout)
                }
                
                logger.info(f"Test execution {execution_id} completed successfully")
            else:
                # Failure
                test_executions[execution_id]["status"] = "failed"
                test_executions[execution_id]["error"] = result.stderr or "Unknown error"
                test_executions[execution_id]["end_time"] = datetime.utcnow().isoformat()
                
                logger.error(f"Test execution {execution_id} failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            test_executions[execution_id]["status"] = "timeout"
            test_executions[execution_id]["error"] = "Execution exceeded time limit"
            test_executions[execution_id]["end_time"] = datetime.utcnow().isoformat()
            logger.error(f"Test execution {execution_id} timed out")
            
        except Exception as e:
            test_executions[execution_id]["status"] = "failed"
            test_executions[execution_id]["error"] = str(e)
            test_executions[execution_id]["end_time"] = datetime.utcnow().isoformat()
            logger.error(f"Test execution {execution_id} failed with exception: {e}")
    
    def _parse_workflow_output(self, output: str) -> dict:
        """Parse workflow output to extract summary information"""
        summary = {
            "total_tests": 0,
            "success_rate": 0.0,
            "execution_time": 0.0,
            "reports_generated": False
        }
        
        try:
            lines = output.split('\n')
            for line in lines:
                if "Total Tests:" in line:
                    summary["total_tests"] = int(line.split(':')[-1].strip())
                elif "Success Rate:" in line:
                    rate_str = line.split(':')[-1].strip().replace('%', '')
                    summary["success_rate"] = float(rate_str)
                elif "Execution Time:" in line:
                    time_str = line.split(':')[-1].strip().replace('s', '')
                    summary["execution_time"] = float(time_str)
                elif "HTML Report:" in line:
                    summary["reports_generated"] = True
        except Exception as e:
            logger.warning(f"Error parsing workflow output: {e}")
        
        return summary
    
    def _handle_test_status(self, execution_id: str):
        """Get test execution status"""
        user = self._authenticate()
        if not user:
            self._send_response(401, {"error": "Authentication required"})
            return
        
        if execution_id not in test_executions:
            self._send_response(404, {"error": "Execution not found"})
            return
        
        self._send_response(200, test_executions[execution_id])
    
    def _handle_test_results(self, execution_id: str):
        """Get test execution results"""
        user = self._authenticate()
        if not user:
            self._send_response(401, {"error": "Authentication required"})
            return
        
        if execution_id not in execution_results:
            self._send_response(404, {"error": "Results not found"})
            return
        
        self._send_response(200, execution_results[execution_id])
    
    def _handle_list_executions(self):
        """List test executions"""
        user = self._authenticate()
        if not user:
            self._send_response(401, {"error": "Authentication required"})
            return
        
        # Filter executions by user
        user_executions = [
            exec_data for exec_data in test_executions.values()
            if exec_data.get("user") == user["username"]
        ]
        
        self._send_response(200, {
            "executions": user_executions,
            "total": len(user_executions)
        })
    
    def _handle_list_templates(self):
        """List available requirements templates"""
        templates = []
        template_dir = Path(__file__).parent.parent
        
        for template_file in template_dir.glob("requirements_*.json"):
            template_name = template_file.stem.replace("requirements_", "")
            templates.append({
                "name": template_name,
                "file": template_file.name,
                "display_name": template_name.replace("_", " ").title()
            })
        
        self._send_response(200, {"templates": templates})
    
    def _handle_get_template(self, template_name: str):
        """Get a specific requirements template"""
        template_file = Path(__file__).parent.parent / f"requirements_{template_name}.json"
        
        if not template_file.exists():
            self._send_response(404, {"error": "Template not found"})
            return
        
        try:
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            self._send_response(200, template_data)
        except Exception as e:
            self._send_response(500, {"error": f"Error loading template: {str(e)}"})
    
    def _handle_validate_requirements(self, data: dict):
        """Validate requirements configuration"""
        validation_result = {
            "valid": True,
            "score": 1.0,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Basic validation
        if not data.get("base_url", "").startswith(("http://", "https://")):
            validation_result["errors"].append("Invalid URL format")
            validation_result["valid"] = False
            validation_result["score"] -= 0.3
        
        if not data.get("test_scenarios"):
            validation_result["warnings"].append("No test scenarios defined")
            validation_result["score"] -= 0.2
        
        if not data.get("priority_areas"):
            validation_result["suggestions"].append("Consider defining priority areas for better test focus")
            validation_result["score"] -= 0.1
        
        self._send_response(200, validation_result)

def main():
    """Start the API server"""
    port = int(os.getenv("API_PORT", 8000))
    
    print(f"""
🚀 AI Test Automation SaaS Platform API Server
==============================================

Server starting on: http://localhost:{port}
API Documentation: http://localhost:{port}/
Health Check: http://localhost:{port}/health

📋 Available Endpoints:
  Authentication:
    POST /auth/register - Register new user
    POST /auth/login - User login
    GET /auth/me - Get user profile
    
  Test Execution:
    POST /test/execute - Start test execution
    GET /test/status/{{id}} - Get execution status
    GET /test/results/{{id}} - Get test results
    GET /test/executions - List user executions
    
  Requirements:
    GET /requirements/templates - List templates
    GET /requirements/template/{{name}} - Get template
    POST /requirements/validate - Validate config

🔐 Demo Credentials:
  Username: admin, Password: admin123 (1000 API calls)
  Username: demo, Password: demo123 (50 API calls)

Press Ctrl+C to stop the server
""")
    
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()

if __name__ == "__main__":
    main()
