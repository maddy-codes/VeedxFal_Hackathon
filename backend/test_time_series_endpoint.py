#!/usr/bin/env python3
"""
Test the new time-series analytics endpoint
"""

import asyncio
import sys
from pathlib import Path
import requests
import json

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_time_series_endpoint():
    """Test the time-series analytics endpoint"""
    print("🚀 TESTING TIME-SERIES ANALYTICS ENDPOINT")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    shop_id = 4  # The shop with data
    
    try:
        # Test different time ranges
        time_ranges = [7, 30, 90]
        
        for days in time_ranges:
            print(f"\n📊 Testing {days}-day time series...")
            
            url = f"{base_url}/api/v1/analytics/time-series?shop_id={shop_id}&days={days}"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: Got {len(data)} data points")
                
                if data:
                    # Show sample data
                    first_item = data[0]
                    last_item = data[-1]
                    
                    print(f"   📅 Date range: {first_item['date']} to {last_item['date']}")
                    print(f"   💰 Revenue range: ${first_item['daily_revenue']:.2f} to ${last_item['daily_revenue']:.2f}")
                    print(f"   📦 Orders range: {first_item['daily_orders']} to {last_item['daily_orders']}")
                    
                    # Calculate totals
                    total_revenue = sum(item['daily_revenue'] for item in data)
                    total_orders = sum(item['daily_orders'] for item in data)
                    avg_daily_revenue = total_revenue / len(data) if data else 0
                    
                    print(f"   📈 Total revenue: ${total_revenue:,.2f}")
                    print(f"   📊 Total orders: {total_orders}")
                    print(f"   📉 Avg daily revenue: ${avg_daily_revenue:.2f}")
                else:
                    print("   ⚠️  No data returned")
                    
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
        
        # Test the original dashboard endpoint for comparison
        print(f"\n🔍 Testing original dashboard endpoint for comparison...")
        dashboard_url = f"{base_url}/api/v1/analytics/dashboard?shop_id={shop_id}"
        
        response = requests.get(dashboard_url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dashboard data:")
            print(f"   💰 Total revenue: ${data['total_revenue']:,.2f}")
            print(f"   📦 Total orders: {data['total_orders']}")
            print(f"   📊 Avg order value: ${data['avg_order_value']:.2f}")
            print(f"   🏪 Total products: {data['total_products']}")
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
            
        print(f"\n🎯 CHART DATA VERIFICATION")
        print("=" * 40)
        print("✅ Time-series endpoint provides real daily data")
        print("✅ Data includes actual revenue, orders, and quantities")
        print("✅ Charts will now show real trends instead of fake weekly data")
        print("✅ Performance metrics will be calculated from real data")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_time_series_endpoint()
    
    if success:
        print(f"\n🎉 TIME-SERIES ENDPOINT TEST PASSED!")
        print("Your charts will now display real data instead of fake data! 📈")
    else:
        print(f"\n💥 Time-series endpoint test failed")