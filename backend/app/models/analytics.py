"""
Analytics-related Pydantic models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DashboardAnalytics(BaseModel):
    """Dashboard analytics model."""
    total_products: int = Field(..., description="Total number of products")
    active_products: int = Field(..., description="Number of active products")
    total_revenue: Decimal = Field(..., description="Total revenue")
    revenue_last_30d: Decimal = Field(..., description="Revenue in last 30 days")
    revenue_change_percent: Optional[Decimal] = Field(default=None, description="Revenue change percentage")
    avg_order_value: Decimal = Field(..., description="Average order value")
    total_orders: int = Field(..., description="Total number of orders")
    orders_last_30d: int = Field(..., description="Orders in last 30 days")
    orders_change_percent: Optional[Decimal] = Field(default=None, description="Orders change percentage")
    top_selling_products: List["TopProduct"] = Field(..., description="Top selling products")
    trending_products: List["TrendingProduct"] = Field(..., description="Trending products")
    pricing_opportunities: List["PricingOpportunity"] = Field(..., description="Pricing opportunities")
    inventory_alerts: List["InventoryAlert"] = Field(..., description="Inventory alerts")
    last_sync_at: Optional[datetime] = Field(default=None, description="Last sync timestamp")
    sync_status: str = Field(..., description="Current sync status")


class TopProduct(BaseModel):
    """Top selling product model."""
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title")
    total_revenue: Decimal = Field(..., description="Total revenue")
    total_quantity: int = Field(..., description="Total quantity sold")
    avg_price: Decimal = Field(..., description="Average selling price")
    image_url: Optional[str] = Field(default=None, description="Product image URL")


class TrendingProduct(BaseModel):
    """Trending product model."""
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title")
    trend_label: str = Field(..., description="Trend label")
    trend_score: Decimal = Field(..., description="Trend score")
    google_trend_index: int = Field(..., description="Google Trends index")
    social_score: int = Field(..., description="Social media score")
    current_price: Decimal = Field(..., description="Current price")
    image_url: Optional[str] = Field(default=None, description="Product image URL")


class PricingOpportunity(BaseModel):
    """Pricing opportunity model."""
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title")
    current_price: Decimal = Field(..., description="Current price")
    recommended_price: Decimal = Field(..., description="Recommended price")
    price_difference: Decimal = Field(..., description="Price difference")
    price_change_percent: Decimal = Field(..., description="Price change percentage")
    recommendation_type: str = Field(..., description="Recommendation type")
    confidence_score: Decimal = Field(..., description="Confidence score")
    potential_revenue_impact: Optional[Decimal] = Field(default=None, description="Potential revenue impact")
    reasoning: str = Field(..., description="Pricing reasoning")


class InventoryAlert(BaseModel):
    """Inventory alert model."""
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title")
    current_inventory: int = Field(..., description="Current inventory level")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    recommended_action: str = Field(..., description="Recommended action")


class BusinessInsight(BaseModel):
    """Business insight model for AI video generation."""
    insight_type: str = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact_level: str = Field(..., description="Impact level")
    priority: int = Field(..., ge=1, le=10, description="Insight priority")
    data: Dict = Field(..., description="Supporting data")
    recommendation: str = Field(..., description="Recommended action")
    potential_value: Optional[Decimal] = Field(default=None, description="Potential value impact")


class InsightsResponse(BaseModel):
    """Business insights response model."""
    insights: List[BusinessInsight] = Field(..., description="List of business insights")
    total_insights: int = Field(..., description="Total number of insights")
    generated_at: datetime = Field(..., description="Insights generation timestamp")
    shop_id: int = Field(..., description="Store ID")


class SalesAnalytics(BaseModel):
    """Sales analytics model."""
    period: str = Field(..., description="Analytics period")
    total_revenue: Decimal = Field(..., description="Total revenue")
    total_orders: int = Field(..., description="Total orders")
    total_quantity: int = Field(..., description="Total quantity sold")
    avg_order_value: Decimal = Field(..., description="Average order value")
    revenue_by_day: List["DailyRevenue"] = Field(..., description="Daily revenue breakdown")
    top_products: List[TopProduct] = Field(..., description="Top selling products")
    revenue_by_product: List["ProductRevenue"] = Field(..., description="Revenue by product")


class DailyRevenue(BaseModel):
    """Daily revenue model."""
    date: datetime = Field(..., description="Date")
    revenue: Decimal = Field(..., description="Revenue for the day")
    orders: int = Field(..., description="Number of orders")
    avg_order_value: Decimal = Field(..., description="Average order value")


class ProductRevenue(BaseModel):
    """Product revenue model."""
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title")
    revenue: Decimal = Field(..., description="Product revenue")
    quantity: int = Field(..., description="Quantity sold")
    avg_price: Decimal = Field(..., description="Average selling price")
    revenue_percent: Decimal = Field(..., description="Percentage of total revenue")


class TrendAnalytics(BaseModel):
    """Trend analytics model."""
    hot_products: int = Field(..., description="Number of hot products")
    rising_products: int = Field(..., description="Number of rising products")
    steady_products: int = Field(..., description="Number of steady products")
    declining_products: int = Field(..., description="Number of declining products")
    avg_trend_score: Decimal = Field(..., description="Average trend score")
    trend_distribution: List["TrendDistribution"] = Field(..., description="Trend distribution")
    top_trending: List[TrendingProduct] = Field(..., description="Top trending products")


class TrendDistribution(BaseModel):
    """Trend distribution model."""
    trend_label: str = Field(..., description="Trend label")
    count: int = Field(..., description="Number of products")
    percentage: Decimal = Field(..., description="Percentage of total products")


class CompetitorAnalytics(BaseModel):
    """Competitor analytics model."""
    products_with_competitor_data: int = Field(..., description="Products with competitor data")
    avg_competitor_count: Decimal = Field(..., description="Average number of competitors per product")
    underpriced_products: int = Field(..., description="Number of underpriced products")
    overpriced_products: int = Field(..., description="Number of overpriced products")
    competitive_products: int = Field(..., description="Number of competitively priced products")
    avg_price_difference: Decimal = Field(..., description="Average price difference vs competitors")
    price_comparison: List["PriceComparison"] = Field(..., description="Price comparison data")


class PriceComparison(BaseModel):
    """Price comparison model."""
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title")
    current_price: Decimal = Field(..., description="Current price")
    competitor_min: Optional[Decimal] = Field(default=None, description="Minimum competitor price")
    competitor_max: Optional[Decimal] = Field(default=None, description="Maximum competitor price")
    competitor_avg: Optional[Decimal] = Field(default=None, description="Average competitor price")
    price_position: str = Field(..., description="Price position vs competitors")
    competitor_count: int = Field(..., description="Number of competitors")


class PerformanceMetrics(BaseModel):
    """Performance metrics model."""
    metric_name: str = Field(..., description="Metric name")
    value: Decimal = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    timestamp: datetime = Field(..., description="Metric timestamp")
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata")


class AnalyticsFilters(BaseModel):
    """Analytics filtering options."""
    start_date: Optional[datetime] = Field(default=None, description="Start date filter")
    end_date: Optional[datetime] = Field(default=None, description="End date filter")
    product_status: Optional[str] = Field(default=None, description="Product status filter")
    trend_label: Optional[str] = Field(default=None, description="Trend label filter")
    recommendation_type: Optional[str] = Field(default=None, description="Recommendation type filter")
    min_revenue: Optional[Decimal] = Field(default=None, description="Minimum revenue filter")
    max_revenue: Optional[Decimal] = Field(default=None, description="Maximum revenue filter")


# Rebuild models to resolve forward references
DashboardAnalytics.model_rebuild()
SalesAnalytics.model_rebuild()
TrendAnalytics.model_rebuild()
CompetitorAnalytics.model_rebuild()