# Shopify API Documentation

This document provides comprehensive API documentation for all Shopify integration endpoints in the Retail AI Advisor platform.

## Table of Contents

1. [Authentication](#authentication)
2. [OAuth Endpoints](#oauth-endpoints)
3. [Store Management](#store-management)
4. [Product Synchronization](#product-synchronization)
5. [Webhook Endpoints](#webhook-endpoints)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Request/Response Examples](#requestresponse-examples)

## Authentication

All Shopify API endpoints require user authentication via JWT tokens, except for webhook endpoints which use HMAC signature verification.

### Headers Required

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Authentication Flow

1. User authenticates with the platform
2. JWT token is issued
3. Token is included in all API requests
4. Token is validated on each request

## OAuth Endpoints

### Generate OAuth URL

Generates a Shopify OAuth authorization URL for store connection.

**Endpoint**: `POST /api/v1/shopify/oauth/authorize`

**Request Body**:
```json
{
  "shop_domain": "example.myshopify.com",
  "redirect_uri": "https://yourapp.com/callback" // Optional
}
```

**Response**:
```json
{
  "oauth_url": "https://example.myshopify.com/admin/oauth/authorize?client_id=...",
  "state": "user_123:192.168.1.1",
  "shop_domain": "example.myshopify.com"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid shop domain
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: OAuth URL generation failed

### Handle OAuth Callback

Processes OAuth callback and exchanges authorization code for access token.

**Endpoint**: `POST /api/v1/shopify/oauth/callback`

**Request Body**:
```json
{
  "shop_domain": "example.myshopify.com",
  "code": "authorization_code_from_shopify",
  "state": "user_123:192.168.1.1" // Optional but recommended
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": "user_123",
  "shop_domain": "example.myshopify.com",
  "shop_name": "Example Store",
  "shop_id": 12345678,
  "scope": "read_products,read_inventory,read_orders",
  "is_active": true,
  "shop_config": {
    "currency": "USD",
    "timezone": "America/New_York",
    "plan_name": "basic"
  },
  "last_sync_at": null,
  "created_at": "2025-01-31T12:00:00Z",
  "updated_at": "2025-01-31T12:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid authorization code or state mismatch
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: OAuth processing failed

## Store Management

### Get User's Stores

Retrieves all Shopify stores connected by the current user.

**Endpoint**: `GET /api/v1/shopify/stores`

**Response**:
```json
[
  {
    "id": 1,
    "user_id": "user_123",
    "shop_domain": "example.myshopify.com",
    "shop_name": "Example Store",
    "shop_id": 12345678,
    "scope": "read_products,read_inventory,read_orders",
    "is_active": true,
    "shop_config": {
      "currency": "USD",
      "timezone": "America/New_York",
      "plan_name": "basic"
    },
    "last_sync_at": "2025-01-31T11:30:00Z",
    "created_at": "2025-01-31T10:00:00Z",
    "updated_at": "2025-01-31T11:30:00Z"
  }
]
```

### Get Store Details

Retrieves details of a specific Shopify store.

**Endpoint**: `GET /api/v1/shopify/stores/{shop_id}`

**Path Parameters**:
- `shop_id` (integer): The store ID

**Response**: Same as individual store object above

**Error Responses**:
- `404 Not Found`: Store not found or not owned by user

### Get Store Statistics

Retrieves statistics and metrics for a Shopify store.

**Endpoint**: `GET /api/v1/shopify/stores/{shop_id}/stats`

**Response**:
```json
{
  "shop_id": 1,
  "total_products": 150,
  "active_products": 120,
  "total_orders": 500,
  "orders_last_30_days": 45,
  "total_revenue": 25000.50,
  "revenue_last_30_days": 3500.75,
  "last_sync_at": "2025-01-31T11:30:00Z",
  "sync_status": "completed"
}
```

### Disconnect Store

Disconnects a Shopify store from the platform.

**Endpoint**: `DELETE /api/v1/shopify/stores/{shop_id}`

**Response**:
```json
{
  "message": "Store disconnected successfully",
  "shop_id": 1
}
```

## Product Synchronization

### Start Product Sync

Initiates a product synchronization job for a Shopify store.

**Endpoint**: `POST /api/v1/shopify/stores/{shop_id}/sync/products`

**Request Body**:
```json
{
  "full_sync": true // Optional, defaults to false for incremental sync
}
```

**Response**:
```json
{
  "id": 1,
  "shop_id": 1,
  "sync_type": "products",
  "status": "pending",
  "total_items": null,
  "processed_items": 0,
  "failed_items": 0,
  "sync_config": {
    "full_sync": true
  },
  "started_at": null,
  "completed_at": null,
  "error_message": null,
  "sync_details": {},
  "created_at": "2025-01-31T12:00:00Z",
  "updated_at": "2025-01-31T12:00:00Z"
}
```

### Get Sync Jobs

Retrieves synchronization jobs for a Shopify store.

**Endpoint**: `GET /api/v1/shopify/stores/{shop_id}/sync/jobs`

**Query Parameters**:
- `limit` (integer): Maximum number of jobs to return (default: 10)

**Response**:
```json
[
  {
    "id": 1,
    "shop_id": 1,
    "sync_type": "products",
    "status": "completed",
    "total_items": 150,
    "processed_items": 150,
    "failed_items": 0,
    "sync_config": {
      "full_sync": true
    },
    "started_at": "2025-01-31T12:00:00Z",
    "completed_at": "2025-01-31T12:05:00Z",
    "error_message": null,
    "sync_details": {
      "products_created": 25,
      "products_updated": 125,
      "products_skipped": 0
    },
    "created_at": "2025-01-31T12:00:00Z",
    "updated_at": "2025-01-31T12:05:00Z"
  }
]
```

## Webhook Endpoints

Webhook endpoints handle real-time updates from Shopify. These endpoints do not require JWT authentication but use HMAC signature verification.

### Headers Required for Webhooks

```http
X-Shopify-Hmac-Sha256: <hmac_signature>
X-Shopify-Shop-Domain: <shop_domain>
X-Shopify-Topic: <webhook_topic>
Content-Type: application/json
```

### Order Created Webhook

Handles new order creation events.

**Endpoint**: `POST /api/v1/shopify/webhooks/orders_create`

**Request Body**: Shopify order object (see Shopify API documentation)

**Response**:
```json
{
  "status": "success",
  "message": "Order webhook processed successfully",
  "event_id": "evt_123"
}
```

### Order Updated Webhook

Handles order update events.

**Endpoint**: `POST /api/v1/shopify/webhooks/orders_update`

### Product Created Webhook

Handles new product creation events.

**Endpoint**: `POST /api/v1/shopify/webhooks/products_create`

### Product Updated Webhook

Handles product update events.

**Endpoint**: `POST /api/v1/shopify/webhooks/products_update`

### App Uninstalled Webhook

Handles app uninstallation events.

**Endpoint**: `POST /api/v1/shopify/webhooks/app_uninstalled`

**Response**:
```json
{
  "status": "success",
  "message": "App uninstall processed successfully"
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message description",
  "error_code": "SHOPIFY_API_ERROR",
  "timestamp": "2025-01-31T12:00:00Z"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_SHOP_DOMAIN` | Shop domain format is invalid | 400 |
| `OAUTH_CODE_INVALID` | OAuth authorization code is invalid | 400 |
| `STATE_MISMATCH` | OAuth state parameter mismatch | 400 |
| `STORE_NOT_FOUND` | Requested store not found | 404 |
| `UNAUTHORIZED_STORE_ACCESS` | User doesn't own the requested store | 403 |
| `SHOPIFY_API_ERROR` | Error from Shopify API | 502 |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded | 429 |
| `WEBHOOK_SIGNATURE_INVALID` | Webhook HMAC signature invalid | 401 |
| `SYNC_JOB_FAILED` | Product sync job failed | 500 |

### Error Response Examples

**Invalid Shop Domain**:
```json
{
  "detail": "Invalid shop domain format. Expected format: store.myshopify.com",
  "error_code": "INVALID_SHOP_DOMAIN",
  "timestamp": "2025-01-31T12:00:00Z"
}
```

**Rate Limit Exceeded**:
```json
{
  "detail": "API rate limit exceeded. Please try again later.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2025-01-31T12:00:00Z",
  "retry_after": 60
}
```

## Rate Limiting

### API Rate Limits

The platform implements rate limiting to comply with Shopify's API limits and protect the service:

- **OAuth Endpoints**: 10 requests per minute per user
- **Store Management**: 100 requests per minute per user
- **Sync Operations**: 5 concurrent sync jobs per store
- **Webhook Endpoints**: 1000 requests per minute per store

### Rate Limit Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643723400
```

### Handling Rate Limits

When rate limits are exceeded, the API returns a `429 Too Many Requests` status with retry information:

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## Request/Response Examples

### Complete OAuth Flow Example

**Step 1: Generate OAuth URL**

```bash
curl -X POST "https://api.example.com/api/v1/shopify/oauth/authorize" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "shop_domain": "example.myshopify.com"
  }'
```

**Response**:
```json
{
  "oauth_url": "https://example.myshopify.com/admin/oauth/authorize?client_id=abc123&scope=read_products,read_inventory,read_orders&redirect_uri=https://api.example.com/api/v1/shopify/oauth/callback&state=user_123:192.168.1.1",
  "state": "user_123:192.168.1.1",
  "shop_domain": "example.myshopify.com"
}
```

**Step 2: Handle OAuth Callback**

```bash
curl -X POST "https://api.example.com/api/v1/shopify/oauth/callback" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "shop_domain": "example.myshopify.com",
    "code": "abc123def456",
    "state": "user_123:192.168.1.1"
  }'
```

### Product Sync Example

**Start Sync**:
```bash
curl -X POST "https://api.example.com/api/v1/shopify/stores/1/sync/products" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_sync": true
  }'
```

**Check Sync Status**:
```bash
curl -X GET "https://api.example.com/api/v1/shopify/stores/1/sync/jobs?limit=5" \
  -H "Authorization: Bearer <jwt_token>"
```

### Webhook Example

**Incoming Webhook Request**:
```bash
curl -X POST "https://api.example.com/api/v1/shopify/webhooks/orders_create" \
  -H "X-Shopify-Hmac-Sha256: <hmac_signature>" \
  -H "X-Shopify-Shop-Domain: example.myshopify.com" \
  -H "X-Shopify-Topic: orders/create" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 12345,
    "order_number": "#1001",
    "total_price": "99.99",
    "currency": "USD",
    "financial_status": "paid",
    "line_items": [...]
  }'
```

## SDK and Client Libraries

### JavaScript/TypeScript Client

```typescript
import { ShopifyApiClient } from '@/lib/shopify-api';

const client = new ShopifyApiClient({
  baseUrl: 'https://api.example.com',
  token: 'jwt_token'
});

// Generate OAuth URL
const oauthData = await client.generateOAuthUrl('example.myshopify.com');

// Get stores
const stores = await client.getStores();

// Start product sync
const syncJob = await client.syncProducts(storeId, { full_sync: true });
```

### Python Client

```python
from shopify_client import ShopifyApiClient

client = ShopifyApiClient(
    base_url='https://api.example.com',
    token='jwt_token'
)

# Generate OAuth URL
oauth_data = client.generate_oauth_url('example.myshopify.com')

# Get stores
stores = client.get_stores()

# Start product sync
sync_job = client.sync_products(store_id, full_sync=True)
```

## Testing and Development

### Development Environment

For development and testing, use these endpoints:

```
Base URL: http://localhost:8000
OAuth Callback: http://localhost:3000/dashboard/shopify/callback
```

### Testing with Shopify Development Stores

1. Create a development store in your Shopify Partner account
2. Install your app on the development store
3. Use the development store for testing OAuth and sync operations
4. Test webhook endpoints using ngrok or similar tools

### Mock Data

For testing without a real Shopify store, mock data is available:

```bash
# Enable mock mode
export SHOPIFY_MOCK_MODE=true

# Mock endpoints will return sample data
curl http://localhost:8000/api/v1/shopify/stores
```

---

This API documentation provides comprehensive information for integrating with the Shopify functionality. For additional support, refer to the [Shopify Setup Guide](./SHOPIFY_SETUP.md) and [User Guide](./SHOPIFY_USER_GUIDE.md).