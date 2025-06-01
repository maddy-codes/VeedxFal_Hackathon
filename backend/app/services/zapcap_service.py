"""
ZapCap API service for adding subtitles to generated videos.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging import get_logger, log_external_api_call, log_error, LoggerMixin


logger = get_logger(__name__)


class ZapCapService(LoggerMixin):
    """Service for ZapCap subtitle generation integration."""
    
    def __init__(self):
        """Initialize ZapCap service."""
        self.api_key = getattr(settings, 'ZAP_CAP_KEY', None)
        self.base_url = "https://api.zapcap.ai"
        
        if self.api_key:
            logger.info(f"ZapCap API configured successfully with key: {self.api_key[:10]}...")
        else:
            logger.warning("ZapCap API key not configured, subtitle generation will be disabled")
    
    async def add_subtitles_to_video(
        self,
        video_url: str,
        template_id: str = "default",
        language: str = "en",
        auto_approve: bool = True
    ) -> Dict[str, Any]:
        """
        Add subtitles to a video using ZapCap API.
        
        Args:
            video_url: URL of the video to add subtitles to
            template_id: ZapCap template ID to use
            language: Language for subtitle generation
            auto_approve: Whether to auto-approve the transcript
            
        Returns:
            ZapCap task result with subtitle video URL
        """
        if not self.api_key:
            logger.warning("ZapCap API not configured, skipping subtitle generation")
            return {
                "status": "skipped",
                "message": "ZapCap API not configured",
                "original_video_url": video_url
            }
        
        self.logger.info(
            "Adding subtitles to video",
            video_url=video_url,
            template_id=template_id,
            language=language
        )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Upload video by URL
                upload_result = await self._upload_video_by_url(client, video_url)
                video_id = upload_result["id"]
                
                # Step 2: Create subtitle task
                task_result = await self._create_subtitle_task(
                    client, video_id, template_id, language, auto_approve
                )
                task_id = task_result["taskId"]
                
                # Step 3: Monitor task progress
                final_result = await self._monitor_task_progress(client, video_id, task_id)
                
                self.logger.info(
                    "Subtitles added successfully",
                    video_url=video_url,
                    subtitle_video_url=final_result.get("downloadUrl"),
                    task_id=task_id
                )
                
                return final_result
                
        except Exception as e:
            log_error(e, {
                "video_url": video_url,
                "service": "zapcap",
                "operation": "add_subtitles_to_video"
            })
            
            # Return original video if subtitle generation fails
            logger.warning(f"ZapCap subtitle generation failed, returning original video: {e}")
            return {
                "status": "failed",
                "message": f"Subtitle generation failed: {str(e)}",
                "original_video_url": video_url,
                "downloadUrl": video_url  # Fallback to original
            }
    
    async def _upload_video_by_url(self, client: httpx.AsyncClient, video_url: str) -> Dict[str, Any]:
        """Upload video to ZapCap by URL."""
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": video_url
        }
        
        response = await client.post(
            f"{self.base_url}/videos/url",
            headers=headers,
            json=payload
        )
        
        log_external_api_call(
            service="zapcap",
            endpoint="/videos/url",
            method="POST",
            status_code=response.status_code,
            duration=0  # We don't track duration here
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ZapCap upload failed: {response.text}"
            )
        
        return response.json()
    
    async def _create_subtitle_task(
        self,
        client: httpx.AsyncClient,
        video_id: str,
        template_id: str,
        language: str,
        auto_approve: bool
    ) -> Dict[str, Any]:
        """Create a subtitle generation task."""
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "templateId": template_id,
            "autoApprove": auto_approve,
            "language": language
        }
        
        response = await client.post(
            f"{self.base_url}/videos/{video_id}/task",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ZapCap task creation failed: {response.text}"
            )
        
        return response.json()
    
    async def _monitor_task_progress(
        self,
        client: httpx.AsyncClient,
        video_id: str,
        task_id: str,
        max_attempts: int = 60
    ) -> Dict[str, Any]:
        """Monitor task progress until completion."""
        
        headers = {
            "x-api-key": self.api_key
        }
        
        for attempt in range(max_attempts):
            response = await client.get(
                f"{self.base_url}/videos/{video_id}/task/{task_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"ZapCap status check failed: {response.text}"
                )
            
            task_data = response.json()
            status_value = task_data.get("status")
            
            logger.info(f"ZapCap task status: {status_value} (attempt {attempt + 1})")
            
            if status_value == "completed":
                return task_data
            elif status_value in ["failed", "error"]:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"ZapCap task failed: {task_data.get('error', 'Unknown error')}"
                )
            
            # Wait 10 seconds before next check
            await asyncio.sleep(10)
        
        # Timeout
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ZapCap task timed out"
        )
    
    async def get_available_templates(self) -> Dict[str, Any]:
        """Get available ZapCap templates."""
        
        if not self.api_key:
            return {
                "templates": [],
                "message": "ZapCap API not configured"
            }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "x-api-key": self.api_key
                }
                
                response = await client.get(
                    f"{self.base_url}/templates",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get ZapCap templates: {response.text}")
                    return {
                        "templates": [],
                        "error": response.text
                    }
                    
        except Exception as e:
            logger.error(f"ZapCap templates request failed: {e}")
            return {
                "templates": [],
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for ZapCap service."""
        
        try:
            status_info = {
                "service": "zapcap",
                "status": "healthy" if self.api_key else "not_configured",
                "api_key_configured": bool(self.api_key),
                "base_url": self.base_url
            }
            
            if self.api_key:
                # Test API connectivity by getting templates
                templates_result = await self.get_available_templates()
                status_info["api_accessible"] = "error" not in templates_result
                status_info["available_templates"] = len(templates_result.get("templates", []))
            
            return status_info
            
        except Exception as e:
            return {
                "service": "zapcap",
                "status": "unhealthy",
                "error": str(e)
            }