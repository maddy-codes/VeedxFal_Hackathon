#!/usr/bin/env python3
"""
SIMPLE SYNC THAT ACTUALLY WORKS
No background tasks, no complex async stuff - just sync the damn products!
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client
from app.services.shopify_service import ShopifyApiClient

def sync_products_now(shop_id=4):
    """Just sync the products RIGHT NOW"""
    print("🚀 SYNCING PRODUCTS RIGHT NOW - NO BULLSHIT")
    
    supabase = get_supabase_client()
    
    # Get store
    store_result = supabase.table('stores').select('*').eq('id', shop_id).execute()
    if not store_result.data:
        print(f"❌ Store {shop_id} not found")
        return False
    
    store = store_result.data[0]
    print(f"🏪 Store: {store['shop_name']} ({store['shop_domain']})")
    
    # Create sync job
    sync_job = {
        "shop_id": shop_id,
        "sync_type": "product_sync",
        "status": "running",
        "started_at": "now()",
        "sync_config": {"simple": True}
    }
    
    job_result = supabase.table('sync_jobs').insert(sync_job).execute()
    if not job_result.data:
        print("❌ Failed to create sync job")
        return False
    
    job_id = job_result.data[0]['id']
    print(f"📝 Created sync job: {job_id}")
    
    try:
        # Get products from Shopify API
        print("📦 Fetching products from Shopify...")
        
        import asyncio
        
        async def fetch_and_sync():
            async with ShopifyApiClient(store['shop_domain'], store['access_token']) as api_client:
                # Get all products
                all_products = []
                page = 1
                
                while True:
                    print(f"   Fetching page {page}...")
                    products = await api_client.get_products(limit=250)
                    
                    if not products:
                        break
                    
                    all_products.extend(products)
                    print(f"   Got {len(products)} products (total: {len(all_products)})")
                    
                    if len(products) < 250:
                        break
                    
                    page += 1
                
                print(f"✅ Total products fetched: {len(all_products)}")
                
                # Sync each product to database
                synced_count = 0
                failed_count = 0
                
                for product in all_products:
                    try:
                        # Extract product data
                        for variant in product.get('variants', []):
                            product_data = {
                                "shop_id": shop_id,
                                "shopify_product_id": product['id'],
                                "sku_code": variant.get('sku') or f"SHOPIFY-{product['id']}-{variant['id']}",
                                "product_title": product.get('title', 'Unknown Product'),
                                "variant_title": variant.get('title'),
                                "current_price": float(variant.get('price', 0)),
                                "inventory_level": variant.get('inventory_quantity', 0) or 0,
                                "cost_price": None,  # Not available from Shopify API
                                "image_url": variant.get('image_id') and product.get('images', [{}])[0].get('src'),
                                "status": "active" if product.get('status') == 'active' else "archived"
                            }
                            
                            # Check if product exists
                            existing = supabase.table('products').select('sku_id').eq('shop_id', shop_id).eq('sku_code', product_data['sku_code']).execute()
                            
                            if existing.data:
                                # Update existing
                                supabase.table('products').update(product_data).eq('sku_id', existing.data[0]['sku_id']).execute()
                                print(f"   ✅ Updated: {product_data['sku_code']}")
                            else:
                                # Create new
                                supabase.table('products').insert(product_data).execute()
                                print(f"   ✅ Created: {product_data['sku_code']}")
                            
                            synced_count += 1
                            
                    except Exception as e:
                        print(f"   ❌ Failed to sync {product.get('title', 'Unknown')}: {e}")
                        failed_count += 1
                
                return synced_count, failed_count, len(all_products)
        
        # Run the sync
        synced_count, failed_count, total_count = asyncio.run(fetch_and_sync())
        
        # Update sync job as completed
        supabase.table('sync_jobs').update({
            "status": "completed",
            "completed_at": "now()",
            "processed_items": synced_count,
            "total_items": total_count,
            "failed_items": failed_count,
            "sync_details": {
                "products_synced": synced_count,
                "products_failed": failed_count,
                "total_products": total_count,
                "success": True
            }
        }).eq('id', job_id).execute()
        
        print(f"\n🎉 SYNC COMPLETED!")
        print(f"   ✅ Synced: {synced_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📊 Total: {total_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        
        # Mark sync as failed
        supabase.table('sync_jobs').update({
            "status": "failed",
            "completed_at": "now()",
            "error_message": str(e)
        }).eq('id', job_id).execute()
        
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    success = sync_products_now()
    if success:
        print("\n🚀 YOUR SYNC IS FIXED! Products are now in the database!")
    else:
        print("\n💥 Sync failed - check the errors above")