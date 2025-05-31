"""
API dependencies for FastAPI endpoints.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from app.core.database import get_database, get_db_manager
from app.core.security_simple import get_permission_checker, get_security_manager
from app.models.auth import User


async def get_current_user(request: Request) -> User:
    """Get current authenticated user."""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user_data = request.state.user
    return User(
        id=user_data["id"],
        email=user_data["email"],
        user_metadata=user_data.get("user_metadata"),
        app_metadata=user_data.get("app_metadata"),
    )


async def get_current_user_id(request: Request) -> str:
    """Get current authenticated user ID."""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user_id


async def get_optional_current_user(request: Request) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if not hasattr(request.state, "user"):
        return None
    
    user_data = request.state.user
    return User(
        id=user_data["id"],
        email=user_data["email"],
        user_metadata=user_data.get("user_metadata"),
        app_metadata=user_data.get("app_metadata"),
    )


async def get_user_store_id(
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager)
) -> int:
    """Get the store ID for the current user."""
    query = """
    SELECT id FROM stores 
    WHERE (shop_config->>'user_id')::text = :user_id 
    AND is_active = true
    """
    
    result = await db_manager.fetch_one(query, {"user_id": user_id})
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active store found for user"
        )
    
    return result["id"]


async def verify_store_access(
    shop_id: int,
    user_id: str = Depends(get_current_user_id),
    permission_checker=Depends(get_permission_checker)
) -> int:
    """Verify user has access to the specified store."""
    has_access = await permission_checker.can_access_store(user_id, shop_id)
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this store"
        )
    
    return shop_id


async def verify_product_access(
    shop_id: int,
    sku_code: str,
    user_id: str = Depends(get_current_user_id),
    permission_checker=Depends(get_permission_checker)
) -> tuple[int, str]:
    """Verify user has access to the specified product."""
    has_access = await permission_checker.can_access_product(user_id, shop_id, sku_code)
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this product"
        )
    
    return shop_id, sku_code


class CommonQueryParams:
    """Common query parameters for pagination and filtering."""
    
    def __init__(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be >= 1"
            )
        
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )
        
        self.page = page
        self.limit = limit
        self.search = search
        self.offset = (page - 1) * limit


def get_pagination_params(
    page: int = 1,
    limit: int = 20
) -> CommonQueryParams:
    """Get pagination parameters."""
    return CommonQueryParams(page=page, limit=limit)


def get_search_params(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None
) -> CommonQueryParams:
    """Get search and pagination parameters."""
    return CommonQueryParams(page=page, limit=limit, search=search)


async def get_client_ip(request: Request) -> str:
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


async def get_user_agent(request: Request) -> str:
    """Get user agent from request."""
    return request.headers.get("User-Agent", "unknown")


class RateLimitInfo:
    """Rate limit information."""
    
    def __init__(self, client_id: str, ip_address: str, user_agent: str):
        self.client_id = client_id
        self.ip_address = ip_address
        self.user_agent = user_agent


async def get_rate_limit_info(
    request: Request,
    user_id: Optional[str] = Depends(get_current_user_id),
    ip_address: str = Depends(get_client_ip),
    user_agent: str = Depends(get_user_agent)
) -> RateLimitInfo:
    """Get rate limiting information."""
    client_id = f"user:{user_id}" if user_id else f"ip:{ip_address}"
    return RateLimitInfo(client_id, ip_address, user_agent)


# Database and service dependencies
async def get_db():
    """Get database connection."""
    return await get_database()


async def get_db_manager_dep():
    """Get database manager."""
    return await get_db_manager()


async def get_security_manager_dep():
    """Get security manager."""
    return get_security_manager()


async def get_permission_checker_dep():
    """Get permission checker."""
    return get_permission_checker()