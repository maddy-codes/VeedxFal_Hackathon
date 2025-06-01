"""
Background video processing service for async video generation.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.database import DatabaseManager
from app.core.logging import get_logger, log_business_event
from app.services.azure_ai_service import AzureAIService
from app.services.fal_ai_service import FALAIService


logger = get_logger(__name__)


class VideoProcessor:
    """Background video processor for async video generation."""
    
    def __init__(self):
        """Initialize video processor."""
        self.azure_ai_service = AzureAIService()
        self.fal_ai_service = FALAIService()
        self.db_manager = DatabaseManager()
        self.processing_jobs = {}  # Track active jobs
        
    async def process_video_generation_job(self, job_id: str) -> Dict[str, Any]:
        """
        Process a video generation job asynchronously.
        
        Args:
            job_id: Video generation job ID
            
        Returns:
            Processing result with status and details
        """
        logger.info(f"Starting video generation job processing: {job_id}")
        
        try:
            # Mark job as processing
            self.processing_jobs[job_id] = {
                "status": "processing",
                "started_at": datetime.utcnow(),
                "current_step": "initializing"
            }
            
            # Get job details from database
            job_data = await self._get_job_data(job_id)
            if not job_data:
                raise Exception(f"Job {job_id} not found")
            
            # Update job status to processing
            await self._update_job_status(
                job_id, 
                "processing", 
                "Initializing video generation",
                progress=5
            )
            
            # Step 1: Generate business insights
            await self._update_job_status(
                job_id, 
                "generating_insights", 
                "Analyzing business data and generating insights",
                progress=20
            )
            
            business_data = await self._generate_business_insights(
                job_data["shop_id"], 
                job_data["request_data"]
            )
            
            # Step 2: Generate script
            await self._update_job_status(
                job_id, 
                "generating_script", 
                "Creating personalized video script",
                progress=40
            )
            
            script_data = await self._generate_video_script(
                job_id,
                job_data["shop_id"], 
                business_data,
                job_data["request_data"]
            )
            
            # Step 3: Generate avatar video
            await self._update_job_status(
                job_id, 
                "generating_video", 
                "Creating AI avatar video",
                progress=70
            )
            
            video_result = await self._generate_avatar_video(
                job_id,
                job_data["shop_id"],
                script_data["script_content"],
                job_data["request_data"]
            )
            
            # Step 4: Finalize and save
            await self._update_job_status(
                job_id, 
                "finalizing", 
                "Finalizing video and saving results",
                progress=90
            )
            
            final_result = await self._finalize_video_generation(
                job_id,
                job_data["shop_id"],
                script_data,
                video_result
            )
            
            # Mark as completed
            await self._update_job_status(
                job_id, 
                "completed", 
                "Video generation completed successfully",
                progress=100
            )
            
            # Clean up processing job
            if job_id in self.processing_jobs:
                del self.processing_jobs[job_id]
            
            # Log completion
            log_business_event(
                "video_generation_completed",
                user_id=job_data["user_id"],
                shop_id=job_data["shop_id"],
                job_id=job_id,
                duration_seconds=(datetime.utcnow() - self.processing_jobs.get(job_id, {}).get("started_at", datetime.utcnow())).total_seconds()
            )
            
            logger.info(f"Video generation job completed successfully: {job_id}")
            
            return {
                "status": "completed",
                "job_id": job_id,
                "video_url": final_result.get("video_url"),
                "script_content": script_data["script_content"],
                "duration_seconds": final_result.get("duration_seconds"),
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Video generation job failed: {job_id} - {str(e)}")
            
            # Mark job as failed
            await self._update_job_status(
                job_id, 
                "failed", 
                f"Video generation failed: {str(e)}",
                progress=0,
                error_message=str(e)
            )
            
            # Clean up processing job
            if job_id in self.processing_jobs:
                del self.processing_jobs[job_id]
            
            # Log failure
            log_business_event(
                "video_generation_failed",
                user_id=job_data.get("user_id", "unknown"),
                shop_id=job_data.get("shop_id", 0),
                job_id=job_id,
                error=str(e)
            )
            
            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
    
    async def _get_job_data(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data from database."""
        query = """
        SELECT job_id, shop_id, user_id, status, request_data, created_at
        FROM video_jobs
        WHERE job_id = :job_id
        """
        
        result = await self.db_manager.fetch_one(query, {"job_id": job_id})
        return dict(result) if result else None
    
    async def _update_job_status(
        self, 
        job_id: str, 
        status: str, 
        current_step: str,
        progress: int = 0,
        error_message: Optional[str] = None
    ):
        """Update job status in database."""
        update_query = """
        UPDATE video_jobs 
        SET 
            status = :status,
            current_step = :current_step,
            progress = :progress,
            error_message = :error_message,
            updated_at = NOW()
        WHERE job_id = :job_id
        """
        
        await self.db_manager.execute_query(update_query, {
            "job_id": job_id,
            "status": status,
            "current_step": current_step,
            "progress": progress,
            "error_message": error_message
        })
        
        # Update processing jobs tracker
        if job_id in self.processing_jobs:
            self.processing_jobs[job_id].update({
                "status": status,
                "current_step": current_step,
                "progress": progress,
                "updated_at": datetime.utcnow()
            })
    
    async def _generate_business_insights(
        self, 
        shop_id: int, 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate business insights for the video."""
        try:
            # Get business data using Azure AI service
            business_data = await self.azure_ai_service.get_business_data(shop_id)
            
            # Get trend analysis if requested
            insights_limit = request_data.get("insights_limit", 5)
            
            return {
                "business_data": business_data,
                "insights_limit": insights_limit,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate business insights: {e}")
            # Return mock data as fallback
            return {
                "business_data": {
                    "store_name": f"Store {shop_id}",
                    "revenue_30d": 45000,
                    "avg_order_value": 250,
                    "conversion_rate": 3.2
                },
                "insights_limit": request_data.get("insights_limit", 5),
                "generated_at": datetime.utcnow().isoformat(),
                "fallback": True
            }
    
    async def _generate_video_script(
        self, 
        job_id: str,
        shop_id: int, 
        business_data: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video script."""
        try:
            # Generate script using FAL AI service
            script_content = await self.fal_ai_service._generate_avatar_script(
                shop_id, 
                include_business_context=True
            )
            
            # Calculate estimated duration (average reading speed: 150 words per minute)
            word_count = len(script_content.split())
            estimated_duration = max(30, (word_count / 150) * 60)  # Minimum 30 seconds
            
            # Save script to database
            script_id = str(uuid.uuid4())
            insert_script_query = """
            INSERT INTO video_scripts (
                script_id, job_id, shop_id, script_content, 
                word_count, estimated_duration, generated_at
            )
            VALUES (
                :script_id, :job_id, :shop_id, :script_content,
                :word_count, :estimated_duration, NOW()
            )
            """
            
            await self.db_manager.execute_query(insert_script_query, {
                "script_id": script_id,
                "job_id": job_id,
                "shop_id": shop_id,
                "script_content": script_content,
                "word_count": word_count,
                "estimated_duration": estimated_duration
            })
            
            return {
                "script_id": script_id,
                "script_content": script_content,
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate video script: {e}")
            raise Exception(f"Script generation failed: {str(e)}")
    
    async def _generate_avatar_video(
        self, 
        job_id: str,
        shop_id: int,
        script_content: str,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate avatar video using FAL AI."""
        try:
            # Generate avatar video
            avatar_result = await self.fal_ai_service.generate_business_avatar_video(
                shop_id=shop_id,
                avatar_id="marcus_primary",  # Default to Jaz/Marcus
                include_business_context=True
            )
            
            return avatar_result
            
        except Exception as e:
            logger.error(f"Failed to generate avatar video: {e}")
            raise Exception(f"Avatar video generation failed: {str(e)}")
    
    async def _finalize_video_generation(
        self, 
        job_id: str,
        shop_id: int,
        script_data: Dict[str, Any],
        video_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Finalize video generation and save to database."""
        try:
            video_id = str(uuid.uuid4())
            
            # Insert generated video record
            insert_video_query = """
            INSERT INTO generated_videos (
                video_id, shop_id, job_id, video_url, script_content,
                duration_seconds, file_size_bytes, resolution, format,
                generated_at, expires_at, metadata
            )
            VALUES (
                :video_id, :shop_id, :job_id, :video_url, :script_content,
                :duration_seconds, :file_size_bytes, :resolution, :format,
                NOW(), :expires_at, :metadata
            )
            """
            
            # Set expiration to 30 days from now
            expires_at = datetime.utcnow() + timedelta(days=30)
            
            await self.db_manager.execute_query(insert_video_query, {
                "video_id": video_id,
                "shop_id": shop_id,
                "job_id": job_id,
                "video_url": video_result.get("video_url"),
                "script_content": script_data["script_content"],
                "duration_seconds": video_result.get("duration_seconds", 45),
                "file_size_bytes": video_result.get("file_size_bytes"),
                "resolution": video_result.get("resolution", "1080p"),
                "format": video_result.get("format", "mp4"),
                "expires_at": expires_at,
                "metadata": video_result
            })
            
            # Update job with completion details
            update_job_query = """
            UPDATE video_jobs 
            SET 
                completed_at = NOW(),
                video_id = :video_id
            WHERE job_id = :job_id
            """
            
            await self.db_manager.execute_query(update_job_query, {
                "job_id": job_id,
                "video_id": video_id
            })
            
            return {
                "video_id": video_id,
                "video_url": video_result.get("video_url"),
                "duration_seconds": video_result.get("duration_seconds", 45),
                "script_content": script_data["script_content"],
                "generated_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to finalize video generation: {e}")
            raise Exception(f"Video finalization failed: {str(e)}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current job status."""
        # Check if job is currently being processed
        if job_id in self.processing_jobs:
            processing_info = self.processing_jobs[job_id]
            return {
                "job_id": job_id,
                "status": processing_info["status"],
                "current_step": processing_info["current_step"],
                "progress": processing_info.get("progress", 0),
                "started_at": processing_info["started_at"].isoformat(),
                "processing": True
            }
        
        # Get status from database
        query = """
        SELECT 
            vj.job_id,
            vj.status,
            vj.current_step,
            vj.progress,
            vj.created_at,
            vj.started_at,
            vj.completed_at,
            vj.error_message,
            gv.video_url,
            gv.duration_seconds,
            vs.script_content
        FROM video_jobs vj
        LEFT JOIN generated_videos gv ON vj.job_id = gv.job_id
        LEFT JOIN video_scripts vs ON vj.job_id = vs.job_id
        WHERE vj.job_id = :job_id
        """
        
        result = await self.db_manager.fetch_one(query, {"job_id": job_id})
        
        if result:
            return {
                "job_id": result["job_id"],
                "status": result["status"],
                "current_step": result["current_step"],
                "progress": result["progress"] or 0,
                "created_at": result["created_at"].isoformat() if result["created_at"] else None,
                "started_at": result["started_at"].isoformat() if result["started_at"] else None,
                "completed_at": result["completed_at"].isoformat() if result["completed_at"] else None,
                "video_url": result["video_url"],
                "duration_seconds": result["duration_seconds"],
                "script_content": result["script_content"],
                "error_message": result["error_message"],
                "processing": False
            }
        
        return None


# Global video processor instance
video_processor = VideoProcessor()


async def start_video_generation_job(job_id: str):
    """Start a video generation job in the background."""
    try:
        # Create background task
        task = asyncio.create_task(video_processor.process_video_generation_job(job_id))
        
        # Don't await the task - let it run in background
        logger.info(f"Started background video generation job: {job_id}")
        
        return task
        
    except Exception as e:
        logger.error(f"Failed to start video generation job {job_id}: {e}")
        raise


async def get_video_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get video generation job status."""
    return await video_processor.get_job_status(job_id)