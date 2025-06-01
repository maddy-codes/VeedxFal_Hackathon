"""
Test script for FAL AI avatar generation functionality.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

async def test_avatar_generation():
    """Test avatar generation endpoints."""
    
    async with httpx.AsyncClient() as client:
        print("🎬 Testing Avatar Generation Functionality")
        print("=" * 50)
        
        # Test 1: Health check
        print("\n1. Testing avatar service health check...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/video/avatar/health")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check successful")
                print(f"Service status: {health_data['data']['status']}")
                print(f"API key configured: {health_data['data']['api_key_configured']}")
                print(f"Available models: {health_data['data']['available_models']}")
            else:
                print(f"❌ Health check failed: {response.text}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test 2: Get available avatars
        print("\n2. Testing get available avatars...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/video/avatar/avatars")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                avatars_data = response.json()
                print(f"✅ Available avatars retrieved")
                print(f"Total avatars: {avatars_data['data']['total']}")
                print(f"Default avatar: {avatars_data['data']['default_avatar']}")
                print(f"Service status: {avatars_data['data']['service_status']}")
                
                # Print avatar details
                for avatar in avatars_data['data']['avatars']:
                    print(f"  - {avatar['name']} ({avatar['id']}): {avatar['description']}")
            else:
                print(f"❌ Get avatars failed: {response.text}")
        except Exception as e:
            print(f"❌ Get avatars error: {e}")
        
        # Test 3: Generate avatar video (mock mode)
        print("\n3. Testing avatar video generation...")
        try:
            params = {
                "shop_id": 1,
                "avatar_id": "marcus_primary",
                "include_business_context": True
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/video/avatar/generate",
                params=params
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                avatar_data = response.json()
                print(f"✅ Avatar video generation successful")
                print(f"Video URL: {avatar_data['data']['video_url']}")
                print(f"Duration: {avatar_data['data']['duration_seconds']} seconds")
                print(f"Avatar ID: {avatar_data['data']['avatar_id']}")
                print(f"AI Provider: {avatar_data['data']['ai_provider']}")
                print(f"Generated at: {avatar_data['data']['generated_at']}")
                
                # Print script preview
                script = avatar_data['data']['script_content']
                print(f"\nScript preview (first 200 chars):")
                print(f"'{script[:200]}...'")
                
                if avatar_data['data'].get('mock_response'):
                    print(f"⚠️  Note: {avatar_data['data']['message']}")
            else:
                print(f"❌ Avatar generation failed: {response.text}")
        except Exception as e:
            print(f"❌ Avatar generation error: {e}")
        
        # Test 4: Generate avatar video with simple context
        print("\n4. Testing avatar video generation (simple context)...")
        try:
            params = {
                "shop_id": 1,
                "avatar_id": "sarah_executive",
                "include_business_context": False
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/video/avatar/generate",
                params=params
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                avatar_data = response.json()
                print(f"✅ Simple avatar video generation successful")
                print(f"Avatar ID: {avatar_data['data']['avatar_id']}")
                print(f"Video URL: {avatar_data['data']['video_url']}")
                
                # Print script preview
                script = avatar_data['data']['script_content']
                print(f"\nSimple script preview (first 150 chars):")
                print(f"'{script[:150]}...'")
            else:
                print(f"❌ Simple avatar generation failed: {response.text}")
        except Exception as e:
            print(f"❌ Simple avatar generation error: {e}")
        
        print("\n" + "=" * 50)
        print("🎬 Avatar Generation Testing Complete!")
        print("\nNext steps:")
        print("1. Configure FAL_KEY in your .env file for real avatar generation")
        print("2. Test with real FAL AI API key")
        print("3. Integrate avatar generation into your frontend")


async def test_business_context_integration():
    """Test integration with business context generation."""
    
    async with httpx.AsyncClient() as client:
        print("\n🔗 Testing Business Context Integration")
        print("=" * 50)
        
        # Test business context endpoint
        print("\n1. Testing business context generation...")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/trend-analysis/business-context/1"
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                context_data = response.json()
                print(f"✅ Business context generated")
                print(f"Executive summary: {context_data['data']['executive_summary'][:100]}...")
                print(f"Key insights count: {len(context_data['data']['key_insights'])}")
                print(f"Performance highlights: {len(context_data['data']['performance_highlights'])}")
            else:
                print(f"❌ Business context failed: {response.text}")
        except Exception as e:
            print(f"❌ Business context error: {e}")
        
        # Test trend analysis
        print("\n2. Testing trend analysis...")
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/trend-analysis/insights/1/summary"
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                trend_data = response.json()
                print(f"✅ Trend analysis retrieved")
                print(f"Total products: {trend_data['data']['total_products']}")
                print(f"Hot products: {trend_data['data']['summary']['Hot']}")
                print(f"Rising products: {trend_data['data']['summary']['Rising']}")
            else:
                print(f"❌ Trend analysis failed: {response.text}")
        except Exception as e:
            print(f"❌ Trend analysis error: {e}")


if __name__ == "__main__":
    print("Starting Avatar Generation Tests...")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Run avatar generation tests
        asyncio.run(test_avatar_generation())
        
        # Run business context integration tests
        asyncio.run(test_business_context_integration())
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)