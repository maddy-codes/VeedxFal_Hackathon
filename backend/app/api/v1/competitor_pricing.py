"""
API endpoints for competitor pricing functionality.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.product import CompetitorPriceUpdate
from app.services.competitor_scraping_service import CompetitorScrapingService

router = APIRouter()


class CompetitorScrapeRequest(BaseModel):
    """Request model for competitor price scraping."""
    sku_code: str = Field(..., description="Product SKU code")
    competitor_urls: List[str] = Field(..., description="List of competitor URLs to scrape")
    currency: str = Field(default="GBP", description="Target currency for price normalization")


class BatchScrapeRequest(BaseModel):
    """Request model for batch competitor price scraping."""
    product_urls: Dict[str, List[str]] = Field(..., description="Dictionary mapping SKU codes to competitor URLs")
    currency: str = Field(default="GBP", description="Target currency for price normalization")


class AmazonUrlRequest(BaseModel):
    """Request model for Amazon URL generation."""
    product_title: str = Field(..., description="Product title to search for")
    brand: Optional[str] = Field(default=None, description="Product brand")
    category: Optional[str] = Field(default=None, description="Product category")
    marketplace: str = Field(default="amazon.co.uk", description="Amazon marketplace domain")


@router.post("/scrape/{shop_id}", response_model=CompetitorPriceUpdate)
async def scrape_competitor_prices(
    shop_id: int,
    request: CompetitorScrapeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Scrape competitor prices for a specific product.
    
    Args:
        shop_id: Store ID
        request: Scraping request parameters
        current_user: Current authenticated user
        
    Returns:
        CompetitorPriceUpdate with scraped pricing data
    """
    try:
        service = CompetitorScrapingService()
        
        result = await service.scrape_competitor_prices(
            shop_id=shop_id,
            sku_code=request.sku_code,
            competitor_urls=request.competitor_urls,
            currency=request.currency
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape competitor prices: {str(e)}"
        )


@router.post("/scrape-batch/{shop_id}")
async def scrape_competitor_prices_batch(
    shop_id: int,
    request: BatchScrapeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Scrape competitor prices for multiple products in batch.
    
    Args:
        shop_id: Store ID
        request: Batch scraping request parameters
        current_user: Current authenticated user
        
    Returns:
        Dictionary mapping SKU codes to CompetitorPriceUpdate objects
    """
    try:
        service = CompetitorScrapingService()
        
        results = await service.scrape_multiple_products(
            shop_id=shop_id,
            product_urls=request.product_urls,
            currency=request.currency
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape competitor prices in batch: {str(e)}"
        )


@router.get("/prices/{shop_id}")
async def get_competitor_prices(
    shop_id: int,
    sku_code: Optional[str] = None,
    max_age_hours: int = 24,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve stored competitor prices from the database.
    
    Args:
        shop_id: Store ID
        sku_code: Optional SKU code filter
        max_age_hours: Maximum age of data in hours
        current_user: Current authenticated user
        
    Returns:
        List of competitor price records
    """
    try:
        service = CompetitorScrapingService()
        
        prices = await service.get_competitor_prices(
            shop_id=shop_id,
            sku_code=sku_code,
            max_age_hours=max_age_hours
        )
        
        return {"prices": prices, "count": len(prices)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve competitor prices: {str(e)}"
        )


@router.post("/generate-amazon-urls")
async def generate_amazon_urls(
    request: AmazonUrlRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate Amazon search URLs for a product.
    
    Args:
        request: Amazon URL generation request
        current_user: Current authenticated user
        
    Returns:
        List of generated Amazon search URLs
    """
    try:
        service = CompetitorScrapingService()
        
        urls = service.generate_amazon_search_urls(
            product_title=request.product_title,
            brand=request.brand,
            category=request.category,
            marketplace=request.marketplace
        )
        
        return {"urls": urls, "count": len(urls)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Amazon URLs: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Perform health check for the competitor scraping service.
    
    Returns:
        Health check status and details
    """
    try:
        service = CompetitorScrapingService()
        health_status = await service.health_check()
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service health check failed: {str(e)}"
        )