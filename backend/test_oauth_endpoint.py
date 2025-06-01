#!/usr/bin/env python3
"""
Test script to debug the OAuth endpoint issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.shopify_service import get_shopify_service
from app.core.config import settings

def test_shopify_service():
    """Test Shopify service initialization."""
    try:
        print("Testing Shopify service initialization...")
        service = get_shopify_service()
        print(f"✓ Shopify service initialized: {service}")
        
        print(f"✓ Shopify Client ID: {settings.SHOPIFY_CLIENT_ID}")
        print(f"✓ Shopify Client Secret: {'***' if settings.SHOPIFY_CLIENT_SECRET else 'NOT SET'}")
        print(f"✓ Shopify Scopes: {settings.SHOPIFY_SCOPES}")
        print(f"✓ Shopify Scope String: {settings.shopify_scope_string}")
        
        # Test OAuth URL generation
        print("\nTesting OAuth URL generation...")
        oauth_url = service.generate_oauth_url(
            shop_domain="bizpredict.myshopify.com",
            redirect_uri="http://localhost:8000/api/v1/shopify/oauth/callback",
            state="test_user:127.0.0.1"
        )
        print(f"✓ OAuth URL generated: {oauth_url}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shopify_service()
    sys.exit(0 if success else 1)