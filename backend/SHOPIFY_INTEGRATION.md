# Shopify Integration Backend Implementation

This document describes the core Shopify integration backend infrastructure that has been implemented.

## Overview

The Shopify integration provides a complete backend infrastructure for connecting and synchronizing data with Shopify stores. It includes OAuth authentication, webhook processing, product synchronization, and order management.

## Architecture

### Core Components

1. **Models** (`app/models/shopify.py`)
   - Pydantic models for all Shopify-related data structures
   - Type-safe data validation and serialization
   - Comprehensive model coverage for stores, products, orders, webhooks, and sync jobs

2. **Service Layer** (`app/services/shopify_service.py`)
   - `ShopifyApiClient`: HTTP client with rate limiting and error handling
   - `ShopifyRateLimiter`: Leaky bucket algorithm for API rate limiting
   - `ShopifyService`: Main business logic and data management

3. **API Endpoints** (`app/api/v1/shopify.py`)
   - OAuth authorization and callback handling
   - Store management endpoints
   - Product and order synchronization
   - Webhook processing endpoints

4. **Database Schema** (`migrations/create_shopify_tables.py`)
   - Comprehensive table structure for Shopify data
   - Proper indexing and foreign key relationships
   - Row Level Security (RLS) policies

## Features Implemented

### 1. OAuth 2.0 Authentication Flow

- **Authorization URL Generation**: Creates secure OAuth URLs with state parameters
- **Token Exchange**: Exchanges authorization codes for access tokens
- **Store Verification**: Validates shop access and retrieves store information
- **Automatic Webhook Setup**: Configures required webhooks during connection

```python
# Generate OAuth URL
oauth_url = shopify_service.generate_oauth_url(
    shop_domain="example.myshopify.com",
    redirect_uri="https://yourapp.com/callback",
    state="user_123"
)

# Exchange code for token
store = await shopify_service.exchange_oauth_code(
    shop_domain="example.myshopify.com",
    code="authorization_code",
    user_id="user_123"
)
```

### 2. Rate Limiting and API Client

- **Leaky Bucket Algorithm**: Respects Shopify's API call limits
- **Automatic Retry Logic**: Handles rate limit responses gracefully
- **Request/Response Logging**: Comprehensive error tracking
- **Connection Pooling**: Efficient HTTP connection management

```python
async with ShopifyApiClient(shop_domain, access_token) as client:
    products = await client.get_products(limit=250)
    shop_info = await client.get_shop_info()
```

### 3. Webhook Processing

- **Signature Verification**: HMAC-SHA256 signature validation
- **Event Processing**: Asynchronous webhook event handling
- **Retry Logic**: Failed webhook processing with retry mechanism
- **Event Logging**: Complete audit trail of webhook events

Supported webhook events:
- `orders/create`, `orders/update`, `orders/paid`, `orders/cancelled`
- `products/create`, `products/update`, `products/delete`
- `inventory_levels/update`
- `app/uninstalled`

### 4. Data Synchronization

- **Product Sync**: Full and incremental product synchronization
- **Order Sync**: Historical and real-time order data
- **Inventory Sync**: Stock level synchronization
- **Background Jobs**: Asynchronous sync job processing

```python
# Start product sync
sync_job = await shopify_service.sync_products(
    shop_id=123,
    full_sync=True
)
```

### 5. Database Schema

#### Tables Created:

- **`shopify_stores`**: Store connections and configuration
- **`shopify_products`**: Shopify product data linked to internal products
- **`shopify_orders`**: Order data for analytics and tracking
- **`shopify_webhook_events`**: Webhook events for real-time sync
- **`shopify_sync_jobs`**: Background sync job tracking

#### Key Features:
- Foreign key relationships with cascade deletes
- Comprehensive indexing for performance
- JSONB columns for flexible data storage
- Automatic timestamp management
- Row Level Security (RLS) policies

## API Endpoints

### OAuth Endpoints

- `POST /api/v1/shopify/oauth/authorize` - Generate OAuth URL
- `POST /api/v1/shopify/oauth/callback` - Handle OAuth callback

### Store Management

- `GET /api/v1/shopify/stores` - List user's stores
- `GET /api/v1/shopify/stores/{shop_id}` - Get store details
- `GET /api/v1/shopify/stores/{shop_id}/stats` - Get store statistics
- `DELETE /api/v1/shopify/stores/{shop_id}` - Disconnect store

### Synchronization

- `POST /api/v1/shopify/stores/{shop_id}/sync/products` - Start product sync
- `GET /api/v1/shopify/stores/{shop_id}/sync/jobs` - Get sync jobs

### Webhooks

- `POST /api/v1/shopify/webhooks/orders_create` - Handle order creation
- `POST /api/v1/shopify/webhooks/orders_update` - Handle order updates
- `POST /api/v1/shopify/webhooks/products_create` - Handle product creation
- `POST /api/v1/shopify/webhooks/products_update` - Handle product updates
- `POST /api/v1/shopify/webhooks/app_uninstalled` - Handle app uninstall

## Configuration

### Required Environment Variables

```bash
# Shopify OAuth Credentials
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret

# Shopify API Configuration
SHOPIFY_API_VERSION=2024-07
SHOPIFY_SCOPES=read_products,read_inventory,read_orders,read_price_rules

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Shopify App Configuration

1. Create a Shopify app in your Partner Dashboard
2. Configure OAuth redirect URLs
3. Set up webhook endpoints
4. Configure required scopes

## Security Features

### 1. Authentication & Authorization

- JWT-based user authentication
- Store ownership verification
- Row Level Security (RLS) policies
- API key validation

### 2. Webhook Security

- HMAC-SHA256 signature verification
- Request timestamp validation
- IP allowlisting (optional)
- Rate limiting on webhook endpoints

### 3. Data Protection

- Encrypted access token storage
- Secure database connections
- Input validation and sanitization
- SQL injection prevention

## Error Handling

### 1. API Errors

- Comprehensive error logging
- Structured error responses
- Retry logic for transient failures
- Circuit breaker pattern for external APIs

### 2. Webhook Failures

- Failed webhook retry mechanism
- Error message logging
- Dead letter queue for persistent failures
- Monitoring and alerting

## Performance Optimizations

### 1. Database

- Optimized indexes for common queries
- Connection pooling
- Query optimization
- Batch operations for bulk data

### 2. API Calls

- Rate limiting compliance
- Request batching where possible
- Caching for frequently accessed data
- Asynchronous processing

## Monitoring and Logging

### 1. Business Events

- Store connections/disconnections
- Sync job status changes
- Webhook processing events
- OAuth flow completion

### 2. Security Events

- Failed authentication attempts
- Invalid webhook signatures
- Suspicious API activity
- Rate limit violations

## Installation and Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Database Migration

```bash
python run_shopify_migration.py
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start the Application

```bash
python main.py
```

## Testing

### 1. Unit Tests

```bash
pytest tests/test_shopify_service.py
pytest tests/test_shopify_api.py
```

### 2. Integration Tests

```bash
pytest tests/integration/test_shopify_oauth.py
pytest tests/integration/test_shopify_webhooks.py
```

### 3. Manual Testing

1. Test OAuth flow with a development store
2. Verify webhook processing
3. Test product synchronization
4. Validate error handling

## Future Enhancements

### 1. Advanced Features

- Multi-location inventory support
- Advanced product variant handling
- Customer data synchronization
- Shopify Plus features

### 2. Performance Improvements

- Redis caching layer
- Background job queue (Celery)
- Database read replicas
- CDN for static assets

### 3. Monitoring

- Prometheus metrics
- Grafana dashboards
- Sentry error tracking
- Custom alerting rules

## Troubleshooting

### Common Issues

1. **OAuth Failures**
   - Verify client ID/secret
   - Check redirect URI configuration
   - Validate shop domain format

2. **Webhook Issues**
   - Verify HMAC signature
   - Check webhook URL accessibility
   - Validate SSL certificate

3. **Sync Problems**
   - Check API rate limits
   - Verify access token validity
   - Review error logs

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('app.services.shopify_service').setLevel(logging.DEBUG)
```

## Support

For issues and questions:

1. Check the error logs
2. Review the API documentation
3. Test with Shopify's development tools
4. Contact the development team

---

This implementation provides a solid foundation for Shopify integration with room for future enhancements and customizations based on specific business requirements.