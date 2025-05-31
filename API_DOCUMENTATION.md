# API Documentation

This document provides comprehensive documentation for the Retail AI Advisor backend API.

## 📋 Overview

The Retail AI Advisor API is built with FastAPI and provides endpoints for product management, analytics, video insights, and platform integrations.

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://app-retail-ai-advisor-backend.azurewebsites.net`

### API Version
- **Current Version**: `v1`
- **Base Path**: `/api/v1`

### Authentication
All protected endpoints require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

## 🔐 Authentication Endpoints

### POST /api/v1/auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
 
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company_name": "Acme Corp",
    "role": "user",
    "subscription_tier": "pro"
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Invalid credentials
- `422`: Validation error

### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company_name": "Acme Corp",
    "role": "user",
    "subscription_tier": "free"
  }
}
```

### POST /api/v1/auth/refresh
Refresh JWT token.

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response:**
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /api/v1/auth/logout
Logout user and invalidate token.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## 📦 Product Endpoints

### GET /api/v1/products
Retrieve user's products with optional filtering and pagination.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 20, max: 100)
- `search` (string, optional): Search term for product name/SKU
- `category` (string, optional): Filter by category
- `platform` (string, optional): Filter by platform (shopify, woocommerce, manual)
- `status` (string, optional): Filter by status (active, inactive)
- `sort_by` (string, optional): Sort field (name, price, created_at)
- `sort_order` (string, optional): Sort order (asc, desc)

**Response:**
```json
{
  "products": [
    {
      "id": "uuid",
      "name": "Premium Wireless Headphones",
      "description": "High-quality wireless headphones with noise cancellation",
      "sku": "WH-001",
      "price": 299.99,
      "cost": 150.00,
      "category": "Electronics",
      "brand": "TechBrand",
      "inventory_count": 45,
      "platform": "shopify",
      "platform_id": "12345",
      "image_url": "https://example.com/image.jpg",
      "status": "active",
      "metadata": {
        "weight": "250g",
        "color": "Black"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

### POST /api/v1/products
Create a new product.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "name": "Premium Wireless Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "sku": "WH-001",
  "price": 299.99,
  "cost": 150.00,
  "category": "Electronics",
  "brand": "TechBrand",
  "inventory_count": 45,
  "platform": "manual",
  "image_url": "https://example.com/image.jpg",
  "metadata": {
    "weight": "250g",
    "color": "Black"
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Premium Wireless Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "sku": "WH-001",
  "price": 299.99,
  "cost": 150.00,
  "category": "Electronics",
  "brand": "TechBrand",
  "inventory_count": 45,
  "platform": "manual",
  "platform_id": null,
  "image_url": "https://example.com/image.jpg",
  "status": "active",
  "metadata": {
    "weight": "250g",
    "color": "Black"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### GET /api/v1/products/{product_id}
Retrieve a specific product by ID.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `product_id` (UUID): Product identifier

**Response:**
```json
{
  "id": "uuid",
  "name": "Premium Wireless Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "sku": "WH-001",
  "price": 299.99,
  "cost": 150.00,
  "category": "Electronics",
  "brand": "TechBrand",
  "inventory_count": 45,
  "platform": "shopify",
  "platform_id": "12345",
  "image_url": "https://example.com/image.jpg",
  "status": "active",
  "metadata": {
    "weight": "250g",
    "color": "Black"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

### PUT /api/v1/products/{product_id}
Update an existing product.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `product_id` (UUID): Product identifier

**Request Body:**
```json
{
  "name": "Premium Wireless Headphones v2",
  "price": 349.99,
  "cost": 175.00,
  "inventory_count": 30
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Premium Wireless Headphones v2",
  "description": "High-quality wireless headphones with noise cancellation",
  "sku": "WH-001",
  "price": 349.99,
  "cost": 175.00,
  "category": "Electronics",
  "brand": "TechBrand",
  "inventory_count": 30,
  "platform": "shopify",
  "platform_id": "12345",
  "image_url": "https://example.com/image.jpg",
  "status": "active",
  "metadata": {
    "weight": "250g",
    "color": "Black"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-25T09:15:00Z"
}
```

### DELETE /api/v1/products/{product_id}
Delete a product.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `product_id` (UUID): Product identifier

**Response:**
```json
{
  "message": "Product deleted successfully"
}
```

### GET /api/v1/products/{product_id}/pricing-suggestions
Get AI-powered pricing suggestions for a product.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `product_id` (UUID): Product identifier

**Query Parameters:**
- `margin_target` (float, optional): Target profit margin percentage
- `competitor_analysis` (bool, optional): Include competitor analysis

**Response:**
```json
{
  "product_id": "uuid",
  "current_price": 299.99,
  "current_cost": 150.00,
  "current_margin": 50.0,
  "suggestions": [
    {
      "strategy": "cost_plus",
      "suggested_price": 325.00,
      "margin": 53.8,
      "reasoning": "Based on 2.17x cost multiplier for optimal margin"
    },
    {
      "strategy": "market_competitive",
      "suggested_price": 289.99,
      "margin": 48.3,
      "reasoning": "Competitive pricing based on market analysis"
    },
    {
      "strategy": "premium_positioning",
      "suggested_price": 399.99,
      "margin": 62.5,
      "reasoning": "Premium positioning for high-quality features"
    }
  ],
  "market_analysis": {
    "average_market_price": 295.00,
    "price_range": {
      "min": 199.99,
      "max": 499.99
    },
    "competitor_count": 15
  },
  "generated_at": "2024-01-25T10:30:00Z"
}
```

## 📊 Analytics Endpoints

### GET /api/v1/analytics/dashboard
Get dashboard analytics summary.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `period` (string, optional): Time period (7d, 30d, 90d, 1y) (default: 30d)
- `product_ids` (array, optional): Filter by specific product IDs

**Response:**
```json
{
  "summary": {
    "total_products": 150,
    "total_revenue": 45750.00,
    "total_orders": 234,
    "average_order_value": 195.51,
    "top_performing_category": "Electronics",
    "growth_rate": 12.5
  },
  "revenue_trend": [
    {
      "date": "2024-01-01",
      "revenue": 1250.00,
      "orders": 8
    },
    {
      "date": "2024-01-02",
      "revenue": 1875.00,
      "orders": 12
    }
  ],
  "top_products": [
    {
      "product_id": "uuid",
      "name": "Premium Wireless Headphones",
      "revenue": 5999.85,
      "units_sold": 20,
      "growth_rate": 15.2
    }
  ],
  "category_performance": [
    {
      "category": "Electronics",
      "revenue": 25000.00,
      "percentage": 54.6
    },
    {
      "category": "Accessories",
      "revenue": 12500.00,
      "percentage": 27.3
    }
  ],
  "period": "30d",
  "generated_at": "2024-01-25T10:30:00Z"
}
```

### GET /api/v1/analytics/products/{product_id}
Get detailed analytics for a specific product.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `product_id` (UUID): Product identifier

**Query Parameters:**
- `period` (string, optional): Time period (7d, 30d, 90d, 1y) (default: 30d)

**Response:**
```json
{
  "product_id": "uuid",
  "product_name": "Premium Wireless Headphones",
  "metrics": {
    "total_revenue": 5999.85,
    "units_sold": 20,
    "average_selling_price": 299.99,
    "total_views": 1250,
    "conversion_rate": 1.6,
    "return_rate": 2.5
  },
  "trends": {
    "sales": [
      {
        "date": "2024-01-01",
        "units_sold": 2,
        "revenue": 599.98
      }
    ],
    "views": [
      {
        "date": "2024-01-01",
        "views": 45
      }
    ]
  },
  "insights": [
    "Sales increased 15% compared to previous period",
    "Conversion rate is above category average",
    "Consider increasing inventory based on demand trend"
  ],
  "period": "30d",
  "generated_at": "2024-01-25T10:30:00Z"
}
```

### POST /api/v1/analytics/events
Record analytics events.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "events": [
    {
      "product_id": "uuid",
      "event_type": "view",
      "timestamp": "2024-01-25T10:30:00Z",
      "metadata": {
        "source": "search",
        "user_agent": "Mozilla/5.0..."
      }
    },
    {
      "product_id": "uuid",
      "event_type": "purchase",
      "value": 299.99,
      "quantity": 1,
      "timestamp": "2024-01-25T11:15:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Events recorded successfully",
  "events_processed": 2
}
```

## 🎥 Video Insights Endpoints

### POST /api/v1/video/upload
Upload a video for analysis.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (file): Video file (max 100MB)
- `product_id` (UUID, optional): Associated product ID
- `title` (string, optional): Video title
- `description` (string, optional): Video description

**Response:**
```json
{
  "video_id": "uuid",
  "upload_url": "https://storage.example.com/video.mp4",
  "status": "uploaded",
  "processing_started": true,
  "estimated_completion": "2024-01-25T11:00:00Z"
}
```

### GET /api/v1/video/{video_id}/insights
Get video analysis insights.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `video_id` (UUID): Video identifier

**Response:**
```json
{
  "video_id": "uuid",
  "product_id": "uuid",
  "video_url": "https://storage.example.com/video.mp4",
  "processing_status": "completed",
  "transcript": "Welcome to our product demonstration...",
  "insights": {
    "sentiment_analysis": {
      "overall_sentiment": "positive",
      "confidence": 0.85,
      "key_emotions": ["excitement", "trust", "satisfaction"]
    },
    "key_topics": [
      {
        "topic": "product_features",
        "confidence": 0.92,
        "mentions": 8
      },
      {
        "topic": "pricing",
        "confidence": 0.78,
        "mentions": 3
      }
    ],
    "engagement_metrics": {
      "speaking_pace": "optimal",
      "clarity_score": 0.89,
      "energy_level": "high"
    }
  },
  "recommendations": [
    {
      "type": "content_optimization",
      "priority": "high",
      "suggestion": "Emphasize unique features more prominently",
      "impact": "Could increase conversion by 15-20%"
    },
    {
      "type": "pricing_strategy",
      "priority": "medium",
      "suggestion": "Consider highlighting value proposition",
      "impact": "May reduce price sensitivity"
    }
  ],
  "created_at": "2024-01-25T10:30:00Z",
  "updated_at": "2024-01-25T10:45:00Z"
}
```

### GET /api/v1/video/insights
Get all video insights for the user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 20)
- `product_id` (UUID, optional): Filter by product
- `status` (string, optional): Filter by processing status

**Response:**
```json
{
  "insights": [
    {
      "video_id": "uuid",
      "product_id": "uuid",
      "product_name": "Premium Wireless Headphones",
      "video_url": "https://storage.example.com/video.mp4",
      "processing_status": "completed",
      "overall_sentiment": "positive",
      "key_recommendations_count": 3,
      "created_at": "2024-01-25T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 25,
    "pages": 2
  }
}
```

## 🔄 Sync Endpoints

### POST /api/v1/sync/shopify
Initiate Shopify product sync.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "shop_domain": "mystore.myshopify.com",
  "access_token": "shopify_access_token",
  "sync_options": {
    "include_variants": true,
    "include_images": true,
    "include_inventory": true,
    "category_mapping": {
      "Electronics": "Tech Products"
    }
  }
}
```

**Response:**
```json
{
  "sync_job_id": "uuid",
  "status": "started",
  "estimated_duration": "5-10 minutes",
  "started_at": "2024-01-25T10:30:00Z"
}
```

### POST /api/v1/sync/woocommerce
Initiate WooCommerce product sync.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "store_url": "https://mystore.com",
  "consumer_key": "ck_...",
  "consumer_secret": "cs_...",
  "sync_options": {
    "include_variations": true,
    "include_images": true,
    "include_stock": true
  }
}
```

**Response:**
```json
{
  "sync_job_id": "uuid",
  "status": "started",
  "estimated_duration": "3-8 minutes",
  "started_at": "2024-01-25T10:30:00Z"
}
```

### GET /api/v1/sync/jobs/{job_id}
Get sync job status.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `job_id` (UUID): Sync job identifier

**Response:**
```json
{
  "job_id": "uuid",
  "platform": "shopify",
  "status": "completed",
  "started_at": "2024-01-25T10:30:00Z",
  "completed_at": "2024-01-25T10:37:00Z",
  "products_synced": 150,
  "products_created": 25,
  "products_updated": 125,
  "errors": [],
  "summary": {
    "total_products_found": 150,
    "successful_syncs": 150,
    "failed_syncs": 0,
    "duration_seconds": 420
  }
}
```

### GET /api/v1/sync/jobs
Get sync job history.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 20)
- `platform` (string, optional): Filter by platform
- `status` (string, optional): Filter by status

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "uuid",
      "platform": "shopify",
      "status": "completed",
      "started_at": "2024-01-25T10:30:00Z",
      "completed_at": "2024-01-25T10:37:00Z",
      "products_synced": 150,
      "duration_seconds": 420
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 10,
    "pages": 1
  }
}
```

## 📤 Upload Endpoints

### POST /api/v1/upload/image
Upload product image.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (file): Image file (max 10MB, jpg/png/webp)
- `product_id` (UUID, optional): Associated product ID

**Response:**
```json
{
  "image_id": "uuid",
  "url": "https://storage.example.com/images/product-image.jpg",
  "thumbnail_url": "https://storage.example.com/images/product-image-thumb.jpg",
  "size": 2048576,
  "format": "jpeg",
  "dimensions": {
    "width": 1920,
    "height": 1080
  },
  "uploaded_at": "2024-01-25T10:30:00Z"
}
```

### POST /api/v1/upload/csv
Upload products via CSV file.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (file): CSV file with product data
- `mapping` (JSON, optional): Column mapping configuration

**CSV Format:**
```csv
name,sku,price,cost,category,brand,description,inventory_count
"Premium Wireless Headphones","WH-001",299.99,150.00,"Electronics","TechBrand","High-quality headphones",45
```

**Response:**
```json
{
  "upload_id": "uuid",
  "status": "processing",
  "total_rows": 150,
  "valid_rows": 148,
  "invalid_rows": 2,
  "errors": [
    {
      "row": 5,
      "error": "Invalid price format"
    },
    {
      "row": 12,
      "error": "Missing required field: name"
    }
  ],
  "estimated_completion": "2024-01-25T10:35:00Z"
}
```

## 🏥 Health & Utility Endpoints

### GET /health
Health check endpoint (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-25T10:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": "healthy"
  }
}
```

### GET /api/v1/user/profile
Get current user profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "role": "user",
  "subscription_tier": "pro",
  "subscription_expires": "2024-12-31T23:59:59Z",
  "usage_stats": {
    "products_count": 150,
    "api_calls_this_month": 2500,
    "storage_used_mb": 125.5
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-20T14:30:00Z"
}
```

### PUT /api/v1/user/profile
Update user profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "full_name": "John Smith",
  "company_name": "Acme Corporation"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Smith",
  "company_name": "Acme Corporation",
  "role": "user",
  "subscription_tier": "pro",
  "updated_at": "2024-01-25T10:30:00Z"
}
```

## 📊 Rate Limiting

All API endpoints are subject to rate limiting:

- **Free Tier**: 100 requests per minute
- **Pro Tier**: 1000 requests per minute
- **Enterprise Tier**: 5000 requests per minute

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643123400
```

## ❌ Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "price",
        "message": "Price must be a positive number"
      }
    ],
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## 🔧 SDK Examples

### Python SDK Example
```python
import requests

class RetailAIClient:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_products(self, page=1, limit=20):
        response = requests.get(
            f"{self.api_url}/api/v1/products",
            headers=self.headers,
            params={"page": page, "limit": limit}
        )
        return response.json()
    
    def create_product(self, product_data):
        response = requests.post(
            f"{self.api_url}/api/v1/products",
            headers=self.headers,
            json=product_data
        )
        return response.json()

# Usage
client = RetailAIClient("https://api.retailaiadvisor.com", "your_token")
products = client.get_products(page=1, limit=10)
```

### JavaScript SDK Example
```javascript
class RetailAIClient {
  constructor(apiUrl, token) {
    this.apiUrl = apiUrl;
    this.headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  async getProducts(page = 1, limit = 20) {
    const response = await fetch(
      `${this.apiUrl}/api/v1/products?page=${page}&limit=${limit}`,
      { headers: this.headers }
    );
    return response.json();
  }

  async createProduct(productData) {
    const response = await fetch(
      `${this.apiUrl}/api/v1/products`,
      {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(productData)
      }
    );
    return response.json();
  }
}

// Usage
const client = new RetailAIClient('https://api.retailaiadvisor.com', 'your_token');
const products = await client.getProducts(1, 10);
```

## 📝 Changelog

### v1.0.0 (2024-01-25)
- Initial API release
- Authentication endpoints
- Product management
- Analytics dashboard
- Video insights
- Platform sync capabilities
- File upload functionality

---

For additional support or questions about the API, please refer to the [User Guide](./USER_GUIDE.md) or contact our support team.