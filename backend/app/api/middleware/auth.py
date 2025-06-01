"""
Authentication middleware for FastAPI.
"""

import logging
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import log_security_event, log_request_safely
from app.core.security import get_security_manager

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI documentation
security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware to validate JWT tokens."""
    
    # Paths that don't require authentication
    EXEMPT_PATHS = {
        "/",
        "/health",
        "/api/v1/health/supabase",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/signup",
        "/api/v1/auth/refresh",
        # Shopify OAuth and webhook endpoints
        "/api/v1/shopify/oauth/callback",
        "/api/v1/shopify/webhooks/orders_create",
        "/api/v1/shopify/webhooks/orders_update",
        "/api/v1/shopify/webhooks/products_create",
        "/api/v1/shopify/webhooks/products_update",
        "/api/v1/shopify/webhooks/app_uninstalled",
        # Trend analysis health check
        "/api/v1/trend-analysis/health",
        # Business context endpoints (temporary for demo)
        "/api/v1/trend-analysis/business-context/1",
        "/api/v1/trend-analysis/business-context-stream/1",
    }
    
    def __init__(self, app):
        super().__init__(app)
        self.security_manager = get_security_manager()
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate authentication."""
        
        # Skip authentication for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Extract and validate token
        try:
            token = self._extract_token(request)
            if not token:
                log_security_event(
                    "missing_token",
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    path=request.url.path
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Validate token with Supabase
            user = await self.security_manager.get_user_from_token(token)
            if not user:
                log_security_event(
                    "invalid_token",
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    path=request.url.path
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Add user information to request state
            request.state.user = user
            request.state.user_id = user["id"]
            request.state.token = token
            
            # Only log authentication for sensitive endpoints using safe logging
            if request.url.path.startswith("/api/v1/auth/") or request.url.path.startswith("/api/v1/sync/"):
                log_request_safely(
                    request,
                    f"User authenticated for sensitive endpoint",
                    level="info",
                    user_id=user['id'],
                    endpoint_type="sensitive"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            log_security_event(
                "auth_error",
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                path=request.url.path,
                error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
        
        response = await call_next(request)
        return response
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"


async def get_current_user(request: Request) -> dict:
    """Get current authenticated user from request state."""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user


async def get_current_user_id(request: Request) -> str:
    """Get current authenticated user ID from request state."""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user_id


async def get_current_token(request: Request) -> str:
    """Get current authentication token from request state."""
    if not hasattr(request.state, "token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.token


def require_auth(request: Request) -> dict:
    """Dependency to require authentication."""
    return request.state.user if hasattr(request.state, "user") else None


class OptionalAuthMiddleware(BaseHTTPMiddleware):
    """Optional authentication middleware that doesn't fail on missing tokens."""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_manager = get_security_manager()
    
    async def dispatch(self, request: Request, call_next):
        """Process request with optional authentication."""
        
        # Try to extract and validate token
        try:
            token = self._extract_token(request)
            if token:
                user = await self.security_manager.get_user_from_token(token)
                if user:
                    request.state.user = user
                    request.state.user_id = user["id"]
                    request.state.token = token
                    request.state.authenticated = True
                else:
                    request.state.authenticated = False
            else:
                request.state.authenticated = False
        except Exception as e:
            logger.warning(f"Optional auth error: {e}")
            request.state.authenticated = False
        
        response = await call_next(request)
        return response
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None


async def get_optional_user(request: Request) -> Optional[dict]:
    """Get current user if authenticated, None otherwise."""
    return getattr(request.state, "user", None)


async def get_optional_user_id(request: Request) -> Optional[str]:
    """Get current user ID if authenticated, None otherwise."""
    return getattr(request.state, "user_id", None)


def is_authenticated(request: Request) -> bool:
    """Check if request is authenticated."""
    return getattr(request.state, "authenticated", False)