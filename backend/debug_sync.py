#!/usr/bin/env python3
"""
Debug the sync issue by testing Shopify API directly
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client
from app.services.shopify_service import ShopifyApiClient

async def debug_shopify_api():
    """Test Shopify API directly"""
    try:
        print("🔍 Debugging Shopify API connection...")
        
        # Get store details
        supabase = get_supabase_client()
        store_result = supabase.table('stores').select('*').eq('id', 4).execute()
        
        if not store_result.data:
            print("❌ Store not found")
            return False
            
        store = store_result.data[0]
        print(f"🏪 Testing store: {store['shop_name']} ({store['shop_domain']})")
        
        # Test Shopify API connection
        async with ShopifyApiClient(store['shop_domain'], store['access_token']) as api_client:
            print("🔗 Testing Shopify API connection...")
            
            # Test 1: Get shop info
            try:
                shop_info = await api_client.get_shop_info()
                print(f"✅ Shop info: {shop_info.get('name', 'Unknown')} - {shop_info.get('plan_name', 'Unknown plan')}")
            except Exception as e:
                print(f"❌ Shop info failed: {e}")
                return False
            
            # Test 2: Get products (small batch)
            try:
                print("📦 Testing product fetch...")
                products = await api_client.get_products(limit=5)
                print(f"✅ Found {len(products)} products")
                
                for i, product in enumerate(products[:3]):
                    print(f"   {i+1}. {product.get('title', 'No title')} (ID: {product.get('id')})")
                    
                if len(products) == 0:
                    print("⚠️  No products found in store - this might be why sync appears stuck")
                    
            except Exception as e:
                print(f"❌ Product fetch failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def fix_stuck_sync():
    """Fix the stuck sync job"""
    try:
        print("\n🔧 Fixing stuck sync job...")
        
        supabase = get_supabase_client()
        
        # Update stuck sync job to failed
        result = supabase.table('sync_jobs').update({
            'status': 'failed',
            'error_message': 'Sync was stuck - manually reset',
            'completed_at': 'now()'
        }).eq('id', 3).execute()
        
        if result.data:
            print("✅ Marked stuck sync as failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix sync: {e}")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🚨 DEBUGGING SYNC ISSUE")
    print("=" * 50)
    
    success = asyncio.run(debug_shopify_api())
    
    if success:
        print("\n✅ Shopify API is working!")
        
        # Fix the stuck sync
        asyncio.run(fix_stuck_sync())
        
        print("\n💡 Try running a new sync now!")
    else:
        print("\n❌ Shopify API has issues - check your credentials")