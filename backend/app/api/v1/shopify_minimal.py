"""
Minimal Shopify integration API endpoints for testing.
"""

import logging
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    return {"message": "Minimal Shopify router is working", "timestamp": "2025-05-31"}


@router.get("/oauth/authorize")
async def generate_oauth_url_get(shop: str, redirect_uri: Optional[str] = None):
    """Generate Shopify OAuth authorization URL via GET request (for testing)."""
    
    try:
        # Import settings here to avoid circular imports
        from app.core.config import settings
        
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