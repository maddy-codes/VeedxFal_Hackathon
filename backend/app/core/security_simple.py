"""
Simplified security utilities for authentication and authorization.
This version removes Supabase dependency to avoid compatibility issues.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Security manager for authentication and authorization."""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Mock authentication for demo purposes."""
        # For demo purposes, accept any email/password combination
        if email and password:
            return {
                "id": "user123",
                "email": email,
                "user_metadata": {"name": "Demo User"},
                "access_token": self.create_access_token({"sub": "user123", "email": email}),
                "refresh_token": "mock_refresh_token",
            }
        return None
    
    async def sign_up_user(self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Mock user signup for demo purposes."""
        # For demo purposes, accept any email/password combination
        if email and password and len(password) >= 8:
            user_id = f"user_{email.split('@')[0]}"
            return {
                "id": user_id,
                "email": email,
                "user_metadata": user_metadata or {},
                "access_token": self.create_access_token({"sub": user_id, "email": email}),
                "refresh_token": "mock_refresh_token",
                "email_confirmed": True,  # For demo, assume email is always confirmed
            }
        return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Mock token refresh."""
        if refresh_token:
            return {
                "access_token": self.create_access_token({"sub": "user123", "email": "demo@retailai.com"}),
                "refresh_token": "mock_refresh_token",
                "expires_in": 3600,
            }
        return None
    
    async def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from access token."""
        payload = self.verify_token(token)
        if payload:
            return {
                "id": payload.get("sub", "user123"),
                "email": payload.get("email", "demo@retailai.com"),
                "user_metadata": {"name": "Demo User"},
                "app_metadata": {},
            }
        return None
    
    async def sign_out(self, token: str) -> bool:
        """Mock sign out."""
        return True


# Global security manager instance
security_manager = SecurityManager()


def get_security_manager() -> SecurityManager:
    """Get security manager instance."""
    return security_manager


def create_access_token_for_user(user_id: str, email: str) -> str:
    """Create access token for user."""
    token_data = {
        "sub": user_id,
        "email": email,
        "type": "access"
    }
    
    return security_manager.create_access_token(token_data)


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify access token and return payload."""
    return security_manager.verify_token(token)


async def get_current_user_id(token: str) -> Optional[str]:
    """Get current user ID from token."""
    user = await security_manager.get_user_from_token(token)
    return user["id"] if user else None


class PermissionChecker:
    """Check user permissions for resources."""
    
    @staticmethod
    async def can_access_store(user_id: str, shop_id: int) -> bool:
        """Mock permission check - always allow for demo."""
        return True
    
    @staticmethod
    async def can_access_product(user_id: str, shop_id: int, sku_code: str) -> bool:
        """Mock permission check - always allow for demo."""
        return True


# Global permission checker
permission_checker = PermissionChecker()


def get_permission_checker() -> PermissionChecker:
    """Get permission checker instance."""
    return permission_checker