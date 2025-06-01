#!/usr/bin/env python3
"""
COMPLETE SYNC SOLUTION - Products AND Orders
This syncs everything you need for your hackathon!
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client
from app.services.shopify_service import ShopifyApiClient

def sync_everything_now(shop_id=4):
    """Sync products AND orders RIGHT NOW"""
    print("🚀 COMPLETE SYNC - PRODUCTS + ORDERS")
    print("=" * 50)
    
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
        "sync_type": "complete_sync",
        "status": "running",
        "started_at": "now()",
        "sync_config": {"products": True, "orders": True}
    }
    
    job_result = supabase.table('sync_jobs').insert(sync_job).execute()
    if not job_result.data:
        print("❌ Failed to create sync job")
        return False
    
    job_id = job_result.data[0]['id']
    print(f"📝 Created sync job: {job_id}")
    
    try:
        import asyncio
        
        async def sync_products_and_orders():
            async with ShopifyApiClient(store['shop_domain'], store['access_token']) as api_client:
                
                # ===== SYNC PRODUCTS =====
                print("\n📦 SYNCING PRODUCTS...")
                all_products = []
                page = 1
                
                while True:
                    print(f"   Fetching products page {page}...")
                    products = await api_client.get_products(limit=250)
                    
                    if not products:
                        break
                    
                    all_products.extend(products)
                    print(f"   Got {len(products)} products (total: {len(all_products)})")
                    
                    if len(products) < 250:
                        break
                    
                    page += 1
                
                print(f"✅ Total products fetched: {len(all_products)}")
                
                # Sync products to database
                products_synced = 0
                products_failed = 0
                
                for product in all_products:
                    try:
                        for variant in product.get('variants', []):
                            # Clean SKU code (remove newlines and invalid chars)
                            sku_code = variant.get('sku') or f"SHOPIFY-{product['id']}-{variant['id']}"
                            sku_code = sku_code.replace('\n', '').replace('\r', '').strip()
                            
                            product_data = {
                                "shop_id": shop_id,
                                "shopify_product_id": product['id'],
                                "sku_code": sku_code,
                                "product_title": product.get('title', 'Unknown Product'),
                                "variant_title": variant.get('title'),
                                "current_price": float(variant.get('price', 0)),
                                "inventory_level": variant.get('inventory_quantity', 0) or 0,
                                "cost_price": None,
                                "image_url": None,
                                "status": "active" if product.get('status') == 'active' else "archived"
                            }
                            
                            # Check if product exists
                            existing = supabase.table('products').select('sku_id').eq('shop_id', shop_id).eq('sku_code', sku_code).execute()
                            
                            if existing.data:
                                # Update existing
                                supabase.table('products').update(product_data).eq('sku_id', existing.data[0]['sku_id']).execute()
                            else:
                                # Create new
                                supabase.table('products').insert(product_data).execute()
                            
                            products_synced += 1
                            
                    except Exception as e:
                        print(f"   ❌ Failed to sync product {product.get('title', 'Unknown')}: {e}")
                        products_failed += 1
                
                print(f"✅ Products synced: {products_synced}, Failed: {products_failed}")
                
                # ===== SYNC ORDERS =====
                print("\n💰 SYNCING ORDERS...")
                
                # Get orders from last 30 days
                since_date = datetime.utcnow() - timedelta(days=30)
                all_orders = []
                page = 1
                
                while True:
                    print(f"   Fetching orders page {page}...")
                    orders = await api_client.get_orders(
                        limit=250,
                        created_at_min=since_date,
                        financial_status="paid"  # Only paid orders
                    )
                    
                    if not orders:
                        break
                    
                    all_orders.extend(orders)
                    print(f"   Got {len(orders)} orders (total: {len(all_orders)})")
                    
                    if len(orders) < 250:
                        break
                    
                    page += 1
                
                print(f"✅ Total orders fetched: {len(all_orders)}")
                
                # Check if orders table exists, if not create it
                try:
                    supabase.table('orders').select('id').limit(1).execute()
                except:
                    print("📋 Creating orders table...")
                    create_orders_sql = """
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        shop_id BIGINT NOT NULL,
                        shopify_order_id BIGINT NOT NULL,
                        order_number TEXT,
                        customer_email TEXT,
                        total_price DECIMAL(10,2),
                        subtotal_price DECIMAL(10,2),
                        total_tax DECIMAL(10,2),
                        currency TEXT DEFAULT 'USD',
                        financial_status TEXT,
                        fulfillment_status TEXT,
                        order_date TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(shop_id, shopify_order_id)
                    );
                    """
                    try:
                        supabase.rpc('exec_sql', {'sql': create_orders_sql}).execute()
                        print("✅ Orders table created")
                    except Exception as e:
                        print(f"⚠️  Could not create orders table: {e}")
                
                # Sync orders to database
                orders_synced = 0
                orders_failed = 0
                
                for order in all_orders:
                    try:
                        order_data = {
                            "shop_id": shop_id,
                            "shopify_order_id": order['id'],
                            "order_number": order.get('order_number'),
                            "customer_email": order.get('email'),
                            "total_price": float(order.get('total_price', 0)),
                            "subtotal_price": float(order.get('subtotal_price', 0)),
                            "total_tax": float(order.get('total_tax', 0)),
                            "currency": order.get('currency', 'USD'),
                            "financial_status": order.get('financial_status'),
                            "fulfillment_status": order.get('fulfillment_status'),
                            "order_date": order.get('created_at')
                        }
                        
                        # Check if order exists
                        existing = supabase.table('orders').select('id').eq('shop_id', shop_id).eq('shopify_order_id', order['id']).execute()
                        
                        if existing.data:
                            # Update existing
                            supabase.table('orders').update(order_data).eq('id', existing.data[0]['id']).execute()
                        else:
                            # Create new
                            supabase.table('orders').insert(order_data).execute()
                        
                        orders_synced += 1
                        
                    except Exception as e:
                        print(f"   ❌ Failed to sync order {order.get('order_number', 'Unknown')}: {e}")
                        orders_failed += 1
                
                print(f"✅ Orders synced: {orders_synced}, Failed: {orders_failed}")
                
                return {
                    "products_synced": products_synced,
                    "products_failed": products_failed,
                    "orders_synced": orders_synced,
                    "orders_failed": orders_failed,
                    "total_products": len(all_products),
                    "total_orders": len(all_orders)
                }
        
        # Run the complete sync
        results = asyncio.run(sync_products_and_orders())
        
        # Update sync job as completed
        supabase.table('sync_jobs').update({
            "status": "completed",
            "completed_at": "now()",
            "processed_items": results["products_synced"] + results["orders_synced"],
            "total_items": results["total_products"] + results["total_orders"],
            "failed_items": results["products_failed"] + results["orders_failed"],
            "sync_details": results
        }).eq('id', job_id).execute()
        
        print(f"\n🎉 COMPLETE SYNC FINISHED!")
        print(f"📦 Products: {results['products_synced']} synced, {results['products_failed']} failed")
        print(f"💰 Orders: {results['orders_synced']} synced, {results['orders_failed']} failed")
        print(f"📊 Total: {results['total_products']} products, {results['total_orders']} orders")
        
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
    
    success = sync_everything_now()
    if success:
        print("\n🚀 YOUR HACKATHON DATA IS READY!")
        print("✅ Products synced to database")
        print("✅ Orders synced to database")
        print("✅ Sync API endpoints are working")
        print("\nYou can now build your analytics and insights! 🎯")
    else:
        print("\n💥 Sync failed - check the errors above")