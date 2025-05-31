"""
Data synchronization API endpoints.
"""

import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user_id, get_db_manager_dep, verify_store_access
from app.core.logging import log_business_event
from app.models.auth import ErrorResponse
from app.models.product import CompetitorPriceUpdate, TrendUpdate
from app.models.sync import (
    CompetitorPricesSyncResult,
    SyncRequest,
    SyncResult,
    SyncStatus,
    TrendsSyncResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/shopify",
    response_model=SyncStatus,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        409: {"model": ErrorResponse, "description": "Sync already in progress"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Sync Shopify data",
    description="Trigger Shopify data synchronization",
)
async def sync_shopify_data(
    sync_request: SyncRequest,
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Trigger Shopify data synchronization."""
    
    try:
        # Check if sync is already in progress
        check_query = """
        SELECT sync_id FROM sync_jobs 
        WHERE shop_id = :shop_id AND status IN ('running', 'pending')
        """
        
        existing_sync = await db_manager.fetch_one(check_query, {"shop_id": shop_id})
        
        if existing_sync:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Sync already in progress"
            )
        
        # Create new sync job
        sync_id = str(uuid.uuid4())
        
        insert_query = """
        INSERT INTO sync_jobs (sync_id, shop_id, sync_type, status, started_at, progress, current_step, total_steps)
        VALUES (:sync_id, :shop_id, 'shopify', 'pending', NOW(), 0, 'Initializing', 5)
        """
        
        await db_manager.execute_query(insert_query, {
            "sync_id": sync_id,
            "shop_id": shop_id,
        })
        
        # TODO: Trigger background job for actual sync
        # This would typically use Celery or Azure Functions
        
        # Log sync initiation
        log_business_event(
            "shopify_sync_initiated",
            user_id=user_id,
            shop_id=shop_id,
            sync_id=sync_id,
            full_sync=sync_request.full_sync
        )
        
        return SyncStatus(
            sync_id=sync_id,
            status="pending",
            started_at=datetime.utcnow(),
            progress=0,
            current_step="Initializing",
            total_steps=5,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shopify sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sync service error"
        )


@router.get(
    "/status",
    response_model=SyncStatus,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "No sync found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get sync status",
    description="Get current synchronization status",
)
async def get_sync_status(
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Get current synchronization status."""
    
    try:
        query = """
        SELECT sync_id, status, started_at, completed_at, progress, current_step, 
               total_steps, results, errors
        FROM sync_jobs 
        WHERE shop_id = :shop_id 
        ORDER BY started_at DESC 
        LIMIT 1
        """
        
        result = await db_manager.fetch_one(query, {"shop_id": shop_id})
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sync found for this store"
            )
        
        return SyncStatus(
            sync_id=result["sync_id"],
            status=result["status"],
            started_at=result["started_at"],
            completed_at=result["completed_at"],
            progress=result["progress"],
            current_step=result["current_step"],
            total_steps=result["total_steps"],
            results=result["results"],
            errors=result["errors"] or [],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sync status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sync status service error"
        )


@router.post(
    "/competitor-prices",
    response_model=CompetitorPricesSyncResult,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Update competitor prices",
    description="Update competitor pricing data",
)
async def update_competitor_prices(
    price_updates: List[CompetitorPriceUpdate],
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Update competitor pricing data."""
    
    try:
        updated_count = 0
        failed_count = 0
        errors = []
        
        for price_update in price_updates:
            try:
                # Upsert competitor price data
                upsert_query = """
                INSERT INTO competitor_prices (
                    shop_id, sku_code, min_price, max_price, competitor_count, 
                    price_details, scraped_at
                )
                VALUES (:shop_id, :sku_code, :min_price, :max_price, :competitor_count, 
                        :price_details, NOW())
                ON CONFLICT (shop_id, sku_code)
                DO UPDATE SET
                    min_price = EXCLUDED.min_price,
                    max_price = EXCLUDED.max_price,
                    competitor_count = EXCLUDED.competitor_count,
                    price_details = EXCLUDED.price_details,
                    scraped_at = EXCLUDED.scraped_at
                """
                
                await db_manager.execute_query(upsert_query, {
                    "shop_id": shop_id,
                    "sku_code": price_update.sku_code,
                    "min_price": price_update.min_price,
                    "max_price": price_update.max_price,
                    "competitor_count": price_update.competitor_count,
                    "price_details": price_update.price_details,
                })
                
                updated_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to update {price_update.sku_code}: {str(e)}")
                logger.error(f"Competitor price update error for {price_update.sku_code}: {e}")
        
        # Log competitor price update
        log_business_event(
            "competitor_prices_updated",
            user_id=user_id,
            shop_id=shop_id,
            updated_count=updated_count,
            failed_count=failed_count
        )
        
        return CompetitorPricesSyncResult(
            updated_count=updated_count,
            failed_count=failed_count,
            errors=errors,
            total_competitors_found=sum(p.competitor_count for p in price_updates),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Competitor prices sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Competitor prices sync service error"
        )


@router.post(
    "/trends",
    response_model=TrendsSyncResult,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Update trend data",
    description="Update market trend data",
)
async def update_trends(
    trend_updates: List[TrendUpdate],
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Update market trend data."""
    
    try:
        updated_count = 0
        failed_count = 0
        errors = []
        trend_counts = {"Hot": 0, "Rising": 0, "Steady": 0, "Declining": 0}
        
        for trend_update in trend_updates:
            try:
                # Upsert trend data
                upsert_query = """
                INSERT INTO trend_insights (
                    shop_id, sku_code, google_trend_index, social_score, 
                    final_score, label, trend_details, computed_at
                )
                VALUES (:shop_id, :sku_code, :google_trend_index, :social_score, 
                        :final_score, :label, :trend_details, NOW())
                ON CONFLICT (shop_id, sku_code)
                DO UPDATE SET
                    google_trend_index = EXCLUDED.google_trend_index,
                    social_score = EXCLUDED.social_score,
                    final_score = EXCLUDED.final_score,
                    label = EXCLUDED.label,
                    trend_details = EXCLUDED.trend_details,
                    computed_at = EXCLUDED.computed_at
                """
                
                await db_manager.execute_query(upsert_query, {
                    "shop_id": shop_id,
                    "sku_code": trend_update.sku_code,
                    "google_trend_index": trend_update.google_trend_index,
                    "social_score": trend_update.social_score,
                    "final_score": trend_update.final_score,
                    "label": trend_update.label,
                    "trend_details": trend_update.trend_details,
                })
                
                updated_count += 1
                trend_counts[trend_update.label] += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to update {trend_update.sku_code}: {str(e)}")
                logger.error(f"Trend update error for {trend_update.sku_code}: {e}")
        
        # Log trend update
        log_business_event(
            "trends_updated",
            user_id=user_id,
            shop_id=shop_id,
            updated_count=updated_count,
            failed_count=failed_count,
            trend_distribution=trend_counts
        )
        
        return TrendsSyncResult(
            updated_count=updated_count,
            failed_count=failed_count,
            errors=errors,
            hot_products=trend_counts["Hot"],
            rising_products=trend_counts["Rising"],
            declining_products=trend_counts["Declining"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trends sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trends sync service error"
        )