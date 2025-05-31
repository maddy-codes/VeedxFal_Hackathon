"""
Product-related Pydantic models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ProductBase(BaseModel):
    """Base product model."""
    sku_code: str = Field(..., pattern=r"^[A-Za-z0-9\-_]+$", description="Product SKU code")
    product_title: str = Field(..., min_length=1, max_length=500, description="Product title")
    variant_title: Optional[str] = Field(default=None, description="Product variant title")
    current_price: Decimal = Field(..., ge=0, description="Current product price")
    inventory_level: int = Field(..., ge=0, description="Current inventory level")
    cost_price: Optional[Decimal] = Field(default=None, ge=0, description="Product cost price")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    status: str = Field(default="active", description="Product status")
    
    @validator("status")
    def validate_status(cls, v):
        allowed_statuses = ["active", "archived", "draft"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v


class ProductCreate(ProductBase):
    """Product creation model."""
    shopify_product_id: Optional[int] = Field(default=None, description="Shopify product ID")


class ProductUpdate(BaseModel):
    """Product update model."""
    product_title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    variant_title: Optional[str] = Field(default=None)
    current_price: Optional[Decimal] = Field(default=None, ge=0)
    inventory_level: Optional[int] = Field(default=None, ge=0)
    cost_price: Optional[Decimal] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    
    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["active", "archived", "draft"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v


class Product(ProductBase):
    """Complete product model."""
    sku_id: int = Field(..., description="Product SKU ID")
    shop_id: int = Field(..., description="Store ID")
    shopify_product_id: Optional[int] = Field(default=None, description="Shopify product ID")
    created_at: datetime = Field(..., description="Product creation timestamp")
    updated_at: datetime = Field(..., description="Product last update timestamp")


class CompetitorPrice(BaseModel):
    """Competitor price model."""
    id: int = Field(..., description="Competitor price ID")
    shop_id: int = Field(..., description="Store ID")
    sku_code: str = Field(..., description="Product SKU code")
    min_price: Optional[Decimal] = Field(default=None, description="Minimum competitor price")
    max_price: Optional[Decimal] = Field(default=None, description="Maximum competitor price")
    competitor_count: int = Field(..., description="Number of competitors found")
    price_details: Dict = Field(..., description="Detailed competitor price information")
    scraped_at: datetime = Field(..., description="Price scraping timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")


class TrendInsight(BaseModel):
    """Trend insight model."""
    id: int = Field(..., description="Trend insight ID")
    shop_id: int = Field(..., description="Store ID")
    sku_code: str = Field(..., description="Product SKU code")
    google_trend_index: int = Field(..., ge=0, le=100, description="Google Trends index")
    social_score: int = Field(..., ge=0, le=100, description="Social media score")
    final_score: Decimal = Field(..., ge=0, le=100, description="Final trend score")
    label: str = Field(..., description="Trend label")
    trend_details: Dict = Field(..., description="Detailed trend information")
    computed_at: datetime = Field(..., description="Trend computation timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")
    
    @validator("label")
    def validate_label(cls, v):
        allowed_labels = ["Hot", "Rising", "Steady", "Declining"]
        if v not in allowed_labels:
            raise ValueError(f"Label must be one of: {allowed_labels}")
        return v


class RecommendedPrice(BaseModel):
    """Recommended price model."""
    id: int = Field(..., description="Recommendation ID")
    shop_id: int = Field(..., description="Store ID")
    sku_code: str = Field(..., description="Product SKU code")
    recommended_price: Decimal = Field(..., ge=0, description="Recommended price")
    pricing_reason: str = Field(..., min_length=10, max_length=500, description="Pricing reason")
    recommendation_type: str = Field(..., description="Recommendation type")
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Confidence score")
    calculation_details: Dict = Field(..., description="Calculation details")
    calculated_at: datetime = Field(..., description="Calculation timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")
    
    @validator("recommendation_type")
    def validate_recommendation_type(cls, v):
        allowed_types = ["underpriced", "overpriced", "competitive", "trending", "standard"]
        if v not in allowed_types:
            raise ValueError(f"Recommendation type must be one of: {allowed_types}")
        return v


class ProductDetail(Product):
    """Detailed product model with related data."""
    competitor_min_price: Optional[Decimal] = Field(default=None, description="Minimum competitor price")
    competitor_max_price: Optional[Decimal] = Field(default=None, description="Maximum competitor price")
    competitor_count: Optional[int] = Field(default=None, description="Number of competitors")
    google_trend_index: Optional[int] = Field(default=None, description="Google Trends index")
    social_score: Optional[int] = Field(default=None, description="Social media score")
    trend_score: Optional[Decimal] = Field(default=None, description="Final trend score")
    trend_label: Optional[str] = Field(default=None, description="Trend label")
    recommended_price: Optional[Decimal] = Field(default=None, description="Recommended price")
    pricing_reason: Optional[str] = Field(default=None, description="Pricing reason")
    recommendation_type: Optional[str] = Field(default=None, description="Recommendation type")
    confidence_score: Optional[Decimal] = Field(default=None, description="Confidence score")
    current_margin_percent: Optional[Decimal] = Field(default=None, description="Current margin percentage")
    recommended_margin_percent: Optional[Decimal] = Field(default=None, description="Recommended margin percentage")


class ProductListResponse(BaseModel):
    """Product list response model."""
    products: List[ProductDetail] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class ProductFilters(BaseModel):
    """Product filtering options."""
    search: Optional[str] = Field(default=None, description="Search term")
    status: Optional[str] = Field(default=None, description="Product status filter")
    trend_label: Optional[str] = Field(default=None, description="Trend label filter")
    recommendation_type: Optional[str] = Field(default=None, description="Recommendation type filter")
    min_price: Optional[Decimal] = Field(default=None, ge=0, description="Minimum price filter")
    max_price: Optional[Decimal] = Field(default=None, ge=0, description="Maximum price filter")
    
    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["active", "archived", "draft"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v
    
    @validator("trend_label")
    def validate_trend_label(cls, v):
        if v is not None:
            allowed_labels = ["Hot", "Rising", "Steady", "Declining"]
            if v not in allowed_labels:
                raise ValueError(f"Trend label must be one of: {allowed_labels}")
        return v
    
    @validator("recommendation_type")
    def validate_recommendation_type(cls, v):
        if v is not None:
            allowed_types = ["underpriced", "overpriced", "competitive", "trending", "standard"]
            if v not in allowed_types:
                raise ValueError(f"Recommendation type must be one of: {allowed_types}")
        return v


class CompetitorPriceUpdate(BaseModel):
    """Competitor price update model."""
    sku_code: str = Field(..., description="Product SKU code")
    min_price: Optional[Decimal] = Field(default=None, ge=0, description="Minimum competitor price")
    max_price: Optional[Decimal] = Field(default=None, ge=0, description="Maximum competitor price")
    competitor_count: int = Field(..., ge=0, description="Number of competitors")
    price_details: Dict = Field(..., description="Detailed price information")


class TrendUpdate(BaseModel):
    """Trend update model."""
    sku_code: str = Field(..., description="Product SKU code")
    google_trend_index: int = Field(..., ge=0, le=100, description="Google Trends index")
    social_score: int = Field(..., ge=0, le=100, description="Social media score")
    final_score: Decimal = Field(..., ge=0, le=100, description="Final trend score")
    label: str = Field(..., description="Trend label")
    trend_details: Dict = Field(..., description="Detailed trend information")
    
    @validator("label")
    def validate_label(cls, v):
        allowed_labels = ["Hot", "Rising", "Steady", "Declining"]
        if v not in allowed_labels:
            raise ValueError(f"Label must be one of: {allowed_labels}")
        return v