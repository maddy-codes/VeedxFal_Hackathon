"""
Authentication API endpoints.
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_db_manager_dep, get_security_manager_dep
from app.core.logging import log_business_event, log_security_event
from app.models.auth import (
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenResponse,
    ShopifyConnectRequest,
    Store,
    User,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="User login",
    description="Authenticate user with email and password, return JWT token",
)
async def login(
    request: Request,
    login_data: LoginRequest,
    security_manager=Depends(get_security_manager_dep),
):
    """Authenticate user and return access token."""
    
    try:
        # Get client information for logging
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Authenticate with Supabase
        auth_result = await security_manager.authenticate_user(
            login_data.email, 
            login_data.password
        )
        
        if not auth_result:
            log_security_event(
                "login_failed",
                ip_address=client_ip,
                user_agent=user_agent,
                email=login_data.email
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create user object
        user = User(
            id=auth_result["id"],
            email=auth_result["email"],
            user_metadata=auth_result.get("user_metadata"),
            app_metadata=auth_result.get("app_metadata"),
        )
        
        # Log successful login
        log_security_event(
            "login_success",
            user_id=user.id,
            ip_address=client_ip,
            user_agent=user_agent,
            email=user.email
        )
        
        log_business_event(
            "user_login",
            user_id=user.id,
            email=user.email
        )
        
        return LoginResponse(
            access_token=auth_result["access_token"],
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Refresh access token",
    description="Refresh JWT access token using refresh token",
)
async def refresh_token(
    request: Request,
    security_manager=Depends(get_security_manager_dep),
):
    """Refresh access token using refresh token."""
    
    try:
        # Extract refresh token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        refresh_token = authorization.split(" ", 1)[1]
        
        # Refresh token with Supabase
        refresh_result = await security_manager.refresh_token(refresh_token)
        
        if not refresh_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        return RefreshTokenResponse(
            access_token=refresh_result["access_token"],
            expires_in=refresh_result["expires_in"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh service error"
        )


@router.post(
    "/logout",
    responses={
        200: {"description": "Successfully logged out"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="User logout",
    description="Logout user and invalidate token",
)
async def logout(
    request: Request,
    security_manager=Depends(get_security_manager_dep),
):
    """Logout user and invalidate token."""
    
    try:
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ", 1)[1]
            
            # Get user info before logout
            user = await security_manager.get_user_from_token(token)
            
            # Sign out with Supabase
            await security_manager.sign_out(token)
            
            # Log logout
            if user:
                log_business_event(
                    "user_logout",
                    user_id=user["id"],
                    email=user["email"]
                )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout service error"
        )


@router.get(
    "/me",
    response_model=User,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get current user",
    description="Get current authenticated user information",
)
async def get_current_user_info(request: Request):
    """Get current authenticated user information."""
    
    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User service error"
        )


@router.get(
    "/stores/current",
    response_model=Store,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get current user's store",
    description="Get current user's store information",
)
async def get_current_store(
    request: Request,
    db_manager=Depends(get_db_manager_dep),
):
    """Get current user's store information."""
    
    try:
        if not hasattr(request.state, "user_id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        user_id = request.state.user_id
        
        # Get user's store
        query = """
        SELECT id, shop_domain, shop_name, is_active, shop_config, created_at, updated_at
        FROM stores 
        WHERE (shop_config->>'user_id')::text = :user_id 
        AND is_active = true
        """
        
        result = await db_manager.fetch_one(query, {"user_id": user_id})
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active store found for user"
            )
        
        return Store(
            id=result["id"],
            shop_domain=result["shop_domain"],
            shop_name=result["shop_name"],
            is_active=result["is_active"],
            shop_config=result["shop_config"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current store error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Store service error"
        )


@router.post(
    "/stores/shopify/connect",
    response_model=Store,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid OAuth code or shop domain"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Connect Shopify store",
    description="Connect Shopify store via OAuth authorization code",
)
async def connect_shopify_store(
    request: Request,
    connect_data: ShopifyConnectRequest,
    db_manager=Depends(get_db_manager_dep),
):
    """Connect Shopify store via OAuth."""
    
    try:
        if not hasattr(request.state, "user_id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        user_id = request.state.user_id
        
        # TODO: Implement Shopify OAuth token exchange
        # This would involve:
        # 1. Exchange authorization code for access token
        # 2. Validate shop domain
        # 3. Get shop information from Shopify
        # 4. Store shop data in database
        
        # For now, create a placeholder store
        shop_config = {
            "user_id": user_id,
            "shopify_connected": True,
            "connected_at": datetime.utcnow().isoformat(),
        }
        
        # Insert or update store
        query = """
        INSERT INTO stores (shop_domain, shop_name, access_token, shop_config, is_active)
        VALUES (:shop_domain, :shop_name, :access_token, :shop_config, true)
        ON CONFLICT (shop_domain) 
        DO UPDATE SET 
            access_token = EXCLUDED.access_token,
            shop_config = EXCLUDED.shop_config,
            updated_at = NOW(),
            is_active = true
        RETURNING id, shop_domain, shop_name, is_active, shop_config, created_at, updated_at
        """
        
        result = await db_manager.fetch_one(query, {
            "shop_domain": connect_data.shop_domain,
            "shop_name": connect_data.shop_domain.split(".")[0].title(),
            "access_token": "placeholder_token",  # Would be real token from OAuth
            "shop_config": shop_config,
        })
        
        # Log store connection
        log_business_event(
            "shopify_store_connected",
            user_id=user_id,
            shop_id=result["id"],
            shop_domain=connect_data.shop_domain
        )
        
        return Store(
            id=result["id"],
            shop_domain=result["shop_domain"],
            shop_name=result["shop_name"],
            is_active=result["is_active"],
            shop_config=result["shop_config"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shopify connect error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Shopify connection service error"
        )