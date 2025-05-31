"""
Analytics API endpoints.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user_id, get_db_manager_dep, verify_store_access
from app.core.logging import log_business_event
from app.models.analytics import (
    BusinessInsight,
    DashboardAnalytics,
    InsightsResponse,
    InventoryAlert,
    PricingOpportunity,
    TopProduct,
    TrendingProduct,
)
from app.models.auth import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=DashboardAnalytics,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get dashboard analytics",
    description="Get comprehensive dashboard analytics data",
)
async def get_dashboard_analytics(
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Get dashboard analytics data."""
    
    try:
        # Get basic product counts
        products_query = """
        SELECT 
            COUNT(*) as total_products,
            COUNT(*) FILTER (WHERE status = 'active') as active_products
        FROM products 
        WHERE shop_id = :shop_id
        """
        
        products_result = await db_manager.fetch_one(products_query, {"shop_id": shop_id})
        
        # Get revenue metrics
        revenue_query = """
        SELECT 
            COALESCE(SUM(quantity_sold * sold_price), 0) as total_revenue,
            COALESCE(SUM(quantity_sold * sold_price) FILTER (
                WHERE sold_at >= NOW() - INTERVAL '30 days'
            ), 0) as revenue_last_30d,
            COALESCE(AVG(sold_price), 0) as avg_order_value,
            COUNT(*) as total_orders,
            COUNT(*) FILTER (WHERE sold_at >= NOW() - INTERVAL '30 days') as orders_last_30d
        FROM sales 
        WHERE shop_id = :shop_id
        """
        
        revenue_result = await db_manager.fetch_one(revenue_query, {"shop_id": shop_id})
        
        # Calculate change percentages
        revenue_change_percent = None
        orders_change_percent = None
        
        if revenue_result["revenue_last_30d"] > 0:
            # Get previous 30 days for comparison
            prev_revenue_query = """
            SELECT COALESCE(SUM(quantity_sold * sold_price), 0) as prev_revenue
            FROM sales 
            WHERE shop_id = :shop_id 
            AND sold_at >= NOW() - INTERVAL '60 days'
            AND sold_at < NOW() - INTERVAL '30 days'
            """
            
            prev_revenue_result = await db_manager.fetch_one(prev_revenue_query, {"shop_id": shop_id})
            
            if prev_revenue_result["prev_revenue"] > 0:
                revenue_change_percent = (
                    (revenue_result["revenue_last_30d"] - prev_revenue_result["prev_revenue"]) 
                    / prev_revenue_result["prev_revenue"] * 100
                )
        
        # Get top selling products
        top_products_query = """
        SELECT 
            s.sku_code,
            p.product_title,
            SUM(s.quantity_sold * s.sold_price) as total_revenue,
            SUM(s.quantity_sold) as total_quantity,
            AVG(s.sold_price) as avg_price,
            p.image_url
        FROM sales s
        JOIN products p ON s.shop_id = p.shop_id AND s.sku_code = p.sku_code
        WHERE s.shop_id = :shop_id
        AND s.sold_at >= NOW() - INTERVAL '30 days'
        GROUP BY s.sku_code, p.product_title, p.image_url
        ORDER BY total_revenue DESC
        LIMIT 5
        """
        
        top_products_result = await db_manager.fetch_all(top_products_query, {"shop_id": shop_id})
        
        top_products = [
            TopProduct(
                sku_code=row["sku_code"],
                product_title=row["product_title"],
                total_revenue=row["total_revenue"],
                total_quantity=row["total_quantity"],
                avg_price=row["avg_price"],
                image_url=row["image_url"],
            )
            for row in top_products_result
        ]
        
        # Get trending products
        trending_query = """
        SELECT 
            p.sku_code,
            p.product_title,
            ti.label as trend_label,
            ti.final_score as trend_score,
            ti.google_trend_index,
            ti.social_score,
            p.current_price,
            p.image_url
        FROM products p
        JOIN trend_insights ti ON p.shop_id = ti.shop_id AND p.sku_code = ti.sku_code
        WHERE p.shop_id = :shop_id
        AND p.status = 'active'
        AND ti.label IN ('Hot', 'Rising')
        ORDER BY ti.final_score DESC
        LIMIT 5
        """
        
        trending_result = await db_manager.fetch_all(trending_query, {"shop_id": shop_id})
        
        trending_products = [
            TrendingProduct(
                sku_code=row["sku_code"],
                product_title=row["product_title"],
                trend_label=row["trend_label"],
                trend_score=row["trend_score"],
                google_trend_index=row["google_trend_index"],
                social_score=row["social_score"],
                current_price=row["current_price"],
                image_url=row["image_url"],
            )
            for row in trending_result
        ]
        
        # Get pricing opportunities
        pricing_query = """
        SELECT 
            p.sku_code,
            p.product_title,
            p.current_price,
            rp.recommended_price,
            (rp.recommended_price - p.current_price) as price_difference,
            CASE 
                WHEN p.current_price > 0 THEN 
                    ((rp.recommended_price - p.current_price) / p.current_price * 100)
                ELSE 0 
            END as price_change_percent,
            rp.recommendation_type,
            rp.confidence_score,
            rp.pricing_reason
        FROM products p
        JOIN recommended_prices rp ON p.shop_id = rp.shop_id AND p.sku_code = rp.sku_code
        WHERE p.shop_id = :shop_id
        AND p.status = 'active'
        AND rp.recommendation_type IN ('underpriced', 'overpriced')
        AND rp.confidence_score > 0.7
        ORDER BY ABS(rp.recommended_price - p.current_price) DESC
        LIMIT 5
        """
        
        pricing_result = await db_manager.fetch_all(pricing_query, {"shop_id": shop_id})
        
        pricing_opportunities = [
            PricingOpportunity(
                sku_code=row["sku_code"],
                product_title=row["product_title"],
                current_price=row["current_price"],
                recommended_price=row["recommended_price"],
                price_difference=row["price_difference"],
                price_change_percent=row["price_change_percent"],
                recommendation_type=row["recommendation_type"],
                confidence_score=row["confidence_score"],
                reasoning=row["pricing_reason"],
            )
            for row in pricing_result
        ]
        
        # Get inventory alerts
        inventory_query = """
        SELECT 
            p.sku_code,
            p.product_title,
            p.inventory_level,
            CASE 
                WHEN p.inventory_level = 0 THEN 'out_of_stock'
                WHEN p.inventory_level <= 5 THEN 'low_stock'
                ELSE 'normal'
            END as alert_type,
            CASE 
                WHEN p.inventory_level = 0 THEN 'critical'
                WHEN p.inventory_level <= 5 THEN 'warning'
                ELSE 'info'
            END as severity
        FROM products p
        WHERE p.shop_id = :shop_id
        AND p.status = 'active'
        AND p.inventory_level <= 5
        ORDER BY p.inventory_level ASC
        LIMIT 5
        """
        
        inventory_result = await db_manager.fetch_all(inventory_query, {"shop_id": shop_id})
        
        inventory_alerts = [
            InventoryAlert(
                sku_code=row["sku_code"],
                product_title=row["product_title"],
                current_inventory=row["inventory_level"],
                alert_type=row["alert_type"],
                severity=row["severity"],
                message=f"Only {row['inventory_level']} units left" if row["inventory_level"] > 0 else "Out of stock",
                recommended_action="Restock immediately" if row["inventory_level"] == 0 else "Consider restocking soon",
            )
            for row in inventory_result
        ]
        
        # Get last sync status
        sync_query = """
        SELECT status, started_at
        FROM sync_jobs 
        WHERE shop_id = :shop_id 
        ORDER BY started_at DESC 
        LIMIT 1
        """
        
        sync_result = await db_manager.fetch_one(sync_query, {"shop_id": shop_id})
        
        # Log analytics access
        log_business_event(
            "dashboard_analytics_accessed",
            user_id=user_id,
            shop_id=shop_id
        )
        
        return DashboardAnalytics(
            total_products=products_result["total_products"] or 0,
            active_products=products_result["active_products"] or 0,
            total_revenue=revenue_result["total_revenue"] or Decimal("0"),
            revenue_last_30d=revenue_result["revenue_last_30d"] or Decimal("0"),
            revenue_change_percent=revenue_change_percent,
            avg_order_value=revenue_result["avg_order_value"] or Decimal("0"),
            total_orders=revenue_result["total_orders"] or 0,
            orders_last_30d=revenue_result["orders_last_30d"] or 0,
            orders_change_percent=orders_change_percent,
            top_selling_products=top_products,
            trending_products=trending_products,
            pricing_opportunities=pricing_opportunities,
            inventory_alerts=inventory_alerts,
            last_sync_at=sync_result["started_at"] if sync_result else None,
            sync_status=sync_result["status"] if sync_result else "never_synced",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics service error"
        )


@router.get(
    "/insights",
    response_model=InsightsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get business insights",
    description="Get top business insights for AI video generation",
)
async def get_business_insights(
    shop_id: int = Query(..., description="Store ID"),
    limit: int = Query(5, ge=1, le=10, description="Number of insights to return"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Get top business insights for AI video generation."""
    
    try:
        insights = []
        
        # Insight 1: Top performing products
        top_performers_query = """
        SELECT 
            s.sku_code,
            p.product_title,
            SUM(s.quantity_sold * s.sold_price) as revenue,
            SUM(s.quantity_sold) as quantity
        FROM sales s
        JOIN products p ON s.shop_id = p.shop_id AND s.sku_code = p.sku_code
        WHERE s.shop_id = :shop_id
        AND s.sold_at >= NOW() - INTERVAL '30 days'
        GROUP BY s.sku_code, p.product_title
        ORDER BY revenue DESC
        LIMIT 3
        """
        
        top_performers = await db_manager.fetch_all(top_performers_query, {"shop_id": shop_id})
        
        if top_performers:
            total_revenue = sum(row["revenue"] for row in top_performers)
            insights.append(
                BusinessInsight(
                    insight_type="top_performers",
                    title="Top Performing Products",
                    description=f"Your top 3 products generated ${total_revenue:,.2f} in the last 30 days",
                    impact_level="high",
                    priority=1,
                    data={
                        "products": [
                            {
                                "sku": row["sku_code"],
                                "title": row["product_title"],
                                "revenue": float(row["revenue"]),
                                "quantity": row["quantity"]
                            }
                            for row in top_performers
                        ],
                        "total_revenue": float(total_revenue)
                    },
                    recommendation="Focus marketing efforts on these high-performing products",
                    potential_value=total_revenue * Decimal("0.1"),  # 10% potential increase
                )
            )
        
        # Insight 2: Pricing opportunities
        pricing_opportunities_query = """
        SELECT 
            p.sku_code,
            p.product_title,
            p.current_price,
            rp.recommended_price,
            rp.recommendation_type,
            rp.confidence_score
        FROM products p
        JOIN recommended_prices rp ON p.shop_id = rp.shop_id AND p.sku_code = rp.sku_code
        WHERE p.shop_id = :shop_id
        AND rp.recommendation_type = 'underpriced'
        AND rp.confidence_score > 0.8
        ORDER BY (rp.recommended_price - p.current_price) DESC
        LIMIT 3
        """
        
        pricing_opps = await db_manager.fetch_all(pricing_opportunities_query, {"shop_id": shop_id})
        
        if pricing_opps:
            potential_increase = sum(
                row["recommended_price"] - row["current_price"] 
                for row in pricing_opps
            )
            
            insights.append(
                BusinessInsight(
                    insight_type="pricing_optimization",
                    title="Pricing Optimization Opportunities",
                    description=f"You have {len(pricing_opps)} underpriced products with potential for price increases",
                    impact_level="high",
                    priority=2,
                    data={
                        "products": [
                            {
                                "sku": row["sku_code"],
                                "title": row["product_title"],
                                "current_price": float(row["current_price"]),
                                "recommended_price": float(row["recommended_price"]),
                                "potential_increase": float(row["recommended_price"] - row["current_price"])
                            }
                            for row in pricing_opps
                        ],
                        "total_potential_increase": float(potential_increase)
                    },
                    recommendation="Consider gradually increasing prices on these products",
                    potential_value=potential_increase * Decimal("10"),  # Assume 10 units sold per month
                )
            )
        
        # Insight 3: Trending products
        trending_query = """
        SELECT 
            p.sku_code,
            p.product_title,
            ti.label,
            ti.final_score,
            ti.google_trend_index
        FROM products p
        JOIN trend_insights ti ON p.shop_id = ti.shop_id AND p.sku_code = ti.sku_code
        WHERE p.shop_id = :shop_id
        AND ti.label IN ('Hot', 'Rising')
        ORDER BY ti.final_score DESC
        LIMIT 3
        """
        
        trending = await db_manager.fetch_all(trending_query, {"shop_id": shop_id})
        
        if trending:
            insights.append(
                BusinessInsight(
                    insight_type="trending_products",
                    title="Trending Products Alert",
                    description=f"You have {len(trending)} products showing strong market trends",
                    impact_level="medium",
                    priority=3,
                    data={
                        "products": [
                            {
                                "sku": row["sku_code"],
                                "title": row["product_title"],
                                "trend_label": row["label"],
                                "trend_score": float(row["final_score"]),
                                "google_trend_index": row["google_trend_index"]
                            }
                            for row in trending
                        ]
                    },
                    recommendation="Increase inventory and marketing for these trending products",
                )
            )
        
        # Insight 4: Inventory alerts
        inventory_query = """
        SELECT 
            p.sku_code,
            p.product_title,
            p.inventory_level
        FROM products p
        WHERE p.shop_id = :shop_id
        AND p.status = 'active'
        AND p.inventory_level <= 5
        ORDER BY p.inventory_level ASC
        LIMIT 5
        """
        
        low_inventory = await db_manager.fetch_all(inventory_query, {"shop_id": shop_id})
        
        if low_inventory:
            out_of_stock = [p for p in low_inventory if p["inventory_level"] == 0]
            low_stock = [p for p in low_inventory if p["inventory_level"] > 0]
            
            insights.append(
                BusinessInsight(
                    insight_type="inventory_management",
                    title="Inventory Management Alert",
                    description=f"You have {len(out_of_stock)} out-of-stock and {len(low_stock)} low-stock products",
                    impact_level="high" if out_of_stock else "medium",
                    priority=4,
                    data={
                        "out_of_stock": len(out_of_stock),
                        "low_stock": len(low_stock),
                        "products": [
                            {
                                "sku": row["sku_code"],
                                "title": row["product_title"],
                                "inventory": row["inventory_level"]
                            }
                            for row in low_inventory
                        ]
                    },
                    recommendation="Restock these products immediately to avoid lost sales",
                )
            )
        
        # Sort insights by priority and limit
        insights.sort(key=lambda x: x.priority)
        insights = insights[:limit]
        
        # Log insights access
        log_business_event(
            "business_insights_accessed",
            user_id=user_id,
            shop_id=shop_id,
            insights_count=len(insights)
        )
        
        return InsightsResponse(
            insights=insights,
            total_insights=len(insights),
            generated_at=datetime.utcnow(),
            shop_id=shop_id,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Business insights error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Insights service error"
        )