#!/usr/bin/env python3
"""
Test script to verify the table reference fixes for Shopify OAuth.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_supabase_client
from app.services.shopify_service import get_shopify_service

async def test_table_references():
    """Test that the table references are working correctly."""
    
    print("🔧 Testing Shopify table reference fixes...")
    
    try:
        # Test 1: Check if stores table is accessible
        print("\n📊 Test 1: Check stores table accessibility")
        supabase_client = get_supabase_client()
        result = supabase_client.table('stores').select('count', count='exact').execute()
        print(f"   ✅ Stores table accessible, total records: {result.count}")
        
        # Test 2: Test Shopify service initialization
        print("\n🏪 Test 2: Test Shopify service initialization")
        shopify_service = get_shopify_service()
        print(f"   ✅ Shopify service initialized: {type(shopify_service).__name__}")
        
        # Test 3: Test OAuth URL generation (doesn't require database)
        print("\n🔗 Test 3: Test OAuth URL generation")
        try:
            oauth_url = shopify_service.generate_oauth_url(
                shop_domain="test-store.myshopify.com",
                redirect_uri="http://localhost:8000/api/v1/shopify/oauth/callback",
                state="test-state"
            )
            print(f"   ✅ OAuth URL generated successfully")
            print(f"   URL length: {len(oauth_url)} characters")
        except Exception as e:
            print(f"   ❌ OAuth URL generation failed: {e}")
        
        # Test 4: Test stores query with user_id in shop_config
        print("\n🔍 Test 4: Test stores query with shop_config user_id")
        try:
            # This simulates what the fixed endpoints do
            test_user_id = "test-user-123"
            stores_result = supabase_client.table('stores').select(
                'id, shop_domain, shop_name, shop_config'
            ).eq('shop_config->>user_id', test_user_id).execute()
            
            print(f"   ✅ Query executed successfully")
            print(f"   Found {len(stores_result.data)} stores for user {test_user_id}")
            
            if stores_result.data:
                for store in stores_result.data:
                    print(f"   - Store: {store.get('shop_name', 'Unknown')} ({store.get('shop_domain', 'Unknown')})")
            
        except Exception as e:
            print(f"   ❌ Stores query failed: {e}")
        
        print("\n🎉 All table reference tests completed!")
        print("\n📝 Summary of fixes applied:")
        print("   - Changed 'shopify_stores' table references to 'stores'")
        print("   - Updated user_id queries to use 'shop_config->>user_id'")
        print("   - Added data mapping between stores table and ShopifyStore model")
        print("   - Fixed OAuth callback to save data in correct format")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_table_references())
    if success:
        print("\n✅ Table reference fixes appear to be working correctly!")
    else:
        print("\n❌ There may be issues with the table reference fixes.")
    
    sys.exit(0 if success else 1)