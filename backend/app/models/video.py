"""
Video generation-related Pydantic models.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class VideoGenerationRequest(BaseModel):
    """Video generation request model."""
    insights_limit: int = Field(default=5, ge=1, le=10, description="Number of insights to include")
    voice_id: Optional[str] = Field(default=None, description="ElevenLabs voice ID")
    template: Optional[str] = Field(default="business", description="Video template")
    custom_message: Optional[str] = Field(default=None, description="Custom message to include")


class VideoGenerationResponse(BaseModel):
    """Video generation response model."""
    job_id: str = Field(..., description="Video generation job ID")
    status: str = Field(..., description="Generation status")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    message: str = Field(..., description="Status message")


class VideoStatus(BaseModel):
    """Video generation status model."""
    job_id: str = Field(..., description="Video generation job ID")
    status: str = Field(..., description="Generation status")
    progress: int = Field(..., ge=0, le=100, description="Generation progress percentage")
    current_step: str = Field(..., description="Current generation step")
    started_at: datetime = Field(..., description="Generation start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Generation completion timestamp")
    video_url: Optional[str] = Field(default=None, description="Generated video URL")
    script: Optional[str] = Field(default=None, description="Generated script")
    audio_url: Optional[str] = Field(default=None, description="Generated audio URL")
    duration_seconds: Optional[float] = Field(default=None, description="Video duration in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata")


class VideoScript(BaseModel):
    """Video script model."""
    script_id: str = Field(..., description="Script ID")
    shop_id: int = Field(..., description="Store ID")
    script_content: str = Field(..., description="Script content")
    insights_used: List[Dict] = Field(..., description="Insights used in script")
    generated_at: datetime = Field(..., description="Script generation timestamp")
    word_count: int = Field(..., description="Script word count")
    estimated_duration: float = Field(..., description="Estimated reading duration in seconds")


class GeneratedVideo(BaseModel):
    """Generated video model."""
    video_id: str = Field(..., description="Video ID")
    shop_id: int = Field(..., description="Store ID")
    job_id: str = Field(..., description="Generation job ID")
    video_url: str = Field(..., description="Video URL")
    script_content: str = Field(..., description="Script content")
    audio_url: Optional[str] = Field(default=None, description="Audio URL")
    duration_seconds: float = Field(..., description="Video duration in seconds")
    file_size_bytes: Optional[int] = Field(default=None, description="Video file size in bytes")
    resolution: Optional[str] = Field(default=None, description="Video resolution")
    format: str = Field(default="mp4", description="Video format")
    generated_at: datetime = Field(..., description="Video generation timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Video expiration timestamp")
    view_count: int = Field(default=0, description="Number of views")
    metadata: Dict = Field(default_factory=dict, description="Video metadata")


class VideoListResponse(BaseModel):
    """Video list response model."""
    videos: List[GeneratedVideo] = Field(..., description="List of generated videos")
    total: int = Field(..., description="Total number of videos")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class VideoGenerationStep(BaseModel):
    """Video generation step model."""
    step_name: str = Field(..., description="Step name")
    status: str = Field(..., description="Step status")
    started_at: Optional[datetime] = Field(default=None, description="Step start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Step completion timestamp")
    duration_seconds: Optional[float] = Field(default=None, description="Step duration")
    output: Optional[Dict] = Field(default=None, description="Step output")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class VideoGenerationJob(BaseModel):
    """Complete video generation job model."""
    job_id: str = Field(..., description="Job ID")
    shop_id: int = Field(..., description="Store ID")
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Job status")
    request_data: VideoGenerationRequest = Field(..., description="Original request data")
    steps: List[VideoGenerationStep] = Field(..., description="Generation steps")
    script: Optional[VideoScript] = Field(default=None, description="Generated script")
    video: Optional[GeneratedVideo] = Field(default=None, description="Generated video")
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion timestamp")
    total_duration_seconds: Optional[float] = Field(default=None, description="Total job duration")
    retry_count: int = Field(default=0, description="Number of retries")
    max_retries: int = Field(default=3, description="Maximum number of retries")


class VideoAnalytics(BaseModel):
    """Video analytics model."""
    total_videos: int = Field(..., description="Total number of videos generated")
    videos_this_month: int = Field(..., description="Videos generated this month")
    total_views: int = Field(..., description="Total video views")
    avg_duration: float = Field(..., description="Average video duration")
    success_rate: float = Field(..., description="Generation success rate")
    avg_generation_time: float = Field(..., description="Average generation time in seconds")
    most_popular_template: str = Field(..., description="Most popular video template")
    total_script_words: int = Field(..., description="Total words in all scripts")


class VideoTemplate(BaseModel):
    """Video template model."""
    template_id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    settings: Dict = Field(..., description="Template settings")
    preview_url: Optional[str] = Field(default=None, description="Template preview URL")
    is_active: bool = Field(default=True, description="Template active status")
    created_at: datetime = Field(..., description="Template creation timestamp")


class VoiceOption(BaseModel):
    """Voice option model for TTS."""
    voice_id: str = Field(..., description="Voice ID")
    name: str = Field(..., description="Voice name")
    gender: str = Field(..., description="Voice gender")
    accent: str = Field(..., description="Voice accent")
    language: str = Field(..., description="Voice language")
    sample_url: Optional[str] = Field(default=None, description="Voice sample URL")
    is_premium: bool = Field(default=False, description="Premium voice flag")


class VideoSettings(BaseModel):
    """Video generation settings model."""
    resolution: str = Field(default="1080p", description="Video resolution")
    format: str = Field(default="mp4", description="Video format")
    quality: str = Field(default="high", description="Video quality")
    background_color: str = Field(default="#427F8C", description="Background color")
    text_color: str = Field(default="#FFFFFF", description="Text color")
    font_family: str = Field(default="Arial", description="Font family")
    font_size: int = Field(default=24, description="Font size")
    logo_url: Optional[str] = Field(default=None, description="Logo URL")
    watermark: bool = Field(default=False, description="Include watermark")
    transitions: bool = Field(default=True, description="Include transitions")
    background_music: bool = Field(default=False, description="Include background music")


class VideoError(BaseModel):
    """Video generation error model."""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    step: str = Field(..., description="Step where error occurred")
    timestamp: datetime = Field(..., description="Error timestamp")
    details: Optional[Dict] = Field(default=None, description="Additional error details")
    is_retryable: bool = Field(..., description="Whether error is retryable")