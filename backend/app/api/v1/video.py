"""
Video generation API endpoints.
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.deps import get_current_user_id, get_db_manager_dep, verify_store_access
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
            job_id, shop_id, user_id, status, request_data, created_at
        )
        VALUES (:job_id, :shop_id, :user_id, 'pending', :request_data, NOW())
        """
        
        await db_manager.execute_query(insert_query, {
            "job_id": job_id,
            "shop_id": shop_id,
            "user_id": user_id,
            "request_data": video_request.dict(),
        })
        
        # TODO: Trigger background video generation job
        # This would typically use Celery or Azure Functions to:
        # 1. Get business insights
        # 2. Generate script with Azure OpenAI
        # 3. Generate audio with ElevenLabs
        # 4. Create video with fal.ai models
        
        # Log video generation request
        log_business_event(
            "video_generation_requested",
            user_id=user_id,
            shop_id=shop_id,
            job_id=job_id,
            insights_limit=video_request.insights_limit
        )
        
        return VideoGenerationResponse(
            job_id=job_id,
            status="pending",
            estimated_completion=datetime.utcnow().replace(microsecond=0),
            message="Video generation started. Check status for updates.",
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
        # Get job status
        query = """
        SELECT 
            vj.job_id,
            vj.shop_id,
            vj.status,
            vj.started_at,
            vj.completed_at,
            vj.current_step,
            vj.progress,
            vj.error_message,
            gv.video_url,
            vs.script_content,
            vs.estimated_duration
        FROM video_jobs vj
        LEFT JOIN generated_videos gv ON vj.job_id = gv.job_id
        LEFT JOIN video_scripts vs ON vj.job_id = vs.job_id
        WHERE vj.job_id = :job_id
        AND vj.user_id = :user_id
        """
        
        result = await db_manager.fetch_one(query, {
            "job_id": job_id,
            "user_id": user_id
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video generation job not found"
            )
        
        # Calculate progress based on status
        progress_map = {
            "pending": 0,
            "generating_insights": 20,
            "generating_script": 40,
            "generating_audio": 60,
            "generating_video": 80,
            "completed": 100,
            "failed": 0,
        }
        
        progress = progress_map.get(result["status"], 0)
        
        return VideoStatus(
            job_id=result["job_id"],
            status=result["status"],
            progress=progress,
            current_step=result["current_step"] or result["status"].replace("_", " ").title(),
            started_at=result["started_at"] or datetime.utcnow(),
            completed_at=result["completed_at"],
            video_url=result["video_url"],
            script=result["script_content"],
            duration_seconds=result["estimated_duration"],
            error_message=result["error_message"],
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
    response_model=VideoListResponse,
    responses={
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
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Get latest generated videos."""
    
    try:
        # Count total videos
        count_query = """
        SELECT COUNT(*) as total
        FROM generated_videos gv
        JOIN video_jobs vj ON gv.job_id = vj.job_id
        WHERE vj.shop_id = :shop_id
        """
        
        total_result = await db_manager.fetch_one(count_query, {"shop_id": shop_id})
        total = total_result["total"] if total_result else 0
        
        # Get videos with pagination
        offset = (page - 1) * limit
        
        videos_query = """
        SELECT 
            gv.video_id,
            gv.shop_id,
            gv.job_id,
            gv.video_url,
            gv.script_content,
            gv.audio_url,
            gv.duration_seconds,
            gv.file_size_bytes,
            gv.resolution,
            gv.format,
            gv.generated_at,
            gv.expires_at,
            gv.view_count,
            gv.metadata
        FROM generated_videos gv
        JOIN video_jobs vj ON gv.job_id = vj.job_id
        WHERE vj.shop_id = :shop_id
        ORDER BY gv.generated_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        videos_result = await db_manager.fetch_all(videos_query, {
            "shop_id": shop_id,
            "limit": limit,
            "offset": offset
        })
        
        videos = [
            GeneratedVideo(
                video_id=row["video_id"],
                shop_id=row["shop_id"],
                job_id=row["job_id"],
                video_url=row["video_url"],
                script_content=row["script_content"],
                audio_url=row["audio_url"],
                duration_seconds=row["duration_seconds"],
                file_size_bytes=row["file_size_bytes"],
                resolution=row["resolution"],
                format=row["format"],
                generated_at=row["generated_at"],
                expires_at=row["expires_at"],
                view_count=row["view_count"],
                metadata=row["metadata"] or {},
            )
            for row in videos_result
        ]
        
        # Log video access
        log_business_event(
            "videos_accessed",
            user_id=user_id,
            shop_id=shop_id,
            count=len(videos)
        )
        
        return VideoListResponse(
            videos=videos,
            total=total,
            page=page,
            limit=limit,
            has_next=(page * limit) < total,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get latest videos error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video service error"
        )


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
    user_id: str = Depends(get_current_user_id),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Generate AI avatar video with business summary."""
    
    try:
        # Initialize FAL AI service
        fal_service = FALAIService()
        
        # Generate avatar video
        avatar_result = await fal_service.generate_business_avatar_video(
            shop_id=shop_id,
            avatar_id=avatar_id,
            include_business_context=include_business_context
        )
        
        # Log avatar generation request
        log_business_event(
            "avatar_video_generated",
            user_id=user_id,
            shop_id=shop_id,
            avatar_id=avatar_id,
            include_business_context=include_business_context
        )
        
        return {
            "status": "success",
            "message": "Avatar video generated successfully",
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
async def get_available_avatars(
    user_id: str = Depends(get_current_user_id),
):
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
        # Initialize FAL AI service
        fal_service = FALAIService()
        
        # Perform health check
        health_result = await fal_service.health_check()
        
        return {
            "status": "success",
            "message": "Avatar service health check completed",
            "data": health_result
        }
        
    except Exception as e:
        logger.error(f"Avatar health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar health check service error"
        )