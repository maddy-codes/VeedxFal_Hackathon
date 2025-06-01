"""
Shopify-specific Pydantic models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field, validator


class ShopifyWebhookEventType(str, Enum):
    """Shopify webhook event types."""
    ORDERS_CREATE = "orders/create"
    ORDERS_UPDATE = "orders/update"
    ORDERS_PAID = "orders/paid"
    ORDERS_CANCELLED = "orders/cancelled"
    PRODUCTS_CREATE = "products/create"
    PRODUCTS_UPDATE = "products/update"
    PRODUCTS_DELETE = "products/delete"
    INVENTORY_LEVELS_UPDATE = "inventory_levels/update"
    APP_UNINSTALLED = "app/uninstalled"


class ShopifySyncStatus(str, Enum):
    """Shopify sync job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ShopifySyncType(str, Enum):
    """Shopify sync operation types."""
    FULL_SYNC = "full_sync"
    INCREMENTAL_SYNC = "incremental_sync"
    PRODUCT_SYNC = "product_sync"
    ORDER_SYNC = "order_sync"
    INVENTORY_SYNC = "inventory_sync"


class ShopifyStoreBase(BaseModel):
    """Base Shopify store model."""
    shop_domain: str = Field(..., description="Shopify store domain")
    shop_name: str = Field(..., description="Store name")
    access_token: str = Field(..., description="Shopify access token")
    scope: str = Field(..., description="OAuth scopes granted")
    is_active: bool = Field(default=True, description="Store active status")


class ShopifyStoreCreate(ShopifyStoreBase):
    """Shopify store creation model."""
    user_id: str = Field(..., description="User ID who owns the store")
    shop_id: Optional[int] = Field(default=None, description="Shopify shop ID")
    shop_config: Optional[Dict[str, Any]] = Field(default=None, description="Additional shop configuration")


class ShopifyStoreUpdate(BaseModel):
    """Shopify store update model."""
    shop_name: Optional[str] = Field(default=None, description="Store name")
    access_token: Optional[str] = Field(default=None, description="Shopify access token")
    scope: Optional[str] = Field(default=None, description="OAuth scopes granted")
    is_active: Optional[bool] = Field(default=None, description="Store active status")
    shop_config: Optional[Dict[str, Any]] = Field(default=None, description="Additional shop configuration")


class ShopifyStore(ShopifyStoreBase):
    """Complete Shopify store model."""
    id: int = Field(..., description="Store ID")
    user_id: str = Field(..., description="User ID who owns the store")
    shop_id: Optional[int] = Field(default=None, description="Shopify shop ID")
    shop_config: Optional[Dict[str, Any]] = Field(default=None, description="Additional shop configuration")
    last_sync_at: Optional[datetime] = Field(default=None, description="Last sync timestamp")
    created_at: datetime = Field(..., description="Store creation timestamp")
    updated_at: datetime = Field(..., description="Store last update timestamp")


class ShopifyProductBase(BaseModel):
    """Base Shopify product model extending existing product."""
    shopify_product_id: int = Field(..., description="Shopify product ID")
    shopify_variant_id: Optional[int] = Field(default=None, description="Shopify variant ID")
    handle: str = Field(..., description="Shopify product handle")
    product_type: Optional[str] = Field(default=None, description="Product type")
    vendor: Optional[str] = Field(default=None, description="Product vendor")
    tags: Optional[str] = Field(default=None, description="Product tags")
    published_at: Optional[datetime] = Field(default=None, description="Product publish timestamp")
    shopify_created_at: Optional[datetime] = Field(default=None, description="Shopify creation timestamp")
    shopify_updated_at: Optional[datetime] = Field(default=None, description="Shopify update timestamp")


class ShopifyProductCreate(ShopifyProductBase):
    """Shopify product creation model."""
    shop_id: int = Field(..., description="Store ID")
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title")
    variant_title: Optional[str] = Field(default=None, description="Product variant title")
    current_price: Decimal = Field(..., ge=0, description="Current product price")
    inventory_level: int = Field(..., ge=0, description="Current inventory level")
    cost_price: Optional[Decimal] = Field(default=None, ge=0, description="Product cost price")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    status: str = Field(default="active", description="Product status")


class ShopifyProduct(ShopifyProductBase):
    """Complete Shopify product model."""
    id: int = Field(..., description="Internal product ID")
    shop_id: int = Field(..., description="Store ID")
    sku_id: int = Field(..., description="Product SKU ID")
    created_at: datetime = Field(..., description="Product creation timestamp")
    updated_at: datetime = Field(..., description="Product last update timestamp")


class ShopifyWebhookEventBase(BaseModel):
    """Base webhook event model."""
    event_type: ShopifyWebhookEventType = Field(..., description="Webhook event type")
    shopify_id: str = Field(..., description="Shopify resource ID")
    event_data: Dict[str, Any] = Field(..., description="Webhook payload data")
    processed: bool = Field(default=False, description="Whether event has been processed")


class ShopifyWebhookEventCreate(ShopifyWebhookEventBase):
    """Webhook event creation model."""
    shop_id: int = Field(..., description="Store ID")
    webhook_id: Optional[str] = Field(default=None, description="Shopify webhook ID")


class ShopifyWebhookEvent(ShopifyWebhookEventBase):
    """Complete webhook event model."""
    id: int = Field(..., description="Event ID")
    shop_id: int = Field(..., description="Store ID")
    webhook_id: Optional[str] = Field(default=None, description="Shopify webhook ID")
    processed_at: Optional[datetime] = Field(default=None, description="Processing timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")
    retry_count: int = Field(default=0, description="Number of processing retries")
    created_at: datetime = Field(..., description="Event creation timestamp")
    updated_at: datetime = Field(..., description="Event last update timestamp")


class ShopifySyncJobBase(BaseModel):
    """Base sync job model."""
    sync_type: ShopifySyncType = Field(..., description="Type of sync operation")
    status: ShopifySyncStatus = Field(default=ShopifySyncStatus.PENDING, description="Sync job status")
    total_items: Optional[int] = Field(default=None, description="Total items to sync")
    processed_items: int = Field(default=0, description="Number of items processed")
    failed_items: int = Field(default=0, description="Number of items that failed")


class ShopifySyncJobCreate(ShopifySyncJobBase):
    """Sync job creation model."""
    shop_id: int = Field(..., description="Store ID")
    sync_config: Optional[Dict[str, Any]] = Field(default=None, description="Sync configuration")


class ShopifySyncJob(ShopifySyncJobBase):
    """Complete sync job model."""
    id: int = Field(..., description="Sync job ID")
    shop_id: int = Field(..., description="Store ID")
    sync_config: Optional[Dict[str, Any]] = Field(default=None, description="Sync configuration")
    started_at: Optional[datetime] = Field(default=None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if job failed")
    sync_details: Optional[Dict[str, Any]] = Field(default=None, description="Detailed sync information")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Job last update timestamp")


class ShopifyOrderBase(BaseModel):
    """Base Shopify order model."""
    shopify_order_id: int = Field(..., description="Shopify order ID")
    order_number: str = Field(..., description="Order number")
    email: Optional[str] = Field(default=None, description="Customer email")
    total_price: Decimal = Field(..., ge=0, description="Total order price")
    subtotal_price: Decimal = Field(..., ge=0, description="Subtotal price")
    total_tax: Decimal = Field(default=Decimal("0"), ge=0, description="Total tax amount")
    currency: str = Field(..., description="Order currency")
    financial_status: str = Field(..., description="Financial status")
    fulfillment_status: Optional[str] = Field(default=None, description="Fulfillment status")
    order_status_url: Optional[str] = Field(default=None, description="Order status URL")
    shopify_created_at: datetime = Field(..., description="Shopify order creation timestamp")
    shopify_updated_at: datetime = Field(..., description="Shopify order update timestamp")


class ShopifyOrderCreate(ShopifyOrderBase):
    """Shopify order creation model."""
    shop_id: int = Field(..., description="Store ID")
    customer_data: Optional[Dict[str, Any]] = Field(default=None, description="Customer information")
    line_items: List[Dict[str, Any]] = Field(..., description="Order line items")
    shipping_address: Optional[Dict[str, Any]] = Field(default=None, description="Shipping address")
    billing_address: Optional[Dict[str, Any]] = Field(default=None, description="Billing address")


class ShopifyOrder(ShopifyOrderBase):
    """Complete Shopify order model."""
    id: int = Field(..., description="Internal order ID")
    shop_id: int = Field(..., description="Store ID")
    customer_data: Optional[Dict[str, Any]] = Field(default=None, description="Customer information")
    line_items: List[Dict[str, Any]] = Field(..., description="Order line items")
    shipping_address: Optional[Dict[str, Any]] = Field(default=None, description="Shipping address")
    billing_address: Optional[Dict[str, Any]] = Field(default=None, description="Billing address")
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime = Field(..., description="Order last update timestamp")


class ShopifyOAuthRequest(BaseModel):
    """Shopify OAuth authorization request."""
    shop_domain: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]*\.myshopify\.com$",
        description="Shopify store domain"
    )
    scopes: Optional[List[str]] = Field(default=None, description="Requested OAuth scopes")
    redirect_uri: Optional[str] = Field(default=None, description="OAuth redirect URI")


class ShopifyOAuthCallback(BaseModel):
    """Shopify OAuth callback data."""
    shop_domain: str = Field(..., description="Shopify store domain")
    code: str = Field(..., description="OAuth authorization code")
    state: Optional[str] = Field(default=None, description="OAuth state parameter")
    hmac: Optional[str] = Field(default=None, description="HMAC signature")
    timestamp: Optional[str] = Field(default=None, description="Request timestamp")


class ShopifyWebhookRequest(BaseModel):
    """Shopify webhook request model."""
    event_type: ShopifyWebhookEventType = Field(..., description="Webhook event type")
    payload: Dict[str, Any] = Field(..., description="Webhook payload")
    shop_domain: str = Field(..., description="Shop domain")
    webhook_id: Optional[str] = Field(default=None, description="Webhook ID")


class ShopifyApiError(BaseModel):
    """Shopify API error model."""
    error_type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    shopify_errors: Optional[Dict[str, Any]] = Field(default=None, description="Shopify-specific errors")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class ShopifyRateLimitInfo(BaseModel):
    """Shopify API rate limit information."""
    call_limit: int = Field(..., description="API call limit")
    call_made: int = Field(..., description="API calls made")
    call_remaining: int = Field(..., description="API calls remaining")
    retry_after: Optional[int] = Field(default=None, description="Retry after seconds")
    bucket_size: Optional[int] = Field(default=None, description="Bucket size for leaky bucket")


class ShopifyProductSyncRequest(BaseModel):
    """Product sync request model."""
    shop_id: int = Field(..., description="Store ID")
    product_ids: Optional[List[int]] = Field(default=None, description="Specific product IDs to sync")
    full_sync: bool = Field(default=False, description="Whether to perform full sync")
    sync_inventory: bool = Field(default=True, description="Whether to sync inventory levels")


class ShopifyOrderSyncRequest(BaseModel):
    """Order sync request model."""
    shop_id: int = Field(..., description="Store ID")
    since_date: Optional[datetime] = Field(default=None, description="Sync orders since this date")
    order_ids: Optional[List[int]] = Field(default=None, description="Specific order IDs to sync")
    financial_status: Optional[str] = Field(default=None, description="Filter by financial status")


class ShopifyInventorySyncRequest(BaseModel):
    """Inventory sync request model."""
    shop_id: int = Field(..., description="Store ID")
    location_ids: Optional[List[int]] = Field(default=None, description="Specific location IDs")
    inventory_item_ids: Optional[List[int]] = Field(default=None, description="Specific inventory item IDs")


class ShopifyStoreStats(BaseModel):
    """Shopify store statistics."""
    shop_id: int = Field(..., description="Store ID")
    total_products: int = Field(..., description="Total number of products")
    active_products: int = Field(..., description="Number of active products")
    total_orders: int = Field(..., description="Total number of orders")
    orders_last_30_days: int = Field(..., description="Orders in last 30 days")
    total_revenue: Decimal = Field(..., description="Total revenue")
    revenue_last_30_days: Decimal = Field(..., description="Revenue in last 30 days")
    last_sync_at: Optional[datetime] = Field(default=None, description="Last sync timestamp")
    sync_status: Optional[ShopifySyncStatus] = Field(default=None, description="Current sync status")