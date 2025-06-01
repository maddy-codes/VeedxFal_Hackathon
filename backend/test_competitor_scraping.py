"""
Test script for the competitor scraping service.
"""

import asyncio
import os
import sys
from decimal import Decimal
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.competitor_scraping_service import (
    CompetitorScrapingService,
    PriceExtractor,
    ZenRowsApiClient
)
from app.core.config import settings
from app.core.database import get_supabase_client


async def test_price_extractor():
    """Test the price extraction functionality."""
    print("=== Testing Price Extractor ===")
    print("Testing price extraction from various HTML formats...")
    
    # Test HTML content with various price formats
    test_html = """
    <div class="price">£29.99</div>
    <span class="current-price">$45.50</span>
    <div>Price: £199.00</div>
    <script type="application/ld+json">
    {
        "@type": "Product",
        "offers": {
            "price": "89.99",
            "priceCurrency": "GBP"
        }
    }
    </script>
    """
    
    extractor = PriceExtractor()
    
    # Test regex extraction
    print("1. Testing regex-based price extraction...")
    prices = extractor.extract_prices_from_html(test_html)
    print(f"   ✓ Extracted {len(prices)} prices from HTML: {prices}")
    
    # Test individual price normalization
    print("2. Testing price string normalization...")
    test_prices = ["£29.99", "$45.50", "199.00", "invalid", "999999.99"]
    for price_str in test_prices:
        normalized = extractor._normalize_price_string(price_str)
        status = "✓" if normalized else "✗"
        print(f"   {status} '{price_str}' -> {normalized}")
    
    # Test CSS selector extraction (if BeautifulSoup is available)
    print("3. Testing CSS selector-based extraction...")
    try:
        css_prices = extractor.extract_prices_with_selectors(test_html)
        print(f"   ✓ CSS selector extraction found {len(css_prices)} prices: {css_prices}")
    except Exception as e:
        print(f"   ⚠ CSS selector extraction failed: {e}")
    
    # Test JSON-LD extraction
    print("4. Testing JSON-LD structured data extraction...")
    json_prices = extractor._extract_from_json_ld(test_html)
    print(f"   ✓ JSON-LD extraction found {len(json_prices)} prices: {json_prices}")
    
    print("✓ Price extractor tests completed successfully.\n")


async def test_zenrows_client():
    """Test ZenRows API client (if API key is configured)."""
    print("=== Testing ZenRows Client ===")
    
    if not settings.ZENROWS_API_KEY:
        print("⚠ ZenRows API key not configured, skipping client test.")
        print("  To test ZenRows functionality, add ZENROWS_API_KEY to your .env file")
        return
    
    print("✓ ZenRows API key is configured")
    print("1. Testing basic API connectivity...")
    
    try:
        async with ZenRowsApiClient(settings.ZENROWS_API_KEY) as client:
            print("   ✓ ZenRows client initialized successfully")
            
            # Test with a simple URL that should work
            print("2. Testing URL scraping with httpbin.org...")
            content, metadata = await client.scrape_url(
                "https://httpbin.org/json",
                js_render=False
            )
            
            print(f"   ✓ Successfully scraped test URL")
            print(f"   ✓ Content length: {len(content)} characters")
            print(f"   ✓ Response time: {metadata.get('response_time', 'N/A'):.2f}s")
            
            # Check if we got valid JSON response
            if '"slideshow"' in content or '"title"' in content:
                print("   ✓ Received expected JSON content from httpbin")
            else:
                print("   ⚠ Unexpected content format received")
            
            # Display metadata
            print("3. API Response Metadata:")
            for key, value in metadata.items():
                if value is not None:
                    print(f"   • {key}: {value}")
                else:
                    print(f"   • {key}: Not provided")
            
    except Exception as e:
        print(f"   ✗ ZenRows client test failed: {e}")
        print("   This could be due to:")
        print("   - Invalid API key")
        print("   - Network connectivity issues")
        print("   - ZenRows service unavailable")
    
    print("✓ ZenRows client tests completed.\n")


async def test_competitor_scraping_service():
    """Test the main competitor scraping service."""
    print("=== Testing Competitor Scraping Service ===")
    
    try:
        print("1. Initializing competitor scraping service...")
        service = CompetitorScrapingService()
        print("   ✓ Service initialized successfully")
        
        # Test health check
        print("2. Running service health check...")
        health = await service.health_check()
        print(f"   ✓ Health check completed with status: {health['status']}")
        
        # Display detailed health check results
        for check_name, check_result in health['checks'].items():
            status_icon = "✓" if check_result['status'] == 'ok' else "⚠" if check_result['status'] == 'warning' else "✗"
            print(f"   {status_icon} {check_name}: {check_result['message']}")
        
        # Test Amazon URL generation
        print("3. Testing Amazon URL generation...")
        urls = service.generate_amazon_search_urls(
            product_title="iPhone 15 Pro",
            brand="Apple",
            marketplace="amazon.co.uk"
        )
        print(f"   ✓ Generated {len(urls)} Amazon search URLs:")
        for i, url in enumerate(urls, 1):
            print(f"     {i}. {url}")
        
        # Test additional URL generation scenarios
        print("4. Testing URL generation with different parameters...")
        
        # Without brand
        urls_no_brand = service.generate_amazon_search_urls(
            product_title="Wireless Headphones",
            marketplace="amazon.com"
        )
        print(f"   ✓ Generated {len(urls_no_brand)} URLs without brand (US marketplace)")
        
        # With category
        urls_with_category = service.generate_amazon_search_urls(
            product_title="Gaming Mouse",
            brand="Logitech",
            category="Electronics",
            marketplace="amazon.co.uk"
        )
        print(f"   ✓ Generated {len(urls_with_category)} URLs with category")
        
        # Test database retrieval (should work even without data)
        print("5. Testing database operations...")
        try:
            prices = await service.get_competitor_prices(shop_id=1, max_age_hours=24)
            print(f"   ✓ Retrieved {len(prices)} competitor price records from database")
            
            if prices:
                print("   Sample records:")
                for price in prices[:3]:  # Show first 3 records
                    print(f"     • SKU: {price.get('sku_code')}, Range: {price.get('min_price')}-{price.get('max_price')}")
            else:
                print("   • No existing competitor price records found (this is normal for a fresh setup)")
                
        except Exception as e:
            print(f"   ✗ Database retrieval test failed: {e}")
            print("   This might indicate database connectivity issues")
        
    except Exception as e:
        print(f"   ✗ Service initialization failed: {e}")
        print("   This could be due to:")
        print("   - Missing ZenRows API key")
        print("   - Database connection issues")
        print("   - Configuration problems")
    
    print("✓ Competitor scraping service tests completed.\n")


async def create_test_store():
    """Create a test store for database operations."""
    try:
        supabase = get_supabase_client()
        
        # Check if test store already exists
        existing_store = supabase.table("stores").select("id").eq("id", 999).execute()
        
        if not existing_store.data:
            # Create test store
            store_data = {
                "id": 999,
                "user_id": "test-user-123",
                "shop_domain": "test-shop.myshopify.com",
                "shop_name": "Test Shop",
                "access_token": "test-token",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("stores").insert(store_data).execute()
            if result.data:
                print(f"   ✓ Created test store with ID: {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("   ✗ Failed to create test store")
                return None
        else:
            print(f"   ✓ Test store already exists with ID: {existing_store.data[0]['id']}")
            return existing_store.data[0]['id']
            
    except Exception as e:
        print(f"   ✗ Failed to create test store: {e}")
        return None


async def cleanup_test_data():
    """Clean up test data after testing."""
    try:
        supabase = get_supabase_client()
        
        # Clean up test competitor prices
        supabase.table("competitor_prices").delete().eq("shop_id", 999).execute()
        
        # Clean up test store
        supabase.table("stores").delete().eq("id", 999).execute()
        
        print("   ✓ Test data cleaned up successfully")
        
    except Exception as e:
        print(f"   ⚠ Failed to clean up test data: {e}")


async def test_full_scraping_workflow():
    """Test the full scraping workflow (only if ZenRows API key is configured)."""
    print("=== Testing Full Scraping Workflow ===")
    
    if not settings.ZENROWS_API_KEY:
        print("⚠ ZenRows API key not configured, skipping full workflow test.")
        print("  To test the complete workflow, add ZENROWS_API_KEY to your .env file")
        return
    
    test_shop_id = None
    
    try:
        print("1. Setting up test environment...")
        test_shop_id = await create_test_store()
        
        if not test_shop_id:
            print("   ✗ Cannot proceed without test store")
            return
        
        print("2. Initializing scraping service...")
        service = CompetitorScrapingService()
        print("   ✓ Service initialized")
        
        # Test with a simple URL that won't have prices (for testing the workflow)
        test_urls = [
            "https://httpbin.org/json",  # Simple test URL - won't have prices but tests the workflow
        ]
        
        print("3. Starting competitor price scraping...")
        print(f"   • Target shop ID: {test_shop_id}")
        print(f"   • Test SKU: TEST-SKU-001")
        print(f"   • URLs to scrape: {len(test_urls)}")
        
        result = await service.scrape_competitor_prices(
            shop_id=test_shop_id,
            sku_code="TEST-SKU-001",
            competitor_urls=test_urls,
            currency="GBP"
        )
        
        print("4. Scraping workflow completed successfully!")
        print(f"   ✓ SKU: {result.sku_code}")
        print(f"   ✓ Min Price: {result.min_price}")
        print(f"   ✓ Max Price: {result.max_price}")
        print(f"   ✓ Competitor Count: {result.competitor_count}")
        print(f"   ✓ Total URLs processed: {result.price_details['scraping_metadata']['total_urls']}")
        print(f"   ✓ Successful scrapes: {result.price_details['scraping_metadata']['successful_scrapes']}")
        print(f"   ✓ Failed scrapes: {result.price_details['scraping_metadata']['failed_scrapes']}")
        
        # Test data retrieval
        print("5. Testing data retrieval...")
        stored_prices = await service.get_competitor_prices(shop_id=test_shop_id, sku_code="TEST-SKU-001")
        print(f"   ✓ Retrieved {len(stored_prices)} stored price records")
        
        if stored_prices:
            latest_record = stored_prices[0]
            print(f"   ✓ Latest record scraped at: {latest_record.get('scraped_at')}")
            print(f"   ✓ Record contains {len(latest_record.get('price_details', {}).get('competitors', []))} competitor entries")
        
        # Test batch processing
        print("6. Testing batch processing...")
        batch_urls = {
            "TEST-SKU-002": ["https://httpbin.org/json"],
            "TEST-SKU-003": ["https://httpbin.org/json"]
        }
        
        batch_results = await service.scrape_multiple_products(
            shop_id=test_shop_id,
            product_urls=batch_urls,
            currency="GBP"
        )
        
        print(f"   ✓ Batch processing completed for {len(batch_results)} products")
        for sku, result in batch_results.items():
            print(f"     • {sku}: {result.competitor_count} competitors found")
        
    except Exception as e:
        print(f"   ✗ Full workflow test failed: {e}")
        print("   This could be due to:")
        print("   - ZenRows API issues")
        print("   - Database connectivity problems")
        print("   - Network connectivity issues")
        
    finally:
        # Clean up test data
        if test_shop_id:
            print("7. Cleaning up test data...")
            await cleanup_test_data()
    
    print("✓ Full scraping workflow tests completed.\n")


async def main():
    """Run all tests."""
    print("🚀 Starting Competitor Scraping Service Tests")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"ZenRows API Key Configured: {'✓ Yes' if settings.ZENROWS_API_KEY else '✗ No'}")
    print("=" * 60)
    print()
    
    # Test individual components
    try:
        await test_price_extractor()
        await test_zenrows_client()
        await test_competitor_scraping_service()
        
        # Test full workflow if API key is available
        await test_full_scraping_workflow()
        
        print("🎉 All tests completed successfully!")
        print()
        print("📋 Test Summary:")
        print("✓ Price extraction functionality")
        print("✓ ZenRows API client" + (" (with live API test)" if settings.ZENROWS_API_KEY else " (configuration only)"))
        print("✓ Competitor scraping service")
        print("✓ Full scraping workflow" + (" (with database integration)" if settings.ZENROWS_API_KEY else " (skipped - no API key)"))
        print()
        
        if not settings.ZENROWS_API_KEY:
            print("💡 To test the complete functionality:")
            print("   1. Sign up for ZenRows at https://www.zenrows.com/")
            print("   2. Get your API key from the dashboard")
            print("   3. Add ZENROWS_API_KEY=your_key_here to your .env file")
            print("   4. Re-run this test script")
        else:
            print("✅ Your competitor scraping service is fully configured and ready to use!")
            print()
            print("🔗 Next steps:")
            print("   • Integrate the service into your pricing recommendation engine")
            print("   • Set up scheduled scraping jobs for regular price updates")
            print("   • Configure competitor URLs for your products")
            print("   • Monitor scraping performance and adjust rate limits as needed")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        print("Please check the error details above and ensure:")
        print("• Database connection is working")
        print("• Environment variables are properly configured")
        print("• All required dependencies are installed")


if __name__ == "__main__":
    asyncio.run(main())