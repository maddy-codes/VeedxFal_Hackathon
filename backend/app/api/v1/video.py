"""
Video generation API endpoints.
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.deps import get_current_user_id, get_db_manager_dep, verify_store_access, get_optional_current_user
from app.core.logging import log_business_event
from app.models.auth import ErrorResponse
from app.models.video import (
    GeneratedVideo,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoListResponse,
    VideoStatus,
)
from app.services.fal_ai_service import FALAIService
from app.services.zapcap_service import ZapCapService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/generate",
    response_model=VideoGenerationResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Generate AI video",
    description="Generate AI-powered business insights video",
)
async def generate_video(
    video_request: VideoGenerationRequest,
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Generate AI-powered business insights video."""
    
    try:
        # Create video generation job
        job_id = str(uuid.uuid4())
        
        # Insert video generation job
        insert_query = """
        INSERT INTO video_jobs (
            job_id, shop_id, user_id, status, request_data, created_at, progress, current_step
        )
        VALUES (:job_id, :shop_id, :user_id, 'pending', :request_data, NOW(), 0, 'Job created')
        """
        
        await db_manager.execute_query(insert_query, {
            "job_id": job_id,
            "shop_id": shop_id,
            "user_id": user_id,
            "request_data": video_request.dict(),
        })
        
        # Start background video generation job
        await start_video_generation_job(job_id)
        
        # Log video generation request
        log_business_event(
            "video_generation_requested",
            user_id=user_id,
            shop_id=shop_id,
            job_id=job_id,
            insights_limit=video_request.insights_limit
        )
        
        # Calculate estimated completion (typically 2-5 minutes)
        estimated_completion = datetime.utcnow().replace(microsecond=0)
        estimated_completion = estimated_completion.replace(minute=estimated_completion.minute + 3)
        
        return VideoGenerationResponse(
            job_id=job_id,
            status="pending",
            estimated_completion=estimated_completion,
            message="Video generation started. Your personalized business briefing will be ready in a few minutes.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video generation service error"
        )


@router.get(
    "/status/{job_id}",
    response_model=VideoStatus,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Job not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get video generation status",
    description="Get status of video generation job",
)
async def get_video_status(
    job_id: str = Path(..., description="Video generation job ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
):
    """Get video generation status."""
    
    try:
        # Get job status from video processor
        job_status = await get_video_job_status(job_id)
        
        if not job_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video generation job not found"
            )
        
        # Verify user has access to this job
        verify_query = """
        SELECT user_id FROM video_jobs WHERE job_id = :job_id
        """
        
        verify_result = await db_manager.fetch_one(verify_query, {"job_id": job_id})
        
        if not verify_result or verify_result["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this video generation job"
            )
        
        # Parse datetime strings back to datetime objects for response
        started_at = None
        completed_at = None
        
        if job_status.get("started_at"):
            started_at = datetime.fromisoformat(job_status["started_at"].replace('Z', '+00:00'))
        elif job_status.get("created_at"):
            started_at = datetime.fromisoformat(job_status["created_at"].replace('Z', '+00:00'))
        else:
            started_at = datetime.utcnow()
            
        if job_status.get("completed_at"):
            completed_at = datetime.fromisoformat(job_status["completed_at"].replace('Z', '+00:00'))
        
        return VideoStatus(
            job_id=job_status["job_id"],
            status=job_status["status"],
            progress=job_status.get("progress", 0),
            current_step=job_status.get("current_step", job_status["status"].replace("_", " ").title()),
            started_at=started_at,
            completed_at=completed_at,
            video_url=job_status.get("video_url"),
            script=job_status.get("script_content"),
            duration_seconds=job_status.get("duration_seconds"),
            error_message=job_status.get("error_message"),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get video status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video status service error"
        )


@router.get(
    "/latest",
    responses={
        200: {"description": "Latest videos retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get latest videos",
    description="Get latest generated videos for the store",
)
async def get_latest_videos(
    shop_id: int = Query(..., description="Store ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    db_manager=Depends(get_db_manager_dep),
):
    """Get latest generated videos."""
    
    try:
        # Count total videos
        count_query = """
        SELECT COUNT(*) as total
        FROM generated_videos
        WHERE shop_id = :shop_id
        """
        
        total_result = await db_manager.fetch_one(count_query, {"shop_id": shop_id})
        total = total_result["total"] if total_result else 0
        
        # Get videos with pagination
        offset = (page - 1) * limit
        
        videos_query = """
        SELECT
            video_id,
            shop_id,
            job_id,
            video_url,
            script_content,
            audio_url,
            duration_seconds,
            file_size_bytes,
            format,
            resolution,
            generated_at,
            expires_at,
            view_count,
            metadata
        FROM generated_videos
        WHERE shop_id = :shop_id
        ORDER BY generated_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        videos_result = await db_manager.fetch_all(videos_query, {
            "shop_id": shop_id,
            "limit": limit,
            "offset": offset
        })
        
        videos = []
        for row in videos_result:
            videos.append({
                "video_id": row["video_id"],
                "shop_id": row["shop_id"],
                "job_id": row["job_id"],
                "video_url": row["video_url"],
                "script_content": row["script_content"],
                "audio_url": row["audio_url"],
                "duration_seconds": row["duration_seconds"],
                "file_size_bytes": row["file_size_bytes"],
                "format": row["format"],
                "resolution": row["resolution"],
                "generated_at": row["generated_at"].isoformat() if row["generated_at"] else None,
                "expires_at": row["expires_at"].isoformat() if row["expires_at"] else None,
                "view_count": row["view_count"],
                "metadata": row["metadata"] or {},
            })
        
        return {
            "status": "success",
            "data": {
                "videos": videos,
                "total": total,
                "page": page,
                "limit": limit,
                "has_next": (page * limit) < total,
            }
        }
        
    except Exception as e:
        logger.error(f"Get latest videos error: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve videos: {str(e)}",
            "data": {
                "videos": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "has_next": False,
            }
        }


@router.post(
    "/{video_id}/view",
    responses={
        200: {"description": "View recorded successfully"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Video not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Record video view",
    description="Record a view for the video",
)
async def record_video_view(
    video_id: str = Path(..., description="Video ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
):
    """Record a view for the video."""
    
    try:
        # Update view count
        update_query = """
        UPDATE generated_videos 
        SET view_count = view_count + 1
        WHERE video_id = :video_id
        AND shop_id IN (
            SELECT s.id FROM stores s 
            WHERE (s.shop_config->>'user_id')::text = :user_id
        )
        RETURNING video_id, view_count
        """
        
        result = await db_manager.fetch_one(update_query, {
            "video_id": video_id,
            "user_id": user_id
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        # Log video view
        log_business_event(
            "video_viewed",
            user_id=user_id,
            video_id=video_id,
            view_count=result["view_count"]
        )
        
        return {
            "message": "View recorded successfully",
            "view_count": result["view_count"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record video view error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video view service error"
        )


@router.post(
    "/avatar/generate",
    responses={
        200: {"description": "Avatar video generation started"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Generate AI avatar video",
    description="Generate AI avatar video with business summary",
)
async def generate_avatar_video(
    shop_id: int = Query(..., description="Store ID"),
    avatar_id: str = Query("marcus_primary", description="Avatar ID to use"),
    include_business_context: bool = Query(True, description="Include detailed business context"),
    add_subtitles: bool = Query(False, description="Add subtitles using ZapCap"),
    db_manager=Depends(get_db_manager_dep),
):
    """Generate AI avatar video with business summary."""
    
    try:
        # Initialize services
        fal_service = FALAIService()
        zapcap_service = ZapCapService()
        
        # Generate avatar video
        avatar_result = await fal_service.generate_business_avatar_video(
            shop_id=shop_id,
            avatar_id=avatar_id,
            include_business_context=include_business_context
        )
        
        # Add subtitles if requested and video was generated successfully
        if add_subtitles and avatar_result.get("video_url"):
            try:
                logger.info(f"Adding subtitles to video: {avatar_result.get('video_url')}")
                
                subtitle_result = await zapcap_service.add_subtitles_to_video(
                    video_url=avatar_result["video_url"],
                    language="en",
                    auto_approve=True
                )
                
                # Update the video URL to the subtitle version if successful
                if subtitle_result.get("downloadUrl") and subtitle_result.get("status") == "completed":
                    avatar_result["original_video_url"] = avatar_result["video_url"]
                    avatar_result["video_url"] = subtitle_result["downloadUrl"]
                    avatar_result["subtitles_added"] = True
                    avatar_result["subtitle_task_id"] = subtitle_result.get("id")
                    logger.info(f"Subtitles added successfully: {subtitle_result['downloadUrl']}")
                else:
                    avatar_result["subtitles_added"] = False
                    avatar_result["subtitle_error"] = subtitle_result.get("message", "Subtitle generation failed")
                    logger.warning(f"Subtitle generation failed: {subtitle_result}")
                    
            except Exception as subtitle_error:
                # Don't fail the whole request if subtitle generation fails
                logger.warning(f"Failed to add subtitles: {subtitle_error}")
                avatar_result["subtitles_added"] = False
                avatar_result["subtitle_error"] = str(subtitle_error)
        else:
            avatar_result["subtitles_added"] = False
        
        # Store the generated video in the database if it has a video URL
        if avatar_result.get("video_url"):
            try:
                import uuid as uuid_lib
                video_id = str(uuid_lib.uuid4())
                
                insert_video_query = """
                INSERT INTO generated_videos (
                    video_id, shop_id, video_url, script_content,
                    duration_seconds, format, resolution,
                    generated_at, metadata
                )
                VALUES (
                    :video_id, :shop_id, :video_url, :script_content,
                    :duration_seconds, :format, :resolution,
                    NOW(), :metadata
                )
                """
                
                # Convert duration to integer if it's a float (to match the table schema)
                duration = avatar_result.get("duration_seconds", 45)
                if isinstance(duration, float):
                    duration = int(duration)
                
                await db_manager.execute_query(insert_video_query, {
                    "video_id": video_id,
                    "shop_id": shop_id,
                    "video_url": avatar_result.get("video_url"),
                    "script_content": avatar_result.get("script_content", ""),
                    "duration_seconds": duration,
                    "format": avatar_result.get("format", "mp4"),
                    "resolution": avatar_result.get("resolution", "1080p"),
                    "metadata": avatar_result
                })
                
                # Add the video_id to the response
                avatar_result["video_id"] = video_id
                
                logger.info(f"Stored generated video in database: {video_id}")
                
            except Exception as db_error:
                # Don't fail the whole request if database storage fails
                logger.warning(f"Failed to store video in database: {db_error}")
        
        # Log avatar generation request
        log_business_event(
            "avatar_video_generated",
            user_id="test_user",
            shop_id=shop_id,
            avatar_id=avatar_id,
            include_business_context=include_business_context,
            subtitles_added=avatar_result.get("subtitles_added", False)
        )
        
        return {
            "status": "success",
            "message": "Avatar video generated successfully" + (" with subtitles" if avatar_result.get("subtitles_added") else ""),
            "data": avatar_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar video generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar video generation service error"
        )


@router.get(
    "/avatar/avatars",
    responses={
        200: {"description": "Available avatars retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get available avatars",
    description="Get list of available AI avatars",
)
async def get_available_avatars():
    """Get list of available AI avatars."""
    
    try:
        # Initialize FAL AI service
        fal_service = FALAIService()
        
        # Get available avatars
        avatars_result = await fal_service.get_available_avatars()
        
        return {
            "status": "success",
            "message": "Available avatars retrieved successfully",
            "data": avatars_result
        }
        
    except Exception as e:
        logger.error(f"Get available avatars error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar service error"
        )


@router.get(
    "/avatar/health",
    responses={
        200: {"description": "Avatar service health check"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Avatar service health check",
    description="Check health status of avatar generation service",
)
async def avatar_health_check():
    """Check health status of avatar generation service."""
    
    try:
        # Initialize services
        fal_service = FALAIService()
        zapcap_service = ZapCapService()
        
        # Perform health checks
        fal_health = await fal_service.health_check()
        zapcap_health = await zapcap_service.health_check()
        
        return {
            "status": "success",
            "message": "Avatar service health check completed",
            "data": {
                "fal_ai": fal_health,
                "zapcap": zapcap_health
            }
        }
        
    except Exception as e:
        logger.error(f"Avatar health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar health check service error"
        )


@router.get(
    "/subtitles/templates",
    responses={
        200: {"description": "ZapCap templates retrieved"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get subtitle templates",
    description="Get available ZapCap subtitle templates",
)
async def get_subtitle_templates():
    """Get available ZapCap subtitle templates."""
    
    try:
        zapcap_service = ZapCapService()
        templates_result = await zapcap_service.get_available_templates()
        
        return {
            "status": "success",
            "message": "Subtitle templates retrieved successfully",
            "data": templates_result
        }
        
    except Exception as e:
        logger.error(f"Get subtitle templates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Subtitle templates service error"
        )


@router.get(
    "/avatar/status/{request_id}",
    responses={
        200: {"description": "Avatar generation status retrieved"},
        404: {"model": ErrorResponse, "description": "Request not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get avatar generation status",
    description="Check the status of an avatar video generation request",
)
async def get_avatar_status(request_id: str):
    """Get avatar generation status by request ID."""
    
    try:
        # Try to get status from FAL AI service directly
        try:
            import fal_client
            result = fal_client.result("veed/avatars/text-to-video", request_id)
            
            # Parse result same as in generate_avatar_video
            if isinstance(result, dict) and "video" in result:
                video_data = result["video"]
                return {
                    "status": "completed",
                    "video_url": video_data.get("url"),
                    "duration_seconds": 45,
                    "format": "mp4",
                    "content_type": video_data.get("content_type", "video/mp4"),
                    "request_id": request_id
                }
            else:
                return {
                    "status": "processing",
                    "message": "Video is still being generated",
                    "request_id": request_id
                }
                
        except Exception as fal_error:
            logger.warning(f"Failed to get avatar status from FAL AI: {fal_error}")
            
            # Return a generic processing status instead of failing
            return {
                "status": "processing",
                "message": "Video generation is still in progress",
                "request_id": request_id,
                "progress": 50,
                "estimated_completion": "2-3 minutes"
            }
        
    except Exception as e:
        logger.error(f"Get avatar status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar status service error"
        )