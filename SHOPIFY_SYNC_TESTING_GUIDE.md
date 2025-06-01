# Shopify Sync Testing Guide

## 🧪 Testing Scripts Overview

I've created comprehensive testing scripts to verify that the Shopify sync functionality works correctly. Here are the available testing tools:

### 1. Quick Test (Recommended First)
**File**: [`backend/test_sync_quick.py`](backend/test_sync_quick.py)
**Purpose**: Fast verification of essential components
**Runtime**: ~10 seconds

### 2. Comprehensive Test
**File**: [`backend/test_shopify_sync_complete.py`](backend/test_shopify_sync_complete.py)
**Purpose**: Thorough testing of all sync functionality
**Runtime**: ~30-60 seconds

### 3. Real Sync Test (If you have connected stores)
**File**: [`backend/test_disconnect_and_sync.py`](backend/test_disconnect_and_sync.py)
**Purpose**: Test actual Shopify API sync with real stores
**Runtime**: Variable (depends on store size)

## 🚀 Step-by-Step Testing Process

### Step 1: Quick Verification
```bash
cd backend
source .env
python test_sync_quick.py
```

**Expected Output**:
```
🚀 QUICK SHOPIFY SYNC TEST
========================================
1. Testing database connection...
   ✅ Database connected
2. Testing required tables...
   ✅ stores table OK
   ✅ products table OK
   ✅ sync_jobs table OK
   ✅ webhook_events table OK
3. Testing ShopifyService...
   ✅ ShopifyService initialized
4. Testing sync job operations...
   ✅ Sync job created: 123
   ✅ Sync job cleaned up
5. Testing product operations...
   ✅ Product created: 456
   ✅ Product cleaned up
6. Checking for active stores...
   ✅ Found 1 active store(s)
      - Your Store Name (yourstore.myshopify.com)

🎉 QUICK TEST PASSED!
```

### Step 2: Comprehensive Testing
```bash
python test_shopify_sync_complete.py
```

**What it tests**:
- ✅ Database table existence and accessibility
- ✅ Sync job creation, update, completion, and cleanup
- ✅ Product creation, update, SKU lookup, and cleanup
- ✅ Webhook event creation, processing, and cleanup
- ✅ Store operations and statistics
- ✅ ShopifyService method functionality
- ✅ Error handling scenarios

**Expected Output**:
```
=== SHOPIFY SYNC COMPREHENSIVE TEST ===
Started at: 2025-05-31T22:55:00.000Z

✅ PASS Database Connection: Supabase client initialized
✅ PASS Service Initialization: ShopifyService initialized

=== TESTING DATABASE TABLES ===
✅ PASS Table: stores: Table exists and accessible
✅ PASS Table: products: Table exists and accessible
✅ PASS Table: sync_jobs: Table exists and accessible
✅ PASS Table: webhook_events: Table exists and accessible

=== TESTING SYNC JOB OPERATIONS ===
✅ PASS Sync Job Creation: Created sync job with ID: 789
✅ PASS Sync Job Update: Successfully updated sync job
✅ PASS Sync Job Retrieval: Successfully retrieved and verified sync job
✅ PASS Sync Job Completion: Successfully marked sync job as completed
✅ PASS Sync Job Cleanup: Test sync job cleaned up

... (more detailed tests)

============================================================
COMPREHENSIVE TEST REPORT
============================================================
Total Tests: 25
Passed: 25 ✅
Failed: 0 ❌
Success Rate: 100.0%

🎉 ALL TESTS PASSED! Shopify sync functionality is ready to use.
```

### Step 3: Real Sync Testing (Optional)
**Only if you have connected Shopify stores**:
```bash
python test_disconnect_and_sync.py
```

## 🔍 What Each Test Verifies

### Quick Test Checks:
1. **Database Connection**: Can connect to Supabase
2. **Table Existence**: All required tables exist and are accessible
3. **Service Initialization**: ShopifyService can be created
4. **Basic Operations**: Can create/update/delete sync jobs and products
5. **Store Status**: Shows connected stores (if any)

### Comprehensive Test Checks:
1. **Database Tables**: Detailed table accessibility testing
2. **Sync Job Lifecycle**: Full CRUD operations on sync jobs
3. **Product Lifecycle**: Full CRUD operations on products
4. **Webhook Operations**: Webhook event handling
5. **Store Operations**: Store statistics and data counting
6. **Service Methods**: ShopifyService internal methods
7. **Error Handling**: Invalid operations and error recovery
8. **Shopify Columns**: Tests if Shopify-specific columns exist

### Real Sync Test Checks:
1. **Store Connection**: Verifies OAuth-connected stores
2. **Product Sync**: Actually syncs products from Shopify API
3. **Progress Monitoring**: Tracks sync progress in real-time
4. **Store Disconnect**: Tests cleanup operations

## 📊 Test Reports

### Quick Test
- Prints results to console
- Simple pass/fail for each component

### Comprehensive Test
- Detailed console output
- Generates `shopify_sync_test_report.json` with full results
- Includes timestamps, error details, and success rates

## 🐛 Troubleshooting Test Failures

### Common Issues and Solutions:

#### 1. Database Connection Failed
```
❌ Database Connection: Failed to initialize services
```
**Solutions**:
- Check `.env` file has correct Supabase credentials
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- Test connection: `python -c "from app.core.database import get_supabase_client; print(get_supabase_client())"`

#### 2. Table Not Found
```
❌ Table: sync_jobs: Table not accessible
```
**Solutions**:
- Ensure you created the `sync_jobs` and `webhook_events` tables
- Check table permissions in Supabase dashboard
- Verify using service role key, not anon key

#### 3. Product Creation Failed
```
❌ Product Creation: No data returned from product insert
```
**Solutions**:
- Check RLS policies allow service role access
- Verify `products` table has required columns
- Run: `python run_add_shopify_columns.py` to add missing columns

#### 4. Shopify Columns Not Available
```
❌ Shopify Columns: Shopify-specific columns not available
```
**Solutions**:
- This is expected if you haven't run the column migration
- Run: `python run_add_shopify_columns.py`
- Or continue with core schema only (sync will still work)

#### 5. No Active Stores
```
⚠️ No active stores found
```
**Solutions**:
- Connect a Shopify store using OAuth flow first
- Check stores table: `SELECT * FROM stores WHERE is_active = true`
- This doesn't prevent testing, just limits real sync tests

## 🎯 Success Criteria

### Minimum Requirements (Quick Test):
- ✅ Database connection works
- ✅ All 4 tables accessible
- ✅ Can create/update sync jobs
- ✅ Can create/update products

### Full Functionality (Comprehensive Test):
- ✅ All basic operations work
- ✅ Error handling works correctly
- ✅ Service methods function properly
- ✅ Webhook operations work

### Production Ready:
- ✅ All tests pass
- ✅ At least one active store connected
- ✅ Real sync test completes successfully

## 📝 Running Tests in CI/CD

For automated testing, use:
```bash
# Quick verification
python test_sync_quick.py

# Full test suite
python test_shopify_sync_complete.py

# Check exit codes
if [ $? -eq 0 ]; then
    echo "Tests passed"
else
    echo "Tests failed"
    exit 1
fi
```

## 🔄 Test Data Cleanup

All test scripts automatically clean up their test data:
- Test sync jobs are deleted after creation
- Test products are removed after testing
- Test webhook events are cleaned up
- No permanent test data is left in your database

## 📞 Getting Help

If tests fail:
1. **Check the error messages** - they usually indicate the specific issue
2. **Review the troubleshooting section** above
3. **Check the generated test report** (`shopify_sync_test_report.json`)
4. **Verify your environment setup** (`.env` file, database permissions)
5. **Run tests individually** to isolate issues

The testing scripts are designed to be comprehensive and help you identify exactly what needs to be fixed for the Shopify sync functionality to work correctly.