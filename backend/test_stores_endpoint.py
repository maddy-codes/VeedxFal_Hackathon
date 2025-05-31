#!/usr/bin/env python3
"""
Test script to verify the stores endpoint is working with Supabase client.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client

async def test_stores_endpoint():
    """Test the stores functionality with Supabase client."""
    
    print("🧪 Testing Stores Endpoint with Supabase Client")
    print("=" * 50)
    
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        print("✅ Supabase client initialized")
        
        # Test 1: Check if stores table is accessible
        print("\n📊 Test 1: Check stores table accessibility")
        result = supabase_client.table('stores').select('count', count='exact').execute()
        print(f"   ✅ Stores table accessible, total records: {result.count}")
        
        # Test 2: Create a test store
        print("\n🏪 Test 2: Create test store")
        test_store_data = {
            "shop_domain": "test-store.myshopify.com",
            "shop_name": "Test Store",
            "access_token": "test_token",
            "shop_config": {
                "user_id": "test-user-123",
                "shopify_connected": True
            },
            "is_active": True
        }
        
        # Insert test store
        insert_result = supabase_client.table('stores').upsert(
            test_store_data,
            on_conflict='shop_domain'
        ).execute()
        
        if insert_result.data:
            print(f"   ✅ Test store created/updated: ID {insert_result.data[0]['id']}")
            test_store_id = insert_result.data[0]['id']
        else:
            print("   ❌ Failed to create test store")
            return False
        
        # Test 3: Query store by user_id (simulating the endpoint logic)
        print("\n🔍 Test 3: Query store by user_id")
        query_result = supabase_client.table('stores').select(
            'id, shop_domain, shop_name, is_active, shop_config, created_at, updated_at'
        ).eq('shop_config->>user_id', 'test-user-123').eq('is_active', True).execute()
        
        if query_result.data:
            store = query_result.data[0]
            print(f"   ✅ Store found: {store['shop_name']} (ID: {store['id']})")
            print(f"      Domain: {store['shop_domain']}")
            print(f"      Active: {store['is_active']}")
            print(f"      User ID: {store['shop_config'].get('user_id')}")
        else:
            print("   ❌ No store found for test user")
            return False
        
        # Test 4: Test the exact query pattern from the endpoint
        print("\n🎯 Test 4: Test endpoint query pattern")
        # This simulates what the fixed endpoint does
        endpoint_result = supabase_client.table('stores').select(
            'id, shop_domain, shop_name, is_active, shop_config, created_at, updated_at'
        ).eq('shop_config->>user_id', 'test-user-123').eq('is_active', True).execute()
        
        if endpoint_result.data:
            print("   ✅ Endpoint query pattern works correctly")
            store_data = endpoint_result.data[0]
            print(f"      Retrieved store: {store_data['shop_name']}")
        else:
            print("   ❌ Endpoint query pattern failed")
            return False
        
        # Test 5: Clean up test data
        print("\n🧹 Test 5: Clean up test data")
        delete_result = supabase_client.table('stores').delete().eq('id', test_store_id).execute()
        if delete_result.data:
            print("   ✅ Test store cleaned up")
        else:
            print("   ⚠️  Test store cleanup may have failed (this is okay)")
        
        print("\n🎉 All tests passed! The stores endpoint should now work correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_stores_endpoint())
    
    if success:
        print("\n✅ Diagnosis: The database connection issue has been resolved!")
        print("   - Supabase client is working correctly")
        print("   - Stores table is accessible")
        print("   - Query patterns are functioning")
        print("\n🎯 Next steps:")
        print("   1. Test the actual API endpoint with authentication")
        print("   2. Create a real store record for testing")
        print("   3. Update other endpoints to use Supabase client if needed")
    else:
        print("\n❌ Issues still exist. Check the error messages above.")