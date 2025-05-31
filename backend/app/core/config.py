"""
Application configuration management using Pydantic settings.
"""

import os
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment Configuration
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="WARNING", description="Logging level")
    
    # Security
    SECRET_KEY: str = Field(..., description="Application secret key")
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRE_MINUTES: int = Field(default=60, description="JWT expiration in minutes")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., description="Database connection URL")
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anonymous key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase service role key")
    
    # Azure Configuration
    AZURE_KEY_VAULT_URL: Optional[str] = Field(default=None, description="Azure Key Vault URL")
    AZURE_CLIENT_ID: Optional[str] = Field(default=None, description="Azure client ID")
    AZURE_CLIENT_SECRET: Optional[str] = Field(default=None, description="Azure client secret")
    AZURE_TENANT_ID: Optional[str] = Field(default=None, description="Azure tenant ID")
    
    # External API Keys
    SHOPIFY_CLIENT_ID: Optional[str] = Field(default=None, description="Shopify client ID")
    SHOPIFY_CLIENT_SECRET: Optional[str] = Field(default=None, description="Shopify client secret")
    ZENROWS_API_KEY: Optional[str] = Field(default=None, description="ZenRows API key")
    APIDECK_API_KEY: Optional[str] = Field(default=None, description="API Deck API key")
    AZURE_OPENAI_API_KEY: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, description="ElevenLabs API key")
    FAL_KEY: Optional[str] = Field(default=None, description="fal.ai API key for video generation")
    # VEED_API_KEY: Optional[str] = Field(default=None, description="VEED.io API key - replaced by fal.ai")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit requests per minute"
    )
    RATE_LIMIT_BURST: int = Field(default=10, description="Rate limit burst capacity")
    
    # Background Jobs
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL"
    )
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    PROMETHEUS_PORT: int = Field(default=8001, description="Prometheus metrics port")
    
    # Shopify Configuration
    SHOPIFY_API_VERSION: str = Field(default="2024-07", description="Shopify API version")
    SHOPIFY_SCOPES: List[str] = Field(
        default=["read_products", "read_inventory", "read_orders", "read_price_rules"],
        description="Shopify OAuth scopes"
    )
    
    # Video Generation Settings
    DEFAULT_VOICE_ID: str = Field(
        default="21m00Tcm4TlvDq8ikWAM",
        description="Default ElevenLabs voice ID"
    )
    VIDEO_TEMPLATE: str = Field(default="business", description="Default video template")
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Max upload size in bytes (10MB)")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".csv", ".xlsx", ".xls"],
        description="Allowed file types for upload"
    )
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("SHOPIFY_SCOPES", mode="before")
    @classmethod
    def parse_shopify_scopes(cls, v):
        """Parse Shopify scopes from string or list."""
        if isinstance(v, str):
            return [scope.strip() for scope in v.split(",")]
        return v
    
    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @property
    def shopify_scope_string(self) -> str:
        """Get Shopify scopes as comma-separated string."""
        return ",".join(self.SHOPIFY_SCOPES)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings