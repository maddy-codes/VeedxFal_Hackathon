"""
Data synchronization-related Pydantic models.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SyncRequest(BaseModel):
    """Data synchronization request model."""
    full_sync: bool = Field(default=False, description="Whether to perform full sync or incremental")
    sync_products: bool = Field(default=True, description="Whether to sync products")
    sync_sales: bool = Field(default=True, description="Whether to sync sales data")


class SyncStatus(BaseModel):
    """Synchronization status model."""
    sync_id: str = Field(..., description="Unique sync job ID")
    status: str = Field(..., description="Sync status")
    started_at: datetime = Field(..., description="Sync start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Sync completion timestamp")
    progress: int = Field(..., ge=0, le=100, description="Sync progress percentage")
    current_step: str = Field(..., description="Current sync step")
    total_steps: int = Field(..., description="Total number of sync steps")
    results: Optional[Dict] = Field(default=None, description="Sync results")
    errors: List[str] = Field(default_factory=list, description="Sync errors")
    
    @property
    def is_running(self) -> bool:
        """Check if sync is currently running."""
        return self.status in ["running", "pending"]
    
    @property
    def is_completed(self) -> bool:
        """Check if sync is completed."""
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if sync failed."""
        return self.status == "failed"


class ShopifyProduct(BaseModel):
    """Shopify product model for sync."""
    id: int = Field(..., description="Shopify product ID")
    title: str = Field(..., description="Product title")
    handle: str = Field(..., description="Product handle")
    product_type: Optional[str] = Field(default=None, description="Product type")
    vendor: Optional[str] = Field(default=None, description="Product vendor")
    status: str = Field(..., description="Product status")
    variants: List["ShopifyVariant"] = Field(..., description="Product variants")
    images: List[Dict] = Field(default_factory=list, description="Product images")
    created_at: datetime = Field(..., description="Product creation timestamp")
    updated_at: datetime = Field(..., description="Product update timestamp")


class ShopifyVariant(BaseModel):
    """Shopify product variant model for sync."""
    id: int = Field(..., description="Variant ID")
    product_id: int = Field(..., description="Product ID")
    title: str = Field(..., description="Variant title")
    sku: Optional[str] = Field(default=None, description="Variant SKU")
    price: str = Field(..., description="Variant price")
    inventory_quantity: int = Field(..., description="Inventory quantity")
    inventory_item_id: int = Field(..., description="Inventory item ID")
    weight: Optional[float] = Field(default=None, description="Variant weight")
    created_at: datetime = Field(..., description="Variant creation timestamp")
    updated_at: datetime = Field(..., description="Variant update timestamp")


class ShopifyOrder(BaseModel):
    """Shopify order model for sync."""
    id: int = Field(..., description="Order ID")
    order_number: int = Field(..., description="Order number")
    email: Optional[str] = Field(default=None, description="Customer email")
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime = Field(..., description="Order update timestamp")
    total_price: str = Field(..., description="Total order price")
    subtotal_price: str = Field(..., description="Subtotal price")
    total_tax: str = Field(..., description="Total tax")
    currency: str = Field(..., description="Order currency")
    financial_status: str = Field(..., description="Financial status")
    fulfillment_status: Optional[str] = Field(default=None, description="Fulfillment status")
    line_items: List["ShopifyLineItem"] = Field(..., description="Order line items")


class ShopifyLineItem(BaseModel):
    """Shopify order line item model for sync."""
    id: int = Field(..., description="Line item ID")
    variant_id: Optional[int] = Field(default=None, description="Product variant ID")
    product_id: Optional[int] = Field(default=None, description="Product ID")
    title: str = Field(..., description="Product title")
    variant_title: Optional[str] = Field(default=None, description="Variant title")
    sku: Optional[str] = Field(default=None, description="Product SKU")
    quantity: int = Field(..., description="Quantity ordered")
    price: str = Field(..., description="Unit price")
    total_discount: str = Field(..., description="Total discount")


class SyncResult(BaseModel):
    """Synchronization result model."""
    sync_type: str = Field(..., description="Type of sync performed")
    started_at: datetime = Field(..., description="Sync start timestamp")
    completed_at: datetime = Field(..., description="Sync completion timestamp")
    duration_seconds: float = Field(..., description="Sync duration in seconds")
    products_processed: int = Field(default=0, description="Number of products processed")
    products_created: int = Field(default=0, description="Number of products created")
    products_updated: int = Field(default=0, description="Number of products updated")
    sales_processed: int = Field(default=0, description="Number of sales records processed")
    sales_created: int = Field(default=0, description="Number of sales records created")
    errors: List[str] = Field(default_factory=list, description="Sync errors")
    warnings: List[str] = Field(default_factory=list, description="Sync warnings")


class CompetitorPricesSyncResult(BaseModel):
    """Competitor prices sync result model."""
    updated_count: int = Field(..., description="Number of products with updated prices")
    failed_count: int = Field(..., description="Number of failed price updates")
    errors: List[str] = Field(default_factory=list, description="Sync errors")
    total_competitors_found: int = Field(..., description="Total competitors found")
    average_price_difference: Optional[float] = Field(default=None, description="Average price difference")


class TrendsSyncResult(BaseModel):
    """Trends sync result model."""
    updated_count: int = Field(..., description="Number of products with updated trends")
    failed_count: int = Field(..., description="Number of failed trend updates")
    errors: List[str] = Field(default_factory=list, description="Sync errors")
    hot_products: int = Field(default=0, description="Number of hot trending products")
    rising_products: int = Field(default=0, description="Number of rising products")
    declining_products: int = Field(default=0, description="Number of declining products")


class PipelineStatus(BaseModel):
    """Data pipeline status model."""
    pipeline_id: str = Field(..., description="Pipeline job ID")
    shop_id: int = Field(..., description="Store ID")
    status: str = Field(..., description="Pipeline status")
    started_at: datetime = Field(..., description="Pipeline start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Pipeline completion timestamp")
    current_step: str = Field(..., description="Current pipeline step")
    steps_completed: int = Field(..., description="Number of completed steps")
    total_steps: int = Field(..., description="Total number of steps")
    results: Dict = Field(default_factory=dict, description="Pipeline results")
    errors: List[str] = Field(default_factory=list, description="Pipeline errors")


class WebhookPayload(BaseModel):
    """Shopify webhook payload model."""
    webhook_type: str = Field(..., description="Type of webhook")
    shop_domain: str = Field(..., description="Shop domain")
    data: Dict = Field(..., description="Webhook data")
    received_at: datetime = Field(default_factory=datetime.utcnow, description="Webhook received timestamp")


# Update forward references
ShopifyProduct.model_rebuild()
ShopifyOrder.model_rebuild()