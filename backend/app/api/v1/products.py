"""
Products API endpoints.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import (
    get_current_user_id,
    get_db_manager_dep,
    get_pagination_params,
    verify_store_access,
)
from app.core.logging import log_business_event
from app.models.auth import ErrorResponse
from app.models.product import (
    Product,
    ProductCreate,
    ProductDetail,
    ProductFilters,
    ProductListResponse,
    ProductUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=ProductListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get products",
    description="Get products with filtering and pagination",
)
async def get_products(
    shop_id: int = Query(..., description="Store ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in product title or SKU"),
    status: Optional[str] = Query(None, description="Product status filter"),
    trend_label: Optional[str] = Query(None, description="Trend label filter"),
    recommendation_type: Optional[str] = Query(None, description="Recommendation type filter"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Get products with filtering and pagination."""
    
    try:
        # Build WHERE clause based on filters
        where_conditions = ["p.shop_id = :shop_id"]
        params = {"shop_id": shop_id}
        
        if search:
            where_conditions.append(
                "(p.product_title ILIKE :search OR p.sku_code ILIKE :search)"
            )
            params["search"] = f"%{search}%"
        
        if status:
            where_conditions.append("p.status = :status")
            params["status"] = status
        
        if trend_label:
            where_conditions.append("ti.label = :trend_label")
            params["trend_label"] = trend_label
        
        if recommendation_type:
            where_conditions.append("rp.recommendation_type = :recommendation_type")
            params["recommendation_type"] = recommendation_type
        
        where_clause = " AND ".join(where_conditions)
        
        # Count total products
        count_query = f"""
        SELECT COUNT(DISTINCT p.sku_id)
        FROM products p
        LEFT JOIN trend_insights ti ON p.shop_id = ti.shop_id AND p.sku_code = ti.sku_code
        LEFT JOIN recommended_prices rp ON p.shop_id = rp.shop_id AND p.sku_code = rp.sku_code
        WHERE {where_clause}
        """
        
        total_result = await db_manager.fetch_one(count_query, params)
        total = total_result["count"] if total_result else 0
        
        # Get products with pagination
        offset = (page - 1) * limit
        params.update({"limit": limit, "offset": offset})
        
        products_query = f"""
        SELECT 
            p.sku_id,
            p.shop_id,
            p.shopify_product_id,
            p.sku_code,
            p.product_title,
            p.variant_title,
            p.current_price,
            p.inventory_level,
            p.cost_price,
            p.image_url,
            p.status,
            p.created_at,
            p.updated_at,
            
            -- Competitor pricing
            cp.min_price as competitor_min_price,
            cp.max_price as competitor_max_price,
            cp.competitor_count,
            
            -- Trend insights
            ti.google_trend_index,
            ti.social_score,
            ti.final_score as trend_score,
            ti.label as trend_label,
            
            -- Recommendations
            rp.recommended_price,
            rp.pricing_reason,
            rp.recommendation_type,
            rp.confidence_score,
            
            -- Calculated fields
            CASE 
                WHEN p.cost_price > 0 THEN ROUND(((p.current_price - p.cost_price) / p.cost_price * 100), 2)
                ELSE NULL 
            END as current_margin_percent,
            
            CASE 
                WHEN rp.recommended_price IS NOT NULL AND p.cost_price > 0 
                THEN ROUND(((rp.recommended_price - p.cost_price) / p.cost_price * 100), 2)
                ELSE NULL 
            END as recommended_margin_percent
            
        FROM products p
        LEFT JOIN competitor_prices cp ON p.shop_id = cp.shop_id AND p.sku_code = cp.sku_code
        LEFT JOIN trend_insights ti ON p.shop_id = ti.shop_id AND p.sku_code = ti.sku_code
        LEFT JOIN recommended_prices rp ON p.shop_id = rp.shop_id AND p.sku_code = rp.sku_code
        WHERE {where_clause}
        ORDER BY p.updated_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        products_result = await db_manager.fetch_all(products_query, params)
        
        # Convert to ProductDetail objects
        products = []
        for row in products_result:
            product = ProductDetail(
                sku_id=row["sku_id"],
                shop_id=row["shop_id"],
                shopify_product_id=row["shopify_product_id"],
                sku_code=row["sku_code"],
                product_title=row["product_title"],
                variant_title=row["variant_title"],
                current_price=row["current_price"],
                inventory_level=row["inventory_level"],
                cost_price=row["cost_price"],
                image_url=row["image_url"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                competitor_min_price=row["competitor_min_price"],
                competitor_max_price=row["competitor_max_price"],
                competitor_count=row["competitor_count"],
                google_trend_index=row["google_trend_index"],
                social_score=row["social_score"],
                trend_score=row["trend_score"],
                trend_label=row["trend_label"],
                recommended_price=row["recommended_price"],
                pricing_reason=row["pricing_reason"],
                recommendation_type=row["recommendation_type"],
                confidence_score=row["confidence_score"],
                current_margin_percent=row["current_margin_percent"],
                recommended_margin_percent=row["recommended_margin_percent"],
            )
            products.append(product)
        
        # Log product access
        log_business_event(
            "products_accessed",
            user_id=user_id,
            shop_id=shop_id,
            count=len(products),
            filters={
                "search": search,
                "status": status,
                "trend_label": trend_label,
                "recommendation_type": recommendation_type,
            }
        )
        
        return ProductListResponse(
            products=products,
            total=total,
            page=page,
            limit=limit,
            has_next=(page * limit) < total,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Products service error"
        )


@router.get(
    "/{sku_code}",
    response_model=ProductDetail,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Product not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get product by SKU",
    description="Get specific product details by SKU code",
)
async def get_product_by_sku(
    sku_code: str,
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Get specific product details by SKU code."""
    
    try:
        query = """
        SELECT 
            p.sku_id,
            p.shop_id,
            p.shopify_product_id,
            p.sku_code,
            p.product_title,
            p.variant_title,
            p.current_price,
            p.inventory_level,
            p.cost_price,
            p.image_url,
            p.status,
            p.created_at,
            p.updated_at,
            
            -- Competitor pricing
            cp.min_price as competitor_min_price,
            cp.max_price as competitor_max_price,
            cp.competitor_count,
            
            -- Trend insights
            ti.google_trend_index,
            ti.social_score,
            ti.final_score as trend_score,
            ti.label as trend_label,
            
            -- Recommendations
            rp.recommended_price,
            rp.pricing_reason,
            rp.recommendation_type,
            rp.confidence_score,
            
            -- Calculated fields
            CASE 
                WHEN p.cost_price > 0 THEN ROUND(((p.current_price - p.cost_price) / p.cost_price * 100), 2)
                ELSE NULL 
            END as current_margin_percent,
            
            CASE 
                WHEN rp.recommended_price IS NOT NULL AND p.cost_price > 0 
                THEN ROUND(((rp.recommended_price - p.cost_price) / p.cost_price * 100), 2)
                ELSE NULL 
            END as recommended_margin_percent
            
        FROM products p
        LEFT JOIN competitor_prices cp ON p.shop_id = cp.shop_id AND p.sku_code = cp.sku_code
        LEFT JOIN trend_insights ti ON p.shop_id = ti.shop_id AND p.sku_code = ti.sku_code
        LEFT JOIN recommended_prices rp ON p.shop_id = rp.shop_id AND p.sku_code = rp.sku_code
        WHERE p.shop_id = :shop_id AND p.sku_code = :sku_code
        """
        
        result = await db_manager.fetch_one(query, {
            "shop_id": shop_id,
            "sku_code": sku_code
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Log product access
        log_business_event(
            "product_accessed",
            user_id=user_id,
            shop_id=shop_id,
            sku_code=sku_code
        )
        
        return ProductDetail(
            sku_id=result["sku_id"],
            shop_id=result["shop_id"],
            shopify_product_id=result["shopify_product_id"],
            sku_code=result["sku_code"],
            product_title=result["product_title"],
            variant_title=result["variant_title"],
            current_price=result["current_price"],
            inventory_level=result["inventory_level"],
            cost_price=result["cost_price"],
            image_url=result["image_url"],
            status=result["status"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            competitor_min_price=result["competitor_min_price"],
            competitor_max_price=result["competitor_max_price"],
            competitor_count=result["competitor_count"],
            google_trend_index=result["google_trend_index"],
            social_score=result["social_score"],
            trend_score=result["trend_score"],
            trend_label=result["trend_label"],
            recommended_price=result["recommended_price"],
            pricing_reason=result["pricing_reason"],
            recommendation_type=result["recommendation_type"],
            confidence_score=result["confidence_score"],
            current_margin_percent=result["current_margin_percent"],
            recommended_margin_percent=result["recommended_margin_percent"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product by SKU error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product service error"
        )


@router.post(
    "",
    response_model=Product,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        409: {"model": ErrorResponse, "description": "Product already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Create product",
    description="Create a new product",
)
async def create_product(
    product_data: ProductCreate,
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Create a new product."""
    
    try:
        # Check if product already exists
        existing_query = """
        SELECT sku_id FROM products 
        WHERE shop_id = :shop_id AND sku_code = :sku_code
        """
        
        existing = await db_manager.fetch_one(existing_query, {
            "shop_id": shop_id,
            "sku_code": product_data.sku_code
        })
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with this SKU already exists"
            )
        
        # Insert new product
        insert_query = """
        INSERT INTO products (
            shop_id, shopify_product_id, sku_code, product_title, variant_title,
            current_price, inventory_level, cost_price, image_url, status
        )
        VALUES (
            :shop_id, :shopify_product_id, :sku_code, :product_title, :variant_title,
            :current_price, :inventory_level, :cost_price, :image_url, :status
        )
        RETURNING sku_id, shop_id, shopify_product_id, sku_code, product_title, 
                  variant_title, current_price, inventory_level, cost_price, 
                  image_url, status, created_at, updated_at
        """
        
        result = await db_manager.fetch_one(insert_query, {
            "shop_id": shop_id,
            "shopify_product_id": product_data.shopify_product_id,
            "sku_code": product_data.sku_code,
            "product_title": product_data.product_title,
            "variant_title": product_data.variant_title,
            "current_price": product_data.current_price,
            "inventory_level": product_data.inventory_level,
            "cost_price": product_data.cost_price,
            "image_url": product_data.image_url,
            "status": product_data.status,
        })
        
        # Log product creation
        log_business_event(
            "product_created",
            user_id=user_id,
            shop_id=shop_id,
            sku_code=product_data.sku_code,
            product_title=product_data.product_title
        )
        
        return Product(
            sku_id=result["sku_id"],
            shop_id=result["shop_id"],
            shopify_product_id=result["shopify_product_id"],
            sku_code=result["sku_code"],
            product_title=result["product_title"],
            variant_title=result["variant_title"],
            current_price=result["current_price"],
            inventory_level=result["inventory_level"],
            cost_price=result["cost_price"],
            image_url=result["image_url"],
            status=result["status"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create product error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product creation service error"
        )


@router.put(
    "/{sku_code}",
    response_model=Product,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Product not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Update product",
    description="Update an existing product",
)
async def update_product(
    sku_code: str,
    product_data: ProductUpdate,
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Update an existing product."""
    
    try:
        # Build update query dynamically based on provided fields
        update_fields = []
        params = {"shop_id": shop_id, "sku_code": sku_code}
        
        for field, value in product_data.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_fields.append("updated_at = NOW()")
        
        update_query = f"""
        UPDATE products 
        SET {', '.join(update_fields)}
        WHERE shop_id = :shop_id AND sku_code = :sku_code
        RETURNING sku_id, shop_id, shopify_product_id, sku_code, product_title, 
                  variant_title, current_price, inventory_level, cost_price, 
                  image_url, status, created_at, updated_at
        """
        
        result = await db_manager.fetch_one(update_query, params)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Log product update
        log_business_event(
            "product_updated",
            user_id=user_id,
            shop_id=shop_id,
            sku_code=sku_code,
            updated_fields=list(product_data.dict(exclude_unset=True).keys())
        )
        
        return Product(
            sku_id=result["sku_id"],
            shop_id=result["shop_id"],
            shopify_product_id=result["shopify_product_id"],
            sku_code=result["sku_code"],
            product_title=result["product_title"],
            variant_title=result["variant_title"],
            current_price=result["current_price"],
            inventory_level=result["inventory_level"],
            cost_price=result["cost_price"],
            image_url=result["image_url"],
            status=result["status"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update product error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product update service error"
        )


@router.delete(
    "/{sku_code}",
    responses={
        200: {"description": "Product deleted successfully"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Product not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Delete product",
    description="Delete a product",
)
async def delete_product(
    sku_code: str,
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Delete a product."""
    
    try:
        # Delete product (CASCADE will handle related records)
        delete_query = """
        DELETE FROM products 
        WHERE shop_id = :shop_id AND sku_code = :sku_code
        RETURNING sku_code, product_title
        """
        
        result = await db_manager.fetch_one(delete_query, {
            "shop_id": shop_id,
            "sku_code": sku_code
        })
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Log product deletion
        log_business_event(
            "product_deleted",
            user_id=user_id,
            shop_id=shop_id,
            sku_code=sku_code,
            product_title=result["product_title"]
        )
        
        return {"message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete product error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product deletion service error"
        )