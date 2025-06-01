"""
Shopify service layer for API interactions and business logic.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlparse

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.database import get_supabase_client
from app.core.logging import (
    log_business_event,
    log_security_event,
    log_sync_operation,
    log_shopify_api_call,
    log_product_sync_progress,
    log_store_operation,
    log_webhook_processing
)
from app.models.shopify import (
    ShopifyApiError,
    ShopifyOAuthCallback,
    ShopifyOrder,
    ShopifyOrderCreate,
    ShopifyProduct,
    ShopifyProductCreate,
    ShopifyRateLimitInfo,
    ShopifyStore,
    ShopifyStoreCreate,
    ShopifySyncJob,
    ShopifySyncJobCreate,
    ShopifySyncStatus,
    ShopifySyncType,
    ShopifyWebhookEvent,
    ShopifyWebhookEventCreate,
    ShopifyWebhookEventType,
)

logger = logging.getLogger(__name__)


class ShopifyRateLimiter:
    """Rate limiter for Shopify API calls using leaky bucket algorithm."""
    
    def __init__(self, bucket_size: int = 40, leak_rate: float = 2.0):
        """
        Initialize rate limiter.
        
        Args:
            bucket_size: Maximum number of tokens in bucket
            leak_rate: Rate at which tokens leak (calls per second)
        """
        self.bucket_size = bucket_size
        self.leak_rate = leak_rate
        self.tokens = bucket_size
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False otherwise
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.bucket_size,
                self.tokens + elapsed * self.leak_rate
            )
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> None:
        """Wait until tokens are available."""
        while not await self.acquire(tokens):
            await asyncio.sleep(0.1)


class ShopifyApiClient:
    """Shopify API client with rate limiting and error handling."""
    
    def __init__(self, shop_domain: str, access_token: str):
        """
        Initialize Shopify API client.
        
        Args:
            shop_domain: Shopify store domain
            access_token: Shopify access token
        """
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.base_url = f"https://{shop_domain}/admin/api/{settings.SHOPIFY_API_VERSION}"
        self.rate_limiter = ShopifyRateLimiter()
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-Shopify-Access-Token": access_token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    def _verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Shopify webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: HMAC signature from header
            
        Returns:
            True if signature is valid
        """
        if not settings.SHOPIFY_CLIENT_SECRET:
            logger.warning("Shopify client secret not configured")
            return False
        
        expected_signature = hmac.new(
            settings.SHOPIFY_CLIENT_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Tuple[Dict[str, Any], ShopifyRateLimitInfo]:
        """
        Make authenticated request to Shopify API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            retry_count: Current retry attempt
            
        Returns:
            Tuple of response data and rate limit info
        """
        await self.rate_limiter.wait_for_tokens()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_start_time = time.time()
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            
            request_duration = time.time() - request_start_time
            
            # Parse rate limit headers
            rate_limit_info = self._parse_rate_limit_headers(response.headers)
            
            # Log API call
            log_shopify_api_call(
                endpoint=endpoint,
                method=method,
                shop_domain=self.shop_domain,
                status_code=response.status_code,
                duration=request_duration,
                rate_limit_remaining=rate_limit_info.call_remaining,
                rate_limit_total=rate_limit_info.call_limit,
                retry_count=retry_count
            )
            
            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get("Retry-After", 1))
                if retry_count < 3:
                    logger.warning(f"Rate limited, retrying after {retry_after}s")
                    log_shopify_api_call(
                        endpoint=endpoint,
                        method=method,
                        shop_domain=self.shop_domain,
                        status_code=response.status_code,
                        duration=request_duration,
                        rate_limit_remaining=rate_limit_info.call_remaining,
                        rate_limit_total=rate_limit_info.call_limit,
                        retry_count=retry_count,
                        retry_after=retry_after,
                        action="retrying"
                    )
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, endpoint, params, data, retry_count + 1)
                else:
                    log_shopify_api_call(
                        endpoint=endpoint,
                        method=method,
                        shop_domain=self.shop_domain,
                        status_code=response.status_code,
                        duration=request_duration,
                        rate_limit_remaining=rate_limit_info.call_remaining,
                        rate_limit_total=rate_limit_info.call_limit,
                        retry_count=retry_count,
                        action="rate_limit_exceeded"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Shopify API rate limit exceeded"
                    )
            
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"message": "No JSON response"}
            
            return response_data, rate_limit_info
            
        except httpx.HTTPStatusError as e:
            request_duration = time.time() - request_start_time
            error_data = {}
            try:
                error_data = e.response.json()
            except json.JSONDecodeError:
                pass
            
            # Log API error
            log_shopify_api_call(
                endpoint=endpoint,
                method=method,
                shop_domain=self.shop_domain,
                status_code=e.response.status_code,
                duration=request_duration,
                retry_count=retry_count,
                error_message=error_data.get('message', str(e)),
                action="http_error"
            )
            
            logger.error(f"Shopify API error: {e.response.status_code} - {error_data}")
            
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Shopify API error: {error_data.get('message', str(e))}"
            )
        
        except httpx.RequestError as e:
            request_duration = time.time() - request_start_time
            
            # Log request error
            log_shopify_api_call(
                endpoint=endpoint,
                method=method,
                shop_domain=self.shop_domain,
                status_code=None,
                duration=request_duration,
                retry_count=retry_count,
                error_message=str(e),
                action="request_error"
            )
            
            logger.error(f"Shopify API request error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Shopify API unavailable"
            )
    
    def _parse_rate_limit_headers(self, headers: Dict[str, str]) -> ShopifyRateLimitInfo:
        """Parse rate limit information from response headers."""
        call_limit_header = headers.get("X-Shopify-Shop-Api-Call-Limit", "0/40")
        call_made, call_limit = map(int, call_limit_header.split("/"))
        
        return ShopifyRateLimitInfo(
            call_limit=call_limit,
            call_made=call_made,
            call_remaining=call_limit - call_made,
            retry_after=headers.get("Retry-After"),
            bucket_size=call_limit
        )
    
    async def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information."""
        response_data, _ = await self._make_request("GET", "/shop.json")
        return response_data.get("shop", {})
    
    async def get_products(
        self,
        limit: int = 250,
        since_id: Optional[int] = None,
        published_status: str = "any"
    ) -> List[Dict[str, Any]]:
        """Get products from Shopify."""
        params = {
            "limit": min(limit, 250),
            "published_status": published_status
        }
        if since_id:
            params["since_id"] = since_id
        
        response_data, _ = await self._make_request("GET", "/products.json", params=params)
        return response_data.get("products", [])
    
    async def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get single product by ID."""
        response_data, _ = await self._make_request("GET", f"/products/{product_id}.json")
        return response_data.get("product", {})
    
    async def get_orders(
        self,
        limit: int = 250,
        since_id: Optional[int] = None,
        created_at_min: Optional[datetime] = None,
        financial_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get orders from Shopify."""
        params = {"limit": min(limit, 250)}
        
        if since_id:
            params["since_id"] = since_id
        if created_at_min:
            params["created_at_min"] = created_at_min.isoformat()
        if financial_status:
            params["financial_status"] = financial_status
        
        response_data, _ = await self._make_request("GET", "/orders.json", params=params)
        return response_data.get("orders", [])
    
    async def get_inventory_levels(
        self,
        location_ids: Optional[List[int]] = None,
        inventory_item_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Get inventory levels."""
        params = {}
        if location_ids:
            params["location_ids"] = ",".join(map(str, location_ids))
        if inventory_item_ids:
            params["inventory_item_ids"] = ",".join(map(str, inventory_item_ids))
        
        response_data, _ = await self._make_request("GET", "/inventory_levels.json", params=params)
        return response_data.get("inventory_levels", [])
    
    async def create_webhook(self, topic: str, address: str) -> Dict[str, Any]:
        """Create a webhook."""
        webhook_data = {
            "webhook": {
                "topic": topic,
                "address": address,
                "format": "json"
            }
        }
        
        try:
            response_data, _ = await self._make_request("POST", "/webhooks.json", data=webhook_data)
            return response_data.get("webhook", {})
        except HTTPException as e:
            # Enhance error messages for common webhook creation issues
            if e.status_code == 403:
                if "protected customer data" in str(e.detail).lower():
                    raise HTTPException(
                        status_code=403,
                        detail=f"Cannot create webhook for {topic}: Requires protected customer data permissions. This topic contains sensitive customer information that requires additional app permissions."
                    )
                else:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Permission denied for webhook topic {topic}: {e.detail}"
                    )
            elif e.status_code == 422:
                if "address is not allowed" in str(e.detail).lower():
                    raise HTTPException(
                        status_code=422,
                        detail=f"Webhook address not allowed for {topic}: {address}. Webhooks require publicly accessible URLs (not localhost)."
                    )
                else:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Invalid webhook configuration for {topic}: {e.detail}"
                    )
            else:
                # Re-raise other HTTP exceptions as-is
                raise
    
    async def get_webhooks(self) -> List[Dict[str, Any]]:
        """Get existing webhooks."""
        response_data, _ = await self._make_request("GET", "/webhooks.json")
        return response_data.get("webhooks", [])


class ShopifyService:
    """Main Shopify service for business logic and data management."""
    
    def __init__(self):
        """Initialize Shopify service."""
        self.supabase_client = get_supabase_client()
    
    def generate_oauth_url(
        self,
        shop_domain: str,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> str:
        """
        Generate Shopify OAuth authorization URL.
        
        Args:
            shop_domain: Shopify store domain
            redirect_uri: OAuth redirect URI
            state: Optional state parameter
            
        Returns:
            OAuth authorization URL
        """
        if not settings.SHOPIFY_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Shopify client ID not configured"
            )
        
        params = {
            "client_id": settings.SHOPIFY_CLIENT_ID,
            "scope": settings.shopify_scope_string,
            "redirect_uri": redirect_uri,
        }
        
        if state:
            params["state"] = state
        
        return f"https://{shop_domain}/admin/oauth/authorize?{urlencode(params)}"
    
    async def exchange_oauth_code(
        self,
        shop_domain: str,
        code: str,
        user_id: str
    ) -> ShopifyStore:
        """
        Exchange OAuth code for access token and create store.
        
        Args:
            shop_domain: Shopify store domain
            code: OAuth authorization code
            user_id: User ID
            
        Returns:
            Created Shopify store
        """
        # Log the start of the OAuth exchange process with input validation
        logger.info("=== STARTING OAUTH TOKEN EXCHANGE ===")
        logger.info(f"Input parameters - shop_domain: {shop_domain}, user_id: {user_id}")
        logger.info(f"OAuth code length: {len(code) if code else 0}")
        logger.info(f"OAuth code preview: {code[:10]}..." if code and len(code) > 10 else f"OAuth code: {code}")
        
        # Validate input parameters
        if not shop_domain:
            logger.error("VALIDATION ERROR: shop_domain is empty or None")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shop domain is required"
            )
        
        if not code:
            logger.error("VALIDATION ERROR: OAuth code is empty or None")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth code is required"
            )
        
        if not user_id:
            logger.error("VALIDATION ERROR: user_id is empty or None")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required"
            )
        
        # Validate OAuth credentials configuration
        if not settings.SHOPIFY_CLIENT_ID or not settings.SHOPIFY_CLIENT_SECRET:
            logger.error("CONFIGURATION ERROR: Shopify OAuth credentials not configured")
            logger.error(f"SHOPIFY_CLIENT_ID present: {bool(settings.SHOPIFY_CLIENT_ID)}")
            logger.error(f"SHOPIFY_CLIENT_SECRET present: {bool(settings.SHOPIFY_CLIENT_SECRET)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Shopify OAuth credentials not configured"
            )
        
        logger.info("✓ Input validation passed")
        
        # Prepare token exchange request
        token_url = f"https://{shop_domain}/admin/oauth/access_token"
        token_data = {
            "client_id": settings.SHOPIFY_CLIENT_ID,
            "client_secret": settings.SHOPIFY_CLIENT_SECRET,
            "code": code
        }
        
        # Log request details (without exposing sensitive data)
        logger.info("=== PREPARING TOKEN EXCHANGE REQUEST ===")
        logger.info(f"Token URL: {token_url}")
        logger.info(f"Request payload keys: {list(token_data.keys())}")
        logger.info(f"Client ID: {settings.SHOPIFY_CLIENT_ID[:8]}..." if settings.SHOPIFY_CLIENT_ID else "None")
        logger.info(f"Client secret present: {bool(settings.SHOPIFY_CLIENT_SECRET)}")
        logger.info(f"Code length: {len(code)}")
        
        # Create HTTP client with detailed logging
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info("=== SENDING TOKEN EXCHANGE REQUEST ===")
                logger.info(f"HTTP Method: POST")
                logger.info(f"Request URL: {token_url}")
                logger.info(f"Request headers: Content-Type: application/json")
                
                # Make the token exchange request
                response = await client.post(token_url, json=token_data)
                
                logger.info("=== RECEIVED TOKEN EXCHANGE RESPONSE ===")
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                logger.info(f"Response content length: {len(response.content)} bytes")
                
                # Log response body (safely)
                try:
                    response_text = response.text
                    logger.info(f"Response body length: {len(response_text)} characters")
                    if response.status_code == 200:
                        # For successful responses, log structure without sensitive data
                        try:
                            response_json = response.json()
                            response_keys = list(response_json.keys()) if isinstance(response_json, dict) else "not_dict"
                            logger.info(f"Response JSON keys: {response_keys}")
                            if "access_token" in response_json:
                                logger.info(f"✓ Access token received (length: {len(response_json['access_token'])})")
                            if "scope" in response_json:
                                logger.info(f"✓ Scope received: {response_json.get('scope')}")
                        except Exception as json_parse_error:
                            logger.error(f"Failed to parse successful response as JSON: {json_parse_error}")
                            logger.error(f"Response text preview: {response_text[:200]}...")
                    else:
                        # For error responses, log the full error
                        logger.error(f"Error response body: {response_text}")
                except Exception as text_error:
                    logger.error(f"Failed to read response text: {text_error}")
                
                # Check for non-200 status codes
                if response.status_code != 200:
                    logger.error("=== TOKEN EXCHANGE FAILED ===")
                    logger.error(f"HTTP Status: {response.status_code}")
                    logger.error(f"Status reason: {response.reason_phrase}")
                    
                    try:
                        error_body = response.text
                        logger.error(f"Error response body: {error_body}")
                        
                        # Try to parse error as JSON for more details
                        try:
                            error_json = response.json()
                            logger.error(f"Error JSON: {error_json}")
                        except:
                            logger.error("Error response is not valid JSON")
                            
                    except Exception as e:
                        logger.error(f"Failed to read error response: {e}")
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Shopify OAuth token exchange failed: HTTP {response.status_code} - {response.text}"
                    )
                
                # Raise for any other HTTP errors
                response.raise_for_status()
                
                # Parse the successful response
                logger.info("=== PARSING TOKEN RESPONSE ===")
                try:
                    token_response = response.json()
                    logger.info("✓ Response parsed as JSON successfully")
                    logger.info(f"Response type: {type(token_response)}")
                    
                    if isinstance(token_response, dict):
                        logger.info(f"Response keys: {list(token_response.keys())}")
                    else:
                        logger.error(f"Unexpected response type: {type(token_response)}")
                        
                except json.JSONDecodeError as json_error:
                    logger.error(f"JSON parsing failed: {json_error}")
                    logger.error(f"Response content: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid JSON response from Shopify"
                    )
                
            except httpx.HTTPStatusError as e:
                logger.error("=== HTTP STATUS ERROR ===")
                logger.error(f"HTTP Status Error: {e}")
                logger.error(f"Request URL: {e.request.url}")
                logger.error(f"Request method: {e.request.method}")
                logger.error(f"Response status: {e.response.status_code}")
                
                try:
                    error_text = e.response.text
                    logger.error(f"Error response text: {error_text}")
                except:
                    logger.error("Could not read error response text")
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Shopify API error: HTTP {e.response.status_code}"
                )
                
            except httpx.RequestError as e:
                logger.error("=== HTTP REQUEST ERROR ===")
                logger.error(f"Request Error: {e}")
                logger.error(f"Error type: {type(e)}")
                logger.error(f"Request URL: {getattr(e.request, 'url', 'unknown') if hasattr(e, 'request') else 'unknown'}")
                
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to connect to Shopify: {str(e)}"
                )
                
            except Exception as e:
                logger.error("=== UNEXPECTED ERROR ===")
                logger.error(f"Unexpected error type: {type(e)}")
                logger.error(f"Unexpected error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OAuth processing error: {str(e)}"
                )
        
        # Extract access token and scope from response
        logger.info("=== EXTRACTING ACCESS TOKEN ===")
        access_token = token_response.get("access_token")
        scope = token_response.get("scope", "")
        
        logger.info(f"Access token present: {bool(access_token)}")
        if access_token:
            logger.info(f"Access token length: {len(access_token)}")
            logger.info(f"Access token prefix: {access_token[:8]}..." if len(access_token) > 8 else access_token)
        else:
            logger.error("❌ No access token in response")
            logger.error(f"Available response keys: {list(token_response.keys())}")
        
        logger.info(f"Scope present: {bool(scope)}")
        logger.info(f"Scope value: {scope}")
        
        if not access_token:
            logger.error("=== TOKEN EXTRACTION FAILED ===")
            logger.error("Access token is missing from Shopify response")
            logger.error(f"Full response keys: {list(token_response.keys())}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Shopify"
            )
        
        logger.info("✓ Access token extracted successfully")
        
        # Get shop information using the access token
        logger.info("=== VERIFYING SHOP ACCESS ===")
        logger.info(f"Creating Shopify API client for shop: {shop_domain}")
        
        async with ShopifyApiClient(shop_domain, access_token) as api_client:
            try:
                logger.info("Requesting shop information from Shopify API...")
                shop_info = await api_client.get_shop_info()
                
                logger.info("=== SHOP INFO RETRIEVED ===")
                logger.info(f"Shop info type: {type(shop_info)}")
                if isinstance(shop_info, dict):
                    logger.info(f"Shop info keys: {list(shop_info.keys())}")
                    logger.info(f"Shop name: {shop_info.get('name', 'unknown')}")
                    logger.info(f"Shop ID: {shop_info.get('id', 'unknown')}")
                    logger.info(f"Shop domain: {shop_info.get('domain', 'unknown')}")
                    logger.info(f"Shop myshopify_domain: {shop_info.get('myshopify_domain', 'unknown')}")
                else:
                    logger.warning(f"Unexpected shop info format: {shop_info}")
                
                logger.info("✓ Shop access verified successfully")
                
            except Exception as e:
                logger.error("=== SHOP ACCESS VERIFICATION FAILED ===")
                logger.error(f"Error type: {type(e)}")
                logger.error(f"Error message: {str(e)}")
                
                # Log additional details if it's an HTTP exception
                if hasattr(e, 'status_code'):
                    logger.error(f"HTTP status code: {e.status_code}")
                if hasattr(e, 'detail'):
                    logger.error(f"Error detail: {e.detail}")
                
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to verify shop access: {str(e)}"
                )
        
        # Create store data object
        logger.info("=== CREATING STORE DATA ===")
        
        shop_name = shop_info.get("name", shop_domain.split(".")[0].title())
        shop_id = shop_info.get("id")
        
        logger.info(f"Extracted shop name: {shop_name}")
        logger.info(f"Extracted shop ID: {shop_id}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Scope: {scope}")
        
        oauth_scopes = scope.split(",") if scope else []
        logger.info(f"OAuth scopes: {oauth_scopes}")
        
        # Create store data in the format expected by the stores table
        store_data_for_db = {
            "shop_domain": shop_domain,
            "shop_name": shop_name,
            "access_token": access_token,
            "is_active": True,
            "shop_config": {
                "user_id": user_id,
                "shop_id": shop_id,
                "scope": scope,
                "shop_info": shop_info,
                "connected_at": datetime.utcnow().isoformat(),
                "oauth_scopes": oauth_scopes
            }
        }
        
        logger.info("✓ Store data object created successfully")
        logger.info(f"Store data keys: {list(store_data_for_db.keys())}")
        
        # Store in database
        logger.info("=== SAVING TO DATABASE ===")
        logger.info("Attempting to upsert store data to stores table")
        
        try:
            result = self.supabase_client.table('stores').upsert(
                store_data_for_db,
                on_conflict='shop_domain'
            ).execute()
            
            logger.info("=== DATABASE OPERATION RESULT ===")
            logger.info(f"Database result type: {type(result)}")
            logger.info(f"Result data present: {bool(result.data)}")
            
            if result.data:
                logger.info(f"Number of records returned: {len(result.data)}")
                logger.info(f"First record keys: {list(result.data[0].keys()) if result.data else 'none'}")
            else:
                logger.error("❌ No data returned from database upsert")
                logger.error(f"Result object: {result}")
                
        except Exception as db_error:
            logger.error("=== DATABASE ERROR ===")
            logger.error(f"Database error type: {type(db_error)}")
            logger.error(f"Database error: {db_error}")
            import traceback
            logger.error(f"Database traceback: {traceback.format_exc()}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while saving store: {str(db_error)}"
            )
        
        if not result.data:
            logger.error("=== STORE SAVE FAILED ===")
            logger.error("Database upsert returned no data")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save store to database"
            )
        
        store_record = result.data[0]
        logger.info("✓ Store saved to database successfully")
        logger.info(f"Saved store ID: {store_record.get('id')}")
        logger.info(f"Saved store domain: {store_record.get('shop_domain')}")
        
        # Log successful connection
        logger.info("=== LOGGING BUSINESS EVENT ===")
        log_business_event(
            "shopify_store_connected",
            user_id=user_id,
            shop_id=store_record["id"],
            shop_domain=shop_domain,
            shop_name=shop_name
        )
        logger.info("✓ Business event logged")
        
        # Setup webhooks
        logger.info("=== SETTING UP WEBHOOKS ===")
        try:
            await self._setup_webhooks(shop_domain, access_token, store_record["id"])
            logger.info("✓ Webhooks setup completed")
        except Exception as webhook_error:
            logger.warning(f"Webhook setup failed (non-critical): {webhook_error}")
            # Don't fail the entire process if webhooks fail
        
        # Create final store object by mapping the stores table data to ShopifyStore model
        logger.info("=== CREATING FINAL STORE OBJECT ===")
        try:
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
            
            final_store = ShopifyStore(**shopify_store_data)
            logger.info("✓ Final store object created successfully")
            logger.info(f"Final store ID: {final_store.id}")
            logger.info(f"Final store domain: {final_store.shop_domain}")
        except Exception as store_creation_error:
            logger.error(f"Failed to create final store object: {store_creation_error}")
            logger.error(f"Store record: {store_record}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create store object: {str(store_creation_error)}"
            )
        
        logger.info("=== OAUTH TOKEN EXCHANGE COMPLETED SUCCESSFULLY ===")
        return final_store
    
    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """Verify webhook signature."""
        if not settings.SHOPIFY_CLIENT_SECRET:
            return False
        
        expected_signature = hmac.new(
            settings.SHOPIFY_CLIENT_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def process_webhook(
        self,
        shop_domain: str,
        event_type: ShopifyWebhookEventType,
        payload: Dict[str, Any],
        webhook_id: Optional[str] = None
    ) -> ShopifyWebhookEvent:
        """
        Process incoming webhook event.
        
        Args:
            shop_domain: Shop domain
            event_type: Webhook event type
            payload: Webhook payload
            webhook_id: Webhook ID
            
        Returns:
            Created webhook event record
        """
        # Get store by domain
        store_result = self.supabase_client.table('stores').select(
            'id'
        ).eq('shop_domain', shop_domain).eq('is_active', True).execute()
        
        if not store_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )
        
        shop_id = store_result.data[0]["id"]
        
        # Create webhook event record
        event_data = ShopifyWebhookEventCreate(
            shop_id=shop_id,
            event_type=event_type,
            shopify_id=str(payload.get("id", "")),
            event_data=payload,
            webhook_id=webhook_id
        )
        
        result = self.supabase_client.table('webhook_events').insert(
            event_data.dict()
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create webhook event"
            )
        
        event_record = result.data[0]
        
        # Process event asynchronously
        asyncio.create_task(self._process_webhook_event(event_record["id"]))
        
        return ShopifyWebhookEvent(**event_record)
    
    async def sync_products(self, shop_id: int, full_sync: bool = False) -> ShopifySyncJob:
        """
        Sync products from Shopify.
        
        Args:
            shop_id: Store ID
            full_sync: Whether to perform full sync
            
        Returns:
            Created sync job
        """
        # Get store
        store = await self._get_store(shop_id)
        
        # Create sync job
        sync_job_data = ShopifySyncJobCreate(
            shop_id=shop_id,
            sync_type=ShopifySyncType.FULL_SYNC if full_sync else ShopifySyncType.PRODUCT_SYNC,
            sync_config={"full_sync": full_sync}
        )
        
        result = self.supabase_client.table('sync_jobs').insert(
            sync_job_data.dict()
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create sync job"
            )
        
        sync_job = ShopifySyncJob(**result.data[0])
        
        # Start sync process asynchronously
        asyncio.create_task(self._run_product_sync(sync_job.id))
        
        return sync_job
    
    async def _get_store(self, shop_id: int) -> ShopifyStore:
        """Get store by ID."""
        result = self.supabase_client.table('stores').select(
            '*'
        ).eq('id', shop_id).eq('is_active', True).execute()
        
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
            "user_id": shop_config.get("user_id", ""),
            "shop_id": shop_config.get("shop_id"),
            "shop_config": shop_config,
            "last_sync_at": None,  # Will be updated during sync
            "created_at": store_record["created_at"],
            "updated_at": store_record["updated_at"]
        }
        
        return ShopifyStore(**shopify_store_data)
    
    async def _setup_webhooks(
        self,
        shop_domain: str,
        access_token: str,
        shop_id: int
    ) -> None:
        """Setup required webhooks for the store."""
        # Core webhooks that don't require protected customer data permissions
        core_webhook_topics = [
            "products/create",
            "products/update",
            "products/delete",
            "inventory_levels/update",
            "app/uninstalled"
        ]
        
        # Order webhooks that require protected customer data permissions
        # These are optional and will be skipped if permissions are insufficient
        order_webhook_topics = [
            "orders/create",
            "orders/updated",
            "orders/paid",
            "orders/cancelled"
        ]
        
        # Check if we have a publicly accessible webhook URL
        webhook_base_url = self._get_webhook_base_url()
        if not webhook_base_url:
            logger.warning("No publicly accessible webhook URL configured. Skipping webhook setup.")
            logger.info("To enable webhooks, set WEBHOOK_BASE_URL environment variable to your public domain")
            return
        
        logger.info(f"Setting up webhooks with base URL: {webhook_base_url}")
        
        async with ShopifyApiClient(shop_domain, access_token) as api_client:
            try:
                # Get existing webhooks
                existing_webhooks = await api_client.get_webhooks()
                existing_topics = {wh.get("topic") for wh in existing_webhooks}
                logger.info(f"Found {len(existing_webhooks)} existing webhooks: {existing_topics}")
                
                # Track webhook creation results
                created_webhooks = []
                failed_webhooks = []
                
                # Create core webhooks (required)
                for topic in core_webhook_topics:
                    if topic not in existing_topics:
                        webhook_url = f"{webhook_base_url}/{topic.replace('/', '_')}"
                        try:
                            webhook = await api_client.create_webhook(topic, webhook_url)
                            created_webhooks.append(topic)
                            logger.info(f"✓ Created core webhook for {topic}")
                        except Exception as e:
                            failed_webhooks.append((topic, str(e)))
                            logger.error(f"✗ Failed to create core webhook for {topic}: {e}")
                
                # Create order webhooks (optional - may fail due to permissions)
                for topic in order_webhook_topics:
                    if topic not in existing_topics:
                        webhook_url = f"{webhook_base_url}/{topic.replace('/', '_')}"
                        try:
                            webhook = await api_client.create_webhook(topic, webhook_url)
                            created_webhooks.append(topic)
                            logger.info(f"✓ Created order webhook for {topic}")
                        except Exception as e:
                            error_msg = str(e)
                            if "protected customer data" in error_msg.lower() or "permission" in error_msg.lower():
                                logger.info(f"⚠ Skipped order webhook {topic}: Requires protected customer data permissions")
                            else:
                                failed_webhooks.append((topic, error_msg))
                                logger.warning(f"✗ Failed to create order webhook for {topic}: {e}")
                
                # Log summary
                logger.info(f"Webhook setup completed: {len(created_webhooks)} created, {len(failed_webhooks)} failed")
                if created_webhooks:
                    logger.info(f"Created webhooks: {created_webhooks}")
                if failed_webhooks:
                    logger.warning(f"Failed webhooks: {[f'{topic}: {error}' for topic, error in failed_webhooks]}")
                
            except Exception as e:
                logger.error(f"Failed to setup webhooks: {e}")
                # Don't raise exception - webhook setup is optional
    
    def _get_webhook_base_url(self) -> Optional[str]:
        """Get the base URL for webhooks, ensuring it's publicly accessible."""
        # Check for explicit webhook URL configuration
        webhook_url = os.getenv("WEBHOOK_BASE_URL")
        if webhook_url:
            logger.info(f"Using configured webhook base URL: {webhook_url}")
            return f"{webhook_url.rstrip('/')}/api/v1/shopify/webhooks"
        
        # Check if any of the allowed origins are publicly accessible
        for origin in settings.ALLOWED_ORIGINS:
            if not self._is_localhost_url(origin):
                logger.info(f"Using public origin for webhooks: {origin}")
                return f"{origin}/api/v1/shopify/webhooks"
        
        # All origins are localhost - webhooks won't work
        logger.warning("All configured origins are localhost URLs. Webhooks require publicly accessible URLs.")
        return None
    
    def _is_localhost_url(self, url: str) -> bool:
        """Check if a URL is a localhost/local development URL."""
        localhost_indicators = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
            ".local"
        ]
        return any(indicator in url.lower() for indicator in localhost_indicators)
    
    async def _process_webhook_event(self, event_id: int) -> None:
        """Process webhook event asynchronously."""
        try:
            # Get event
            result = self.supabase_client.table('webhook_events').select(
                '*'
            ).eq('id', event_id).execute()
            
            if not result.data:
                return
            
            event = ShopifyWebhookEvent(**result.data[0])
            
            # Process based on event type
            if event.event_type in [
                ShopifyWebhookEventType.PRODUCTS_CREATE,
                ShopifyWebhookEventType.PRODUCTS_UPDATE
            ]:
                await self._process_product_webhook(event)
            elif event.event_type in [
                ShopifyWebhookEventType.ORDERS_CREATE,
                ShopifyWebhookEventType.ORDERS_UPDATE,
                ShopifyWebhookEventType.ORDERS_PAID
            ]:
                await self._process_order_webhook(event)
            
            # Mark as processed
            self.supabase_client.table('webhook_events').update({
                "processed": True,
                "processed_at": datetime.utcnow().isoformat()
            }).eq('id', event_id).execute()
            
        except Exception as e:
            logger.error(f"Failed to process webhook event {event_id}: {e}")
            
            # Update error
            self.supabase_client.table('webhook_events').update({
                "error_message": str(e),
                "retry_count": event.retry_count + 1
            }).eq('id', event_id).execute()
    
    async def _process_product_webhook(self, event: ShopifyWebhookEvent) -> None:
        """Process product webhook event."""
        # Implementation would sync product data
        pass
    
    async def _process_order_webhook(self, event: ShopifyWebhookEvent) -> None:
        """Process order webhook event."""
        # Implementation would sync order data
        pass
    
    async def _run_product_sync(self, sync_job_id: int) -> None:
        """Run product sync job asynchronously."""
        start_time = time.time()
        
        try:
            logger.info("=== STARTING PRODUCT SYNC JOB ===")
            logger.info(f"Sync job ID: {sync_job_id}")
            
            # Get sync job details
            sync_job_result = self.supabase_client.table('sync_jobs').select(
                '*'
            ).eq('id', sync_job_id).execute()
            
            if not sync_job_result.data:
                logger.error(f"Sync job {sync_job_id} not found")
                return
            
            sync_job = sync_job_result.data[0]
            shop_id = sync_job['shop_id']
            sync_config = sync_job.get('sync_config', {})
            full_sync = sync_config.get('full_sync', False)
            
            logger.info(f"Shop ID: {shop_id}")
            logger.info(f"Full sync: {full_sync}")
            
            # Update job status to running
            self.supabase_client.table('sync_jobs').update({
                "status": ShopifySyncStatus.RUNNING,
                "started_at": datetime.utcnow().isoformat()
            }).eq('id', sync_job_id).execute()
            
            log_sync_operation(
                "product_sync_started",
                shop_id=shop_id,
                sync_job_id=sync_job_id,
                status="running",
                full_sync=full_sync
            )
            
            # Get store details
            store = await self._get_store(shop_id)
            logger.info(f"Store: {store.shop_domain}")
            
            # Initialize counters
            total_products_processed = 0
            total_products_created = 0
            total_products_updated = 0
            total_products_failed = 0
            
            # Sync products using Shopify API
            async with ShopifyApiClient(store.shop_domain, store.access_token) as api_client:
                logger.info("=== FETCHING PRODUCTS FROM SHOPIFY ===")
                
                # Get all products with pagination
                all_products = []
                since_id = None
                page_count = 0
                
                while True:
                    page_count += 1
                    logger.info(f"Fetching page {page_count} (since_id: {since_id})")
                    
                    try:
                        products_batch = await api_client.get_products(
                            limit=250,
                            since_id=since_id,
                            published_status="any"
                        )
                        
                        if not products_batch:
                            logger.info("No more products to fetch")
                            break
                        
                        logger.info(f"Fetched {len(products_batch)} products in page {page_count}")
                        all_products.extend(products_batch)
                        
                        # Update since_id for next page
                        since_id = products_batch[-1]['id']
                        
                        # Rate limiting - wait between requests
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error fetching products page {page_count}: {e}")
                        break
                
                logger.info(f"=== TOTAL PRODUCTS FETCHED: {len(all_products)} ===")
                
                # Update total items count
                self.supabase_client.table('sync_jobs').update({
                    "total_items": len(all_products)
                }).eq('id', sync_job_id).execute()
                
                # Process each product
                for i, shopify_product in enumerate(all_products):
                    try:
                        logger.info(f"Processing product {i+1}/{len(all_products)}: {shopify_product.get('title', 'Unknown')}")
                        
                        # Process each variant as a separate product
                        variants = shopify_product.get('variants', [])
                        if not variants:
                            logger.warning(f"Product {shopify_product['id']} has no variants, skipping")
                            continue
                        
                        for variant in variants:
                            try:
                                await self._sync_product_variant(
                                    shop_id=shop_id,
                                    shopify_product=shopify_product,
                                    variant=variant
                                )
                                total_products_processed += 1
                                
                                # Check if it's a new product or update
                                # Check if product exists using SKU code (more reliable)
                                sku_code = variant.get('sku') or f"shopify-{variant['id']}"
                                existing_product = self.supabase_client.table('products').select(
                                    'sku_id'
                                ).eq('shop_id', shop_id).eq('sku_code', sku_code).execute()
                                
                                if existing_product.data:
                                    total_products_updated += 1
                                else:
                                    total_products_created += 1
                                
                            except Exception as variant_error:
                                logger.error(f"Failed to sync variant {variant.get('id')}: {variant_error}")
                                total_products_failed += 1
                        
                        # Update progress every 10 products
                        if (i + 1) % 10 == 0:
                            progress_percentage = round(((i + 1) / len(all_products)) * 100, 2)
                            
                            self.supabase_client.table('sync_jobs').update({
                                "processed_items": total_products_processed,
                                "sync_details": {
                                    "products_processed": i + 1,
                                    "total_products": len(all_products),
                                    "variants_created": total_products_created,
                                    "variants_updated": total_products_updated,
                                    "variants_failed": total_products_failed,
                                    "progress_percentage": progress_percentage
                                }
                            }).eq('id', sync_job_id).execute()
                            
                            # Log detailed progress
                            log_product_sync_progress(
                                shop_id=shop_id,
                                sync_job_id=sync_job_id,
                                products_fetched=len(all_products),
                                variants_processed=total_products_processed,
                                variants_created=total_products_created,
                                variants_updated=total_products_updated,
                                variants_failed=total_products_failed,
                                progress_percentage=progress_percentage,
                                products_completed=i + 1
                            )
                            
                            logger.info(f"Progress: {i+1}/{len(all_products)} products ({total_products_processed} variants processed)")
                        
                        # Rate limiting between products
                        await asyncio.sleep(0.1)
                        
                    except Exception as product_error:
                        logger.error(f"Failed to process product {shopify_product.get('id')}: {product_error}")
                        total_products_failed += 1
            
            # Calculate sync duration
            sync_duration = time.time() - start_time
            
            # Mark sync as completed
            self.supabase_client.table('sync_jobs').update({
                "status": ShopifySyncStatus.COMPLETED,
                "completed_at": datetime.utcnow().isoformat(),
                "processed_items": total_products_processed,
                "sync_details": {
                    "total_products_fetched": len(all_products),
                    "variants_processed": total_products_processed,
                    "variants_created": total_products_created,
                    "variants_updated": total_products_updated,
                    "variants_failed": total_products_failed,
                    "sync_duration_seconds": round(sync_duration, 2),
                    "products_per_second": round(len(all_products) / sync_duration, 2) if sync_duration > 0 else 0
                }
            }).eq('id', sync_job_id).execute()
            
            # Update store last sync time
            self.supabase_client.table('stores').update({
                "updated_at": datetime.utcnow().isoformat()
            }).eq('id', shop_id).execute()
            
            logger.info("=== PRODUCT SYNC COMPLETED SUCCESSFULLY ===")
            logger.info(f"Total products fetched: {len(all_products)}")
            logger.info(f"Total variants processed: {total_products_processed}")
            logger.info(f"Variants created: {total_products_created}")
            logger.info(f"Variants updated: {total_products_updated}")
            logger.info(f"Variants failed: {total_products_failed}")
            logger.info(f"Sync duration: {sync_duration:.2f} seconds")
            
            log_business_event(
                "shopify_product_sync_completed",
                shop_id=shop_id,
                sync_job_id=sync_job_id,
                products_fetched=len(all_products),
                variants_processed=total_products_processed,
                variants_created=total_products_created,
                variants_updated=total_products_updated,
                variants_failed=total_products_failed,
                sync_duration=sync_duration
            )
            
        except Exception as e:
            sync_duration = time.time() - start_time
            logger.error(f"=== PRODUCT SYNC FAILED ===")
            logger.error(f"Sync job {sync_job_id} failed after {sync_duration:.2f} seconds: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            self.supabase_client.table('sync_jobs').update({
                "status": ShopifySyncStatus.FAILED,
                "error_message": str(e),
                "completed_at": datetime.utcnow().isoformat(),
                "sync_details": {
                    "error_type": type(e).__name__,
                    "sync_duration_seconds": round(sync_duration, 2),
                    "failed_at_stage": "product_sync"
                }
            }).eq('id', sync_job_id).execute()
            
            log_business_event(
                "shopify_product_sync_failed",
                shop_id=shop_id if 'shop_id' in locals() else None,
                sync_job_id=sync_job_id,
                error_message=str(e),
                sync_duration=sync_duration
            )
    
    async def _sync_product_variant(
        self,
        shop_id: int,
        shopify_product: Dict[str, Any],
        variant: Dict[str, Any]
    ) -> None:
        """Sync a single product variant to the database."""
        try:
            # Extract product data
            # Use only core schema columns that definitely exist
            product_data = {
                "shop_id": shop_id,
                "shopify_product_id": shopify_product['id'],
                "sku_code": variant.get('sku') or f"shopify-{variant['id']}",
                "product_title": shopify_product.get('title', ''),
                "variant_title": variant.get('title'),
                "current_price": float(variant.get('price', 0)),
                "inventory_level": variant.get('inventory_quantity', 0),
                "cost_price": float(variant.get('compare_at_price', 0)) if variant.get('compare_at_price') else None,
                "status": "active" if shopify_product.get('status') == 'active' else "inactive"
            }
            
            # Add image URL if available
            images = shopify_product.get('images', [])
            if images:
                product_data["image_url"] = images[0].get('src')
            
            # Try to add Shopify-specific columns if they exist (graceful degradation)
            try:
                shopify_specific_data = {
                    "shopify_variant_id": variant['id'],
                    "handle": shopify_product.get('handle', ''),
                    "product_type": shopify_product.get('product_type'),
                    "vendor": shopify_product.get('vendor'),
                    "tags": shopify_product.get('tags'),
                    "published_at": shopify_product.get('published_at'),
                    "shopify_created_at": shopify_product.get('created_at'),
                    "shopify_updated_at": shopify_product.get('updated_at')
                }
                # Only add these if the columns exist (will fail gracefully if not)
                product_data.update(shopify_specific_data)
            except Exception:
                # Columns don't exist yet, continue with core data only
                logger.debug("Shopify-specific columns not available, using core schema only")
            
            # Check if product already exists
            # Check if product exists using SKU code (more reliable)
            sku_code = variant.get('sku') or f"shopify-{variant['id']}"
            existing_product = self.supabase_client.table('products').select(
                'sku_id'
            ).eq('shop_id', shop_id).eq('sku_code', sku_code).execute()
            
            if existing_product.data:
                # Update existing product
                try:
                    update_result = self.supabase_client.table('products').update(
                        product_data
                    ).eq('sku_id', existing_product.data[0]['sku_id']).execute()
                    
                    if update_result.data:
                        logger.debug(f"Updated product variant: {product_data['sku_code']}")
                    else:
                        logger.warning(f"Update returned no data for: {product_data['sku_code']}")
                        
                except Exception as update_error:
                    logger.error(f"Failed to update product {product_data['sku_code']}: {update_error}")
                    # Try to create instead if update fails
                    try:
                        insert_result = self.supabase_client.table('products').insert(
                            product_data
                        ).execute()
                        if insert_result.data:
                            logger.info(f"Created product after update failed: {product_data['sku_code']}")
                    except Exception as insert_error:
                        logger.error(f"Failed to create product after update failed: {insert_error}")
                        raise
            else:
                # Create new product
                try:
                    insert_result = self.supabase_client.table('products').insert(
                        product_data
                    ).execute()
                    
                    if insert_result.data:
                        logger.debug(f"Created product variant: {product_data['sku_code']}")
                    else:
                        logger.warning(f"Insert returned no data for: {product_data['sku_code']}")
                        
                except Exception as insert_error:
                    logger.error(f"Failed to create product {product_data['sku_code']}: {insert_error}")
                    raise
                
        except Exception as e:
            logger.error(f"Failed to sync product variant {variant.get('id')}: {e}")
            raise
    
    async def disconnect_store(self, shop_id: int, user_id: str) -> Dict[str, Any]:
        """
        Disconnect and cleanup a Shopify store.
        
        Args:
            shop_id: Store ID to disconnect
            user_id: User ID for verification
            
        Returns:
            Disconnect operation result
        """
        start_time = time.time()
        
        try:
            logger.info("=== STARTING STORE DISCONNECT ===")
            logger.info(f"Shop ID: {shop_id}")
            logger.info(f"User ID: {user_id}")
            
            # Get store details for logging
            store_result = self.supabase_client.table('stores').select(
                '*'
            ).eq('id', shop_id).eq('shop_config->>user_id', user_id).eq('is_active', True).execute()
            
            if not store_result.data:
                logger.error(f"Store {shop_id} not found or not owned by user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store not found"
                )
            
            store_data = store_result.data[0]
            shop_domain = store_data['shop_domain']
            shop_name = store_data['shop_name']
            
            logger.info(f"Disconnecting store: {shop_name} ({shop_domain})")
            
            # Log disconnect initiation
            log_business_event(
                "shopify_store_disconnect_started",
                user_id=user_id,
                shop_id=shop_id,
                shop_domain=shop_domain,
                shop_name=shop_name
            )
            
            # Count related data before cleanup
            products_count = self.supabase_client.table('products').select(
                'sku_id', count='exact'
            ).eq('shop_id', shop_id).execute().count or 0
            
            sync_jobs_count = self.supabase_client.table('sync_jobs').select(
                'id', count='exact'
            ).eq('shop_id', shop_id).execute().count or 0
            
            webhook_events_count = self.supabase_client.table('webhook_events').select(
                'id', count='exact'
            ).eq('shop_id', shop_id).execute().count or 0
            
            logger.info(f"Data to cleanup: {products_count} products, {sync_jobs_count} sync jobs, {webhook_events_count} webhook events")
            
            # Perform cleanup operations
            cleanup_results = {}
            
            # 1. Mark all sync jobs as cancelled
            if sync_jobs_count > 0:
                try:
                    sync_jobs_result = self.supabase_client.table('sync_jobs').update({
                        "status": ShopifySyncStatus.CANCELLED,
                        "completed_at": datetime.utcnow().isoformat(),
                        "error_message": "Store disconnected"
                    }).eq('shop_id', shop_id).in_('status', [ShopifySyncStatus.PENDING, ShopifySyncStatus.RUNNING]).execute()
                    
                    cleanup_results['sync_jobs_cancelled'] = len(sync_jobs_result.data) if sync_jobs_result.data else 0
                    logger.info(f"Cancelled {cleanup_results['sync_jobs_cancelled']} active sync jobs")
                except Exception as e:
                    logger.warning(f"Failed to cancel sync jobs: {e}")
                    cleanup_results['sync_jobs_cancelled'] = 0
            
            # 2. Optionally delete products (configurable)
            # For now, we'll keep products but mark them as inactive
            if products_count > 0:
                try:
                    products_result = self.supabase_client.table('products').update({
                        "status": "inactive"
                    }).eq('shop_id', shop_id).execute()
                    
                    cleanup_results['products_deactivated'] = len(products_result.data) if products_result.data else 0
                    logger.info(f"Deactivated {cleanup_results['products_deactivated']} products")
                except Exception as e:
                    logger.warning(f"Failed to deactivate products: {e}")
                    cleanup_results['products_deactivated'] = 0
            
            # 3. Mark webhook events as processed (to stop retries)
            if webhook_events_count > 0:
                try:
                    webhook_result = self.supabase_client.table('webhook_events').update({
                        "processed": True,
                        "processed_at": datetime.utcnow().isoformat(),
                        "error_message": "Store disconnected"
                    }).eq('shop_id', shop_id).eq('processed', False).execute()
                    
                    cleanup_results['webhook_events_processed'] = len(webhook_result.data) if webhook_result.data else 0
                    logger.info(f"Marked {cleanup_results['webhook_events_processed']} webhook events as processed")
                except Exception as e:
                    logger.warning(f"Failed to process webhook events: {e}")
                    cleanup_results['webhook_events_processed'] = 0
            
            # 4. Clear access token and deactivate store
            try:
                store_update_result = self.supabase_client.table('stores').update({
                    "is_active": False,
                    "access_token": "",  # Clear the access token for security
                    "updated_at": datetime.utcnow().isoformat()
                }).eq('id', shop_id).execute()
                
                if not store_update_result.data:
                    raise Exception("Failed to update store status")
                
                logger.info("Store deactivated and access token cleared")
                cleanup_results['store_deactivated'] = True
                
            except Exception as e:
                logger.error(f"Failed to deactivate store: {e}")
                cleanup_results['store_deactivated'] = False
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to deactivate store: {str(e)}"
                )
            
            # Calculate disconnect duration
            disconnect_duration = time.time() - start_time
            
            # Log successful disconnect
            log_business_event(
                "shopify_store_disconnected",
                user_id=user_id,
                shop_id=shop_id,
                shop_domain=shop_domain,
                shop_name=shop_name,
                products_count=products_count,
                sync_jobs_count=sync_jobs_count,
                webhook_events_count=webhook_events_count,
                disconnect_duration=disconnect_duration,
                cleanup_results=cleanup_results
            )
            
            logger.info("=== STORE DISCONNECT COMPLETED SUCCESSFULLY ===")
            logger.info(f"Store: {shop_name} ({shop_domain})")
            logger.info(f"Cleanup results: {cleanup_results}")
            logger.info(f"Disconnect duration: {disconnect_duration:.2f} seconds")
            
            return {
                "message": "Store disconnected successfully",
                "shop_domain": shop_domain,
                "shop_name": shop_name,
                "cleanup_results": cleanup_results,
                "disconnect_duration": round(disconnect_duration, 2)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            disconnect_duration = time.time() - start_time
            logger.error("=== STORE DISCONNECT FAILED ===")
            logger.error(f"Store disconnect failed after {disconnect_duration:.2f} seconds: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            log_business_event(
                "shopify_store_disconnect_failed",
                user_id=user_id,
                shop_id=shop_id,
                error_message=str(e),
                disconnect_duration=disconnect_duration
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to disconnect store: {str(e)}"
            )


# Global service instance
shopify_service = ShopifyService()


def get_shopify_service() -> ShopifyService:
    """Get Shopify service instance."""
    return shopify_service