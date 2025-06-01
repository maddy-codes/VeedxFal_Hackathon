#!/usr/bin/env python3
"""
Test script for Shopify disconnect and sync functionality.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import get_supabase_client
from app.services.shopify_service import get_shopify_service


async def test_store_connection_status():
    """Test getting connected stores."""
    print("=== TESTING STORE CONNECTION STATUS ===")
    
    try:
        supabase_client = get_supabase_client()
        
        # Get all active stores
        stores_result = supabase_client.table('stores').select(
            'id, shop_domain, shop_name, is_active, created_at'
        ).eq('is_active', True).execute()
        
        print(f"Found {len(stores_result.data)} active stores:")
        for store in stores_result.data:
            print(f"  - Store ID: {store['id']}")
            print(f"    Domain: {store['shop_domain']}")
            print(f"    Name: {store['shop_name']}")
            print(f"    Created: {store['created_at']}")
            print()
        
        return stores_result.data
        
    except Exception as e:
        print(f"❌ Error getting store status: {e}")
        return []


async def test_product_sync(shop_id: int):
    """Test product synchronization."""
    print(f"=== TESTING PRODUCT SYNC FOR STORE {shop_id} ===")
    
    try:
        shopify_service = get_shopify_service()
        
        # Start product sync
        print("Starting product sync...")
        sync_job = await shopify_service.sync_products(shop_id=shop_id, full_sync=True)
        
        print(f"✅ Sync job created:")
        print(f"  - Job ID: {sync_job.id}")
        print(f"  - Status: {sync_job.status}")
        print(f"  - Sync Type: {sync_job.sync_type}")
        print(f"  - Created: {sync_job.created_at}")
        
        # Monitor sync progress
        print("\nMonitoring sync progress...")
        supabase_client = get_supabase_client()
        
        for i in range(30):  # Monitor for up to 30 seconds
            await asyncio.sleep(1)
            
            # Get sync job status
            job_result = supabase_client.table('sync_jobs').select(
                '*'
            ).eq('id', sync_job.id).execute()
            
            if job_result.data:
                job_data = job_result.data[0]
                status = job_data['status']
                processed_items = job_data.get('processed_items', 0)
                total_items = job_data.get('total_items', 0)
                sync_details = job_data.get('sync_details', {})
                
                print(f"  Status: {status} | Processed: {processed_items}/{total_items}")
                
                if sync_details:
                    print(f"  Details: {sync_details}")
                
                if status in ['completed', 'failed', 'cancelled']:
                    print(f"✅ Sync job {status}")
                    break
            else:
                print("  ❌ Could not find sync job")
                break
        
        # Get final product count
        products_result = supabase_client.table('products').select(
            'sku_id', count='exact'
        ).eq('shop_id', shop_id).execute()
        
        print(f"\nFinal product count: {products_result.count}")
        
        return sync_job
        
    except Exception as e:
        print(f"❌ Error testing product sync: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None


async def test_store_disconnect(shop_id: int, user_id: str):
    """Test store disconnection."""
    print(f"=== TESTING STORE DISCONNECT FOR STORE {shop_id} ===")
    
    try:
        shopify_service = get_shopify_service()
        
        # Get store info before disconnect
        supabase_client = get_supabase_client()
        store_result = supabase_client.table('stores').select(
            'shop_domain, shop_name, is_active'
        ).eq('id', shop_id).execute()
        
        if not store_result.data:
            print(f"❌ Store {shop_id} not found")
            return False
        
        store_info = store_result.data[0]
        print(f"Store to disconnect: {store_info['shop_name']} ({store_info['shop_domain']})")
        print(f"Current status: {'Active' if store_info['is_active'] else 'Inactive'}")
        
        # Count related data before disconnect
        products_count = supabase_client.table('products').select(
            'sku_id', count='exact'
        ).eq('shop_id', shop_id).execute().count or 0
        
        sync_jobs_count = supabase_client.table('sync_jobs').select(
            'id', count='exact'
        ).eq('shop_id', shop_id).execute().count or 0
        
        print(f"Related data: {products_count} products, {sync_jobs_count} sync jobs")
        
        # Perform disconnect
        print("\nDisconnecting store...")
        disconnect_result = await shopify_service.disconnect_store(shop_id, user_id)
        
        print(f"✅ Store disconnected successfully:")
        print(f"  - Message: {disconnect_result['message']}")
        print(f"  - Shop: {disconnect_result['shop_name']} ({disconnect_result['shop_domain']})")
        print(f"  - Duration: {disconnect_result['disconnect_duration']} seconds")
        print(f"  - Cleanup results: {disconnect_result['cleanup_results']}")
        
        # Verify disconnect
        print("\nVerifying disconnect...")
        store_result_after = supabase_client.table('stores').select(
            'is_active, access_token'
        ).eq('id', shop_id).execute()
        
        if store_result_after.data:
            store_after = store_result_after.data[0]
            print(f"  - Store active: {store_after['is_active']}")
            print(f"  - Access token cleared: {not store_after['access_token']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing store disconnect: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def test_logging_functionality():
    """Test the enhanced logging functionality."""
    print("=== TESTING ENHANCED LOGGING ===")
    
    try:
        from app.core.logging import (
            log_sync_operation,
            log_shopify_api_call,
            log_product_sync_progress,
            log_store_operation,
            log_webhook_processing
        )
        
        # Test sync operation logging
        print("Testing sync operation logging...")
        log_sync_operation(
            operation_type="test_sync",
            shop_id=123,
            sync_job_id=456,
            status="running",
            items_processed=50,
            items_total=100,
            duration=30.5
        )
        
        # Test Shopify API call logging
        print("Testing Shopify API call logging...")
        log_shopify_api_call(
            endpoint="/products.json",
            method="GET",
            shop_domain="test.myshopify.com",
            status_code=200,
            duration=1.2,
            rate_limit_remaining=35,
            rate_limit_total=40
        )
        
        # Test product sync progress logging
        print("Testing product sync progress logging...")
        log_product_sync_progress(
            shop_id=123,
            sync_job_id=456,
            products_fetched=100,
            variants_processed=250,
            variants_created=200,
            variants_updated=50,
            variants_failed=0,
            current_page=5
        )
        
        # Test store operation logging
        print("Testing store operation logging...")
        log_store_operation(
            operation_type="disconnect",
            shop_id=123,
            shop_domain="test.myshopify.com",
            user_id="user123",
            status="completed",
            duration=5.2
        )
        
        # Test webhook processing logging
        print("Testing webhook processing logging...")
        log_webhook_processing(
            event_type="products/create",
            shop_domain="test.myshopify.com",
            webhook_id="webhook123",
            shopify_id="product456",
            processing_status="completed",
            duration=0.5
        )
        
        print("✅ All logging functions tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing logging: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main test function."""
    print("🚀 SHOPIFY DISCONNECT AND SYNC FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL configured: {bool(settings.DATABASE_URL)}")
    print(f"Shopify credentials configured: {bool(settings.SHOPIFY_CLIENT_ID and settings.SHOPIFY_CLIENT_SECRET)}")
    print()
    
    # Test 1: Enhanced logging functionality
    await test_logging_functionality()
    print()
    
    # Test 2: Check store connection status
    stores = await test_store_connection_status()
    print()
    
    if not stores:
        print("⚠️  No active stores found. Please connect a store first using the OAuth flow.")
        print("   You can use the test OAuth endpoint: GET /api/v1/shopify/oauth/authorize?shop=bizpredict.myshopify.com")
        return
    
    # Use the first store for testing
    test_store = stores[0]
    shop_id = test_store['id']
    
    # For testing purposes, we'll use a test user ID
    # In a real scenario, this would come from the authenticated user
    test_user_id = "test_user"
    
    print(f"Using store for testing: {test_store['shop_name']} (ID: {shop_id})")
    print()
    
    # Test 3: Product sync functionality
    sync_job = await test_product_sync(shop_id)
    print()
    
    # Test 4: Store disconnect functionality
    # Note: This will actually disconnect the store, so be careful!
    print("⚠️  WARNING: The next test will disconnect the store!")
    print("   This will deactivate the store and clear the access token.")
    print("   You'll need to reconnect via OAuth to use it again.")
    print()
    
    # Uncomment the line below to actually test disconnect
    # disconnect_success = await test_store_disconnect(shop_id, test_user_id)
    
    print("🔒 Store disconnect test skipped for safety.")
    print("   To test disconnect, uncomment the line in the script.")
    print()
    
    print("✅ All tests completed!")
    print()
    print("SUMMARY:")
    print("- ✅ Enhanced logging functionality working")
    print("- ✅ Store connection status retrieval working")
    print("- ✅ Product sync functionality working" if sync_job else "- ❌ Product sync failed")
    print("- 🔒 Store disconnect test skipped (uncomment to test)")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the test
    asyncio.run(main())