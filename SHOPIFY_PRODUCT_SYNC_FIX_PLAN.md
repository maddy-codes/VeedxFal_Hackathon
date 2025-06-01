# Shopify Product Sync Fix Implementation Plan

## Issue Analysis

After reviewing the codebase, I've identified the specific issues preventing the Shopify product sync from working:

### 1. Table Reference Issues
- **Problem**: Code references `shopify_sync_jobs` but you created `sync_jobs`
- **Location**: [`backend/app/services/shopify_service.py`](backend/app/services/shopify_service.py) lines 964, 1187, 1204, 1267, 1309, 1347, 1394

### 2. Database Schema Mismatch
- **Problem**: Code tries to insert Shopify-specific fields into core `products` table
- **Missing Columns**: `shopify_variant_id`, `handle`, `product_type`, `vendor`, `tags`, `published_at`, `shopify_created_at`, `shopify_updated_at`
- **Location**: [`backend/app/services/shopify_service.py`](backend/app/services/shopify_service.py) lines 1422-1441

### 3. Query Logic Issues
- **Problem**: Queries assume `shopify_variant_id` column exists
- **Location**: Lines 1292-1294, 1449-1451

## Solution Strategy

### Option A: Minimal Database Changes (Recommended)

#### Step 1: Add Missing Columns to `products` Table
```sql
-- Add Shopify-specific columns to existing products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS shopify_variant_id BIGINT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS handle TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS product_type TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS vendor TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tags TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS shopify_created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS shopify_updated_at TIMESTAMP WITH TIME ZONE;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_shopify_variant_id ON products(shopify_variant_id);
CREATE INDEX IF NOT EXISTS idx_products_handle ON products(handle);
CREATE INDEX IF NOT EXISTS idx_products_vendor ON products(vendor);

-- Update unique constraint to include variant_id
ALTER TABLE products DROP CONSTRAINT IF EXISTS products_shopify_product_unique;
ALTER TABLE products ADD CONSTRAINT products_shopify_product_variant_unique 
    UNIQUE (shop_id, shopify_product_id, shopify_variant_id);
```

#### Step 2: Update Service Layer Code

**File**: [`backend/app/services/shopify_service.py`](backend/app/services/shopify_service.py)

**Changes Required**:

1. **Replace all `shopify_sync_jobs` with `sync_jobs`**:
   - Line 964: `self.supabase_client.table('sync_jobs').insert(`
   - Line 1187: `sync_job_result = self.supabase_client.table('sync_jobs').select(`
   - Line 1204: `self.supabase_client.table('sync_jobs').update({`
   - Line 1267: `self.supabase_client.table('sync_jobs').update({`
   - Line 1309: `self.supabase_client.table('sync_jobs').update({`
   - Line 1347: `self.supabase_client.table('sync_jobs').update({`
   - Line 1394: `self.supabase_client.table('sync_jobs').update({`

2. **Update Product Variant Sync Logic** (lines 1292-1294):
```python
# OLD CODE:
existing_product = self.supabase_client.table('products').select(
    'sku_id'
).eq('shop_id', shop_id).eq('shopify_product_id', shopify_product['id']).eq('shopify_variant_id', variant['id']).execute()

# NEW CODE:
existing_product = self.supabase_client.table('products').select(
    'sku_id'
).eq('shop_id', shop_id).eq('shopify_product_id', shopify_product['id']).eq('shopify_variant_id', variant['id']).execute()
```

3. **Update Product Data Structure** (lines 1422-1441):
```python
# Keep all existing fields, they should work with the new columns
product_data = {
    "shop_id": shop_id,
    "shopify_product_id": shopify_product['id'],
    "shopify_variant_id": variant['id'],  # This will now work
    "sku_code": variant.get('sku') or f"shopify-{variant['id']}",
    "product_title": shopify_product.get('title', ''),
    "variant_title": variant.get('title'),
    "current_price": float(variant.get('price', 0)),
    "inventory_level": variant.get('inventory_quantity', 0),
    "cost_price": float(variant.get('compare_at_price', 0)) if variant.get('compare_at_price') else None,
    "image_url": None,
    "status": "active" if shopify_product.get('status') == 'active' else "inactive",
    "handle": shopify_product.get('handle', ''),
    "product_type": shopify_product.get('product_type'),
    "vendor": shopify_product.get('vendor'),
    "tags": shopify_product.get('tags'),
    "published_at": shopify_product.get('published_at'),
    "shopify_created_at": shopify_product.get('created_at'),
    "shopify_updated_at": shopify_product.get('updated_at')
}
```

### Option B: Use Core Schema Only (Alternative)

If you prefer not to add columns, modify the product sync to only use existing columns:

#### Step 1: Update Service Layer to Use Core Schema Only

**File**: [`backend/app/services/shopify_service.py`](backend/app/services/shopify_service.py)

1. **Replace `shopify_sync_jobs` with `sync_jobs`** (same as Option A)

2. **Simplify Product Data Structure** (lines 1422-1441):
```python
# Simplified product data using only core schema
product_data = {
    "shop_id": shop_id,
    "shopify_product_id": shopify_product['id'],
    "sku_code": variant.get('sku') or f"shopify-{variant['id']}",
    "product_title": shopify_product.get('title', ''),
    "variant_title": variant.get('title'),
    "current_price": float(variant.get('price', 0)),
    "inventory_level": variant.get('inventory_quantity', 0),
    "cost_price": float(variant.get('compare_at_price', 0)) if variant.get('compare_at_price') else None,
    "image_url": None,
    "status": "active" if shopify_product.get('status') == 'active' else "inactive"
}

# Store additional Shopify data in a separate table or JSONB field
shopify_metadata = {
    "variant_id": variant['id'],
    "handle": shopify_product.get('handle', ''),
    "product_type": shopify_product.get('product_type'),
    "vendor": shopify_product.get('vendor'),
    "tags": shopify_product.get('tags'),
    "published_at": shopify_product.get('published_at'),
    "shopify_created_at": shopify_product.get('created_at'),
    "shopify_updated_at": shopify_product.get('updated_at')
}
# Could store this in shop_config or a separate metadata table
```

3. **Update Existing Product Check** (lines 1292-1294 and 1449-1451):
```python
# Use only shopify_product_id and sku_code for uniqueness
existing_product = self.supabase_client.table('products').select(
    'sku_id'
).eq('shop_id', shop_id).eq('shopify_product_id', shopify_product['id']).eq('sku_code', variant.get('sku') or f"shopify-{variant['id']}").execute()
```

## Additional Fixes Required

### 1. Update API Endpoints

**File**: [`backend/app/api/v1/shopify.py`](backend/app/api/v1/shopify.py)

**Lines 562, 690**: Replace `shopify_sync_jobs` with `sync_jobs`
```python
# Line 562:
sync_result = supabase_client.table('sync_jobs').select(
    'status'
).eq('shop_id', shop_id).execute()

# Line 690:
result = supabase_client.table('sync_jobs').select(
    '*'
).eq('shop_id', shop_id).order('created_at', desc=True).limit(limit).execute()
```

### 2. Update Disconnect Store Logic

**File**: [`backend/app/services/shopify_service.py`](backend/app/services/shopify_service.py)

**Lines 1522, 1538**: Replace `shopify_sync_jobs` with `sync_jobs`
```python
# Line 1522:
sync_jobs_count = self.supabase_client.table('sync_jobs').select(
    'id', count='exact'
).eq('shop_id', shop_id).eq('status', 'running').execute()

# Line 1538:
sync_jobs_result = self.supabase_client.table('sync_jobs').update({
    "status": ShopifySyncStatus.CANCELLED,
    "completed_at": datetime.utcnow().isoformat()
}).eq('shop_id', shop_id).eq('status', 'running').execute()
```

### 3. Update Test Files

**File**: [`backend/test_disconnect_and_sync.py`](backend/test_disconnect_and_sync.py)

**Lines 73, 138**: Replace `shopify_sync_jobs` with `sync_jobs`
```python
# Line 73:
job_result = supabase_client.table('sync_jobs').select(
    '*'
).eq('id', sync_job_id).execute()

# Line 138:
sync_jobs_count = supabase_client.table('sync_jobs').select(
    'id', count='exact'
).eq('shop_id', shop_id).execute()
```

## Implementation Steps

### Step 1: Choose Your Approach
- **Option A**: Add columns to `products` table (more complete Shopify integration)
- **Option B**: Use core schema only (simpler, less storage)

### Step 2: Apply Database Changes (if Option A)
Run the SQL migration to add missing columns to `products` table.

### Step 3: Update Service Layer
Apply all the code changes listed above to [`backend/app/services/shopify_service.py`](backend/app/services/shopify_service.py).

### Step 4: Update API Layer
Apply changes to [`backend/app/api/v1/shopify.py`](backend/app/api/v1/shopify.py).

### Step 5: Update Test Files
Apply changes to test files to use correct table names.

### Step 6: Test the Implementation
1. **Test Product Sync**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/shopify/stores/{shop_id}/sync/products" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer {token}" \
        -d '{"shop_id": 123, "full_sync": true}'
   ```

2. **Monitor Sync Progress**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/shopify/stores/{shop_id}/sync/jobs" \
        -H "Authorization: Bearer {token}"
   ```

3. **Check Database**:
   ```sql
   SELECT COUNT(*) FROM sync_jobs WHERE shop_id = {shop_id};
   SELECT COUNT(*) FROM products WHERE shop_id = {shop_id};
   ```

## Expected Results

After implementing these fixes:

1. ✅ **Sync Jobs Created**: `sync_jobs` table will track sync operations
2. ✅ **Products Synced**: Products will be stored in `products` table with correct schema
3. ✅ **Progress Tracking**: Real-time sync progress updates will work
4. ✅ **Error Handling**: Failed syncs will be properly logged and tracked
5. ✅ **Store Disconnect**: Cleanup operations will work correctly

## Rollback Plan

If issues occur:
1. **Database Rollback**: Remove added columns if using Option A
2. **Code Rollback**: Revert service layer changes
3. **Table Cleanup**: Clear any test data from `sync_jobs` and `products` tables

## Monitoring and Validation

After implementation, monitor:
1. **Sync Job Status**: Check `sync_jobs` table for successful completions
2. **Product Count**: Verify products are being created/updated
3. **Error Logs**: Monitor application logs for any remaining issues
4. **API Response Times**: Ensure sync operations don't timeout

This plan provides a comprehensive solution to fix the Shopify product sync functionality while maintaining compatibility with your existing database schema.