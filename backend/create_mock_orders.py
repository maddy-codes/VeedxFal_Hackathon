#!/usr/bin/env python3
"""
CREATE MOCK ORDERS - Get your dashboard working NOW!
This creates realistic order data so your dashboard works immediately.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client

def create_sales_table():
    """Create sales table if it doesn't exist"""
    print("📋 Creating sales table...")
    
    supabase = get_supabase_client()
    
    create_sales_sql = """
    CREATE TABLE IF NOT EXISTS sales (
        id SERIAL PRIMARY KEY,
        shop_id BIGINT NOT NULL,
        shopify_order_id BIGINT NOT NULL,
        order_number TEXT,
        customer_email TEXT,
        customer_name TEXT,
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
        supabase.rpc('exec_sql', {'sql': create_sales_sql}).execute()
        print("✅ Sales table created/verified")
        return True
    except Exception as e:
        print(f"❌ Failed to create sales table: {e}")
        return False

def create_mock_sales(shop_id=4):
    """Create realistic mock sales for dashboard testing"""
    print("🎭 Creating mock sales for dashboard...")
    
    supabase = get_supabase_client()
    
    # Get some products to reference
    products = supabase.table('products').select('sku_code, product_title, current_price').eq('shop_id', shop_id).limit(20).execute()
    
    if not products.data:
        print("❌ No products found - run product sync first")
        return False
    
    # Generate mock sales for the last 30 days
    mock_sales = []
    base_date = datetime.now() - timedelta(days=30)
    
    customer_names = [
        "John Smith", "Sarah Johnson", "Mike Davis", "Emily Brown", "David Wilson",
        "Lisa Anderson", "Chris Taylor", "Amanda Martinez", "Ryan Garcia", "Jessica Lee",
        "Kevin White", "Michelle Thompson", "Daniel Rodriguez", "Ashley Clark", "James Lewis"
    ]
    
    financial_statuses = ["paid", "pending", "refunded"]
    fulfillment_statuses = ["fulfilled", "partial", "unfulfilled"]
    
    for i in range(100):  # Create 100 mock sales
        # Random date in last 30 days
        days_ago = random.randint(0, 30)
        order_date = base_date + timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        # Random customer
        customer_name = random.choice(customer_names)
        customer_email = f"{customer_name.lower().replace(' ', '.')}@example.com"
        
        # Random products and quantities
        num_items = random.randint(1, 4)
        selected_products = random.sample(products.data, min(num_items, len(products.data)))
        
        subtotal = 0
        for product in selected_products:
            quantity = random.randint(1, 3)
            subtotal += float(product['current_price']) * quantity
        
        tax_rate = 0.08  # 8% tax
        total_tax = round(subtotal * tax_rate, 2)
        total_price = round(subtotal + total_tax, 2)
        
        mock_sale = {
            "shop_id": shop_id,
            "shopify_order_id": 1000000 + i,  # Mock Shopify IDs
            "order_number": f"#{1001 + i}",
            "customer_email": customer_email,
            "customer_name": customer_name,
            "total_price": total_price,
            "subtotal_price": subtotal,
            "total_tax": total_tax,
            "currency": "USD",
            "financial_status": random.choice(financial_statuses),
            "fulfillment_status": random.choice(fulfillment_statuses),
            "order_date": order_date.isoformat()
        }
        
        mock_sales.append(mock_sale)
    
    # Insert mock sales
    try:
        # Clear existing mock sales first
        supabase.table('sales').delete().eq('shop_id', shop_id).gte('shopify_order_id', 1000000).execute()
        
        # Insert new mock sales in batches
        batch_size = 20
        sales_created = 0
        
        for i in range(0, len(mock_sales), batch_size):
            batch = mock_sales[i:i + batch_size]
            result = supabase.table('sales').insert(batch).execute()
            sales_created += len(result.data) if result.data else 0
            print(f"   Created batch {i//batch_size + 1}: {len(batch)} sales")
        
        print(f"✅ Created {sales_created} mock sales")
        
        # Show summary statistics
        print(f"\n📊 SALES SUMMARY:")
        
        # Total revenue
        total_revenue = sum(sale['total_price'] for sale in mock_sales)
        print(f"   💰 Total Revenue: ${total_revenue:,.2f}")
        
        # Sales by status
        paid_sales = len([s for s in mock_sales if s['financial_status'] == 'paid'])
        pending_sales = len([s for s in mock_sales if s['financial_status'] == 'pending'])
        refunded_sales = len([s for s in mock_sales if s['financial_status'] == 'refunded'])
        
        print(f"   📈 Paid Sales: {paid_sales}")
        print(f"   ⏳ Pending Sales: {pending_sales}")
        print(f"   🔄 Refunded Sales: {refunded_sales}")
        
        # Recent sales
        recent_sales = sorted(mock_sales, key=lambda x: x['order_date'], reverse=True)[:5]
        print(f"\n📋 Recent Sales:")
        for sale in recent_sales:
            print(f"   {sale['order_number']}: {sale['customer_name']} - ${sale['total_price']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create mock sales: {e}")
        return False

def show_real_orders_setup():
    """Show how to get real orders from Shopify"""
    print(f"\n🔧 TO GET REAL ORDERS FROM SHOPIFY:")
    print("=" * 50)
    print("1. Your Shopify app needs 'read_orders' permission")
    print("2. Update your app scopes in Shopify Partner Dashboard")
    print("3. Users need to re-authorize your app")
    print("4. Current scopes are likely just 'read_products'")
    print("\n📝 Required scopes for full functionality:")
    print("   - read_products (✅ you have this)")
    print("   - read_orders (❌ you need this)")
    print("   - read_inventory (optional)")
    print("   - read_customers (optional)")
    
    print(f"\n💡 FOR NOW: Use the mock data to build your dashboard!")
    print("   The mock orders have realistic data patterns")
    print("   Your dashboard will work perfectly with this data")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🚀 CREATING SALES DATA FOR YOUR DASHBOARD")
    print("=" * 50)
    
    # Create sales table
    if not create_sales_table():
        print("💥 Failed to create sales table")
        sys.exit(1)
    
    # Create mock sales
    if create_mock_sales():
        print(f"\n🎉 YOUR DASHBOARD DATA IS READY!")
        print("✅ Sales table created")
        print("✅ 100 realistic mock sales generated")
        print("✅ Revenue, customer, and date data available")
        print("✅ Your dashboard can now show:")
        print("   📊 Sales analytics")
        print("   💰 Revenue trends")
        print("   👥 Customer insights")
        print("   📈 Order status tracking")
        
        show_real_orders_setup()
        
        print(f"\n🚀 GO BUILD YOUR HACKATHON DASHBOARD! 🎯")
    else:
        print("💥 Failed to create mock sales")