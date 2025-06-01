# Webhook Configuration Guide

## Overview

This guide explains how to configure webhooks for the Shopify integration. Webhooks allow your application to receive real-time notifications when events occur in connected Shopify stores.

## Webhook Setup Issues Fixed

### 1. Localhost URL Problem
**Issue**: Shopify webhooks require publicly accessible URLs, but the application was trying to use `http://localhost:3000` which Shopify rejects with "address is not allowed" errors.

**Solution**: The application now:
- Checks if configured URLs are publicly accessible
- Skips webhook setup if only localhost URLs are available
- Provides clear logging about webhook configuration status
- Allows explicit webhook URL configuration via environment variable

### 2. Protected Customer Data Permissions
**Issue**: Order-related webhooks (`orders/create`, `orders/updated`, `orders/paid`, `orders/cancelled`) require protected customer data permissions that the app doesn't have by default.

**Solution**: The application now:
- Separates core webhooks from order webhooks
- Treats order webhooks as optional
- Gracefully handles permission errors for order webhooks
- Continues OAuth flow even if order webhooks fail

### 3. Webhook Creation Blocking OAuth
**Issue**: Webhook creation errors were potentially blocking the OAuth flow completion.

**Solution**: The application now:
- Makes webhook setup completely optional
- Provides detailed error handling and logging
- Never fails OAuth flow due to webhook issues
- Gives clear feedback about webhook status

## Configuration Options

### Development Environment
For local development, webhooks are automatically disabled since localhost URLs don't work with Shopify.

```bash
# In development, these localhost URLs will skip webhook setup
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### Production Environment
For production, you have two options:

#### Option 1: Use ALLOWED_ORIGINS (Automatic)
Set your production domain in ALLOWED_ORIGINS:

```bash
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

The application will automatically use this for webhooks: `https://yourdomain.com/api/v1/shopify/webhooks`

#### Option 2: Explicit Webhook URL (Recommended)
Set a specific webhook base URL:

```bash
WEBHOOK_BASE_URL=https://yourdomain.com
```

This will create webhooks at: `https://yourdomain.com/api/v1/shopify/webhooks`

## Webhook Types

### Core Webhooks (Always Attempted)
These webhooks don't require special permissions:
- `products/create` - New product created
- `products/update` - Product updated
- `products/delete` - Product deleted
- `inventory_levels/update` - Inventory level changed
- `app/uninstalled` - App uninstalled from store

### Order Webhooks (Optional)
These webhooks require protected customer data permissions:
- `orders/create` - New order created
- `orders/updated` - Order updated
- `orders/paid` - Order payment completed
- `orders/cancelled` - Order cancelled

## Webhook Endpoints

The application expects webhooks at these endpoints:
- `POST /api/v1/shopify/webhooks/products_create`
- `POST /api/v1/shopify/webhooks/products_update`
- `POST /api/v1/shopify/webhooks/products_delete`
- `POST /api/v1/shopify/webhooks/inventory_levels_update`
- `POST /api/v1/shopify/webhooks/app_uninstalled`
- `POST /api/v1/shopify/webhooks/orders_create` (if permissions allow)
- `POST /api/v1/shopify/webhooks/orders_updated` (if permissions allow)
- `POST /api/v1/shopify/webhooks/orders_paid` (if permissions allow)
- `POST /api/v1/shopify/webhooks/orders_cancelled` (if permissions allow)

## Troubleshooting

### No Webhooks Created
If you see "No publicly accessible webhook URL configured" in the logs:
1. Check your `ALLOWED_ORIGINS` setting
2. Ensure it contains a public domain (not localhost)
3. Or set `WEBHOOK_BASE_URL` explicitly

### Order Webhook Permissions
If you see "Requires protected customer data permissions" for order webhooks:
1. This is normal for basic Shopify apps
2. Order webhooks are optional and the app works without them
3. To enable order webhooks, you need to request protected customer data access from Shopify

### Webhook Address Not Allowed
If you see "address is not allowed" errors:
1. Ensure your webhook URL is publicly accessible
2. Check that your domain has valid SSL/TLS certificate
3. Verify the URL is reachable from the internet

## Testing Webhooks

### Local Development
For local development, you can use tools like ngrok to create a public tunnel:

```bash
# Install ngrok
npm install -g ngrok

# Create tunnel to your local server
ngrok http 8000

# Use the ngrok URL for webhooks
WEBHOOK_BASE_URL=https://abc123.ngrok.io
```

### Production Testing
1. Deploy your application to a public domain
2. Set the webhook URL in your environment
3. Complete OAuth flow with a test store
4. Check logs for webhook creation status
5. Test webhook endpoints manually if needed

## Security

All webhooks are verified using HMAC signatures with your Shopify client secret. The application automatically:
- Validates webhook signatures
- Rejects unsigned or invalid webhooks
- Logs security events for webhook verification failures

Make sure your `SHOPIFY_CLIENT_SECRET` is properly configured and kept secure.