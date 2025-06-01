# Competitor Price Scraping Service

This document provides comprehensive information about the competitor price scraping service implementation using ZenRows API for Amazon product price analysis.

## Overview

The competitor scraping service is designed to:
- Scrape competitor prices from Amazon and other e-commerce sites
- Extract and normalize pricing data from various formats
- Store results in the `competitor_prices` database table
- Provide aggregated pricing insights for the recommendation engine
- Handle rate limiting, retries, and error recovery

## Architecture

### Core Components

1. **ZenRowsApiClient**: Handles API communication with ZenRows service
2. **PriceExtractor**: Extracts and normalizes prices from HTML content
3. **CompetitorScrapingService**: Main service orchestrating the scraping workflow
4. **Rate Limiting**: Token bucket algorithm for API rate limiting

### Database Integration

The service integrates with the existing `competitor_prices` table:
- `shop_id`: Store identifier
- `sku_code`: Product SKU
- `min_price`: Minimum competitor price found
- `max_price`: Maximum competitor price found
- `competitor_count`: Number of competitors with valid prices
- `price_details`: JSON object with detailed scraping results
- `scraped_at`: Timestamp of last scraping operation

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
# ZenRows API Configuration
ZENROWS_API_KEY=your_zenrows_api_key_here
```

The ZenRows API key is already configured in the settings system at `backend/app/core/config.py`.

### ZenRows Setup

1. Sign up for a ZenRows account at https://www.zenrows.com/
2. Get your API key from the dashboard
3. Add the API key to your environment variables
4. The service supports both free and premium ZenRows features

## Usage Examples

### Basic Price Scraping

```python
from app.services.competitor_scraping_service import CompetitorScrapingService

# Initialize the service
service = CompetitorScrapingService()

# Scrape competitor prices for a single product
result = await service.scrape_competitor_prices(
    shop_id=1,
    sku_code="PROD-001",
    competitor_urls=[
        "https://amazon.co.uk/dp/B08N5WRWNW",
        "https://amazon.co.uk/s?k=iphone+15+pro"
    ],
    currency="GBP"
)

print(f"Min Price: {result.min_price}")
print(f"Max Price: {result.max_price}")
print(f"Competitors: {result.competitor_count}")
```

### Batch Processing

```python
# Scrape multiple products at once
product_urls = {
    "PROD-001": [
        "https://amazon.co.uk/dp/B08N5WRWNW",
        "https://amazon.co.uk/s?k=product+1"
    ],
    "PROD-002": [
        "https://amazon.co.uk/dp/B09ABCDEFG",
        "https://amazon.co.uk/s?k=product+2"
    ]
}

results = await service.scrape_multiple_products(
    shop_id=1,
    product_urls=product_urls,
    currency="GBP"
)

for sku, result in results.items():
    print(f"{sku}: {result.min_price} - {result.max_price}")
```

### Retrieving Stored Data

```python
# Get competitor prices from database
prices = await service.get_competitor_prices(
    shop_id=1,
    sku_code="PROD-001",  # Optional: filter by SKU
    max_age_hours=24      # Only get recent data
)

for price_record in prices:
    print(f"SKU: {price_record['sku_code']}")
    print(f"Price Range: {price_record['min_price']} - {price_record['max_price']}")
    print(f"Scraped: {price_record['scraped_at']}")
```

### Amazon URL Generation

```python
# Generate Amazon search URLs automatically
urls = service.generate_amazon_search_urls(
    product_title="iPhone 15 Pro",
    brand="Apple",
    category="Electronics",
    marketplace="amazon.co.uk"
)

print("Generated URLs:", urls)
```

## Price Extraction Features

### Supported Price Formats

The service can extract prices from various formats:

- **Currency symbols**: £29.99, $45.50, €35.00
- **Currency codes**: GBP 29.99, USD 45.50
- **JSON-LD structured data**: Microdata and schema.org formats
- **CSS selectors**: Common e-commerce price classes and IDs

### Extraction Strategies

1. **Regex Patterns**: Multiple regex patterns for different price formats
2. **CSS Selectors**: Common e-commerce price element selectors
3. **Structured Data**: JSON-LD and microdata extraction
4. **Fallback Methods**: Multiple extraction attempts for reliability

### Price Normalization

- Removes currency symbols and formatting
- Converts to Decimal for precision
- Validates reasonable price ranges (£0.01 - £999,999.99)
- Handles comma separators and decimal points

## Rate Limiting and Error Handling

### Rate Limiting

- **Token Bucket Algorithm**: Configurable requests per minute
- **Burst Capacity**: Allows short bursts of requests
- **Automatic Throttling**: Waits for tokens when rate limited

### Error Handling

- **Retry Logic**: Automatic retries for failed requests
- **Graceful Degradation**: Continues processing other URLs on failures
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

### Monitoring

```python
# Health check endpoint
health = await service.health_check()
print(health)
# Output:
# {
#     "service": "competitor_scraping",
#     "status": "healthy",
#     "checks": {
#         "zenrows_api_key": {"status": "ok"},
#         "database": {"status": "ok"},
#         "zenrows_api": {"status": "ok"}
#     }
# }
```

## Testing

### Running Tests

```bash
# Run the test script
cd backend
python test_competitor_scraping.py
```

### Test Coverage

The test script covers:
- Price extraction from HTML content
- ZenRows API client functionality
- Service initialization and health checks
- Database operations
- Full scraping workflow (if API key configured)

### Manual Testing

```python
# Test price extraction
from app.services.competitor_scraping_service import PriceExtractor

extractor = PriceExtractor()
html = '<div class="price">£29.99</div>'
prices = extractor.extract_prices_from_html(html)
print(prices)  # [Decimal('29.99')]
```

## Integration with Pricing Engine

### Data Flow

1. **Product Sync**: Products are synced from Shopify
2. **URL Generation**: Amazon URLs are generated for each product
3. **Price Scraping**: Competitor prices are scraped and stored
4. **Price Analysis**: Recommendation engine uses competitor data
5. **Price Recommendations**: Final pricing recommendations are generated

### Database Schema

```sql
-- competitor_prices table structure
CREATE TABLE competitor_prices (
    id SERIAL PRIMARY KEY,
    shop_id INTEGER NOT NULL,
    sku_code VARCHAR(255) NOT NULL,
    min_price DECIMAL(10,2),
    max_price DECIMAL(10,2),
    competitor_count INTEGER NOT NULL DEFAULT 0,
    price_details JSONB NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(shop_id, sku_code)
);
```

### API Integration

The service can be integrated into API endpoints:

```python
from fastapi import APIRouter
from app.services.competitor_scraping_service import CompetitorScrapingService

router = APIRouter()

@router.post("/scrape-competitors/{shop_id}/{sku_code}")
async def scrape_competitor_prices(shop_id: int, sku_code: str):
    service = CompetitorScrapingService()
    
    # Generate Amazon URLs
    urls = service.generate_amazon_search_urls(
        product_title=product_title,  # From request
        marketplace="amazon.co.uk"
    )
    
    # Scrape prices
    result = await service.scrape_competitor_prices(
        shop_id=shop_id,
        sku_code=sku_code,
        competitor_urls=urls
    )
    
    return result
```

## Performance Considerations

### Optimization Strategies

1. **Batch Processing**: Process multiple products in batches
2. **Caching**: Cache results to avoid unnecessary re-scraping
3. **Selective Scraping**: Only scrape when data is stale
4. **Parallel Processing**: Use asyncio for concurrent requests

### Resource Usage

- **Memory**: Minimal memory usage with streaming HTML parsing
- **Network**: Respects rate limits and uses efficient HTTP client
- **Database**: Optimized queries with proper indexing
- **CPU**: Efficient regex and parsing algorithms

### Scaling Considerations

- **Horizontal Scaling**: Service can run on multiple instances
- **Queue Integration**: Can be integrated with Celery for background processing
- **Load Balancing**: ZenRows handles load balancing automatically
- **Monitoring**: Comprehensive logging for performance monitoring

## Troubleshooting

### Common Issues

1. **API Key Not Configured**
   ```
   Error: ZenRows API key not configured
   Solution: Add ZENROWS_API_KEY to environment variables
   ```

2. **Rate Limiting**
   ```
   Error: ZenRows API rate limit exceeded
   Solution: Reduce scraping frequency or upgrade ZenRows plan
   ```

3. **No Prices Found**
   ```
   Issue: Competitor count is 0
   Solution: Check URL validity and price extraction patterns
   ```

4. **Database Connection Issues**
   ```
   Error: Failed to store competitor prices
   Solution: Check database connection and table schema
   ```

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger("app.services.competitor_scraping_service").setLevel(logging.DEBUG)
```

### Support

- Check ZenRows documentation: https://docs.zenrows.com/
- Review service logs for detailed error information
- Use the health check endpoint to verify service status
- Test individual components using the provided test script

## Security Considerations

### Data Privacy

- No personal data is scraped or stored
- Only public pricing information is collected
- Competitor URLs and pricing data are stored securely

### API Security

- ZenRows API key is stored securely in environment variables
- All API calls are made over HTTPS
- Rate limiting prevents abuse

### Compliance

- Respects robots.txt and website terms of service
- Uses ethical scraping practices
- Implements proper delays between requests

## Future Enhancements

### Planned Features

1. **Multi-Currency Support**: Automatic currency conversion
2. **Price History**: Track price changes over time
3. **Alert System**: Notifications for significant price changes
4. **ML Integration**: Machine learning for better price extraction
5. **Additional Sources**: Support for more e-commerce platforms

### API Improvements

1. **GraphQL Support**: More flexible data querying
2. **Webhook Integration**: Real-time price update notifications
3. **Bulk Operations**: Improved batch processing capabilities
4. **Analytics Dashboard**: Visual insights into competitor pricing

This service provides a robust foundation for competitor price analysis and integrates seamlessly with the existing pricing recommendation system.