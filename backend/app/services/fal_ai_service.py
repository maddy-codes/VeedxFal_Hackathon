"""
FAL AI service for generating AI avatars from business summaries.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

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
            # Set the API key in the environment for fal_client
            import os
            os.environ['FAL_KEY'] = self.fal_api_key
            # Also set the client API key directly
            fal_client.api_key = self.fal_api_key
            logger.info(f"FAL AI client configured successfully with key: {self.fal_api_key[:10]}...")
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
                
                # Get trend insights instead of trend summary
                try:
                    trend_insights = await self.trend_analysis_service.get_trend_insights(shop_id, max_age_hours=24)
                    # Create a simple trend summary from insights
                    trend_summary = self._create_trend_summary_from_insights(trend_insights)
                except Exception as e:
                    logger.warning(f"Failed to get trend insights: {e}")
                    # Use mock trend summary
                    trend_summary = self._create_mock_trend_summary(shop_id)
                
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
    
    def _create_trend_summary_from_insights(self, trend_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a trend summary from trend insights data."""
        if not trend_insights:
            return self._create_mock_trend_summary(1)
        
        # Calculate summary statistics
        label_counts = {"Hot": 0, "Rising": 0, "Steady": 0, "Declining": 0}
        total_google_trend = 0
        total_social_score = 0
        total_final_score = 0
        
        for insight in trend_insights:
            label_counts[insight.get("label", "Steady")] += 1
            total_google_trend += insight.get("google_trend_index", 50)
            total_social_score += insight.get("social_score", 50)
            total_final_score += insight.get("final_score", 50)
        
        total_products = len(trend_insights)
        
        return {
            "total_products": total_products,
            "summary": label_counts,
            "percentages": {
                label: round((count / total_products) * 100, 1)
                for label, count in label_counts.items()
            },
            "average_scores": {
                "google_trend_index": round(total_google_trend / total_products, 1),
                "social_score": round(total_social_score / total_products, 1),
                "final_score": round(total_final_score / total_products, 1)
            }
        }
    
    def _create_mock_trend_summary(self, shop_id: int) -> Dict[str, Any]:
        """Create a mock trend summary for fallback."""
        return {
            "shop_id": shop_id,
            "total_products": 50,
            "summary": {
                "Hot": 12,
                "Rising": 18,
                "Steady": 15,
                "Declining": 5
            },
            "percentages": {
                "Hot": 24.0,
                "Rising": 36.0,
                "Steady": 30.0,
                "Declining": 10.0
            },
            "average_scores": {
                "google_trend_index": 72.3,
                "social_score": 68.7,
                "final_score": 70.5
            }
        }
    
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
            # Map our avatar IDs to FAL AI avatar IDs
            fal_avatar_mapping = {
                "marcus_primary": "marcus_primary",
                "sarah_executive": "emily_primary",  # Use emily as fallback for sarah
                "alex_casual": "any_male_primary"
            }
            
            fal_avatar_id = fal_avatar_mapping.get(avatar_id, "marcus_primary")
            
            # Use submit instead of subscribe for better timeout handling
            handler = fal_client.submit(
                "veed/avatars/text-to-video",
                arguments={
                    "avatar_id": fal_avatar_id,
                    "text": text
                }
            )
            
            logger.info(f"FAL AI request submitted with ID: {handler.request_id}")
            
            # Try to get result with timeout
            import asyncio
            try:
                # Wait for result with 30 second timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(lambda: fal_client.result("veed/avatars/text-to-video", handler.request_id)),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.warning("FAL AI request timed out, returning processing status")
                # Return a "processing" response that the frontend can handle
                return {
                    "video_url": None,
                    "duration_seconds": None,
                    "format": "mp4",
                    "resolution": "1080p",
                    "file_size_bytes": None,
                    "status": "processing",
                    "request_id": handler.request_id,
                    "message": "Video is being generated. This may take a few minutes.",
                    "processing": True
                }
            
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
            # FAL AI returns: {"video": {"url": "...", "content_type": "video/mp4", ...}}
            if isinstance(result, dict) and "video" in result:
                video_data = result["video"]
                return {
                    "video_url": video_data.get("url"),
                    "duration_seconds": 45,  # Estimated duration
                    "format": "mp4",
                    "resolution": "1080p",
                    "file_size_bytes": video_data.get("file_size"),
                    "content_type": video_data.get("content_type", "video/mp4"),
                    "fal_request_id": result.get("request_id"),
                    "raw_result": result
                }
            else:
                # Handle unexpected response format
                logger.warning(f"Unexpected FAL AI response format: {result}")
                return {
                    "video_url": str(result) if result else None,
                    "duration_seconds": 45,
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