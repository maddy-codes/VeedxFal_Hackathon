# Shopify User Guide

This guide helps end users understand and use the Shopify integration features in the Retail AI Advisor platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Connecting Your Shopify Store](#connecting-your-shopify-store)
3. [Managing Connected Stores](#managing-connected-stores)
4. [Product Synchronization](#product-synchronization)
5. [Analytics and Insights](#analytics-and-insights)
6. [Troubleshooting](#troubleshooting)
7. [Frequently Asked Questions](#frequently-asked-questions)

## Getting Started

The Shopify integration allows you to connect your Shopify store to the Retail AI Advisor platform to:

- **Sync Products**: Automatically import and update your product catalog
- **Track Orders**: Monitor sales performance and order analytics
- **Get AI Insights**: Receive intelligent pricing recommendations
- **Real-time Updates**: Keep data synchronized automatically via webhooks
- **Multi-store Support**: Connect and manage multiple Shopify stores

### Prerequisites

Before connecting your Shopify store, ensure you have:

- **Shopify Store**: An active Shopify store with admin access
- **Platform Account**: A registered account on the Retail AI Advisor platform
- **Admin Permissions**: Admin or staff permissions on your Shopify store

## Connecting Your Shopify Store

### Step 1: Navigate to Shopify Integration

1. Log in to your Retail AI Advisor account
2. Go to the **Dashboard**
3. Click on **Shopify** in the navigation menu
4. You'll see the Shopify integration page

### Step 2: Enter Your Store Information

1. In the "Connect Your Shopify Store" section
2. Enter your **Shopify store domain**
   - Enter just the store name (e.g., "my-store")
   - Don't include ".myshopify.com" - it will be added automatically
   - Example: If your store is `awesome-store.myshopify.com`, enter `awesome-store`

### Step 3: Authorize the Connection

1. Click **"Connect to Shopify"**
2. You'll be redirected to Shopify's authorization page
3. Review the permissions requested:
   - **Read products**: To sync your product catalog
   - **Read inventory**: To track stock levels
   - **Read orders**: To analyze sales data
   - **Read price rules**: To understand your pricing strategy
4. Click **"Install app"** to authorize the connection

### Step 4: Complete the Setup

1. You'll be redirected back to the platform
2. Your store will appear in the "Connected Stores" section
3. An initial product sync will start automatically
4. You'll receive a confirmation message

## Managing Connected Stores

### Viewing Connected Stores

In the Shopify dashboard, you can see all your connected stores with:

- **Store Name**: Your Shopify store name
- **Domain**: Your store's Shopify domain
- **Connection Status**: Active/Inactive status
- **Last Sync**: When data was last synchronized
- **Product Count**: Number of synced products
- **Order Count**: Number of tracked orders

### Store Actions

For each connected store, you can:

#### View Store Details
- Click on a store card to see detailed information
- View store statistics and performance metrics
- Check sync job history and status

#### Sync Products
- Click **"Sync Products"** to manually trigger synchronization
- Choose between:
  - **Quick Sync**: Updates only changed products (faster)
  - **Full Sync**: Re-imports all products (more thorough)

#### Disconnect Store
- Click **"Disconnect"** to remove the store connection
- This will stop data synchronization
- Historical data will be preserved

### Store Statistics

Each store shows key metrics:

- **Total Products**: All products in your store
- **Active Products**: Currently published products
- **Total Orders**: All-time order count
- **Recent Orders**: Orders in the last 30 days
- **Total Revenue**: All-time revenue
- **Recent Revenue**: Revenue in the last 30 days

## Product Synchronization

### How Sync Works

The platform synchronizes your Shopify products in two ways:

#### 1. Automatic Sync (Webhooks)
- Real-time updates when you create, update, or delete products
- Happens automatically in the background
- No action required from you

#### 2. Manual Sync
- Triggered by you when needed
- Useful for initial setup or troubleshooting
- Two types available: Quick Sync and Full Sync

### Sync Types

#### Quick Sync (Incremental)
- **When to use**: Regular updates and maintenance
- **What it does**: Only syncs products modified since last sync
- **Duration**: Usually 1-5 minutes
- **Recommended**: For daily/weekly updates

#### Full Sync (Complete)
- **When to use**: Initial setup or after major changes
- **What it does**: Re-imports all products from scratch
- **Duration**: 5-30 minutes depending on product count
- **Recommended**: For troubleshooting or major catalog changes

### Monitoring Sync Progress

1. **Sync Status Indicator**: Shows current sync status
   - 🟢 **Completed**: Sync finished successfully
   - 🟡 **In Progress**: Sync is currently running
   - 🔴 **Failed**: Sync encountered errors
   - ⚪ **Pending**: Sync is queued to start

2. **Sync History**: View past sync jobs
   - Start and completion times
   - Number of products processed
   - Success/failure status
   - Error details if applicable

3. **Real-time Updates**: Progress bar during active syncs

### What Gets Synced

The following product information is synchronized:

#### Basic Product Data
- Product title and description
- Product type and vendor
- Tags and categories
- Handle (URL slug)
- Publication status

#### Pricing Information
- Product price
- Compare-at price
- Cost per item (if available)
- Currency

#### Inventory Data
- Stock quantities
- Inventory tracking status
- SKU information
- Barcode data

#### Product Variants
- Size, color, and other variant options
- Individual variant pricing
- Variant-specific inventory
- Variant images

#### Images and Media
- Product images
- Alt text for images
- Image ordering

## Analytics and Insights

### Product Performance

Once your products are synced, you can access:

#### Sales Analytics
- **Top Performers**: Best-selling products
- **Revenue Trends**: Sales over time
- **Conversion Rates**: Product page performance
- **Inventory Turnover**: How quickly products sell

#### Pricing Insights
- **Competitive Analysis**: How your prices compare
- **Margin Analysis**: Profit margins by product
- **Price Optimization**: AI-powered pricing recommendations
- **Dynamic Pricing**: Suggested price adjustments

#### Inventory Management
- **Stock Levels**: Current inventory status
- **Low Stock Alerts**: Products running low
- **Reorder Points**: When to restock
- **Demand Forecasting**: Predicted future demand

### AI-Powered Recommendations

The platform provides intelligent insights:

#### Pricing Recommendations
- **Optimal Pricing**: AI-suggested prices for maximum profit
- **Competitive Positioning**: Price adjustments based on market data
- **Seasonal Adjustments**: Price changes for seasonal demand
- **Bundle Opportunities**: Products that sell well together

#### Inventory Optimization
- **Reorder Suggestions**: When and how much to restock
- **Slow-Moving Items**: Products that need attention
- **Trend Analysis**: Emerging product trends
- **Demand Patterns**: Customer buying behavior

## Troubleshooting

### Common Issues and Solutions

#### Store Connection Problems

**Issue**: "Failed to connect to Shopify"
**Solutions**:
1. Verify your store domain is correct (just the store name, not the full URL)
2. Ensure you have admin access to the Shopify store
3. Check that your store is active and not password-protected
4. Try connecting again after a few minutes

**Issue**: "Authorization failed"
**Solutions**:
1. Make sure you clicked "Install app" on the Shopify authorization page
2. Check that you're logged into the correct Shopify account
3. Verify your Shopify store has the necessary permissions
4. Clear your browser cache and try again

#### Sync Issues

**Issue**: "Product sync failed"
**Solutions**:
1. Try a manual sync by clicking "Sync Products"
2. Check if your Shopify store is accessible
3. Verify you haven't exceeded API limits
4. Contact support if the issue persists

**Issue**: "Some products missing"
**Solutions**:
1. Run a Full Sync to re-import all products
2. Check if missing products are published in Shopify
3. Verify products meet sync criteria (not archived/deleted)
4. Review sync job logs for specific errors

#### Data Discrepancies

**Issue**: "Product data doesn't match Shopify"
**Solutions**:
1. Trigger a manual sync to update data
2. Check the last sync time - data might be outdated
3. Verify the product was saved properly in Shopify
4. Allow time for webhook updates to process

### Getting Help

If you encounter issues not covered here:

1. **Check Sync Status**: Look for error messages in sync history
2. **Review Store Connection**: Ensure the store is still connected
3. **Try Manual Sync**: Often resolves temporary issues
4. **Contact Support**: Provide specific error messages and store details

### Support Information

When contacting support, please provide:
- Your store domain
- Error messages (exact text)
- When the issue started
- Steps you've already tried
- Screenshots if applicable

## Frequently Asked Questions

### General Questions

**Q: How many Shopify stores can I connect?**
A: You can connect multiple Shopify stores to your account. Each store is managed separately with its own sync settings and analytics.

**Q: Will connecting affect my Shopify store performance?**
A: No, the integration uses Shopify's standard APIs and follows best practices. It won't slow down your store or affect customer experience.

**Q: Can I disconnect my store anytime?**
A: Yes, you can disconnect your store at any time. Historical data will be preserved, but real-time sync will stop.

### Data and Privacy

**Q: What data is accessed from my Shopify store?**
A: We only access the data necessary for the features you use:
- Product information (for catalog sync)
- Order data (for analytics)
- Inventory levels (for stock tracking)
- Customer data is NOT accessed

**Q: Is my data secure?**
A: Yes, all data is encrypted in transit and at rest. We follow industry-standard security practices and comply with data protection regulations.

**Q: Can I control what data is synced?**
A: Currently, all published products are synced. We're working on selective sync options for future releases.

### Sync and Updates

**Q: How often is data updated?**
A: Data is updated in real-time via webhooks when you make changes in Shopify. Manual syncs can be triggered anytime for immediate updates.

**Q: What happens if I change a product in Shopify?**
A: Changes are automatically detected and synced within minutes via webhooks. You'll see updates reflected in the platform shortly after making changes.

**Q: Can I edit product data in the platform?**
A: Currently, the platform is read-only for Shopify data. All changes must be made in your Shopify admin. We're considering two-way sync for future releases.

### Pricing and Features

**Q: Does the Shopify integration cost extra?**
A: The Shopify integration is included with your platform subscription. There are no additional charges for connecting stores or syncing data.

**Q: Are there limits on the number of products?**
A: There are no hard limits on product count. Sync times may be longer for stores with many products (1000+), but all products will be processed.

**Q: What Shopify plans are supported?**
A: The integration works with all Shopify plans, including Basic Shopify, Shopify, and Advanced Shopify. Some features may vary based on your Shopify plan's API access.

### Technical Questions

**Q: What if my store uses a custom domain?**
A: Use your myshopify.com domain for connection (e.g., "my-store" for my-store.myshopify.com). Custom domains are automatically detected after connection.

**Q: Can I use this with Shopify Plus?**
A: Yes, the integration fully supports Shopify Plus stores and takes advantage of enhanced API limits for faster sync.

**Q: What about multi-location inventory?**
A: Multi-location inventory is supported. The platform aggregates inventory across all locations for total stock levels.

---

This user guide provides comprehensive information for using the Shopify integration. For technical setup information, see the [Shopify Setup Guide](./SHOPIFY_SETUP.md). For API details, refer to the [Shopify API Documentation](./SHOPIFY_API.md).