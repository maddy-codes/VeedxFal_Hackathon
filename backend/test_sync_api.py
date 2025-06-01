#!/usr/bin/env python3
"""
Test the sync API endpoint directly
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import httpx

async def test_sync_api():
    """Test the sync API endpoint"""
    try:
        print("🧪 Testing sync API endpoint...")
        
        # Test data
        sync_request = {
            "full_sync": False
        }
        
        # Make request to sync endpoint
        async with httpx.AsyncClient() as client:
            # First, let's test if the server is running
            try:
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                print(f"✅ Server is running: {response.status_code}")
            except Exception as e:
                print(f"❌ Server not running: {e}")
                print("💡 Start the server with: uvicorn main:app --reload")
                return False
            
            # Test the sync endpoint
            try:
                response = await client.post(
                    "http://localhost:8000/api/v1/sync/shopify?shop_id=4",
                    json=sync_request,
                    headers={"Authorization": "Bearer test-token"},  # You might need a real token
                    timeout=10.0
                )
                
                print(f"📊 Sync API Response: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Sync started: {json.dumps(data, indent=2)}")
                    return True
                else:
                    print(f"❌ API Error: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ API request failed: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_sync_status():
    """Check current sync status"""
    try:
        from app.core.database import get_supabase_client
        supabase = get_supabase_client()
        
        # Get latest sync job
        result = supabase.table('sync_jobs').select('*').eq('shop_id', 4).order('started_at', desc=True).limit(1).execute()
        
        if result.data:
            job = result.data[0]
            print(f"\n📊 Latest Sync Job:")
            print(f"   ID: {job['id']}")
            print(f"   Status: {job['status']}")
            print(f"   Started: {job.get('started_at')}")
            print(f"   Processed: {job.get('processed_items', 0)}/{job.get('total_items', 'unknown')}")
            if job.get('error_message'):
                print(f"   Error: {job['error_message']}")
        else:
            print("📊 No sync jobs found")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🔍 Checking current sync status...")
    asyncio.run(check_sync_status())
    
    print("\n🧪 Testing sync API...")
    success = asyncio.run(test_sync_api())
    print(f"\n🎯 API test {'PASSED' if success else 'FAILED'}")