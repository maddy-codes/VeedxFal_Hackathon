# Database Schema Fix Summary

## Issue Description

The application was experiencing a database schema error when trying to retrieve store statistics after successful OAuth completion:

```
Get store stats error: {'code': '42703', 'details': None, 'hint': None, 'message': 'column products.id does not exist'}
```

## Root Cause Analysis

1. **Schema Mismatch**: The `products` table in the database schema uses `sku_id` as the primary key, not `id`
2. **Query Error**: The store statistics endpoint was trying to select `'id'` from the `products` table
3. **Location**: The error was in `/backend/app/api/v1/shopify.py` line 527

## Database Schema

The `products` table has the following structure (from `backend/migrations/001_initial_schema.sql`):

```sql
CREATE TABLE products (
    sku_id BIGSERIAL PRIMARY KEY,  -- Primary key is sku_id, NOT id
    shop_id BIGINT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    shopify_product_id BIGINT,
    sku_code TEXT NOT NULL,
    product_title TEXT NOT NULL,
    variant_title TEXT,
    current_price NUMERIC(10,2) NOT NULL CHECK (current_price >= 0),
    inventory_level INTEGER NOT NULL DEFAULT 0 CHECK (inventory_level >= 0),
    cost_price NUMERIC(10,2) DEFAULT 0.00 CHECK (cost_price >= 0),
    image_url TEXT,
    status product_status_enum DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- ... constraints and indexes
);
```

## Fix Applied

**File**: `backend/app/api/v1/shopify.py`
**Line**: 527
**Change**: Updated the query to use the correct column name

### Before (Broken):
```python
# Get active products count
active_products_stats = supabase_client.table('products').select(
    'id', count='exact'  # ❌ 'id' column doesn't exist
).eq('shop_id', shop_id).eq('status', 'active').execute()
```

### After (Fixed):
```python
# Get active products count
active_products_stats = supabase_client.table('products').select(
    'sku_id', count='exact'  # ✅ 'sku_id' is the correct primary key
).eq('shop_id', shop_id).eq('status', 'active').execute()
```

## Impact

This fix resolves the database error that was preventing store statistics from being retrieved after successful OAuth authentication. The store statistics endpoint (`GET /api/v1/shopify/stores/{shop_id}/stats`) now works correctly.

## Testing

A test script was created (`test_store_stats_fix.py`) to verify the fix:

1. ✅ Confirms `products` table is accessible with `sku_id` column
2. ✅ Verifies old query with `'id'` fails as expected
3. ✅ Tests the store statistics query pattern works
4. ✅ Tests shop-specific queries work correctly

## Files Modified

1. **`backend/app/api/v1/shopify.py`** - Fixed the store statistics query
2. **`backend/test_store_stats_fix.py`** - Created test script to verify the fix
3. **`backend/DATABASE_SCHEMA_FIX_SUMMARY.md`** - This documentation

## Verification Steps

To verify the fix works:

1. **Run the test script**:
   ```bash
   cd backend
   source .env
   python test_store_stats_fix.py
   ```

2. **Test the API endpoint** (after OAuth setup):
   ```bash
   curl -X GET "http://localhost:8000/api/v1/shopify/stores/{shop_id}/stats" \
        -H "Authorization: Bearer {your_token}"
   ```

## Related Issues

This fix ensures that:
- Store statistics can be retrieved after successful OAuth completion
- The Shopify integration dashboard can display store metrics
- No more `column products.id does not exist` errors occur

## Database Schema Consistency

All queries in the codebase should use the correct column names:
- `products` table: Use `sku_id` (primary key)
- `stores` table: Use `id` (primary key)
- `shopify_products` table: Use `id` (primary key)
- `shopify_stores` table: Use `id` (primary key)

## Future Considerations

1. Consider adding database schema validation tests
2. Add type checking to prevent similar column name mismatches
3. Document the database schema more clearly in the API documentation