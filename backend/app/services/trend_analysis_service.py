"""
Trend analysis service using Google Trends API to provide market trend insights for pricing recommendations.
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException, status
from pytrends.request import TrendReq

from app.core.config import settings
from app.core.database import get_supabase_client
from app.core.logging import (
    get_logger,
    log_external_api_call,
    log_error,
    log_business_event,
    LoggerMixin
)
from app.models.product import TrendUpdate


logger = get_logger(__name__)


class GoogleTrendsRateLimiter:
    """Rate limiter for Google Trends API calls using token bucket algorithm."""
    
    def __init__(self, requests_per_minute: int = 30, burst_capacity: int = 5):
        """
        Initialize rate limiter for Google Trends.
        
        Args:
            requests_per_minute: Maximum requests per minute (conservative for Google Trends)
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
            await asyncio.sleep(2.0)  # Longer wait for Google Trends


class GoogleTrendsClient:
    """Google Trends API client with rate limiting and error handling."""
    
    def __init__(self):
        """Initialize Google Trends client."""
        self.rate_limiter = GoogleTrendsRateLimiter()
        self._pytrends = None
        self._last_request_time = 0
        self._min_request_interval = 2.0  # Minimum 2 seconds between requests
    
    def _get_pytrends(self) -> TrendReq:
        """Get or create pytrends instance."""
        if self._pytrends is None:
            self._pytrends = TrendReq(
                hl='en-US',
                tz=360,
                timeout=(10, 25),
                proxies=None,
                retries=2,
                backoff_factor=0.1
            )
        return self._pytrends
    
    async def get_interest_over_time(
        self,
        keywords: List[str],
        timeframe: str = 'today 12-m',
        geo: str = '',
        category: int = 0,
        retry_count: int = 0
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Get interest over time data from Google Trends.
        
        Args:
            keywords: List of keywords to analyze
            timeframe: Time frame for analysis (default: last 12 months)
            geo: Geographic location (empty for worldwide)
            category: Category filter
            retry_count: Current retry attempt
            
        Returns:
            Tuple of trend data and metadata
        """
        await self.rate_limiter.wait_for_tokens()
        
        # Ensure minimum interval between requests
        now = time.time()
        time_since_last = now - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        
        request_start_time = time.time()
        
        try:
            pytrends = self._get_pytrends()
            
            # Build payload
            pytrends.build_payload(
                kw_list=keywords,
                cat=category,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )
            
            # Get interest over time data
            interest_data = pytrends.interest_over_time()
            
            request_duration = time.time() - request_start_time
            self._last_request_time = time.time()
            
            # Log API call
            log_external_api_call(
                service="google_trends",
                endpoint="interest_over_time",
                method="GET",
                status_code=200,
                duration=request_duration,
                retry_count=retry_count,
                keywords=keywords,
                timeframe=timeframe,
                geo=geo
            )
            
            # Convert DataFrame to dict if not empty
            if not interest_data.empty:
                # Remove 'isPartial' column if it exists
                if 'isPartial' in interest_data.columns:
                    interest_data = interest_data.drop('isPartial', axis=1)
                
                trend_data = {
                    'data': interest_data.to_dict('records'),
                    'dates': [date.isoformat() for date in interest_data.index],
                    'keywords': keywords,
                    'max_values': {col: int(interest_data[col].max()) for col in interest_data.columns}
                }
            else:
                trend_data = {
                    'data': [],
                    'dates': [],
                    'keywords': keywords,
                    'max_values': {}
                }
            
            metadata = {
                "request_time": request_start_time,
                "response_time": request_duration,
                "timeframe": timeframe,
                "geo": geo,
                "category": category,
                "keywords_count": len(keywords)
            }
            
            return trend_data, metadata
            
        except Exception as e:
            request_duration = time.time() - request_start_time
            self._last_request_time = time.time()
            
            log_external_api_call(
                service="google_trends",
                endpoint="interest_over_time",
                method="GET",
                status_code=None,
                duration=request_duration,
                retry_count=retry_count,
                error_message=str(e),
                action="request_error",
                keywords=keywords
            )
            
            # Handle rate limiting and retries
            if "429" in str(e) or "rate" in str(e).lower():
                if retry_count < 3:
                    retry_delay = (retry_count + 1) * 30  # Exponential backoff: 30s, 60s, 90s
                    logger.warning(f"Google Trends rate limited, retrying after {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    return await self.get_interest_over_time(keywords, timeframe, geo, category, retry_count + 1)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Google Trends API rate limit exceeded"
                    )
            
            logger.error(f"Google Trends API error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Google Trends API error: {str(e)}"
            )


class TrendScoreCalculator:
    """Utility class for calculating trend scores and assigning labels."""
    
    @staticmethod
    def calculate_trend_momentum(trend_data: List[Dict[str, Any]], keyword: str) -> float:
        """
        Calculate trend momentum based on recent vs historical performance.
        
        Args:
            trend_data: Time series trend data
            keyword: Keyword to analyze
            
        Returns:
            Momentum score (0-100)
        """
        if not trend_data or len(trend_data) < 4:
            return 50.0  # Neutral score for insufficient data
        
        # Extract values for the keyword
        values = []
        for point in trend_data:
            if keyword in point and point[keyword] is not None:
                values.append(point[keyword])
        
        if len(values) < 4:
            return 50.0
        
        # Calculate recent trend (last 25% of data) vs historical average
        split_point = max(1, len(values) // 4)
        recent_values = values[-split_point:]
        historical_values = values[:-split_point] if len(values) > split_point else values
        
        recent_avg = sum(recent_values) / len(recent_values)
        historical_avg = sum(historical_values) / len(historical_values)
        
        # Calculate momentum as percentage change
        if historical_avg > 0:
            momentum = ((recent_avg - historical_avg) / historical_avg) * 100
        else:
            momentum = 0
        
        # Normalize to 0-100 scale
        # Strong positive momentum (+50% or more) = 100
        # Strong negative momentum (-50% or more) = 0
        # No change = 50
        normalized_momentum = max(0, min(100, 50 + momentum))
        
        return normalized_momentum
    
    @staticmethod
    def calculate_google_trend_index(trend_data: Dict[str, Any], keyword: str) -> int:
        """
        Calculate Google Trends index (0-100) based on trend data.
        
        Args:
            trend_data: Google Trends data
            keyword: Primary keyword
            
        Returns:
            Google Trends index (0-100)
        """
        if not trend_data.get('data') or not trend_data.get('max_values'):
            return 50  # Default neutral score
        
        # Get maximum value for the keyword
        max_value = trend_data['max_values'].get(keyword, 0)
        
        # Calculate momentum
        momentum = TrendScoreCalculator.calculate_trend_momentum(trend_data['data'], keyword)
        
        # Combine max popularity with momentum
        # 70% weight on momentum, 30% weight on max popularity
        trend_index = int((momentum * 0.7) + (max_value * 0.3))
        
        return max(0, min(100, trend_index))
    
    @staticmethod
    def generate_mock_social_score() -> int:
        """
        Generate mock social media score for MVP.
        
        Returns:
            Social score (20-80)
        """
        return random.randint(20, 80)
    
    @staticmethod
    def calculate_final_score(google_trend_index: int, social_score: int) -> Decimal:
        """
        Calculate final trend score as weighted combination.
        
        Args:
            google_trend_index: Google Trends index (0-100)
            social_score: Social media score (0-100)
            
        Returns:
            Final score (0-100) as Decimal
        """
        # 60% weight on Google Trends, 40% weight on social score
        final_score = (google_trend_index * 0.6) + (social_score * 0.4)
        return Decimal(str(round(final_score, 2)))
    
    @staticmethod
    def assign_trend_label(final_score: Decimal) -> str:
        """
        Assign trend label based on final score.
        
        Args:
            final_score: Final trend score (0-100)
            
        Returns:
            Trend label: Hot, Rising, Steady, or Declining
        """
        score = float(final_score)
        
        if score >= 80:
            return "Hot"
        elif score >= 60:
            return "Rising"
        elif score >= 40:
            return "Steady"
        else:
            return "Declining"


class TrendAnalysisService(LoggerMixin):
    """Main service for trend analysis and market insights."""
    
    def __init__(self):
        """Initialize trend analysis service."""
        self.supabase_client = get_supabase_client()
        self.google_trends_client = GoogleTrendsClient()
        self.score_calculator = TrendScoreCalculator()
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = 3600  # 1 hour cache TTL
    
    async def analyze_product_trend(
        self,
        shop_id: int,
        sku_code: str,
        product_title: str,
        category: Optional[str] = None,
        brand: Optional[str] = None
    ) -> TrendUpdate:
        """
        Analyze trend for a specific product.
        
        Args:
            shop_id: Store ID
            sku_code: Product SKU code
            product_title: Product title for trend analysis
            category: Optional product category
            brand: Optional product brand
            
        Returns:
            TrendUpdate with trend analysis data
        """
        self.logger.info(
            "Starting product trend analysis",
            shop_id=shop_id,
            sku_code=sku_code,
            product_title=product_title,
            category=category,
            brand=brand
        )
        
        try:
            # Generate search keywords
            keywords = self._generate_search_keywords(product_title, brand, category)
            
            # Check cache first
            cache_key = f"trend_{hash('_'.join(keywords))}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.logger.info("Using cached trend data", cache_key=cache_key)
                return self._create_trend_update_from_cache(sku_code, cached_result)
            
            # Fetch trend data from Google Trends
            trend_data, metadata = await self.google_trends_client.get_interest_over_time(
                keywords=keywords,
                timeframe='today 12-m',
                geo='',  # Worldwide
                category=0
            )
            
            # Calculate trend scores
            primary_keyword = keywords[0]
            google_trend_index = self.score_calculator.calculate_google_trend_index(
                trend_data, primary_keyword
            )
            
            social_score = self.score_calculator.generate_mock_social_score()
            final_score = self.score_calculator.calculate_final_score(
                google_trend_index, social_score
            )
            label = self.score_calculator.assign_trend_label(final_score)
            
            # Create detailed trend information
            trend_details = {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "keywords_analyzed": keywords,
                "google_trends_data": {
                    "timeframe": "12_months",
                    "data_points": len(trend_data.get('data', [])),
                    "max_popularity": trend_data.get('max_values', {}).get(primary_keyword, 0),
                    "trend_momentum": self.score_calculator.calculate_trend_momentum(
                        trend_data.get('data', []), primary_keyword
                    )
                },
                "social_analysis": {
                    "score_type": "mock_mvp",
                    "score_range": "20-80",
                    "note": "Mock social score for MVP - will be replaced with real social media analysis"
                },
                "scoring_methodology": {
                    "google_trends_weight": 0.6,
                    "social_score_weight": 0.4,
                    "momentum_calculation": "recent_25%_vs_historical_average"
                },
                "metadata": metadata
            }
            
            # Cache the result
            cache_data = {
                "google_trend_index": google_trend_index,
                "social_score": social_score,
                "final_score": final_score,
                "label": label,
                "trend_details": trend_details,
                "timestamp": time.time()
            }
            self._set_cache(cache_key, cache_data)
            
            # Create trend update object
            trend_update = TrendUpdate(
                sku_code=sku_code,
                google_trend_index=google_trend_index,
                social_score=social_score,
                final_score=final_score,
                label=label,
                trend_details=trend_details
            )
            
            # Log business event
            log_business_event(
                event_type="trend_analysis_completed",
                shop_id=shop_id,
                sku_code=sku_code,
                google_trend_index=google_trend_index,
                social_score=social_score,
                final_score=float(final_score),
                label=label
            )
            
            self.logger.info(
                "Product trend analysis completed",
                shop_id=shop_id,
                sku_code=sku_code,
                google_trend_index=google_trend_index,
                social_score=social_score,
                final_score=float(final_score),
                label=label
            )
            
            return trend_update
            
        except Exception as e:
            log_error(e, {
                "shop_id": shop_id,
                "sku_code": sku_code,
                "product_title": product_title,
                "operation": "analyze_product_trend"
            })
            raise
    
    async def analyze_multiple_products(
        self,
        shop_id: int,
        products: List[Dict[str, Any]]
    ) -> Dict[str, TrendUpdate]:
        """
        Analyze trends for multiple products in batch.
        
        Args:
            shop_id: Store ID
            products: List of product dictionaries with sku_code, product_title, etc.
            
        Returns:
            Dictionary mapping SKU codes to TrendUpdate objects
        """
        self.logger.info(
            "Starting batch trend analysis",
            shop_id=shop_id,
            product_count=len(products)
        )
        
        results = {}
        
        for i, product in enumerate(products):
            try:
                self.logger.info(f"Analyzing product {i+1}/{len(products)}", sku_code=product.get('sku_code'))
                
                trend_update = await self.analyze_product_trend(
                    shop_id=shop_id,
                    sku_code=product['sku_code'],
                    product_title=product['product_title'],
                    category=product.get('category'),
                    brand=product.get('brand')
                )
                
                results[product['sku_code']] = trend_update
                
                # Add delay between requests to be respectful to Google Trends
                if i < len(products) - 1:  # Don't delay after the last request
                    await asyncio.sleep(3.0)
                
            except Exception as e:
                self.logger.error(
                    f"Failed to analyze trend for product {product.get('sku_code')}",
                    error=str(e)
                )
                # Continue with other products even if one fails
                continue
        
        self.logger.info(
            "Batch trend analysis completed",
            shop_id=shop_id,
            total_products=len(products),
            successful_analyses=len(results),
            failed_analyses=len(products) - len(results)
        )
        
        return results
    
    async def store_trend_insights(
        self,
        shop_id: int,
        trend_updates: List[TrendUpdate]
    ) -> bool:
        """
        Store trend insights in the database.
        
        Args:
            shop_id: Store ID
            trend_updates: List of trend updates to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for trend_update in trend_updates:
                # Prepare data for database insertion
                trend_data = {
                    "shop_id": shop_id,
                    "sku_code": trend_update.sku_code,
                    "google_trend_index": trend_update.google_trend_index,
                    "social_score": trend_update.social_score,
                    "final_score": float(trend_update.final_score),
                    "label": trend_update.label,
                    "trend_details": trend_update.trend_details,
                    "computed_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Insert or update trend insight
                result = self.supabase_client.table("trend_insights").upsert(
                    trend_data,
                    on_conflict="shop_id,sku_code"
                ).execute()
                
                if not result.data:
                    self.logger.error(f"Failed to store trend insight for {trend_update.sku_code}")
                    return False
            
            self.logger.info(
                "Trend insights stored successfully",
                shop_id=shop_id,
                insights_count=len(trend_updates)
            )
            
            return True
            
        except Exception as e:
            log_error(e, {
                "shop_id": shop_id,
                "insights_count": len(trend_updates),
                "operation": "store_trend_insights"
            })
            return False
    
    async def get_trend_insights(
        self,
        shop_id: int,
        sku_code: Optional[str] = None,
        max_age_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Retrieve trend insights from the database.
        
        Args:
            shop_id: Store ID
            sku_code: Optional SKU code filter
            max_age_hours: Maximum age of data in hours
            
        Returns:
            List of trend insight records
        """
        try:
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Build query
            query = self.supabase_client.table("trend_insights").select("*").eq("shop_id", shop_id)
            
            if sku_code:
                query = query.eq("sku_code", sku_code)
            
            query = query.gte("computed_at", cutoff_time.isoformat()).order("computed_at", desc=True)
            
            result = query.execute()
            
            self.logger.info(
                "Retrieved trend insights",
                shop_id=shop_id,
                sku_code=sku_code,
                max_age_hours=max_age_hours,
                insights_count=len(result.data)
            )
            
            return result.data
            
        except Exception as e:
            log_error(e, {
                "shop_id": shop_id,
                "sku_code": sku_code,
                "max_age_hours": max_age_hours,
                "operation": "get_trend_insights"
            })
            return []
    
    async def refresh_trend_data(
        self,
        shop_id: int,
        sku_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Refresh trend data for products.
        
        Args:
            shop_id: Store ID
            sku_codes: Optional list of SKU codes to refresh (if None, refresh all)
            
        Returns:
            Refresh operation results
        """
        try:
            # Get products to refresh
            if sku_codes:
                # Get specific products
                products_query = self.supabase_client.table("products").select(
                    "sku_code, product_title"
                ).eq("shop_id", shop_id).in_("sku_code", sku_codes)
            else:
                # Get all active products
                products_query = self.supabase_client.table("products").select(
                    "sku_code, product_title"
                ).eq("shop_id", shop_id).eq("status", "active")
            
            products_result = products_query.execute()
            products = products_result.data
            
            if not products:
                return {
                    "status": "no_products",
                    "message": "No products found to refresh",
                    "refreshed_count": 0
                }
            
            # Analyze trends for products
            trend_results = await self.analyze_multiple_products(shop_id, products)
            
            # Store the results
            if trend_results:
                trend_updates = list(trend_results.values())
                success = await self.store_trend_insights(shop_id, trend_updates)
                
                return {
                    "status": "success" if success else "partial_success",
                    "message": f"Refreshed trend data for {len(trend_results)} products",
                    "refreshed_count": len(trend_results),
                    "total_products": len(products),
                    "results": {sku: {"label": update.label, "score": float(update.final_score)} 
                              for sku, update in trend_results.items()}
                }
            else:
                return {
                    "status": "failed",
                    "message": "Failed to refresh trend data",
                    "refreshed_count": 0
                }
                
        except Exception as e:
            log_error(e, {
                "shop_id": shop_id,
                "sku_codes": sku_codes,
                "operation": "refresh_trend_data"
            })
            return {
                "status": "error",
                "message": f"Error refreshing trend data: {str(e)}",
                "refreshed_count": 0
            }
    
    def _generate_search_keywords(
        self,
        product_title: str,
        brand: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[str]:
        """
        Generate search keywords for trend analysis.
        
        Args:
            product_title: Product title
            brand: Optional brand name
            category: Optional category
            
        Returns:
            List of search keywords
        """
        keywords = []
        
        # Primary keyword: clean product title
        clean_title = self._clean_product_title(product_title)
        keywords.append(clean_title)
        
        # Add brand + product combination if brand is available
        if brand:
            brand_combo = f"{brand} {clean_title}"
            keywords.append(brand_combo)
        
        # Add category if available and different from title
        if category and category.lower() not in clean_title.lower():
            keywords.append(category)
        
        # Limit to 3 keywords to avoid API limits
        return keywords[:3]
    
    def _clean_product_title(self, title: str) -> str:
        """
        Clean product title for better trend analysis.
        
        Args:
            title: Raw product title
            
        Returns:
            Cleaned title
        """
        # Remove common e-commerce words and symbols
        import re
        
        # Remove size indicators, SKUs, and common suffixes
        cleaned = re.sub(r'\b(size|sz|color|colour|pack|set|piece|pcs|qty|quantity)\b', '', title, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b\d+\s*(ml|l|kg|g|oz|lb|inch|cm|mm)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b[A-Z0-9]{3,}\b', '', cleaned)  # Remove likely SKUs
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)  # Remove special characters
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
        
        # Take first 50 characters to avoid very long search terms
        return cleaned[:50].strip()
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired."""
        if key in self._cache:
            data = self._cache[key]
            if time.time() - data['timestamp'] < self._cache_ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Set data in cache."""
        self._cache[key] = data
    
    def _create_trend_update_from_cache(self, sku_code: str, cached_data: Dict[str, Any]) -> TrendUpdate:
        """Create TrendUpdate from cached data."""
        return TrendUpdate(
            sku_code=sku_code,
            google_trend_index=cached_data['google_trend_index'],
            social_score=cached_data['social_score'],
            final_score=cached_data['final_score'],
            label=cached_data['label'],
            trend_details=cached_data['trend_details']
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the trend analysis service.
        
        Returns:
            Health check status and details
        """
        health_status = {
            "service": "trend_analysis",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        try:
            # Test Google Trends connectivity with a simple query
            test_keywords = ["test"]
            start_time = time.time()
            
            try:
                await self.google_trends_client.get_interest_over_time(
                    keywords=test_keywords,
                    timeframe='today 1-m'
                )
                health_status["checks"]["google_trends"] = {
                    "status": "healthy",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2)
                }
            except Exception as e:
                health_status["checks"]["google_trends"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Test database connectivity
            try:
                db_start = time.time()
                self.supabase_client.table("trend_insights").select("id").limit(1).execute()
                health_status["checks"]["database"] = {
                    "status": "healthy",
                    "response_time_ms": round((time.time() - db_start) * 1000, 2)
                }
            except Exception as e:
                health_status["checks"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "unhealthy"
            
            # Cache status
            health_status["checks"]["cache"] = {
                "status": "healthy",
                "cached_items": len(self._cache),
                "cache_ttl_seconds": self._cache_ttl
            }
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status