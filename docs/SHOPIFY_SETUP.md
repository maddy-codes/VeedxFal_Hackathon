# Shopify Integration Setup Guide

This comprehensive guide will walk you through setting up the Shopify integration for the Retail AI Advisor platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Shopify App Creation](#shopify-app-creation)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Backend Configuration](#backend-configuration)
6. [Frontend Configuration](#frontend-configuration)
7. [Webhook Configuration](#webhook-configuration)
8. [Testing the Integration](#testing-the-integration)
9. [Deployment Considerations](#deployment-considerations)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before setting up the Shopify integration, ensure you have:

- **Shopify Partner Account**: Required to create Shopify apps
- **Development Store**: For testing the integration
- **PostgreSQL Database**: Supabase or self-hosted PostgreSQL
- **SSL Certificate**: Required for webhook endpoints in production
- **Domain Name**: For production webhook URLs

### Required Permissions

- Access to Shopify Partner Dashboard
- Database admin access for running migrations
- Server admin access for environment configuration

## Shopify App Creation

### Step 1: Create a Shopify Partner Account

1. Visit [Shopify Partners](https://partners.shopify.com/)
2. Sign up for a partner account if you don't have one
3. Complete the partner onboarding process

### Step 2: Create a New App

1. **Navigate to Apps**:
   - Go to your Partner Dashboard
   - Click on "Apps" in the left sidebar
   - Click "Create app"

2. **Choose App Type**:
   - Select "Public app" for production deployment
   - Select "Custom app" for private/internal use

3. **Configure Basic Information**:
   ```
   App name: Retail AI Advisor
   App URL: https://your-domain.com
   Allowed redirection URL(s): 
     - https://your-domain.com/api/v1/shopify/oauth/callback
     - http://localhost:3000/dashboard/shopify/callback (for development)
   ```

### Step 3: Configure App Permissions

Set the following scopes in your app configuration:

```
read_products          # Read product information
write_products         # Update product information (optional)
read_inventory         # Read inventory levels
read_orders            # Read order information
read_price_rules       # Read pricing rules and discounts
read_customers         # Read customer information (optional)
```

### Step 4: Get API Credentials

After creating the app, note down:
- **Client ID** (API key)
- **Client Secret**
- **API Version** (use `2024-07` or latest stable)

## Environment Configuration

### Backend Environment Variables

Create or update your backend `.env` file:

```bash
# Shopify OAuth Credentials
SHOPIFY_CLIENT_ID=your_client_id_here
SHOPIFY_CLIENT_SECRET=your_client_secret_here

# Shopify API Configuration
SHOPIFY_API_VERSION=2024-07
SHOPIFY_SCOPES=read_products,read_inventory,read_orders,read_price_rules

# Webhook Configuration
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret_here

# Database Configuration (if not already set)
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Application URLs
FRONTEND_URL=https://your-frontend-domain.com
BACKEND_URL=https://your-backend-domain.com
```

### Frontend Environment Variables

Update your frontend `.env.local` file:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend-domain.com

# Shopify Configuration (if needed for direct client access)
NEXT_PUBLIC_SHOPIFY_CLIENT_ID=your_client_id_here

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### Environment Variable Templates

Create template files for easy deployment:

**backend/.env.example**:
```bash
# Shopify Integration
SHOPIFY_CLIENT_ID=your_shopify_client_id
SHOPIFY_CLIENT_SECRET=your_shopify_client_secret
SHOPIFY_API_VERSION=2024-07
SHOPIFY_SCOPES=read_products,read_inventory,read_orders,read_price_rules
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret

# Database
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Application
ENVIRONMENT=production
DEBUG=false
FRONTEND_URL=https://your-frontend-domain.com
BACKEND_URL=https://your-backend-domain.com
```

**frontend/.env.example**:
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend-domain.com

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# App Configuration
NEXT_PUBLIC_APP_NAME=Retail AI Advisor
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## Database Setup

### Step 1: Run Shopify Migration

The Shopify integration requires specific database tables. Run the migration:

```bash
# Navigate to backend directory
cd backend

# Run the Shopify migration
python run_shopify_migration.py
```

### Step 2: Verify Database Schema

Check that the following tables were created:

- `shopify_stores` - Store connections and configuration
- `shopify_products` - Shopify product data linked to internal products
- `shopify_orders` - Order data for analytics and tracking
- `shopify_webhook_events` - Webhook events for real-time sync
- `shopify_sync_jobs` - Background sync job tracking

### Step 3: Database Permissions

Ensure your application has the necessary permissions:

```sql
-- Grant permissions to your application user
GRANT ALL ON shopify_stores TO your_app_user;
GRANT ALL ON shopify_products TO your_app_user;
GRANT ALL ON shopify_orders TO your_app_user;
GRANT ALL ON shopify_webhook_events TO your_app_user;
GRANT ALL ON shopify_sync_jobs TO your_app_user;

-- Grant sequence permissions
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
```

## Backend Configuration

### Step 1: Install Dependencies

Ensure all required dependencies are installed:

```bash
cd backend
pip install -r requirements.txt
```

Key Shopify-related dependencies:
- `httpx` - HTTP client for API requests
- `pydantic` - Data validation and serialization
- `cryptography` - For webhook signature verification

### Step 2: Verify Service Configuration

Check that the Shopify service is properly configured in [`app/services/shopify_service.py`](../backend/app/services/shopify_service.py):

```python
# Verify these configurations exist:
- ShopifyApiClient with rate limiting
- ShopifyService with OAuth and sync capabilities
- Webhook signature verification
- Error handling and logging
```

### Step 3: Test Backend Endpoints

Start the backend and verify endpoints:

```bash
# Start the backend
python main.py

# Test health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

Verify these Shopify endpoints are available:
- `POST /api/v1/shopify/oauth/authorize`
- `POST /api/v1/shopify/oauth/callback`
- `GET /api/v1/shopify/stores`
- `POST /api/v1/shopify/stores/{shop_id}/sync/products`

## Frontend Configuration

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Verify Components

Check that Shopify components are available:
- [`ShopifyStoreConnection`](../frontend/src/components/shopify/ShopifyStoreConnection.tsx)
- [`ShopifyStoreDashboard`](../frontend/src/components/shopify/ShopifyStoreDashboard.tsx)
- [`ShopifyOAuthCallback`](../frontend/src/components/shopify/ShopifyOAuthCallback.tsx)
- [`ShopifySyncProgress`](../frontend/src/components/shopify/ShopifySyncProgress.tsx)

### Step 3: Test Frontend

```bash
# Start the frontend
npm run dev

# Navigate to Shopify integration
open http://localhost:3000/dashboard/shopify
```

## Webhook Configuration

### Step 1: Configure Webhook Endpoints

In your Shopify app settings, configure these webhook endpoints:

```
Order creation: https://your-domain.com/api/v1/shopify/webhooks/orders_create
Order updates: https://your-domain.com/api/v1/shopify/webhooks/orders_update
Product creation: https://your-domain.com/api/v1/shopify/webhooks/products_create
Product updates: https://your-domain.com/api/v1/shopify/webhooks/products_update
App uninstalled: https://your-domain.com/api/v1/shopify/webhooks/app_uninstalled
```

### Step 2: Webhook Security

1. **Generate Webhook Secret**:
   ```bash
   # Generate a secure webhook secret
   openssl rand -hex 32
   ```

2. **Configure in Shopify**:
   - Add the webhook secret to your Shopify app settings
   - Set the webhook format to JSON

3. **Update Environment**:
   ```bash
   SHOPIFY_WEBHOOK_SECRET=your_generated_secret
   ```

### Step 3: Test Webhooks

Use tools like ngrok for local testing:

```bash
# Install ngrok
npm install -g ngrok

# Expose local backend
ngrok http 8000

# Use the ngrok URL for webhook endpoints
# Example: https://abc123.ngrok.io/api/v1/shopify/webhooks/orders_create
```

## Testing the Integration

### Step 1: Create a Development Store

1. In your Shopify Partner Dashboard
2. Go to "Stores" → "Add store"
3. Select "Development store"
4. Choose "Create a store to test and build"

### Step 2: Install Your App

1. In your Partner Dashboard, go to your app
2. Click "Test on development store"
3. Select your development store
4. Complete the installation process

### Step 3: Test OAuth Flow

1. Navigate to your frontend Shopify page
2. Enter your development store domain
3. Complete the OAuth authorization
4. Verify the store appears in your connected stores

### Step 4: Test Product Sync

1. Add some products to your development store
2. Trigger a product sync from your application
3. Verify products appear in your database
4. Check sync job status and logs

### Step 5: Test Webhooks

1. Create an order in your development store
2. Check webhook event logs in your database
3. Verify order data is synchronized
4. Test product updates and other webhook events

## Deployment Considerations

### Production Environment

1. **SSL Certificate**: Required for webhook endpoints
2. **Domain Configuration**: Update all URLs to production domains
3. **Database**: Use production PostgreSQL instance
4. **Monitoring**: Set up logging and error tracking
5. **Rate Limiting**: Configure appropriate rate limits

### Security Checklist

- [ ] Environment variables are secure and not exposed
- [ ] Webhook signatures are verified
- [ ] Database access is properly restricted
- [ ] API endpoints have proper authentication
- [ ] Rate limiting is configured
- [ ] Error messages don't expose sensitive information

### Performance Optimization

1. **Database Indexing**: Ensure proper indexes are in place
2. **Connection Pooling**: Configure database connection pooling
3. **Caching**: Implement caching for frequently accessed data
4. **Background Jobs**: Use background processing for sync operations

## Troubleshooting

### Common Issues

#### 1. OAuth Authorization Fails

**Symptoms**: Redirect to Shopify fails or returns error

**Solutions**:
- Verify client ID and secret are correct
- Check redirect URLs match exactly (including protocol)
- Ensure scopes are properly configured
- Verify shop domain format (should be `store.myshopify.com`)

#### 2. Webhook Signature Verification Fails

**Symptoms**: Webhooks return 401 Unauthorized

**Solutions**:
- Verify webhook secret matches Shopify configuration
- Check HMAC signature calculation
- Ensure request body is read correctly
- Verify timestamp validation logic

#### 3. Product Sync Fails

**Symptoms**: Sync jobs fail or products don't appear

**Solutions**:
- Check API rate limits and implement proper throttling
- Verify access token is valid and has required scopes
- Check database constraints and foreign key relationships
- Review error logs for specific API errors

#### 4. Database Connection Issues

**Symptoms**: Database operations fail

**Solutions**:
- Verify database URL and credentials
- Check network connectivity to database
- Ensure migration was run successfully
- Verify user permissions on tables

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('app.services.shopify_service').setLevel(logging.DEBUG)
logging.getLogger('app.api.v1.shopify').setLevel(logging.DEBUG)
```

### Health Checks

Implement health checks for monitoring:

```bash
# Check backend health
curl https://your-domain.com/health

# Check database connectivity
curl https://your-domain.com/api/v1/health/database

# Check Shopify API connectivity
curl https://your-domain.com/api/v1/health/shopify
```

### Log Analysis

Key log events to monitor:

- OAuth flow completion
- Webhook processing success/failure
- Sync job status changes
- API rate limit warnings
- Database connection issues

## Support and Resources

### Documentation Links

- [Shopify API Documentation](https://shopify.dev/docs/api)
- [Shopify OAuth Documentation](https://shopify.dev/docs/apps/auth/oauth)
- [Shopify Webhooks Documentation](https://shopify.dev/docs/apps/webhooks)

### Internal Documentation

- [Shopify API Reference](./SHOPIFY_API.md)
- [Shopify User Guide](./SHOPIFY_USER_GUIDE.md)
- [Backend Integration Details](../backend/SHOPIFY_INTEGRATION.md)

### Getting Help

1. Check the error logs for specific error messages
2. Review the API documentation for endpoint requirements
3. Test with Shopify's development tools
4. Contact the development team with specific error details

---

This setup guide provides a comprehensive walkthrough for implementing the Shopify integration. Follow each section carefully and test thoroughly before deploying to production.