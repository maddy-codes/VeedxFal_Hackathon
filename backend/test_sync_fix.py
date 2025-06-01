#!/usr/bin/env python3
"""
Test the sync fix
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.shopify_service import ShopifyService

async def test_sync():
    try:
        print("🧪 Testing sync with real store...")
        service = ShopifyService()
        
        # Test with store ID 4 (the one that exists)
        sync_job = await service.sync_products(shop_id=4, full_sync=False)
        print(f"✅ Sync started! Job ID: {sync_job.id}, Status: {sync_job.status}")
        
        # Wait a moment and check status
        await asyncio.sleep(2)
        
        # Check sync status
        from app.core.database import get_supabase_client
        supabase = get_supabase_client()
        
        result = supabase.table('sync_jobs').select('*').eq('id', sync_job.id).execute()
        if result.data:
            job = result.data[0]
            print(f"📊 Sync status: {job['status']}")
            print(f"📊 Processed: {job.get('processed_items', 0)}/{job.get('total_items', 0)}")
            if job.get('error_message'):
                print(f"❌ Error: {job['error_message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sync test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    success = asyncio.run(test_sync())
    print(f"\n🎯 Sync test {'PASSED' if success else 'FAILED'}")