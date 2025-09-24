"""
Authentication utilities for API and WebSocket connections
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()

# Demo users for testing
DEMO_USERS = {
    "admin@demo.com": {
        "id": "admin_user",
        "email": "admin@demo.com",
        "full_name": "Admin User",
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "api_calls_limit": 1000,
        "api_calls_used": 0,
        "tenant_id": "demo_tenant",
        "subscription_plan": "enterprise"
    },
    "user@demo.com": {
        "id": "demo_user",
        "email": "user@demo.com",
        "full_name": "Demo User",
        "role": "user",
        "hashed_password": pwd_context.hash("user123"),
        "api_calls_limit": 50,
        "api_calls_used": 0,
        "tenant_id": "demo_tenant",
        "subscription_plan": "free"
    },
    "admin@company.local": {
        "id": "enterprise_admin",
        "email": "admin@company.local",
        "full_name": "Enterprise Admin",
        "role": "admin",
        "hashed_password": pwd_context.hash("enterprise123"),
        "api_calls_limit": 10000,
        "api_calls_used": 0,
        "tenant_id": "enterprise_tenant",
        "subscription_plan": "enterprise"
    },
    "qa@company.local": {
        "id": "qa_manager",
        "email": "qa@company.local",
        "full_name": "QA Manager",
        "role": "manager",
        "hashed_password": pwd_context.hash("qa123"),
        "api_calls_limit": 5000,
        "api_calls_used": 0,
        "tenant_id": "enterprise_tenant",
        "subscription_plan": "professional"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with email and password"""
    user = DEMO_USERS.get(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        user = DEMO_USERS.get(email)
        return user
    except jwt.PyJWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get the current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        user = verify_token(credentials.credentials)
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception

async def get_current_user_websocket(token: str) -> Optional[Dict[str, Any]]:
    """Get the current user from JWT token for WebSocket connections"""
    try:
        user = verify_token(token)
        return user
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    for user in DEMO_USERS.values():
        if user["id"] == user_id:
            return user
    return None

def check_api_quota(user: Dict[str, Any]) -> bool:
    """Check if user has remaining API quota"""
    return user["api_calls_used"] < user["api_calls_limit"]

def increment_api_usage(user_id: str) -> bool:
    """Increment API usage for a user"""
    for user in DEMO_USERS.values():
        if user["id"] == user_id:
            if user["api_calls_used"] < user["api_calls_limit"]:
                user["api_calls_used"] += 1
                return True
            return False
    return False

def has_permission(user: Dict[str, Any], permission: str) -> bool:
    """Check if user has a specific permission"""
    role = user.get("role", "user")
    
    # Define role permissions
    permissions = {
        "admin": ["read", "write", "delete", "manage_users", "view_analytics", "system_config"],
        "manager": ["read", "write", "view_analytics", "manage_team"],
        "user": ["read", "write"],
        "viewer": ["read"]
    }
    
    return permission in permissions.get(role, [])

# Middleware for API quota checking
async def check_quota_middleware(user: Dict[str, Any] = Depends(get_current_user)):
    """Middleware to check API quota before processing requests"""
    if not check_api_quota(user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="API quota exceeded. Please upgrade your plan or wait for quota reset."
        )
    
    # Increment usage
    increment_api_usage(user["id"])
    return user
