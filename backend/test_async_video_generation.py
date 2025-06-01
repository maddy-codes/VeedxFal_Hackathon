"""
Test script for async video generation functionality.
"""

import asyncio
import json
import logging
import time
from datetime import datetime

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

async def test_async_video_generation():
    """Test the async video generation workflow."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Step 1: Start video generation
            logger.info("🚀 Starting async video generation...")
            
            generate_response = await client.post(
                f"{BASE_URL}/api/v1/video/avatar/generate",
                params={
                    "shop_id": 1,
                    "avatar_id": "marcus_primary",
                    "include_business_context": True
                }
            )
            
            if generate_response.status_code != 200:
                logger.error(f"Failed to start video generation: {generate_response.status_code}")
                logger.error(f"Response: {generate_response.text}")
                return
            
            generation_data = generate_response.json()
            logger.info(f"✅ Video generation started successfully")
            logger.info(f"Response: {json.dumps(generation_data, indent=2)}")
            
            job_id = generation_data["data"]["job_id"]
            logger.info(f"📋 Job ID: {job_id}")
            
            # Step 2: Poll for completion
            logger.info("⏳ Polling for completion...")
            
            max_attempts = 60  # 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                
                # Wait before checking status
                await asyncio.sleep(5)
                
                # Check job status
                status_response = await client.get(
                    f"{BASE_URL}/api/v1/video/status/{job_id}"
                )
                
                if status_response.status_code != 200:
                    logger.warning(f"Failed to get status: {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                status = status_data["status"]
                progress = status_data.get("progress", 0)
                current_step = status_data.get("current_step", "Unknown")
                
                logger.info(f"📊 Attempt {attempt}: {status} - {current_step} ({progress}%)")
                
                if status == "completed":
                    logger.info("🎉 Video generation completed!")
                    logger.info(f"Video URL: {status_data.get('video_url', 'N/A')}")
                    logger.info(f"Duration: {status_data.get('duration_seconds', 'N/A')} seconds")
                    logger.info(f"Script preview: {status_data.get('script', 'N/A')[:100]}...")
                    break
                elif status == "failed":
                    logger.error(f"❌ Video generation failed: {status_data.get('error_message', 'Unknown error')}")
                    break
                elif status in ["pending", "processing", "generating_insights", "generating_script", "generating_video", "finalizing"]:
                    # Still processing, continue polling
                    continue
                else:
                    logger.warning(f"⚠️ Unknown status: {status}")
            
            if attempt >= max_attempts:
                logger.error("⏰ Polling timed out after 5 minutes")
            
        except Exception as e:
            logger.error(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

async def test_video_generation_api():
    """Test the regular video generation API."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info("🚀 Testing regular video generation API...")
            
            # Create a video generation request
            request_data = {
                "insights_limit": 5,
                "voice_id": None,
                "template": "business",
                "custom_message": None
            }
            
            generate_response = await client.post(
                f"{BASE_URL}/api/v1/video/generate",
                params={"shop_id": 1},
                json=request_data
            )
            
            if generate_response.status_code != 200:
                logger.error(f"Failed to start video generation: {generate_response.status_code}")
                logger.error(f"Response: {generate_response.text}")
                return
            
            generation_data = generate_response.json()
            logger.info(f"✅ Video generation started successfully")
            logger.info(f"Job ID: {generation_data['job_id']}")
            logger.info(f"Status: {generation_data['status']}")
            logger.info(f"Message: {generation_data['message']}")
            
        except Exception as e:
            logger.error(f"❌ Regular video generation test failed: {e}")

async def test_health_checks():
    """Test health check endpoints."""
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            logger.info("🏥 Testing health check endpoints...")
            
            # Test avatar health check
            health_response = await client.get(f"{BASE_URL}/api/v1/video/avatar/health")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                logger.info(f"✅ Avatar service health: {health_data['data']['status']}")
            else:
                logger.warning(f"⚠️ Avatar health check failed: {health_response.status_code}")
            
            # Test available avatars
            avatars_response = await client.get(f"{BASE_URL}/api/v1/video/avatar/avatars")
            
            if avatars_response.status_code == 200:
                avatars_data = avatars_response.json()
                logger.info(f"✅ Available avatars: {len(avatars_data['data']['avatars'])}")
            else:
                logger.warning(f"⚠️ Get avatars failed: {avatars_response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Health check test failed: {e}")

async def main():
    """Run all tests."""
    
    logger.info("🧪 Starting async video generation tests...")
    logger.info(f"⏰ Test started at: {datetime.now()}")
    
    # Run database migration first
    try:
        logger.info("🗄️ Running database migration...")
        import subprocess
        result = subprocess.run(
            ["python", "add_video_async_columns.py"],
            cwd=".",
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("✅ Database migration completed")
        else:
            logger.warning(f"⚠️ Database migration warning: {result.stderr}")
    except Exception as e:
        logger.warning(f"⚠️ Could not run database migration: {e}")
    
    # Test health checks first
    await test_health_checks()
    
    # Test async avatar generation
    await test_async_video_generation()
    
    # Test regular video generation API
    await test_video_generation_api()
    
    logger.info(f"🏁 Tests completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main())