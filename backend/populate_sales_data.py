#!/usr/bin/env python3
"""
POPULATE SALES DATA - Fill the existing sales table with realistic data
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client

def populate_sales_data(shop_id=4):
    """Populate the sales table with realistic data"""
    print("🎯 POPULATING SALES TABLE WITH REAL DATA")
    print("=" * 50)
    
    supabase = get_supabase_client()
    
    # Get products to create sales for
    products = supabase.table('products').select('sku_code, current_price').eq('shop_id', shop_id).execute()
    
    if not products.data:
        print("❌ No products found - run product sync first")
        return False
    
    print(f"📦 Found {len(products.data)} products to create sales for")
    
    # Clear existing sales data
    try:
        supabase.table('sales').delete().eq('shop_id', shop_id).execute()
        print("🧹 Cleared existing sales data")
    except:
        pass
    
    # Generate sales data for last 30 days
    sales_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    # Create 200-500 sales records (realistic for a month)
    num_sales = random.randint(200, 500)
    print(f"📊 Generating {num_sales} sales records...")
    
    for i in range(num_sales):
        # Random date in last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        sold_at = base_date + timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Random product
        product = random.choice(products.data)
        
        # Random quantity (1-5 items per sale)
        quantity = random.randint(1, 5)
        
        # Price variation (±20% from current price)
        base_price = float(product['current_price'])
        price_variation = random.uniform(0.8, 1.2)
        sold_price = round(base_price * price_variation, 2)
        
        sale_record = {
            "shop_id": shop_id,
            "shopify_order_id": 2000000 + (i // 3),  # Group 3 items per order on average
            "shopify_line_item_id": 3000000 + i,
            "sku_code": product['sku_code'],
            "quantity_sold": quantity,
            "sold_price": sold_price,
            "sold_at": sold_at.isoformat()
        }
        
        sales_data.append(sale_record)
    
    # Insert sales data in batches
    try:
        batch_size = 50
        sales_created = 0
        
        for i in range(0, len(sales_data), batch_size):
            batch = sales_data[i:i + batch_size]
            result = supabase.table('sales').insert(batch).execute()
            sales_created += len(result.data) if result.data else 0
            print(f"   ✅ Inserted batch {i//batch_size + 1}: {len(batch)} sales")
        
        print(f"\n🎉 SALES DATA POPULATED!")
        print(f"   📊 Total sales records: {sales_created}")
        
        # Calculate and show analytics
        total_revenue = sum(sale['sold_price'] * sale['quantity_sold'] for sale in sales_data)
        total_items_sold = sum(sale['quantity_sold'] for sale in sales_data)
        unique_orders = len(set(sale['shopify_order_id'] for sale in sales_data))
        
        print(f"\n📈 SALES ANALYTICS:")
        print(f"   💰 Total Revenue: ${total_revenue:,.2f}")
        print(f"   📦 Total Items Sold: {total_items_sold:,}")
        print(f"   🛒 Unique Orders: {unique_orders:,}")
        print(f"   📊 Average Order Value: ${total_revenue/unique_orders:.2f}")
        print(f"   📅 Sales Period: Last 30 days")
        
        # Show top selling products
        product_sales = {}
        for sale in sales_data:
            sku = sale['sku_code']
            if sku not in product_sales:
                product_sales[sku] = {'quantity': 0, 'revenue': 0}
            product_sales[sku]['quantity'] += sale['quantity_sold']
            product_sales[sku]['revenue'] += sale['sold_price'] * sale['quantity_sold']
        
        top_products = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:5]
        
        print(f"\n🏆 TOP SELLING PRODUCTS:")
        for i, (sku, data) in enumerate(top_products, 1):
            print(f"   {i}. {sku}: {data['quantity']} sold, ${data['revenue']:.2f} revenue")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to populate sales data: {e}")
        return False

def verify_sales_data():
    """Verify the sales data was populated correctly"""
    print(f"\n🔍 VERIFYING SALES DATA...")
    
    supabase = get_supabase_client()
    
    # Check total records
    sales = supabase.table('sales').select('*').eq('shop_id', 4).execute()
    print(f"   📊 Total sales records: {len(sales.data)}")
    
    if sales.data:
        # Show recent sales
        recent_sales = sorted(sales.data, key=lambda x: x['sold_at'], reverse=True)[:5]
        print(f"   📋 Recent sales:")
        for sale in recent_sales:
            print(f"      {sale['sku_code']}: {sale['quantity_sold']} × ${sale['sold_price']} = ${sale['quantity_sold'] * sale['sold_price']:.2f}")
        
        return True
    else:
        print("   ❌ No sales data found")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    success = populate_sales_data()
    
    if success:
        verify_sales_data()
        print(f"\n🚀 YOUR SALES DATA IS READY!")
        print("✅ Sales table populated with realistic data")
        print("✅ Revenue analytics available")
        print("✅ Product performance data ready")
        print("✅ Time-series data for trends")
        print("\n🎯 NOW BUILD YOUR DASHBOARD! 🚀")
    else:
        print("\n💥 Failed to populate sales data")