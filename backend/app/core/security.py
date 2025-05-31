"""
Security utilities for authentication and authorization.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


class SecurityManager:
    """Security manager for authentication and authorization."""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.supabase = supabase
    
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
        
        to_encode.update({"exp": expire})
        
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
        """Authenticate user with Supabase."""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata,
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None,
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_in": 3600,  # 1 hour
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    async def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from access token."""
        try:
            # Verify token with Supabase
            response = self.supabase.auth.get_user(token)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata,
                    "app_metadata": response.user.app_metadata,
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"User retrieval from token failed: {e}")
            return None
    
    async def sign_out(self, token: str) -> bool:
        """Sign out user."""
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Sign out failed: {e}")
            return False


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
        """Check if user can access store."""
        from app.core.database import database
        
        query = """
        SELECT 1 FROM stores 
        WHERE id = :shop_id 
        AND (shop_config->>'user_id')::text = :user_id
        """
        
        result = await database.fetch_one(
            query,
            {"shop_id": shop_id, "user_id": user_id}
        )
        
        return result is not None
    
    @staticmethod
    async def can_access_product(user_id: str, shop_id: int, sku_code: str) -> bool:
        """Check if user can access product."""
        from app.core.database import database
        
        query = """
        SELECT 1 FROM products p
        JOIN stores s ON p.shop_id = s.id
        WHERE p.shop_id = :shop_id 
        AND p.sku_code = :sku_code
        AND (s.shop_config->>'user_id')::text = :user_id
        """
        
        result = await database.fetch_one(
            query,
            {"shop_id": shop_id, "sku_code": sku_code, "user_id": user_id}
        )
        
        return result is not None


# Global permission checker
permission_checker = PermissionChecker()


def get_permission_checker() -> PermissionChecker:
    """Get permission checker instance."""
    return permission_checker