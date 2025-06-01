#!/usr/bin/env python3
"""
Direct test of FAL AI avatar generation without server dependencies.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_fal_direct():
    """Test FAL AI directly."""
    
    print("🎬 Testing FAL AI Direct Integration")
    print("=" * 50)
    
    # Check if FAL_KEY is available
    fal_key = os.getenv('FAL_KEY')
    if not fal_key:
        print("❌ FAL_KEY not found in environment")
        return
    
    print(f"✅ FAL_KEY found: {fal_key[:20]}...")
    
    try:
        import fal_client
        
        # Set the API key
        os.environ['FAL_KEY'] = fal_key
        fal_client.api_key = fal_key
        
        print("✅ FAL client imported and configured")
        
        # Test script
        test_script = """Welcome to your briefing! I'm Jaz, analyst at BizPredict.

Your store delivered $45,000 in revenue over the last 30 days with a solid average order value of $250 and a 3.2% conversion rate.

Your business is showing strong performance across multiple metrics with good momentum in electronics and clothing categories.

I recommend focusing on your top-performing products and optimizing your marketing strategy to capitalize on current trends."""
        
        print("\n🚀 Starting FAL AI avatar generation...")
        print(f"Script length: {len(test_script)} characters")
        
        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    print(f"📝 FAL AI: {log.get('message', 'Processing...')}")
        
        # Call FAL AI
        result = fal_client.subscribe(
            "veed/avatars/text-to-video",
            arguments={
                "avatar_id": "marcus_primary",
                "text": test_script
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        
        print("\n✅ FAL AI generation completed!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and "video" in result:
            video_url = result["video"].get("url")
            print(f"🎥 Video URL: {video_url}")
            print(f"📊 Content type: {result['video'].get('content_type')}")
            print(f"📏 File size: {result['video'].get('file_size', 'Unknown')} bytes")
        else:
            print(f"⚠️  Unexpected result format: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ FAL AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_fal_direct())