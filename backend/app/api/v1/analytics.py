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
        
        # Get trending products (based on recent sales performance)
        trending_query = """
        SELECT
            p.sku_code,
            p.product_title,
            p.current_price,
            p.image_url,
            SUM(s.quantity_sold) as recent_sales,
            COUNT(DISTINCT DATE(s.sold_at)) as sales_days,
            AVG(s.sold_price) as avg_sold_price
        FROM products p
        JOIN sales s ON p.shop_id = s.shop_id AND p.sku_code = s.sku_code
        WHERE p.shop_id = :shop_id
        AND p.status = 'active'
        AND s.sold_at >= NOW() - INTERVAL '7 days'
        GROUP BY p.sku_code, p.product_title, p.current_price, p.image_url
        HAVING SUM(s.quantity_sold) >= 3
        ORDER BY (SUM(s.quantity_sold) / COUNT(DISTINCT DATE(s.sold_at))) DESC
        LIMIT 5
        """
        
        trending_result = await db_manager.fetch_all(trending_query, {"shop_id": shop_id})
        
        trending_products = [
            TrendingProduct(
                sku_code=row["sku_code"],
                product_title=row["product_title"],
                trend_label="Hot" if row["recent_sales"] >= 10 else "Rising",
                trend_score=min(100, row["recent_sales"] * 10),  # Mock trend score
                google_trend_index=min(100, row["recent_sales"] * 8),  # Mock Google trends
                social_score=min(100, row["recent_sales"] * 12),  # Mock social score
                current_price=row["current_price"],
                image_url=row["image_url"],
            )
            for row in trending_result
        ]
        
        # Get pricing opportunities (based on sales performance vs price)
        pricing_query = """
        SELECT
            p.sku_code,
            p.product_title,
            p.current_price,
            AVG(s.sold_price) as avg_sold_price,
            SUM(s.quantity_sold) as total_sold,
            COUNT(*) as sale_count
        FROM products p
        JOIN sales s ON p.shop_id = s.shop_id AND p.sku_code = s.sku_code
        WHERE p.shop_id = :shop_id
        AND p.status = 'active'
        AND s.sold_at >= NOW() - INTERVAL '30 days'
        GROUP BY p.sku_code, p.product_title, p.current_price
        HAVING SUM(s.quantity_sold) >= 5
        ORDER BY SUM(s.quantity_sold) DESC
        LIMIT 10
        """
        
        pricing_result = await db_manager.fetch_all(pricing_query, {"shop_id": shop_id})
        
        pricing_opportunities = []
        for row in pricing_result:
            current_price = float(row["current_price"])
            avg_sold_price = float(row["avg_sold_price"])
            total_sold = row["total_sold"]
            
            # Generate pricing recommendations based on sales performance
            if total_sold >= 20 and avg_sold_price > current_price * 1.05:
                # High sales + selling above list price = underpriced
                recommended_price = current_price * 1.15
                recommendation_type = "underpriced"
                reasoning = f"High demand ({total_sold} sold) and selling above list price suggests room for increase"
                confidence_score = 0.85
            elif total_sold <= 8 and avg_sold_price < current_price * 0.95:
                # Low sales + selling below list price = overpriced
                recommended_price = current_price * 0.9
                recommendation_type = "overpriced"
                reasoning = f"Low sales ({total_sold} sold) and selling below list price suggests price reduction needed"
                confidence_score = 0.75
            else:
                continue
            
            price_difference = recommended_price - current_price
            price_change_percent = (price_difference / current_price * 100) if current_price > 0 else 0
            
            pricing_opportunities.append(
                PricingOpportunity(
                    sku_code=row["sku_code"],
                    product_title=row["product_title"],
                    current_price=current_price,
                    recommended_price=recommended_price,
                    price_difference=price_difference,
                    price_change_percent=price_change_percent,
                    recommendation_type=recommendation_type,
                    confidence_score=confidence_score,
                    reasoning=reasoning,
                )
            )
        
        # Limit to top 5 opportunities
        pricing_opportunities = pricing_opportunities[:5]
        
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
    "/time-series",
    response_model=List[dict],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get time-series analytics data",
    description="Get daily revenue and sales data for charts",
)
async def get_time_series_analytics(
    shop_id: int = Query(..., description="Store ID"),
    days: int = Query(30, ge=7, le=365, description="Number of days to include"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Get time-series analytics data for charts."""
    
    try:
        # Get daily revenue and sales data
        time_series_query = """
        SELECT
            DATE(sold_at) as date,
            SUM(quantity_sold * sold_price) as daily_revenue,
            COUNT(*) as daily_orders,
            SUM(quantity_sold) as daily_quantity
        FROM sales
        WHERE shop_id = :shop_id
        AND sold_at >= NOW() - INTERVAL ':days days'
        GROUP BY DATE(sold_at)
        ORDER BY date ASC
        """
        
        # Note: PostgreSQL doesn't allow parameterized INTERVAL, so we need to format it
        formatted_query = time_series_query.replace(':days', str(days))
        
        time_series_result = await db_manager.fetch_all(formatted_query, {"shop_id": shop_id})
        
        # Convert to list of dictionaries with proper formatting
        time_series_data = []
        for row in time_series_result:
            time_series_data.append({
                "date": row["date"].isoformat() if row["date"] else None,
                "daily_revenue": float(row["daily_revenue"]) if row["daily_revenue"] else 0,
                "daily_orders": row["daily_orders"] or 0,
                "daily_quantity": row["daily_quantity"] or 0,
            })
        
        # Log time-series access
        log_business_event(
            "time_series_analytics_accessed",
            user_id=user_id,
            shop_id=shop_id,
            days_requested=days
        )
        
        return time_series_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Time-series analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Time-series analytics service error"
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
        
        # Insight 2: Pricing opportunities (based on sales performance)
        pricing_opportunities_query = """
        SELECT
            p.sku_code,
            p.product_title,
            p.current_price,
            AVG(s.sold_price) as avg_sold_price,
            SUM(s.quantity_sold) as total_sold
        FROM products p
        JOIN sales s ON p.shop_id = s.shop_id AND p.sku_code = s.sku_code
        WHERE p.shop_id = :shop_id
        AND s.sold_at >= NOW() - INTERVAL '30 days'
        GROUP BY p.sku_code, p.product_title, p.current_price
        HAVING SUM(s.quantity_sold) >= 10 AND AVG(s.sold_price) > p.current_price * 1.05
        ORDER BY SUM(s.quantity_sold) DESC
        LIMIT 3
        """
        
        pricing_opps = await db_manager.fetch_all(pricing_opportunities_query, {"shop_id": shop_id})
        
        if pricing_opps:
            potential_increase = sum(
                float(row["current_price"]) * 0.15  # 15% potential increase
                for row in pricing_opps
            )
            
            insights.append(
                BusinessInsight(
                    insight_type="pricing_optimization",
                    title="Pricing Optimization Opportunities",
                    description=f"You have {len(pricing_opps)} products selling above list price with high demand",
                    impact_level="high",
                    priority=2,
                    data={
                        "products": [
                            {
                                "sku": row["sku_code"],
                                "title": row["product_title"],
                                "current_price": float(row["current_price"]),
                                "avg_sold_price": float(row["avg_sold_price"]),
                                "total_sold": row["total_sold"],
                                "recommended_price": float(row["current_price"]) * 1.15
                            }
                            for row in pricing_opps
                        ],
                        "total_potential_increase": potential_increase
                    },
                    recommendation="Consider increasing prices on these high-demand products",
                    potential_value=Decimal(str(potential_increase)) * Decimal("10"),  # Assume 10 units sold per month
                )
            )
        
        # Insight 3: Trending products (based on recent sales velocity)
        trending_query = """
        SELECT
            p.sku_code,
            p.product_title,
            SUM(s.quantity_sold) as recent_sales,
            COUNT(DISTINCT DATE(s.sold_at)) as sales_days,
            SUM(s.quantity_sold) / COUNT(DISTINCT DATE(s.sold_at)) as daily_velocity
        FROM products p
        JOIN sales s ON p.shop_id = s.shop_id AND p.sku_code = s.sku_code
        WHERE p.shop_id = :shop_id
        AND s.sold_at >= NOW() - INTERVAL '7 days'
        GROUP BY p.sku_code, p.product_title
        HAVING SUM(s.quantity_sold) >= 5
        ORDER BY (SUM(s.quantity_sold) / COUNT(DISTINCT DATE(s.sold_at))) DESC
        LIMIT 3
        """
        
        trending = await db_manager.fetch_all(trending_query, {"shop_id": shop_id})
        
        if trending:
            insights.append(
                BusinessInsight(
                    insight_type="trending_products",
                    title="High Velocity Products",
                    description=f"You have {len(trending)} products with strong recent sales momentum",
                    impact_level="medium",
                    priority=3,
                    data={
                        "products": [
                            {
                                "sku": row["sku_code"],
                                "title": row["product_title"],
                                "recent_sales": row["recent_sales"],
                                "daily_velocity": float(row["daily_velocity"]),
                                "trend_label": "Hot" if row["daily_velocity"] >= 3 else "Rising"
                            }
                            for row in trending
                        ]
                    },
                    recommendation="Increase inventory and marketing for these high-velocity products",
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