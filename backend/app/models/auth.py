"""
Authentication-related Pydantic models.
"""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class LoginResponse(BaseModel):
    """User login response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "User" = Field(..., description="User information")


class RefreshTokenResponse(BaseModel):
    """Token refresh response model."""
    access_token: str = Field(..., description="New JWT access token")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class User(BaseModel):
    """User model."""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    user_metadata: Optional[Dict] = Field(default=None, description="User metadata")
    app_metadata: Optional[Dict] = Field(default=None, description="App metadata")
    created_at: Optional[datetime] = Field(default=None, description="User creation timestamp")


class TokenPayload(BaseModel):
    """JWT token payload model."""
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    type: str = Field(..., description="Token type")
    exp: datetime = Field(..., description="Expiration timestamp")


class ShopifyConnectRequest(BaseModel):
    """Shopify store connection request model."""
    shop_domain: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]*\.myshopify\.com$",
        description="Shopify store domain"
    )
    code: str = Field(..., description="OAuth authorization code from Shopify")


class Store(BaseModel):
    """Store model."""
    id: int = Field(..., description="Store ID")
    shop_domain: str = Field(..., description="Shopify store domain")
    shop_name: str = Field(..., description="Store name")
    is_active: bool = Field(..., description="Store active status")
    shop_config: Optional[Dict] = Field(default=None, description="Store configuration")
    created_at: datetime = Field(..., description="Store creation timestamp")
    updated_at: datetime = Field(..., description="Store last update timestamp")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


# Update forward references
LoginResponse.model_rebuild()