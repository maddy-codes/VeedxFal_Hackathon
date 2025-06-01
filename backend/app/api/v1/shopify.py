"""
Shopify integration API endpoints.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.deps import get_current_user_id
from app.core.logging import log_business_event, log_security_event
from app.models.shopify import (
    ShopifyOAuthCallback,
    ShopifyOAuthRequest,
    ShopifyOrder,
    ShopifyOrderSyncRequest,
    ShopifyProduct,
    ShopifyProductSyncRequest,
    ShopifyStore,
    ShopifyStoreStats,
    ShopifySyncJob,
    ShopifyWebhookEvent,
    ShopifyWebhookEventType,
    ShopifyWebhookRequest,
)
from app.models.auth import ErrorResponse
from app.services.shopify_service import get_shopify_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    return {"message": "Shopify router is working", "timestamp": "2025-05-31"}


@router.get("/oauth/authorize")
async def generate_oauth_url_get(shop: str, redirect_uri: Optional[str] = None):
    """Generate Shopify OAuth authorization URL via GET request (for testing)."""
    
    try:
        from app.core.config import settings
        from urllib.parse import urlencode
        
        # Generate state parameter for security (using test user for GET requests)
        state = f"test_user:127.0.0.1"
        
        # Generate OAuth URL manually without service dependency
        final_redirect_uri = redirect_uri or "http://localhost:8000/api/v1/shopify/oauth/callback"
        
        if not settings.SHOPIFY_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Shopify client ID not configured"
            )
        
        params = {
            "client_id": settings.SHOPIFY_CLIENT_ID,
            "scope": ",".join(settings.SHOPIFY_SCOPES),
            "redirect_uri": final_redirect_uri,
            "state": state
        }
        
        oauth_url = f"https://{shop}/admin/oauth/authorize?{urlencode(params)}"
        
        return {
            "oauth_url": oauth_url,
            "state": state,
            "shop_domain": shop,
            "redirect_uri": final_redirect_uri,
            "instructions": "Visit the oauth_url to authorize the app, then you'll be redirected back with a code"
        }
        
    except Exception as e:
        logger.error(f"OAuth URL generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )


@router.post(
    "/oauth/authorize",
    response_model=Dict[str, str],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Generate Shopify OAuth URL",
    description="Generate OAuth authorization URL for Shopify store connection",
)
async def generate_oauth_url(
    request: Request,
    oauth_request: ShopifyOAuthRequest,
    user_id: str = Depends(get_current_user_id),
    shopify_service=Depends(get_shopify_service),
):
    """Generate Shopify OAuth authorization URL."""
    
    try:
        # Get client information for logging
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        
        # Generate state parameter for security
        state = f"{user_id}:{client_ip}"
        
        # Generate OAuth URL
        redirect_uri = oauth_request.redirect_uri or f"{request.base_url}api/v1/shopify/oauth/callback"
        
        oauth_url = shopify_service.generate_oauth_url(
            shop_domain=oauth_request.shop_domain,
            redirect_uri=redirect_uri,
            state=state
        )
        
        # Log OAuth initiation
        log_business_event(
            "shopify_oauth_initiated",
            user_id=user_id,
            shop_domain=oauth_request.shop_domain,
            ip_address=client_ip
        )
        
        return {
            "oauth_url": oauth_url,
            "state": state,
            "shop_domain": oauth_request.shop_domain
        }
        
    except Exception as e:
        logger.error(f"OAuth URL generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OAuth URL"
        )


@router.get(
    "/oauth/callback",
    responses={
        302: {"description": "Redirect to frontend dashboard"},
        400: {"description": "Invalid OAuth callback - redirect to frontend with error"},
        500: {"description": "Internal server error - redirect to frontend with error"},
    },
    summary="Handle Shopify OAuth callback (GET)",
    description="Process OAuth callback from query parameters and redirect to frontend dashboard",
)
async def handle_oauth_callback_get(
    request: Request,
    code: str,
    shop: str,
    state: Optional[str] = None,
    hmac: Optional[str] = None,
    timestamp: Optional[str] = None,
    host: Optional[str] = None,
    shopify_service=Depends(get_shopify_service),
):
    """Handle Shopify OAuth callback via GET request with query parameters."""
    
    # Create callback data from query parameters
    callback_data = ShopifyOAuthCallback(
        shop_domain=shop,
        code=code,
        state=state,
        hmac=hmac,
        timestamp=timestamp
    )
    
    # Process the callback using shared logic
    return await _process_oauth_callback(request, callback_data, shopify_service)


@router.post(
    "/oauth/callback",
    responses={
        302: {"description": "Redirect to frontend dashboard"},
        400: {"description": "Invalid OAuth callback - redirect to frontend with error"},
        500: {"description": "Internal server error - redirect to frontend with error"},
    },
    summary="Handle Shopify OAuth callback (POST)",
    description="Process OAuth callback from request body and redirect to frontend dashboard",
)
async def handle_oauth_callback_post(
    request: Request,
    callback_data: ShopifyOAuthCallback,
    shopify_service=Depends(get_shopify_service),
):
    """Handle Shopify OAuth callback via POST request with body data."""
    
    # Process the callback using shared logic
    return await _process_oauth_callback(request, callback_data, shopify_service)


async def _process_oauth_callback(
    request: Request,
    callback_data: ShopifyOAuthCallback,
    shopify_service,
) -> RedirectResponse:
    """Shared OAuth callback processing logic."""
    
    try:
        # Get client information for logging
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        
        logger.info("=== OAUTH CALLBACK RECEIVED ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Client IP: {client_ip}")
        logger.info(f"Shop domain: {callback_data.shop_domain}")
        logger.info(f"Code present: {bool(callback_data.code)}")
        logger.info(f"Code length: {len(callback_data.code) if callback_data.code else 0}")
        logger.info(f"State present: {bool(callback_data.state)}")
        logger.info(f"HMAC present: {bool(callback_data.hmac)}")
        logger.info(f"Timestamp present: {bool(callback_data.timestamp)}")
        
        # Log the callback attempt with method information
        log_business_event(
            "shopify_oauth_callback_received",
            shop_domain=callback_data.shop_domain,
            ip_address=client_ip,
            method=request.method,
            has_state=bool(callback_data.state),
            has_hmac=bool(callback_data.hmac)
        )
        
        # Validate required parameters
        if not callback_data.shop_domain:
            logger.error("CALLBACK ERROR: Missing shop domain")
            frontend_url = "http://localhost:3000/dashboard/shopify?success=false&error=Shop%20domain%20is%20required"
            logger.info(f"Redirecting to frontend with error: {frontend_url}")
            return RedirectResponse(url=frontend_url, status_code=302)
        
        if not callback_data.code:
            logger.error("CALLBACK ERROR: Missing OAuth code")
            frontend_url = "http://localhost:3000/dashboard/shopify?success=false&error=OAuth%20code%20is%20required"
            logger.info(f"Redirecting to frontend with error: {frontend_url}")
            return RedirectResponse(url=frontend_url, status_code=302)
        
        # For GET requests, we need to extract user_id from state parameter
        # For POST requests, we can use the dependency injection
        logger.info("=== EXTRACTING USER ID FROM STATE ===")
        user_id = None
        if callback_data.state and ":" in callback_data.state:
            # State format: "user_id:client_ip"
            try:
                user_id, expected_ip = callback_data.state.split(":", 1)
                logger.info(f"Extracted user ID: {user_id}")
                logger.info(f"Expected IP from state: {expected_ip}")
                logger.info(f"Actual client IP: {client_ip}")
                
                # Verify IP matches for security
                if expected_ip != client_ip:
                    logger.warning(f"IP mismatch detected: expected {expected_ip}, got {client_ip}")
                    log_security_event(
                        "shopify_oauth_ip_mismatch",
                        user_id=user_id,
                        shop_domain=callback_data.shop_domain,
                        ip_address=client_ip,
                        expected_ip=expected_ip,
                        received_ip=client_ip
                    )
                    # Log warning but don't fail - IP might change due to proxies
                    logger.warning(f"IP mismatch in OAuth callback: expected {expected_ip}, got {client_ip}")
                else:
                    logger.info("✓ IP verification passed")
                
            except ValueError as ve:
                logger.error(f"State parsing error: {ve}")
                logger.error(f"State value: {callback_data.state}")
                log_security_event(
                    "shopify_oauth_invalid_state_format",
                    shop_domain=callback_data.shop_domain,
                    ip_address=client_ip,
                    state=callback_data.state
                )
                frontend_url = "http://localhost:3000/dashboard/shopify?success=false&error=Invalid%20state%20parameter%20format"
                logger.info(f"Redirecting to frontend with error: {frontend_url}")
                return RedirectResponse(url=frontend_url, status_code=302)
        else:
            logger.error("State parameter missing or invalid format")
            logger.error(f"State value: {callback_data.state}")
        
        if not user_id:
            logger.error("CALLBACK ERROR: Could not extract user ID")
            log_security_event(
                "shopify_oauth_missing_user_id",
                shop_domain=callback_data.shop_domain,
                ip_address=client_ip,
                state=callback_data.state
            )
            frontend_url = "http://localhost:3000/dashboard/shopify?success=false&error=Missing%20or%20invalid%20user%20identification%20in%20state%20parameter"
            logger.info(f"Redirecting to frontend with error: {frontend_url}")
            return RedirectResponse(url=frontend_url, status_code=302)
        
        logger.info("✓ User ID extracted successfully")
        
        # Exchange OAuth code for access token
        logger.info("=== CALLING TOKEN EXCHANGE SERVICE ===")
        logger.info(f"Calling exchange_oauth_code with:")
        logger.info(f"  - shop_domain: {callback_data.shop_domain}")
        logger.info(f"  - user_id: {user_id}")
        logger.info(f"  - code length: {len(callback_data.code)}")
        
        store = await shopify_service.exchange_oauth_code(
            shop_domain=callback_data.shop_domain,
            code=callback_data.code,
            user_id=user_id
        )
        
        logger.info("=== TOKEN EXCHANGE COMPLETED ===")
        logger.info(f"Store created with ID: {store.id}")
        logger.info(f"Store domain: {store.shop_domain}")
        logger.info(f"Store name: {store.shop_name}")
        
        # Log successful OAuth completion
        log_business_event(
            "shopify_oauth_completed",
            user_id=user_id,
            shop_id=store.id,
            shop_domain=callback_data.shop_domain,
            ip_address=client_ip,
            method=request.method
        )
        
        logger.info("=== OAUTH CALLBACK PROCESSING COMPLETED SUCCESSFULLY ===")
        
        # Redirect to frontend dashboard with success parameters
        frontend_url = f"http://localhost:3000/dashboard/shopify?success=true&shop={store.shop_domain}&store_id={store.id}"
        logger.info(f"Redirecting to frontend: {frontend_url}")
        
        return RedirectResponse(url=frontend_url, status_code=302)
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in OAuth callback: {he.status_code} - {he.detail}")
        
        # Redirect to frontend with error parameters
        error_message = he.detail.replace(" ", "%20")  # URL encode spaces
        frontend_url = f"http://localhost:3000/dashboard/shopify?success=false&error={error_message}"
        logger.info(f"Redirecting to frontend with error: {frontend_url}")
        
        return RedirectResponse(url=frontend_url, status_code=302)
        
    except Exception as e:
        logger.error("=== OAUTH CALLBACK UNEXPECTED ERROR ===")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error message: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Redirect to frontend with error parameters
        error_message = f"OAuth callback processing failed: {str(e)}".replace(" ", "%20")  # URL encode spaces
        frontend_url = f"http://localhost:3000/dashboard/shopify?success=false&error={error_message}"
        logger.info(f"Redirecting to frontend with error: {frontend_url}")
        
        return RedirectResponse(url=frontend_url, status_code=302)


@router.get(
    "/stores",
    response_model=List[ShopifyStore],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get user's Shopify stores",
    description="Get all Shopify stores connected by the current user",
)
async def get_user_stores(
    user_id: str = Depends(get_current_user_id),
    shopify_service=Depends(get_shopify_service),
):
    """Get user's connected Shopify stores."""
    
    try:
        from app.core.database import get_supabase_client
        supabase_client = get_supabase_client()
        
        # Get user's stores
        result = supabase_client.table('stores').select(
            '*'
        ).eq('shop_config->>user_id', user_id).eq('is_active', True).execute()
        
        stores = []
        for store_record in result.data:
            shop_config = store_record.get("shop_config", {})
            
            # Map the stores table data to ShopifyStore model format
            shopify_store_data = {
                "id": store_record["id"],
                "shop_domain": store_record["shop_domain"],
                "shop_name": store_record["shop_name"],
                "access_token": store_record["access_token"],
                "scope": shop_config.get("scope", ""),
                "is_active": store_record["is_active"],
                "user_id": shop_config.get("user_id", user_id),
                "shop_id": shop_config.get("shop_id"),
                "shop_config": shop_config,
                "last_sync_at": None,  # Will be updated during sync
                "created_at": store_record["created_at"],
                "updated_at": store_record["updated_at"]
            }
            
            stores.append(ShopifyStore(**shopify_store_data))
        
        return stores
        
    except Exception as e:
        logger.error(f"Get stores error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stores"
        )


@router.get(
    "/stores/{shop_id}",
    response_model=ShopifyStore,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get Shopify store details",
    description="Get details of a specific Shopify store",
)
async def get_store(
    shop_id: int,
    user_id: str = Depends(get_current_user_id),
    shopify_service=Depends(get_shopify_service),
):
    """Get Shopify store details."""
    
    try:
        from app.core.database import get_supabase_client
        supabase_client = get_supabase_client()
        
        # Get store with user verification
        result = supabase_client.table('stores').select(
            '*'
        ).eq('id', shop_id).eq('shop_config->>user_id', user_id).eq('is_active', True).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        store_record = result.data[0]
        shop_config = store_record.get("shop_config", {})
        
        # Map the stores table data to ShopifyStore model format
        shopify_store_data = {
            "id": store_record["id"],
            "shop_domain": store_record["shop_domain"],
            "shop_name": store_record["shop_name"],
            "access_token": store_record["access_token"],
            "scope": shop_config.get("scope", ""),
            "is_active": store_record["is_active"],
            "user_id": shop_config.get("user_id", user_id),
            "shop_id": shop_config.get("shop_id"),
            "shop_config": shop_config,
            "last_sync_at": None,  # Will be updated during sync
            "created_at": store_record["created_at"],
            "updated_at": store_record["updated_at"]
        }
        
        return ShopifyStore(**shopify_store_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get store error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve store"
        )


@router.get(
    "/stores/{shop_id}/stats",
    response_model=ShopifyStoreStats,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get store statistics",
    description="Get statistics and metrics for a Shopify store",
)
async def get_store_stats(
    shop_id: int,
    user_id: str = Depends(get_current_user_id),
    shopify_service=Depends(get_shopify_service),
):
    """Get store statistics."""
    
    try:
        from app.core.database import get_supabase_client
        supabase_client = get_supabase_client()
        
        # Verify store ownership
        store_result = supabase_client.table('stores').select(
            'id, shop_config'
        ).eq('id', shop_id).eq('shop_config->>user_id', user_id).eq('is_active', True).execute()
        
        if not store_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        store_data = store_result.data[0]
        
        # Get product statistics
        product_stats = supabase_client.table('products').select(
            'status', count='exact'
        ).eq('shop_id', shop_id).execute()
        
        total_products = product_stats.count or 0
        
        # Get active products count
        active_products_stats = supabase_client.table('products').select(
            'sku_id', count='exact'
        ).eq('shop_id', shop_id).eq('status', 'active').execute()
        
        active_products = active_products_stats.count or 0
        
        # Get order statistics (if orders table exists)
        try:
            order_stats = supabase_client.table('shopify_orders').select(
                'total_price', count='exact'
            ).eq('shop_id', shop_id).execute()
            
            total_orders = order_stats.count or 0
            total_revenue = sum(float(order.get('total_price', 0)) for order in order_stats.data)
            
            # Orders in last 30 days
            from datetime import datetime, timedelta
            thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
            
            recent_orders = supabase_client.table('shopify_orders').select(
                'total_price', count='exact'
            ).eq('shop_id', shop_id).gte('created_at', thirty_days_ago).execute()
            
            orders_last_30_days = recent_orders.count or 0
            revenue_last_30_days = sum(float(order.get('total_price', 0)) for order in recent_orders.data)
            
        except Exception:
            # Orders table might not exist yet
            total_orders = 0
            orders_last_30_days = 0
            total_revenue = 0.0
            revenue_last_30_days = 0.0
        
        # Get current sync status
        sync_status = None
        try:
            sync_result = supabase_client.table('sync_jobs').select(
                'status'
            ).eq('shop_id', shop_id).order('created_at', desc=True).limit(1).execute()
            
            if sync_result.data:
                sync_status = sync_result.data[0]['status']
        except Exception:
            pass
        
        return ShopifyStoreStats(
            shop_id=shop_id,
            total_products=total_products,
            active_products=active_products,
            total_orders=total_orders,
            orders_last_30_days=orders_last_30_days,
            total_revenue=total_revenue,
            revenue_last_30_days=revenue_last_30_days,
            last_sync_at=store_data.get('last_sync_at'),
            sync_status=sync_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get store stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve store statistics"
        )


@router.post(
    "/stores/{shop_id}/sync/products",
    response_model=ShopifySyncJob,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Sync products from Shopify",
    description="Start a product synchronization job for a Shopify store",
)
async def sync_products(
    shop_id: int,
    sync_request: ShopifyProductSyncRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    shopify_service=Depends(get_shopify_service),
):
    """Sync products from Shopify."""
    
    try:
        # Verify store ownership
        from app.core.database import get_supabase_client
        supabase_client = get_supabase_client()
        
        store_result = supabase_client.table('stores').select(
            'id'
        ).eq('id', shop_id).eq('shop_config->>user_id', user_id).eq('is_active', True).execute()
        
        if not store_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        # Start product sync
        sync_job = await shopify_service.sync_products(
            shop_id=shop_id,
            full_sync=sync_request.full_sync
        )
        
        # Log sync initiation
        log_business_event(
            "shopify_product_sync_started",
            user_id=user_id,
            shop_id=shop_id,
            sync_job_id=sync_job.id,
            full_sync=sync_request.full_sync
        )
        
        return sync_job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start product sync"
        )


@router.get(
    "/stores/{shop_id}/sync/jobs",
    response_model=List[ShopifySyncJob],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get sync jobs",
    description="Get synchronization jobs for a Shopify store",
)
async def get_sync_jobs(
    shop_id: int,
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    shopify_service=Depends(get_shopify_service),
):
    """Get sync jobs for a store."""
    
    try:
        from app.core.database import get_supabase_client
        supabase_client = get_supabase_client()
        
        # Verify store ownership
        store_result = supabase_client.table('stores').select(
            'id'
        ).eq('id', shop_id).eq('shop_config->>user_id', user_id).eq('is_active', True).execute()
        
        if not store_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        # Get sync jobs
        result = supabase_client.table('sync_jobs').select(
            '*'
        ).eq('shop_id', shop_id).order('created_at', desc=True).limit(limit).execute()
        
        sync_jobs = [ShopifySyncJob(**job_data) for job_data in result.data]
        
        return sync_jobs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sync jobs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sync jobs"
        )


@router.post(
    "/webhooks/orders_create",
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid webhook"},
        401: {"model": ErrorResponse, "description": "Invalid signature"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Handle orders/create webhook",
    description="Process Shopify orders/create webhook",
)
async def handle_orders_create_webhook(
    request: Request,
    shopify_service=Depends(get_shopify_service),
):
    """Handle orders/create webhook."""
    return await _handle_webhook(request, ShopifyWebhookEventType.ORDERS_CREATE, shopify_service)


@router.post(
    "/webhooks/orders_update",
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid webhook"},
        401: {"model": ErrorResponse, "description": "Invalid signature"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Handle orders/update webhook",
    description="Process Shopify orders/update webhook",
)
async def handle_orders_update_webhook(
    request: Request,
    shopify_service=Depends(get_shopify_service),
):
    """Handle orders/update webhook."""
    return await _handle_webhook(request, ShopifyWebhookEventType.ORDERS_UPDATE, shopify_service)


@router.post(
    "/webhooks/products_create",
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid webhook"},
        401: {"model": ErrorResponse, "description": "Invalid signature"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Handle products/create webhook",
    description="Process Shopify products/create webhook",
)
async def handle_products_create_webhook(
    request: Request,
    shopify_service=Depends(get_shopify_service),
):
    """Handle products/create webhook."""
    return await _handle_webhook(request, ShopifyWebhookEventType.PRODUCTS_CREATE, shopify_service)


@router.post(
    "/webhooks/products_update",
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid webhook"},
        401: {"model": ErrorResponse, "description": "Invalid signature"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Handle products/update webhook",
    description="Process Shopify products/update webhook",
)
async def handle_products_update_webhook(
    request: Request,
    shopify_service=Depends(get_shopify_service),
):
    """Handle products/update webhook."""
    return await _handle_webhook(request, ShopifyWebhookEventType.PRODUCTS_UPDATE, shopify_service)


@router.post(
    "/webhooks/app_uninstalled",
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid webhook"},
        401: {"model": ErrorResponse, "description": "Invalid signature"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Handle app/uninstalled webhook",
    description="Process Shopify app/uninstalled webhook",
)
async def handle_app_uninstalled_webhook(
    request: Request,
    shopify_service=Depends(get_shopify_service),
):
    """Handle app/uninstalled webhook."""
    return await _handle_webhook(request, ShopifyWebhookEventType.APP_UNINSTALLED, shopify_service)


async def _handle_webhook(
    request: Request,
    event_type: ShopifyWebhookEventType,
    shopify_service,
) -> JSONResponse:
    """Common webhook handler."""
    
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Get headers
        signature = request.headers.get("X-Shopify-Hmac-Sha256")
        shop_domain = request.headers.get("X-Shopify-Shop-Domain")
        webhook_id = request.headers.get("X-Shopify-Webhook-Id")
        
        if not signature:
            log_security_event(
                "shopify_webhook_missing_signature",
                shop_domain=shop_domain,
                event_type=event_type.value
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature"
            )
        
        if not shop_domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing shop domain"
            )
        
        # Verify signature
        if not await shopify_service.verify_webhook_signature(body, signature):
            log_security_event(
                "shopify_webhook_invalid_signature",
                shop_domain=shop_domain,
                event_type=event_type.value,
                signature=signature
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse payload
        try:
            import json
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Process webhook
        webhook_event = await shopify_service.process_webhook(
            shop_domain=shop_domain,
            event_type=event_type,
            payload=payload,
            webhook_id=webhook_id
        )
        
        # Log webhook processing
        log_business_event(
            "shopify_webhook_processed",
            shop_domain=shop_domain,
            event_type=event_type.value,
            webhook_event_id=webhook_event.id,
            shopify_id=webhook_event.shopify_id
        )
        
        return JSONResponse(
            status_code=200,
            content={"message": "Webhook processed successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.delete(
    "/stores/{shop_id}",
    responses={
        200: {"description": "Store disconnected successfully"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Store not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Disconnect Shopify store",
    description="Disconnect and deactivate a Shopify store with comprehensive cleanup",
)
async def disconnect_store(
    shop_id: int,
    user_id: str = Depends(get_current_user_id),
    shopify_service=Depends(get_shopify_service),
):
    """Disconnect Shopify store with comprehensive cleanup."""
    
    try:
        # Use the enhanced disconnect functionality from the service
        result = await shopify_service.disconnect_store(shop_id, user_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Store disconnect error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect store"
        )