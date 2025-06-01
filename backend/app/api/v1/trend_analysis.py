"""
API endpoints for trend analysis functionality.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.product import TrendUpdate
from app.services.trend_analysis_service import TrendAnalysisService

router = APIRouter()


class TrendAnalysisRequest(BaseModel):
    """Request model for single product trend analysis."""
    sku_code: str = Field(..., description="Product SKU code")
    product_title: str = Field(..., description="Product title for trend analysis")
    category: Optional[str] = Field(default=None, description="Product category")
    brand: Optional[str] = Field(default=None, description="Product brand")


class BatchTrendAnalysisRequest(BaseModel):
    """Request model for batch trend analysis."""
    products: List[Dict[str, str]] = Field(
        ..., 
        description="List of products with sku_code, product_title, category, brand"
    )


class TrendRefreshRequest(BaseModel):
    """Request model for trend data refresh."""
    sku_codes: Optional[List[str]] = Field(
        default=None, 
        description="Optional list of SKU codes to refresh (if None, refresh all)"
    )


@router.post("/analyze/{shop_id}", response_model=TrendUpdate)
async def analyze_product_trend(
    shop_id: int,
    request: TrendAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze trend for a specific product.
    
    Args:
        shop_id: Store ID
        request: Trend analysis request parameters
        current_user: Current authenticated user
        
    Returns:
        TrendUpdate with trend analysis data
    """
    try:
        service = TrendAnalysisService()
        
        result = await service.analyze_product_trend(
            shop_id=shop_id,
            sku_code=request.sku_code,
            product_title=request.product_title,
            category=request.category,
            brand=request.brand
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze product trend: {str(e)}"
        )


@router.post("/analyze-batch/{shop_id}")
async def analyze_trends_batch(
    shop_id: int,
    request: BatchTrendAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze trends for multiple products in batch.
    
    Args:
        shop_id: Store ID
        request: Batch trend analysis request parameters
        current_user: Current authenticated user
        
    Returns:
        Dictionary mapping SKU codes to TrendUpdate objects
    """
    try:
        service = TrendAnalysisService()
        
        results = await service.analyze_multiple_products(
            shop_id=shop_id,
            products=request.products
        )
        
        return {
            "results": results,
            "total_products": len(request.products),
            "successful_analyses": len(results),
            "failed_analyses": len(request.products) - len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze trends in batch: {str(e)}"
        )


@router.post("/store/{shop_id}")
async def store_trend_insights(
    shop_id: int,
    trend_updates: List[TrendUpdate],
    current_user: dict = Depends(get_current_user)
):
    """
    Store trend insights in the database.
    
    Args:
        shop_id: Store ID
        trend_updates: List of trend updates to store
        current_user: Current authenticated user
        
    Returns:
        Storage operation result
    """
    try:
        service = TrendAnalysisService()
        
        success = await service.store_trend_insights(
            shop_id=shop_id,
            trend_updates=trend_updates
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully stored {len(trend_updates)} trend insights",
                "insights_stored": len(trend_updates)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store trend insights"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store trend insights: {str(e)}"
        )


@router.get("/insights/{shop_id}")
async def get_trend_insights(
    shop_id: int,
    sku_code: Optional[str] = None,
    max_age_hours: int = 24,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve trend insights from the database.
    
    Args:
        shop_id: Store ID
        sku_code: Optional SKU code filter
        max_age_hours: Maximum age of data in hours
        current_user: Current authenticated user
        
    Returns:
        List of trend insight records
    """
    try:
        service = TrendAnalysisService()
        
        insights = await service.get_trend_insights(
            shop_id=shop_id,
            sku_code=sku_code,
            max_age_hours=max_age_hours
        )
        
        return {
            "insights": insights,
            "count": len(insights),
            "shop_id": shop_id,
            "sku_code": sku_code,
            "max_age_hours": max_age_hours
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trend insights: {str(e)}"
        )


@router.post("/refresh/{shop_id}")
async def refresh_trend_data(
    shop_id: int,
    request: TrendRefreshRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Refresh trend data for products.
    
    Args:
        shop_id: Store ID
        request: Trend refresh request parameters
        current_user: Current authenticated user
        
    Returns:
        Refresh operation results
    """
    try:
        service = TrendAnalysisService()
        
        result = await service.refresh_trend_data(
            shop_id=shop_id,
            sku_codes=request.sku_codes
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh trend data: {str(e)}"
        )


@router.get("/insights/{shop_id}/summary")
async def get_trend_summary(
    shop_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get trend analysis summary for a store.
    
    Args:
        shop_id: Store ID
        current_user: Current authenticated user
        
    Returns:
        Trend analysis summary with statistics
    """
    try:
        service = TrendAnalysisService()
        
        # Get all recent trend insights
        insights = await service.get_trend_insights(
            shop_id=shop_id,
            max_age_hours=24
        )
        
        if not insights:
            return {
                "shop_id": shop_id,
                "total_products": 0,
                "summary": {
                    "Hot": 0,
                    "Rising": 0,
                    "Steady": 0,
                    "Declining": 0
                },
                "average_scores": {
                    "google_trend_index": 0,
                    "social_score": 0,
                    "final_score": 0
                },
                "last_updated": None
            }
        
        # Calculate summary statistics
        label_counts = {"Hot": 0, "Rising": 0, "Steady": 0, "Declining": 0}
        total_google_trend = 0
        total_social_score = 0
        total_final_score = 0
        latest_update = None
        
        for insight in insights:
            label_counts[insight["label"]] += 1
            total_google_trend += insight["google_trend_index"]
            total_social_score += insight["social_score"]
            total_final_score += insight["final_score"]
            
            if latest_update is None or insight["computed_at"] > latest_update:
                latest_update = insight["computed_at"]
        
        total_products = len(insights)
        
        return {
            "shop_id": shop_id,
            "total_products": total_products,
            "summary": label_counts,
            "percentages": {
                label: round((count / total_products) * 100, 1) 
                for label, count in label_counts.items()
            },
            "average_scores": {
                "google_trend_index": round(total_google_trend / total_products, 1),
                "social_score": round(total_social_score / total_products, 1),
                "final_score": round(total_final_score / total_products, 1)
            },
            "last_updated": latest_update
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trend summary: {str(e)}"
        )


@router.get("/insights/{shop_id}/trending")
async def get_trending_products(
    shop_id: int,
    label: Optional[str] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Get trending products based on trend analysis.
    
    Args:
        shop_id: Store ID
        label: Optional trend label filter (Hot, Rising, Steady, Declining)
        limit: Maximum number of products to return
        current_user: Current authenticated user
        
    Returns:
        List of trending products with trend data
    """
    try:
        service = TrendAnalysisService()
        
        # Get trend insights
        insights = await service.get_trend_insights(
            shop_id=shop_id,
            max_age_hours=24
        )
        
        # Filter by label if specified
        if label:
            insights = [insight for insight in insights if insight["label"] == label]
        
        # Sort by final score (descending)
        insights.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Limit results
        insights = insights[:limit]
        
        # Get product details for the trending products
        if insights:
            sku_codes = [insight["sku_code"] for insight in insights]
            
            # Fetch product details from database
            products_query = service.supabase_client.table("products").select(
                "sku_code, product_title, current_price, image_url, status"
            ).eq("shop_id", shop_id).in_("sku_code", sku_codes)
            
            products_result = products_query.execute()
            products_dict = {p["sku_code"]: p for p in products_result.data}
            
            # Combine trend data with product details
            trending_products = []
            for insight in insights:
                sku_code = insight["sku_code"]
                product = products_dict.get(sku_code, {})
                
                trending_products.append({
                    "sku_code": sku_code,
                    "product_title": product.get("product_title", "Unknown"),
                    "current_price": product.get("current_price"),
                    "image_url": product.get("image_url"),
                    "status": product.get("status"),
                    "trend_data": {
                        "google_trend_index": insight["google_trend_index"],
                        "social_score": insight["social_score"],
                        "final_score": insight["final_score"],
                        "label": insight["label"],
                        "computed_at": insight["computed_at"]
                    }
                })
        else:
            trending_products = []
        
        return {
            "shop_id": shop_id,
            "label_filter": label,
            "trending_products": trending_products,
            "count": len(trending_products),
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending products: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Perform health check for the trend analysis service.
    
    Returns:
        Health check status and details
    """
    try:
        service = TrendAnalysisService()
        health_status = await service.health_check()
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service health check failed: {str(e)}"
        )