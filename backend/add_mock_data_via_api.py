#!/usr/bin/env python3
"""
Add mock trend data via API endpoints
"""

import requests
import json
import random
from datetime import datetime, timedelta

# API Configuration
API_BASE = 'http://localhost:8000'
LOGIN_EMAIL = 'jatinarora2689@gmail.com'
LOGIN_PASSWORD = 'Jazz@1552'

# Mock product data for trend analysis
MOCK_TREND_DATA = [
    {
        "sku_code": "DEMO-001",
        "product_title": "Wireless Bluetooth Headphones",
        "google_trend_index": 85.5,
        "social_score": 78.2,
        "final_score": 82.1,
        "label": "Hot"
    },
    {
        "sku_code": "DEMO-002", 
        "product_title": "Smart Fitness Tracker",
        "google_trend_index": 72.3,
        "social_score": 68.9,
        "final_score": 70.8,
        "label": "Rising"
    },
    {
        "sku_code": "DEMO-003",
        "product_title": "Organic Coffee Beans",
        "google_trend_index": 45.7,
        "social_score": 52.1,
        "final_score": 48.9,
        "label": "Steady"
    },
    {
        "sku_code": "DEMO-004",
        "product_title": "Yoga Mat Premium",
        "google_trend_index": 91.2,
        "social_score": 87.6,
        "final_score": 89.4,
        "label": "Hot"
    },
    {
        "sku_code": "DEMO-005",
        "product_title": "Smart Home Speaker",
        "google_trend_index": 65.8,
        "social_score": 71.3,
        "final_score": 68.5,
        "label": "Rising"
    },
    {
        "sku_code": "DEMO-006",
        "product_title": "Skincare Serum Set",
        "google_trend_index": 55.4,
        "social_score": 49.7,
        "final_score": 52.6,
        "label": "Steady"
    },
    {
        "sku_code": "DEMO-007",
        "product_title": "Gaming Mechanical Keyboard",
        "google_trend_index": 78.9,
        "social_score": 82.4,
        "final_score": 80.7,
        "label": "Rising"
    },
    {
        "sku_code": "DEMO-008",
        "product_title": "Protein Powder Vanilla",
        "google_trend_index": 38.2,
        "social_score": 41.6,
        "final_score": 39.9,
        "label": "Declining"
    }
]

def login_and_get_token():
    """Login and get authentication token"""
    print("🔐 Logging in...")
    
    login_data = {
        'email': LOGIN_EMAIL,
        'password': LOGIN_PASSWORD
    }
    
    response = requests.post(f'{API_BASE}/api/v1/auth/login', json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def add_trend_data_via_api(token):
    """Add trend data using the analyze endpoint"""
    print("📊 Adding mock trend data...")
    
    headers = {'Authorization': f'Bearer {token}'}
    shop_id = 1
    
    success_count = 0
    
    for trend_data in MOCK_TREND_DATA:
        # Prepare trend analysis request
        analysis_request = {
            "sku_code": trend_data["sku_code"],
            "product_title": trend_data["product_title"],
            "search_terms": [trend_data["product_title"].lower()],
            "category": "demo"
        }
        
        try:
            # Call the analyze endpoint
            response = requests.post(
                f'{API_BASE}/api/v1/trend-analysis/analyze/{shop_id}',
                json=analysis_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Added trend data for {trend_data['product_title']}")
                success_count += 1
            else:
                print(f"⚠️  Failed to add {trend_data['product_title']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error adding {trend_data['product_title']}: {e}")
    
    print(f"📈 Successfully added {success_count}/{len(MOCK_TREND_DATA)} trend analyses")
    return success_count

def test_trend_endpoints(token):
    """Test the trend analysis endpoints"""
    print("\n🧪 Testing trend analysis endpoints...")
    
    headers = {'Authorization': f'Bearer {token}'}
    shop_id = 1
    
    try:
        # Test trend summary
        response = requests.get(f'{API_BASE}/api/v1/trend-analysis/insights/{shop_id}/summary', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Trend Summary:")
            print(f"   Total Products: {data.get('total_products', 0)}")
            
            if data.get('summary'):
                print("   Distribution:")
                for label, count in data['summary'].items():
                    print(f"     {label}: {count}")
            
            if data.get('average_scores'):
                scores = data['average_scores']
                print(f"   Avg Scores: Google: {scores.get('google_trend_index', 0):.1f}, "
                      f"Social: {scores.get('social_score', 0):.1f}, "
                      f"Final: {scores.get('final_score', 0):.1f}")
        else:
            print(f"❌ Trend summary failed: {response.status_code}")
        
        # Test trending products
        response = requests.get(f'{API_BASE}/api/v1/trend-analysis/insights/{shop_id}/trending?limit=5', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔥 Trending Products: {data.get('count', 0)} found")
            
            if data.get('trending_products'):
                for product in data['trending_products'][:3]:
                    title = product.get('product_title', 'N/A')
                    label = product.get('trend_data', {}).get('label', 'N/A')
                    score = product.get('trend_data', {}).get('final_score', 0)
                    print(f"   • {title} - {label} (Score: {score:.1f})")
        else:
            print(f"❌ Trending products failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

def main():
    """Main function"""
    print("🚀 CREATING MOCK TREND DATA FOR DEMO")
    print("=" * 50)
    
    # Login
    token = login_and_get_token()
    if not token:
        return
    
    # Add mock data
    success_count = add_trend_data_via_api(token)
    
    if success_count > 0:
        # Test endpoints
        test_trend_endpoints(token)
        
        print(f"\n🎉 Mock data creation completed!")
        print(f"✅ {success_count} trend analyses created")
        print(f"🚀 Ready for demo!")
        print(f"📱 Frontend: http://localhost:3000/dashboard/insights")
        print(f"🔑 Login: {LOGIN_EMAIL} / {LOGIN_PASSWORD}")
    else:
        print("\n❌ No mock data was created successfully")

if __name__ == "__main__":
    main()