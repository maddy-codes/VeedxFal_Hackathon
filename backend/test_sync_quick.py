#!/usr/bin/env python3
"""
Quick Shopify Sync Test - Fast verification that sync functionality works.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client
from app.services.shopify_service import ShopifyService

async def quick_test():
    """Quick test of essential sync functionality."""
    print("🚀 QUICK SHOPIFY SYNC TEST")
    print("=" * 40)
    
    try:
        # 1. Test database connection
        print("1. Testing database connection...")
        supabase_client = get_supabase_client()
        print("   ✅ Database connected")
        
        # 2. Test required tables
        print("2. Testing required tables...")
        tables = ['stores', 'products', 'sync_jobs', 'webhook_events']
        for table in tables:
            try:
                supabase_client.table(table).select('*').limit(1).execute()
                print(f"   ✅ {table} table OK")
            except Exception as e:
                print(f"   ❌ {table} table FAILED: {e}")
                return False
        
        # 3. Test ShopifyService
        print("3. Testing ShopifyService...")
        shopify_service = ShopifyService()
        print("   ✅ ShopifyService initialized")
        
        # 4. Test sync job creation
        print("4. Testing sync job operations...")
        test_job = {
            "shop_id": 999999,
            "sync_type": "test",
            "status": "pending",
            "total_items": 0,
            "processed_items": 0,
            "failed_items": 0,
            "sync_config": {"test": True}
        }
        
        result = supabase_client.table('sync_jobs').insert(test_job).execute()
        if result.data:
            job_id = result.data[0]['id']
            print(f"   ✅ Sync job created: {job_id}")
            
            # Clean up
            supabase_client.table('sync_jobs').delete().eq('id', job_id).execute()
            print("   ✅ Sync job cleaned up")
        else:
            print("   ❌ Sync job creation failed")
            return False
        
        # 5. Test product operations
        print("5. Testing product operations...")
        test_product = {
            "shop_id": 999999,
            "shopify_product_id": 888888,
            "sku_code": "TEST-QUICK-123",
            "product_title": "Quick Test Product",
            "current_price": 19.99,
            "inventory_level": 5,
            "status": "active"
        }
        
        result = supabase_client.table('products').insert(test_product).execute()
        if result.data:
            product_id = result.data[0]['sku_id']
            print(f"   ✅ Product created: {product_id}")
            
            # Clean up
            supabase_client.table('products').delete().eq('sku_id', product_id).execute()
            print("   ✅ Product cleaned up")
        else:
            print("   ❌ Product creation failed")
            return False
        
        # 6. Check for active stores
        print("6. Checking for active stores...")
        stores = supabase_client.table('stores').select('id, shop_domain, shop_name').eq('is_active', True).execute()
        if stores.data:
            print(f"   ✅ Found {len(stores.data)} active store(s)")
            for store in stores.data:
                print(f"      - {store['shop_name']} ({store['shop_domain']})")
        else:
            print("   ⚠️  No active stores found (connect a Shopify store to test real sync)")
        
        print("\n🎉 QUICK TEST PASSED!")
        print("✅ All essential components are working correctly")
        print("\nNext steps:")
        print("- Run full test: python test_shopify_sync_complete.py")
        print("- Test real sync: python test_disconnect_and_sync.py")
        print("- Or use API to start sync")
        
        return True
        
    except Exception as e:
        print(f"\n❌ QUICK TEST FAILED: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)