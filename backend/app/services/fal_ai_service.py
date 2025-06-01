"""
FAL AI service for generating AI avatars from business summaries.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import fal_client
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging import get_logger, log_external_api_call, log_error, LoggerMixin
from app.services.azure_ai_service import AzureAIService
from app.services.trend_analysis_service import TrendAnalysisService


logger = get_logger(__name__)


class FALAIService(LoggerMixin):
    """Service for FAL AI avatar generation integration."""
    
    def __init__(self):
        """Initialize FAL AI service."""
        self.azure_ai_service = AzureAIService()
        self.trend_analysis_service = TrendAnalysisService()
        
        # Configure FAL client if API key is available
        self.fal_api_key = getattr(settings, 'FAL_KEY', None)
        if self.fal_api_key:
            fal_client.api_key = self.fal_api_key
            logger.info("FAL AI client configured successfully")
        else:
            logger.warning("FAL API key not configured, will use mock responses")
    
    async def generate_business_avatar_video(
        self,
        shop_id: int,
        avatar_id: str = "marcus_primary",
        include_business_context: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an AI avatar video with business summary.
        
        Args:
            shop_id: Store ID
            avatar_id: FAL AI avatar ID to use
            include_business_context: Whether to include business context in the script
            
        Returns:
            Avatar video generation result with URL and metadata
        """
        self.logger.info(
            "Generating business avatar video",
            shop_id=shop_id,
            avatar_id=avatar_id,
            include_business_context=include_business_context
        )
        
        try:
            # Generate business summary text for the avatar
            avatar_script = await self._generate_avatar_script(shop_id, include_business_context)
            
            # Check if FAL AI is properly configured
            if not self.fal_api_key:
                logger.warning("FAL AI not configured, using mock avatar video")
                return self._generate_mock_avatar_video(avatar_script, avatar_id)
            
            # Generate avatar video using FAL AI
            avatar_result = await self._call_fal_ai_avatar(avatar_id, avatar_script)
            
            # Add metadata
            avatar_result.update({
                "generated_at": datetime.utcnow().isoformat(),
                "shop_id": shop_id,
                "avatar_id": avatar_id,
                "script_content": avatar_script,
                "ai_provider": "fal_ai",
                "model": "veed/avatars/text-to-video"
            })
            
            self.logger.info(
                "Business avatar video generated successfully",
                shop_id=shop_id,
                avatar_id=avatar_id,
                video_url=avatar_result.get("video_url", ""),
                script_length=len(avatar_script)
            )
            
            return avatar_result
            
        except Exception as e:
            log_error(e, {
                "shop_id": shop_id,
                "service": "fal_ai",
                "operation": "generate_business_avatar_video",
                "avatar_id": avatar_id
            })
            
            # Fallback to mock avatar on error
            logger.warning(f"FAL AI failed, using mock avatar video: {e}")
            avatar_script = await self._generate_avatar_script(shop_id, include_business_context)
            return self._generate_mock_avatar_video(avatar_script, avatar_id)
    
    async def _generate_avatar_script(self, shop_id: int, include_business_context: bool = True) -> str:
        """
        Generate the script text for the avatar to speak.
        
        Args:
            shop_id: Store ID
            include_business_context: Whether to include detailed business context
            
        Returns:
            Script text for the avatar
        """
        try:
            if include_business_context:
                # Get business data and trend analysis
                business_data = await self.azure_ai_service.get_business_data(shop_id)
                trend_summary = await self.trend_analysis_service.get_trend_summary(shop_id)
                
                # Generate business summary
                business_summary = await self.azure_ai_service.generate_business_summary(
                    shop_id, business_data, trend_summary
                )
                
                # Create avatar script from business summary
                script = self._create_avatar_script_from_summary(business_data, business_summary)
            else:
                # Generate a simple welcome script
                script = self._create_simple_avatar_script(shop_id)
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating avatar script: {e}")
            # Fallback to simple script
            return self._create_simple_avatar_script(shop_id)
    
    def _create_avatar_script_from_summary(
        self,
        business_data: Dict[str, Any],
        business_summary: Dict[str, Any]
    ) -> str:
        """Create avatar script from business summary data."""
        
        store_name = business_data.get('store_name', 'Your Store')
        revenue = business_data.get('revenue_30d', 45000)
        avg_order_value = business_data.get('avg_order_value', 250)
        conversion_rate = business_data.get('conversion_rate', 3.2)
        
        # Get key insights from the summary
        executive_summary = business_summary.get('executive_summary', '')
        key_insights = business_summary.get('key_insights', [])
        performance_highlights = business_summary.get('performance_highlights', [])
        
        # Create the script with Jaz persona
        script = f"""Welcome to your briefing! I'm Jaz, analyst at BizPredict.

{store_name} delivered ${revenue:,.0f} in revenue over the last 30 days with a solid average order value of ${avg_order_value:.0f} and a {conversion_rate:.1f}% conversion rate.

{executive_summary}

Here are the key highlights: {' '.join(performance_highlights[:2]) if performance_highlights else 'Your business is showing strong performance across multiple metrics.'}

{key_insights[0] if key_insights else 'Your product portfolio is well-positioned in the current market.'}

I recommend focusing on your top-performing products and optimizing your marketing strategy to capitalize on current trends. Keep monitoring your metrics and I'll be here with your next briefing soon."""

        return script
    
    def _create_simple_avatar_script(self, shop_id: int) -> str:
        """Create a simple avatar script without detailed business context."""
        
        script = """Welcome to your briefing! I'm Jaz, analyst at BizPredict.

Your store is performing well with strong metrics across the board. I've analyzed your latest data and identified several opportunities for growth.

Your product portfolio shows good momentum with many items trending positively in the market. The analytics indicate healthy customer engagement and solid conversion rates.

I recommend continuing your current strategy while keeping an eye on emerging trends. I'll be back with more detailed insights in your next briefing."""

        return script
    
    async def _call_fal_ai_avatar(self, avatar_id: str, text: str) -> Dict[str, Any]:
        """
        Call FAL AI avatar generation API.
        
        Args:
            avatar_id: Avatar ID to use
            text: Text for the avatar to speak
            
        Returns:
            FAL AI response with video URL and metadata
        """
        if not self.fal_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="FAL AI client not configured"
            )
        
        request_start_time = datetime.utcnow()
        
        try:
            def on_queue_update(update):
                """Handle queue updates from FAL AI."""
                if isinstance(update, fal_client.InProgress):
                    for log in update.logs:
                        logger.info(f"FAL AI progress: {log.get('message', 'Processing...')}")
            
            # Call FAL AI avatar generation
            result = fal_client.subscribe(
                "veed/avatars/text-to-video",
                arguments={
                    "avatar_id": avatar_id,
                    "text": text
                },
                with_logs=True,
                on_queue_update=on_queue_update,
            )
            
            request_duration = (datetime.utcnow() - request_start_time).total_seconds()
            
            # Log the successful API call
            log_external_api_call(
                service="fal_ai",
                endpoint="veed/avatars/text-to-video",
                method="POST",
                status_code=200,
                duration=request_duration,
                model="veed/avatars/text-to-video"
            )
            
            logger.info(
                "FAL AI avatar generation successful",
                avatar_id=avatar_id,
                duration=request_duration,
                result_keys=list(result.keys()) if isinstance(result, dict) else "non-dict-result"
            )
            
            # Extract video URL and metadata from result
            if isinstance(result, dict):
                return {
                    "video_url": result.get("video", {}).get("url") if isinstance(result.get("video"), dict) else result.get("video"),
                    "duration_seconds": result.get("duration"),
                    "format": "mp4",
                    "resolution": result.get("resolution", "1080p"),
                    "file_size_bytes": result.get("file_size"),
                    "fal_request_id": result.get("request_id"),
                    "raw_result": result
                }
            else:
                # Handle non-dict responses
                return {
                    "video_url": str(result) if result else None,
                    "duration_seconds": None,
                    "format": "mp4",
                    "resolution": "1080p",
                    "file_size_bytes": None,
                    "raw_result": result
                }
            
        except Exception as e:
            request_duration = (datetime.utcnow() - request_start_time).total_seconds()
            
            # Log the failed API call
            log_external_api_call(
                service="fal_ai",
                endpoint="veed/avatars/text-to-video",
                method="POST",
                status_code=None,
                duration=request_duration,
                error_message=str(e),
                model="veed/avatars/text-to-video"
            )
            
            logger.error(f"FAL AI avatar generation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"FAL AI avatar generation error: {str(e)}"
            )
    
    def _generate_mock_avatar_video(self, script: str, avatar_id: str) -> Dict[str, Any]:
        """Generate a mock avatar video response for development/fallback."""
        
        return {
            "video_url": f"https://mock-fal-ai.com/avatars/{avatar_id}/video.mp4",
            "duration_seconds": 45,
            "format": "mp4",
            "resolution": "1080p",
            "file_size_bytes": 8500000,  # ~8.5MB
            "script_content": script,
            "avatar_id": avatar_id,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "mock_fal_ai",
            "model": "veed/avatars/text-to-video",
            "status": "completed",
            "mock_response": True,
            "message": "This is a mock response. Configure FAL_API_KEY for real avatar generation."
        }
    
    async def get_available_avatars(self) -> Dict[str, Any]:
        """
        Get list of available avatars from FAL AI.
        
        Returns:
            List of available avatars with their IDs and metadata
        """
        try:
            # For now, return a predefined list of avatars
            # In a real implementation, this could query FAL AI for available avatars
            avatars = [
                {
                    "id": "marcus_primary",
                    "name": "Marcus",
                    "description": "Professional business analyst",
                    "gender": "male",
                    "style": "business_professional",
                    "preview_image": "https://mock-fal-ai.com/avatars/marcus_primary/preview.jpg"
                },
                {
                    "id": "sarah_executive",
                    "name": "Sarah",
                    "description": "Executive business consultant",
                    "gender": "female",
                    "style": "business_executive",
                    "preview_image": "https://mock-fal-ai.com/avatars/sarah_executive/preview.jpg"
                },
                {
                    "id": "alex_casual",
                    "name": "Alex",
                    "description": "Casual business advisor",
                    "gender": "non-binary",
                    "style": "business_casual",
                    "preview_image": "https://mock-fal-ai.com/avatars/alex_casual/preview.jpg"
                }
            ]
            
            return {
                "avatars": avatars,
                "total": len(avatars),
                "default_avatar": "marcus_primary",
                "service_status": "available" if self.fal_api_key else "mock_mode"
            }
            
        except Exception as e:
            log_error(e, {
                "service": "fal_ai",
                "operation": "get_available_avatars"
            })
            
            return {
                "avatars": [],
                "total": 0,
                "error": str(e),
                "service_status": "error"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for FAL AI service.
        
        Returns:
            Health check status and details
        """
        try:
            status_info = {
                "service": "fal_ai",
                "status": "healthy" if self.fal_api_key else "configured_mock",
                "api_key_configured": bool(self.fal_api_key),
                "timestamp": datetime.utcnow().isoformat(),
                "available_models": ["veed/avatars/text-to-video"],
                "default_avatar": "marcus_primary"
            }
            
            if self.fal_api_key:
                # Could add a simple API test here if needed
                status_info["connection_test"] = "skipped"
            else:
                status_info["message"] = "Running in mock mode - configure FAL_API_KEY for real avatar generation"
            
            return status_info
            
        except Exception as e:
            return {
                "service": "fal_ai",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }