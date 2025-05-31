"""
File upload API endpoints.
"""

import csv
import io
import logging
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.api.deps import get_current_user_id, get_db_manager_dep, verify_store_access
from app.core.config import settings
from app.core.logging import log_business_event
from app.models.auth import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/csv/products",
    responses={
        200: {"description": "Products uploaded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid file or data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Upload products CSV",
    description="Upload products data via CSV file",
)
async def upload_products_csv(
    file: UploadFile = File(..., description="CSV file with products data"),
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Upload products data via CSV file."""
    
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Parse CSV
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Required columns
        required_columns = ['sku_code', 'product_title', 'current_price']
        
        # Validate headers
        if not all(col in csv_reader.fieldnames for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        # Process rows
        created_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Validate required fields
                if not row.get('sku_code') or not row.get('product_title'):
                    errors.append(f"Row {row_num}: Missing required fields")
                    error_count += 1
                    continue
                
                try:
                    current_price = float(row['current_price'])
                    if current_price < 0:
                        raise ValueError("Price cannot be negative")
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid price value")
                    error_count += 1
                    continue
                
                # Prepare data
                product_data = {
                    'shop_id': shop_id,
                    'sku_code': row['sku_code'].strip(),
                    'product_title': row['product_title'].strip(),
                    'variant_title': row.get('variant_title', '').strip() or None,
                    'current_price': current_price,
                    'inventory_level': int(row.get('inventory_level', 0)),
                    'cost_price': float(row.get('cost_price', 0)) if row.get('cost_price') else None,
                    'image_url': row.get('image_url', '').strip() or None,
                    'status': row.get('status', 'active').strip(),
                }
                
                # Validate status
                if product_data['status'] not in ['active', 'archived', 'draft']:
                    product_data['status'] = 'active'
                
                # Upsert product
                upsert_query = """
                INSERT INTO products (
                    shop_id, sku_code, product_title, variant_title, current_price,
                    inventory_level, cost_price, image_url, status
                )
                VALUES (
                    :shop_id, :sku_code, :product_title, :variant_title, :current_price,
                    :inventory_level, :cost_price, :image_url, :status
                )
                ON CONFLICT (shop_id, sku_code)
                DO UPDATE SET
                    product_title = EXCLUDED.product_title,
                    variant_title = EXCLUDED.variant_title,
                    current_price = EXCLUDED.current_price,
                    inventory_level = EXCLUDED.inventory_level,
                    cost_price = EXCLUDED.cost_price,
                    image_url = EXCLUDED.image_url,
                    status = EXCLUDED.status,
                    updated_at = NOW()
                RETURNING (xmax = 0) AS inserted
                """
                
                result = await db_manager.fetch_one(upsert_query, product_data)
                
                if result['inserted']:
                    created_count += 1
                else:
                    updated_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                error_count += 1
                logger.error(f"CSV upload error for row {row_num}: {e}")
        
        # Log upload
        log_business_event(
            "products_csv_uploaded",
            user_id=user_id,
            shop_id=shop_id,
            filename=file.filename,
            created_count=created_count,
            updated_count=updated_count,
            error_count=error_count
        )
        
        return {
            "message": "CSV upload completed",
            "created_count": created_count,
            "updated_count": updated_count,
            "error_count": error_count,
            "errors": errors[:10],  # Limit errors shown
            "total_errors": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CSV upload service error"
        )


@router.post(
    "/csv/sales",
    responses={
        200: {"description": "Sales uploaded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid file or data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Upload sales CSV",
    description="Upload sales data via CSV file",
)
async def upload_sales_csv(
    file: UploadFile = File(..., description="CSV file with sales data"),
    shop_id: int = Query(..., description="Store ID"),
    user_id: str = Depends(get_current_user_id),
    db_manager=Depends(get_db_manager_dep),
    verified_shop_id: int = Depends(verify_store_access),
):
    """Upload sales data via CSV file."""
    
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Parse CSV
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Required columns
        required_columns = ['sku_code', 'quantity_sold', 'sold_price', 'sold_at']
        
        # Validate headers
        if not all(col in csv_reader.fieldnames for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        # Process rows
        created_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Validate required fields
                if not all(row.get(col) for col in required_columns):
                    errors.append(f"Row {row_num}: Missing required fields")
                    error_count += 1
                    continue
                
                # Validate and parse data
                try:
                    quantity_sold = int(row['quantity_sold'])
                    if quantity_sold <= 0:
                        raise ValueError("Quantity must be positive")
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid quantity value")
                    error_count += 1
                    continue
                
                try:
                    sold_price = float(row['sold_price'])
                    if sold_price < 0:
                        raise ValueError("Price cannot be negative")
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Invalid price value")
                    error_count += 1
                    continue
                
                # Parse date
                from datetime import datetime
                try:
                    sold_at = datetime.fromisoformat(row['sold_at'].replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid date format (use ISO format)")
                    error_count += 1
                    continue
                
                # Check if product exists
                product_check_query = """
                SELECT sku_id FROM products 
                WHERE shop_id = :shop_id AND sku_code = :sku_code
                """
                
                product_exists = await db_manager.fetch_one(product_check_query, {
                    'shop_id': shop_id,
                    'sku_code': row['sku_code'].strip()
                })
                
                if not product_exists:
                    errors.append(f"Row {row_num}: Product with SKU '{row['sku_code']}' not found")
                    error_count += 1
                    continue
                
                # Insert sales record
                insert_query = """
                INSERT INTO sales (
                    shop_id, shopify_order_id, shopify_line_item_id, sku_code,
                    quantity_sold, sold_price, sold_at
                )
                VALUES (
                    :shop_id, :shopify_order_id, :shopify_line_item_id, :sku_code,
                    :quantity_sold, :sold_price, :sold_at
                )
                ON CONFLICT (shop_id, shopify_order_id, shopify_line_item_id) DO NOTHING
                """
                
                # Generate unique IDs for CSV uploads
                import hashlib
                unique_string = f"{shop_id}_{row['sku_code']}_{sold_at.isoformat()}_{quantity_sold}_{sold_price}"
                order_id = int(hashlib.md5(unique_string.encode()).hexdigest()[:8], 16)
                line_item_id = order_id + 1
                
                await db_manager.execute_query(insert_query, {
                    'shop_id': shop_id,
                    'shopify_order_id': order_id,
                    'shopify_line_item_id': line_item_id,
                    'sku_code': row['sku_code'].strip(),
                    'quantity_sold': quantity_sold,
                    'sold_price': sold_price,
                    'sold_at': sold_at
                })
                
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                error_count += 1
                logger.error(f"Sales CSV upload error for row {row_num}: {e}")
        
        # Log upload
        log_business_event(
            "sales_csv_uploaded",
            user_id=user_id,
            shop_id=shop_id,
            filename=file.filename,
            created_count=created_count,
            error_count=error_count
        )
        
        return {
            "message": "Sales CSV upload completed",
            "created_count": created_count,
            "error_count": error_count,
            "errors": errors[:10],  # Limit errors shown
            "total_errors": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sales CSV upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sales CSV upload service error"
        )