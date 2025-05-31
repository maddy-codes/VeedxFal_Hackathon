"""
Rate limiting middleware for FastAPI.
"""

import asyncio
import logging
import time
from typing import Dict, Optional

import redis.asyncio as redis
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import log_security_event

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis for distributed rate limiting."""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client: Optional[redis.Redis] = None
        self.requests_per_minute = settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        self.burst_capacity = settings.RATE_LIMIT_BURST
        
        # Paths with different rate limits
        self.rate_limits = {
            "/api/v1/auth/login": {"requests": 5, "window": 60},  # 5 per minute for login
            "/api/v1/sync/": {"requests": 10, "window": 60},      # 10 per minute for sync
            "/api/v1/video/generate": {"requests": 3, "window": 300},  # 3 per 5 minutes for video
        }
        
        # Exempt paths from rate limiting
        self.exempt_paths = {
            "/health",
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            # Initialize Redis client if not already done
            if self.redis_client is None:
                await self._init_redis()
            
            # Get client identifier
            client_id = self._get_client_identifier(request)
            
            # Check rate limit
            allowed = await self._check_rate_limit(request, client_id)
            
            if not allowed:
                log_security_event(
                    "rate_limit_exceeded",
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    path=request.url.path,
                    client_id=client_id
                )
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + 60),
                    }
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if Redis is unavailable
        
        response = await call_next(request)
        
        # Add rate limit headers to response
        try:
            remaining = await self._get_remaining_requests(request, client_id)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        except Exception as e:
            logger.debug(f"Failed to add rate limit headers: {e}")
        
        return response
    
    async def _init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.debug("Redis connection established for rate limiting")
            
        except Exception as e:
            logger.warning(f"Redis unavailable for rate limiting: {e}")
            self.redis_client = None
    
    async def _check_rate_limit(self, request: Request, client_id: str) -> bool:
        """Check if request is within rate limits."""
        if self.redis_client is None:
            return True  # Allow if Redis is unavailable
        
        # Get rate limit configuration for this path
        rate_config = self._get_rate_config(request.url.path)
        requests_limit = rate_config["requests"]
        window_seconds = rate_config["window"]
        
        # Use sliding window rate limiting
        now = time.time()
        window_start = now - window_seconds
        
        # Redis key for this client and endpoint
        key = f"rate_limit:{client_id}:{request.url.path}:{request.method}"
        
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiration
            pipe.expire(key, window_seconds + 1)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            # Check if within limit
            return current_requests < requests_limit
            
        except Exception as e:
            logger.debug(f"Rate limit check failed: {e}")
            return True  # Allow if check fails
    
    async def _get_remaining_requests(self, request: Request, client_id: str) -> int:
        """Get remaining requests for client."""
        if self.redis_client is None:
            return self.requests_per_minute
        
        rate_config = self._get_rate_config(request.url.path)
        requests_limit = rate_config["requests"]
        window_seconds = rate_config["window"]
        
        now = time.time()
        window_start = now - window_seconds
        
        key = f"rate_limit:{client_id}:{request.url.path}:{request.method}"
        
        try:
            # Count current requests in window
            current_requests = await self.redis_client.zcount(key, window_start, now)
            return max(0, requests_limit - current_requests)
        except Exception as e:
            logger.debug(f"Failed to get remaining requests: {e}")
            return requests_limit
    
    def _get_rate_config(self, path: str) -> Dict[str, int]:
        """Get rate limit configuration for path."""
        # Check for exact match first
        if path in self.rate_limits:
            return self.rate_limits[path]
        
        # Check for prefix matches
        for rate_path, config in self.rate_limits.items():
            if path.startswith(rate_path):
                return config
        
        # Default rate limit
        return {"requests": self.requests_per_minute, "window": 60}
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for client."""
        # Use user ID if authenticated
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Use IP address for unauthenticated requests
        ip = self._get_client_ip(request)
        return f"ip:{ip}"
    
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


class InMemoryRateLimiter:
    """In-memory rate limiter fallback when Redis is unavailable."""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(
        self,
        client_id: str,
        requests_limit: int,
        window_seconds: int
    ) -> bool:
        """Check rate limit using in-memory storage."""
        async with self.lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Get or create request list for client
            if client_id not in self.requests:
                self.requests[client_id] = []
            
            client_requests = self.requests[client_id]
            
            # Remove old requests outside window
            self.requests[client_id] = [
                req_time for req_time in client_requests
                if req_time > window_start
            ]
            
            # Check if within limit
            if len(self.requests[client_id]) >= requests_limit:
                return False
            
            # Add current request
            self.requests[client_id].append(now)
            return True
    
    async def cleanup_old_entries(self):
        """Clean up old entries to prevent memory leaks."""
        async with self.lock:
            now = time.time()
            cutoff = now - 3600  # Remove entries older than 1 hour
            
            for client_id in list(self.requests.keys()):
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if req_time > cutoff
                ]
                
                # Remove empty lists
                if not self.requests[client_id]:
                    del self.requests[client_id]


# Global in-memory rate limiter instance
memory_rate_limiter = InMemoryRateLimiter()


async def cleanup_rate_limiter():
    """Background task to cleanup old rate limiter entries."""
    while True:
        try:
            await memory_rate_limiter.cleanup_old_entries()
            await asyncio.sleep(300)  # Cleanup every 5 minutes
        except Exception as e:
            logger.error(f"Rate limiter cleanup error: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute on error