"""
Competitor price scraping service using ZenRows API for Amazon product price analysis.
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlparse

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.database import get_supabase_client
from app.core.logging import (
    get_logger,
    log_external_api_call,
    log_error,
    log_business_event,
    LoggerMixin
)
from app.models.product import CompetitorPriceUpdate

logger = get_logger(__name__)


class ZenRowsRateLimiter:
    """Rate limiter for ZenRows API calls using token bucket algorithm."""
    
    def __init__(self, requests_per_minute: int = 60, burst_capacity: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            burst_capacity: Burst capacity for short bursts
        """
        self.requests_per_minute = requests_per_minute
        self.burst_capacity = burst_capacity
        self.tokens = burst_capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False otherwise
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            
            # Refill tokens based on elapsed time
            tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
            self.tokens = min(self.burst_capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> None:
        """Wait until tokens are available."""
        while not await self.acquire(tokens):
            await asyncio.sleep(1.0)


class ZenRowsApiClient:
    """ZenRows API client with rate limiting and error handling."""
    
    def __init__(self, api_key: str):
        """
        Initialize ZenRows API client.
        
        Args:
            api_key: ZenRows API key
        """
        self.api_key = api_key
        self.base_url = "https://api.zenrows.com/v1/"
        self.rate_limiter = ZenRowsRateLimiter()
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def scrape_url(
        self,
        url: str,
        css_selector: Optional[str] = None,
        js_render: bool = True,
        premium_proxy: bool = True,
        retry_count: int = 0
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Scrape a URL using ZenRows API.
        
        Args:
            url: URL to scrape
            css_selector: Optional CSS selector to extract specific elements
            js_render: Whether to render JavaScript
            premium_proxy: Whether to use premium proxy
            retry_count: Current retry attempt
            
        Returns:
            Tuple of scraped content and metadata
        """
        await self.rate_limiter.wait_for_tokens()
        
        params = {
            "apikey": self.api_key,
            "url": url,
            "js_render": "true" if js_render else "false",
            "premium_proxy": "true" if premium_proxy else "false",
            "autoparse": "false",  # We'll parse manually for better control
        }
        
        if css_selector:
            params["css_extractor"] = css_selector
        
        request_start_time = time.time()
        
        try:
            response = await self.client.get(
                f"{self.base_url}",
                params=params
            )
            
            request_duration = time.time() - request_start_time
            
            # Log API call
            log_external_api_call(
                service="zenrows",
                endpoint=url,
                method="GET",
                status_code=response.status_code,
                duration=request_duration,
                retry_count=retry_count,
                js_render=js_render,
                premium_proxy=premium_proxy
            )
            
            if response.status_code == 429:  # Rate limited
                if retry_count < 3:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"ZenRows rate limited, retrying after {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self.scrape_url(url, css_selector, js_render, premium_proxy, retry_count + 1)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="ZenRows API rate limit exceeded"
                    )
            
            response.raise_for_status()
            
            # Extract metadata from headers
            metadata = {
                "credits_used": response.headers.get("zenrows-credits-used"),
                "credits_remaining": response.headers.get("zenrows-credits-remaining"),
                "request_id": response.headers.get("zenrows-request-id"),
                "proxy_country": response.headers.get("zenrows-proxy-country"),
                "response_time": request_duration
            }
            
            return response.text, metadata
            
        except httpx.HTTPStatusError as e:
            request_duration = time.time() - request_start_time
            
            log_external_api_call(
                service="zenrows",
                endpoint=url,
                method="GET",
                status_code=e.response.status_code,
                duration=request_duration,
                retry_count=retry_count,
                error_message=str(e),
                action="http_error"
            )
            
            logger.error(f"ZenRows API error: {e.response.status_code} - {e}")
            
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"ZenRows API error: {e}"
            )
        
        except httpx.RequestError as e:
            request_duration = time.time() - request_start_time
            
            log_external_api_call(
                service="zenrows",
                endpoint=url,
                method="GET",
                status_code=None,
                duration=request_duration,
                retry_count=retry_count,
                error_message=str(e),
                action="request_error"
            )
            
            logger.error(f"ZenRows API request error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ZenRows API unavailable"
            )


class PriceExtractor:
    """Utility class for extracting and normalizing prices from scraped content."""
    
    # Common price patterns for Amazon and other e-commerce sites
    PRICE_PATTERNS = [
        # Amazon UK patterns
        r'£(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'GBP\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*£',
        
        # Amazon US patterns
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD',
        
        # Generic patterns
        r'price["\']?\s*:\s*["\']?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'amount["\']?\s*:\s*["\']?(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'value["\']?\s*:\s*["\']?(\d+(?:,\d{3})*(?:\.\d{2})?)',
    ]
    
    # CSS selectors for common price elements
    PRICE_SELECTORS = [
        # Amazon specific selectors
        '.a-price-whole',
        '.a-price .a-offscreen',
        '.a-price-range',
        '#priceblock_dealprice',
        '#priceblock_ourprice',
        '.a-price.a-text-price.a-size-medium.apexPriceToPay',
        
        # Generic e-commerce selectors
        '.price',
        '.product-price',
        '.current-price',
        '.sale-price',
        '[data-price]',
        '[class*="price"]',
        '[id*="price"]',
    ]
    
    @classmethod
    def extract_prices_from_html(cls, html_content: str) -> List[Decimal]:
        """
        Extract prices from HTML content using multiple strategies.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            List of extracted prices as Decimal objects
        """
        prices = []
        
        # Strategy 1: Regex patterns
        for pattern in cls.PRICE_PATTERNS:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                price = cls._normalize_price_string(match)
                if price:
                    prices.append(price)
        
        # Strategy 2: Look for structured data (JSON-LD, microdata)
        json_ld_prices = cls._extract_from_json_ld(html_content)
        prices.extend(json_ld_prices)
        
        # Remove duplicates and sort
        unique_prices = list(set(prices))
        unique_prices.sort()
        
        return unique_prices
    
    @classmethod
    def extract_prices_with_selectors(cls, html_content: str) -> List[Decimal]:
        """
        Extract prices using CSS selectors (requires BeautifulSoup).
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            List of extracted prices as Decimal objects
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.warning("BeautifulSoup not available, falling back to regex extraction")
            return cls.extract_prices_from_html(html_content)
        
        prices = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for selector in cls.PRICE_SELECTORS:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text:
                        price = cls._normalize_price_string(text)
                        if price:
                            prices.append(price)
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Remove duplicates and sort
        unique_prices = list(set(prices))
        unique_prices.sort()
        
        return unique_prices
    
    @classmethod
    def _normalize_price_string(cls, price_str: str) -> Optional[Decimal]:
        """
        Normalize a price string to a Decimal object.
        
        Args:
            price_str: Raw price string
            
        Returns:
            Normalized price as Decimal or None if invalid
        """
        if not price_str:
            return None
        
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[£$€¥₹,\s]', '', price_str.strip())
        
        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', cleaned)
        
        if not cleaned:
            return None
        
        try:
            price = Decimal(cleaned)
            # Validate reasonable price range (0.01 to 999999.99)
            if 0.01 <= price <= 999999.99:
                return price
        except (InvalidOperation, ValueError):
            pass
        
        return None
    
    @classmethod
    def _extract_from_json_ld(cls, html_content: str) -> List[Decimal]:
        """
        Extract prices from JSON-LD structured data.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            List of extracted prices
        """
        prices = []
        
        # Find JSON-LD scripts
        json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.findall(json_ld_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            try:
                data = json.loads(match.strip())
                extracted_prices = cls._extract_prices_from_json(data)
                prices.extend(extracted_prices)
            except json.JSONDecodeError:
                continue
        
        return prices
    
    @classmethod
    def _extract_prices_from_json(cls, data: Any) -> List[Decimal]:
        """
        Recursively extract prices from JSON data.
        
        Args:
            data: JSON data structure
            
        Returns:
            List of extracted prices
        """
        prices = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in ['price', 'lowprice', 'highprice', 'amount', 'value']:
                    if isinstance(value, (str, int, float)):
                        price = cls._normalize_price_string(str(value))
                        if price:
                            prices.append(price)
                else:
                    prices.extend(cls._extract_prices_from_json(value))
        elif isinstance(data, list):
            for item in data:
                prices.extend(cls._extract_prices_from_json(item))
        
        return prices


class CompetitorScrapingService(LoggerMixin):
    """Main service for competitor price scraping and analysis."""
    
    def __init__(self):
        """Initialize competitor scraping service."""
        if not settings.ZENROWS_API_KEY:
            raise ValueError("ZenRows API key not configured")
        
        self.supabase_client = get_supabase_client()
        self.price_extractor = PriceExtractor()
    
    async def scrape_competitor_prices(
        self,
        shop_id: int,
        sku_code: str,
        competitor_urls: List[str],
        currency: str = "GBP"
    ) -> CompetitorPriceUpdate:
        """
        Scrape competitor prices for a specific product.
        
        Args:
            shop_id: Store ID
            sku_code: Product SKU code
            competitor_urls: List of competitor URLs to scrape
            currency: Target currency for normalization
            
        Returns:
            CompetitorPriceUpdate with aggregated pricing data
        """
        self.logger.info(
            "Starting competitor price scraping",
            shop_id=shop_id,
            sku_code=sku_code,
            competitor_count=len(competitor_urls),
            currency=currency
        )
        
        all_prices = []
        price_details = {
            "scraped_at": datetime.utcnow().isoformat(),
            "currency": currency,
            "competitors": [],
            "scraping_metadata": {
                "total_urls": len(competitor_urls),
                "successful_scrapes": 0,
                "failed_scrapes": 0,
                "total_prices_found": 0
            }
        }
        
        async with ZenRowsApiClient(settings.ZENROWS_API_KEY) as client:
            for i, url in enumerate(competitor_urls):
                try:
                    self.logger.info(f"Scraping competitor {i+1}/{len(competitor_urls)}", url=url)
                    
                    # Scrape the URL
                    html_content, metadata = await client.scrape_url(
                        url=url,
                        js_render=True,
                        premium_proxy=True
                    )
                    
                    # Extract prices from the content
                    extracted_prices = self.price_extractor.extract_prices_from_html(html_content)
                    
                    # Try CSS selector extraction as fallback
                    if not extracted_prices:
                        extracted_prices = self.price_extractor.extract_prices_with_selectors(html_content)
                    
                    competitor_data = {
                        "url": url,
                        "prices_found": [float(p) for p in extracted_prices],
                        "price_count": len(extracted_prices),
                        "scraping_metadata": metadata,
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                    
                    price_details["competitors"].append(competitor_data)
                    all_prices.extend(extracted_prices)
                    
                    price_details["scraping_metadata"]["successful_scrapes"] += 1
                    price_details["scraping_metadata"]["total_prices_found"] += len(extracted_prices)
                    
                    self.logger.info(
                        "Successfully scraped competitor",
                        url=url,
                        prices_found=len(extracted_prices),
                        credits_used=metadata.get("credits_used")
                    )
                    
                    # Small delay between requests to be respectful
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    self.logger.error(f"Failed to scrape competitor URL: {url}", error=str(e))
                    log_error(e, context={"url": url, "shop_id": shop_id, "sku_code": sku_code})
                    
                    price_details["competitors"].append({
                        "url": url,
                        "error": str(e),
                        "scraped_at": datetime.utcnow().isoformat()
                    })
                    
                    price_details["scraping_metadata"]["failed_scrapes"] += 1
        
        # Calculate aggregated pricing data
        min_price = min(all_prices) if all_prices else None
        max_price = max(all_prices) if all_prices else None
        competitor_count = len([c for c in price_details["competitors"] if "prices_found" in c and c["prices_found"]])
        
        # Create competitor price update
        competitor_price_update = CompetitorPriceUpdate(
            sku_code=sku_code,
            min_price=min_price,
            max_price=max_price,
            competitor_count=competitor_count,
            price_details=price_details
        )
        
        # Store in database
        await self._store_competitor_prices(shop_id, competitor_price_update)
        
        # Log business event
        log_business_event(
            event_type="competitor_prices_scraped",
            shop_id=shop_id,
            sku_code=sku_code,
            competitor_count=competitor_count,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None,
            total_prices_found=len(all_prices)
        )
        
        self.logger.info(
            "Completed competitor price scraping",
            shop_id=shop_id,
            sku_code=sku_code,
            competitor_count=competitor_count,
            min_price=min_price,
            max_price=max_price,
            total_prices_found=len(all_prices)
        )
        
        return competitor_price_update
    
    async def scrape_multiple_products(
        self,
        shop_id: int,
        product_urls: Dict[str, List[str]],
        currency: str = "GBP"
    ) -> Dict[str, CompetitorPriceUpdate]:
        """
        Scrape competitor prices for multiple products.
        
        Args:
            shop_id: Store ID
            product_urls: Dictionary mapping SKU codes to competitor URLs
            currency: Target currency for normalization
            
        Returns:
            Dictionary mapping SKU codes to CompetitorPriceUpdate objects
        """
        results = {}
        
        for sku_code, urls in product_urls.items():
            try:
                result = await self.scrape_competitor_prices(
                    shop_id=shop_id,
                    sku_code=sku_code,
                    competitor_urls=urls,
                    currency=currency
                )
                results[sku_code] = result
                
                # Small delay between products
                await asyncio.sleep(2.0)
                
            except Exception as e:
                self.logger.error(f"Failed to scrape prices for SKU {sku_code}", error=str(e))
                log_error(e, context={"sku_code": sku_code, "shop_id": shop_id})
        
        return results
    
    async def _store_competitor_prices(
        self,
        shop_id: int,
        competitor_price_update: CompetitorPriceUpdate
    ) -> None:
        """
        Store competitor prices in the database.
        
        Args:
            shop_id: Store ID
            competitor_price_update: Competitor price data to store
        """
        try:
            # Check if record exists
            existing_result = self.supabase_client.table("competitor_prices").select("id").eq(
                "shop_id", shop_id
            ).eq("sku_code", competitor_price_update.sku_code).execute()
            
            data = {
                "shop_id": shop_id,
                "sku_code": competitor_price_update.sku_code,
                "min_price": float(competitor_price_update.min_price) if competitor_price_update.min_price else None,
                "max_price": float(competitor_price_update.max_price) if competitor_price_update.max_price else None,
                "competitor_count": competitor_price_update.competitor_count,
                "price_details": competitor_price_update.price_details,
                "scraped_at": datetime.utcnow().isoformat()
            }
            
            if existing_result.data:
                # Update existing record
                result = self.supabase_client.table("competitor_prices").update(data).eq(
                    "shop_id", shop_id
                ).eq("sku_code", competitor_price_update.sku_code).execute()
            else:
                # Insert new record
                data["created_at"] = datetime.utcnow().isoformat()
                result = self.supabase_client.table("competitor_prices").insert(data).execute()
            
            if not result.data:
                raise Exception("Failed to store competitor prices in database")
            
            self.logger.info(
                "Stored competitor prices in database",
                shop_id=shop_id,
                sku_code=competitor_price_update.sku_code,
                record_id=result.data[0].get("id") if result.data else None
            )
            
        except Exception as e:
            self.logger.error("Failed to store competitor prices", error=str(e))
            log_error(e, context={
                "shop_id": shop_id,
                "sku_code": competitor_price_update.sku_code
            })
            raise
    
    async def get_competitor_prices(
        self,
        shop_id: int,
        sku_code: Optional[str] = None,
        max_age_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Retrieve competitor prices from the database.
        
        Args:
            shop_id: Store ID
            sku_code: Optional SKU code filter
            max_age_hours: Maximum age of data in hours
            
        Returns:
            List of competitor price records
        """
        try:
            query = self.supabase_client.table("competitor_prices").select("*").eq("shop_id", shop_id)
            
            if sku_code:
                query = query.eq("sku_code", sku_code)
            
            # Filter by age
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            query = query.gte("scraped_at", cutoff_time.isoformat())
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            self.logger.error("Failed to retrieve competitor prices", error=str(e))
            log_error(e, context={"shop_id": shop_id, "sku_code": sku_code})
            return []
    
    def generate_amazon_search_urls(
        self,
        product_title: str,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        marketplace: str = "amazon.co.uk"
    ) -> List[str]:
        """
        Generate Amazon search URLs for a product.
        
        Args:
            product_title: Product title to search for
            brand: Optional brand name
            category: Optional category
            marketplace: Amazon marketplace domain
            
        Returns:
            List of Amazon search URLs
        """
        urls = []
        base_url = f"https://{marketplace}/s"
        
        # Basic search with product title
        params = {"k": product_title}
        urls.append(f"{base_url}?{urlencode(params)}")
        
        # Search with brand if provided
        if brand:
            params = {"k": f"{brand} {product_title}"}
            urls.append(f"{base_url}?{urlencode(params)}")
        
        # Search with category if provided
        if category:
            params = {"k": product_title, "rh": f"n:{category}"}
            urls.append(f"{base_url}?{urlencode(params)}")
        
        return urls
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the scraping service.
        
        Returns:
            Health check status
        """
        health_status = {
            "service": "competitor_scraping",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Check ZenRows API key
        health_status["checks"]["zenrows_api_key"] = {
            "status": "ok" if settings.ZENROWS_API_KEY else "error",
            "message": "API key configured" if settings.ZENROWS_API_KEY else "API key not configured"
        }
        
        # Check database connection
        try:
            result = self.supabase_client.table("competitor_prices").select("id").limit(1).execute()
            health_status["checks"]["database"] = {
                "status": "ok",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "error",
                "message": f"Database connection failed: {str(e)}"
            }
            health_status["status"] = "unhealthy"
        
        # Test ZenRows API (optional, only if API key is configured)
        if settings.ZENROWS_API_KEY:
            try:
                async with ZenRowsApiClient(settings.ZENROWS_API_KEY) as client:
                    # Test with a simple URL
                    await client.scrape_url("https://httpbin.org/json", js_render=False)
                health_status["checks"]["zenrows_api"] = {
                    "status": "ok",
                    "message": "ZenRows API accessible"
                }
            except Exception as e:
                health_status["checks"]["zenrows_api"] = {
                    "status": "warning",
                    "message": f"ZenRows API test failed: {str(e)}"
                }
        
        return health_status