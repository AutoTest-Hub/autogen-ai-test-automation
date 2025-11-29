#!/usr/bin/env python3
"""
Simplified API Server for AI Test Automation Platform
Works with basic dependencies for development and testing
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIGURATION
# =====================================================

# Deployment configuration
DEPLOYMENT_MODE = os.getenv('DEPLOYMENT_MODE', 'SaaS')
API_VERSION = "v1"
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# =====================================================
# FASTAPI APP SETUP
# =====================================================

app = FastAPI(
    title="AI Test Automation Platform API",
    description="Simplified API for development and testing",
    version="1.0.0",
    docs_url=f"/api/{API_VERSION}/docs",
    redoc_url=f"/api/{API_VERSION}/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# =====================================================
# MODELS
# =====================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class SystemInfo(BaseModel):
    deployment_mode: str
    version: str
    features: Dict[str, bool]
    branding: Dict[str, str]

class TestExecutionRequest(BaseModel):
    url: str
    test_name: str
    headless: bool = True
    requirements_type: str = "basic"

# =====================================================
# MOCK DATA AND HELPERS
# =====================================================

# Mock users database
MOCK_USERS = {
    "admin": {
        "id": "admin",
        "username": "admin", 
        "password": "admin123",
        "role": "admin",
        "plan": "enterprise",
        "api_quota": 1000,
        "api_used": 0
    },
    "demo": {
        "id": "demo",
        "username": "demo",
        "password": "demo123", 
        "role": "user",
        "plan": "basic",
        "api_quota": 50,
        "api_used": 0
    }
}

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Simple authentication"""
    user = MOCK_USERS.get(username)
    if user and user["password"] == password:
        return {k: v for k, v in user.items() if k != "password"}
    return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current user from token (simplified)"""
    if not credentials:
        return MOCK_USERS["demo"]  # Default to demo user for development
    
    # In a real implementation, you'd validate the JWT token here
    # For now, just return admin user
    return {k: v for k, v in MOCK_USERS["admin"].items() if k != "password"}

# =====================================================
# API ENDPOINTS
# =====================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get(f"/api/{API_VERSION}/system/info")
async def get_system_info():
    """Get system information and deployment configuration"""
    return SystemInfo(
        deployment_mode=DEPLOYMENT_MODE,
        version="1.0.0",
        features={
            "real_time_monitoring": True,
            "multi_modal_creation": True,
            "agent_orchestration": True,
            "advanced_analytics": DEPLOYMENT_MODE == "SaaS",
            "ldap_integration": DEPLOYMENT_MODE == "OnPrem",
            "custom_branding": DEPLOYMENT_MODE == "OnPrem"
        },
        branding={
            "name": "AI Test Automation Platform",
            "edition": f"{DEPLOYMENT_MODE} Edition",
            "logo_url": "/logo.png",
            "primary_color": "#3b82f6",
            "secondary_color": "#1e40af"
        }
    )

@app.post(f"/api/{API_VERSION}/auth/login")
async def login(request: LoginRequest):
    """User authentication"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # In a real implementation, you'd generate a proper JWT token
    fake_token = f"fake-jwt-token-{user['id']}"
    
    return LoginResponse(
        access_token=fake_token,
        token_type="bearer",
        user=user
    )

@app.get(f"/api/{API_VERSION}/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post(f"/api/{API_VERSION}/test/execute")
async def execute_test(request: TestExecutionRequest, current_user: Dict = Depends(get_current_user)):
    """Execute test automation"""
    logger.info(f"Test execution requested by {current_user['username']}: {request.url}")
    
    # Mock test execution response
    return {
        "task_id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "started",
        "message": "Test execution started successfully",
        "estimated_duration": "2-5 minutes",
        "agents_assigned": ["discovery_agent", "test_generation_agent"]
    }

@app.get(f"/api/{API_VERSION}/test/executions")
async def get_test_executions(current_user: Dict = Depends(get_current_user)):
    """Get test execution history"""
    # Mock test executions
    return {
        "executions": [
            {
                "id": "exec_001",
                "url": "https://demo.automationexercise.com",
                "status": "completed",
                "created_at": "2024-01-15T10:30:00Z",
                "duration": "3m 45s",
                "tests_generated": 12,
                "success_rate": 95.5
            },
            {
                "id": "exec_002", 
                "url": "https://opensource-demo.orangehrmlive.com",
                "status": "running",
                "created_at": "2024-01-15T11:15:00Z",
                "duration": "1m 20s",
                "tests_generated": 8,
                "success_rate": 100.0
            }
        ],
        "total": 2
    }

@app.get(f"/api/{API_VERSION}/requirements/templates")
async def get_requirements_templates(current_user: Dict = Depends(get_current_user)):
    """Get available requirements templates"""
    return {
        "templates": [
            {
                "id": "ecommerce",
                "name": "E-commerce Application",
                "description": "Comprehensive testing for online stores",
                "scenarios": 6,
                "file": "requirements_ecommerce.json"
            },
            {
                "id": "hrms",
                "name": "HR Management System", 
                "description": "Employee management and HR workflows",
                "scenarios": 7,
                "file": "requirements_hrms.json"
            },
            {
                "id": "banking",
                "name": "Banking Application",
                "description": "Financial services and transactions",
                "scenarios": 7,
                "file": "requirements_banking.json"
            }
        ]
    }

# =====================================================
# STARTUP
# =====================================================

if __name__ == "__main__":
    print(f"🚀 Starting AI Test Automation Platform API")
    print(f"📋 Deployment Mode: {DEPLOYMENT_MODE}")
    print(f"🔗 API Documentation: http://localhost:8000/api/{API_VERSION}/docs")
    print(f"💡 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "server_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
