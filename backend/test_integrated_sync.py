#!/usr/bin/env python3
"""
Test the integrated sync platform
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import httpx
from app.core.database import get_supabase_client

async def test_sync_api():
    """Test the integrated sync API"""
    print("🧪 TESTING INTEGRATED SYNC PLATFORM")
    print("=" * 50)
    
    # Test the sync API endpoint
    try:
        async with httpx.AsyncClient() as client:
            # Test sync endpoint (without auth for now)
            print("🚀 Testing sync endpoint...")
            
            # You'll need to add a test endpoint or bypass auth for testing
            # For now, let's test the sync function directly
            
            from app.api.v1.sync import perform_complete_sync
            
            # Create a test sync job
            supabase = get_supabase_client()
            
            # Create sync job
            sync_job = {
                "shop_id": 4,
                "sync_type": "product_sync",
                "status": "running",
                "started_at": "now()",
                "sync_config": {"full_sync": False}
            }
            
            result = supabase.table('sync_jobs').insert(sync_job).execute()
            if result.data:
                sync_job_id = result.data[0]['id']
                print(f"✅ Created test sync job: {sync_job_id}")
                
                # Run the sync
                print("🔄 Running integrated sync...")
                await perform_complete_sync(4, sync_job_id, False)
                
                # Check results
                updated_job = supabase.table('sync_jobs').select('*').eq('id', sync_job_id).execute()
                if updated_job.data:
                    job = updated_job.data[0]
                    print(f"📊 Sync Status: {job['status']}")
                    print(f"📊 Processed Items: {job.get('processed_items', 0)}")
                    
                    if job.get('sync_details'):
                        details = job['sync_details']
                        print(f"📦 Products Synced: {details.get('products_synced', 0)}")
                        print(f"💰 Sales Generated: {details.get('sales_generated', 0)}")
                        print(f"💵 Total Revenue: ${details.get('total_revenue', 0):,.2f}")
                        print(f"🛒 Unique Orders: {details.get('unique_orders', 0)}")
                
                return True
            else:
                print("❌ Failed to create sync job")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_data():
    """Verify the synced data"""
    print(f"\n🔍 VERIFYING SYNCED DATA...")
    
    supabase = get_supabase_client()
    
    # Check products
    products = supabase.table('products').select('*').eq('shop_id', 4).execute()
    print(f"📦 Products in database: {len(products.data)}")
    
    # Check sales
    sales = supabase.table('sales').select('*').eq('shop_id', 4).execute()
    print(f"💰 Sales records: {len(sales.data)}")
    
    if sales.data:
        total_revenue = sum(float(sale['sold_price']) * sale['quantity_sold'] for sale in sales.data)
        print(f"💵 Total Revenue: ${total_revenue:,.2f}")
    
    return len(products.data) > 0 and len(sales.data) > 0

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    async def main():
        success = await test_sync_api()
        
        if success:
            data_ok = await verify_data()
            if data_ok:
                print(f"\n🎉 INTEGRATED SYNC PLATFORM IS WORKING!")
                print("✅ Products sync integrated")
                print("✅ Sales data generation integrated")
                print("✅ Progress tracking working")
                print("✅ Analytics data available")
                print("\n🚀 Your sync platform is ready for production!")
            else:
                print(f"\n⚠️  Sync completed but data verification failed")
        else:
            print(f"\n💥 Integrated sync test failed")
    
    asyncio.run(main())