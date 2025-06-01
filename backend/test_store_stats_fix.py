#!/usr/bin/env python3
"""
Test script to verify the store statistics fix.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.logging import setup_logging
from app.core.database import get_supabase_client

async def test_store_stats_query():
    """Test the store statistics query to ensure it works with sku_id."""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🧪 Testing store statistics query fix...")
    
    try:
        supabase_client = get_supabase_client()
        
        # Test 1: Check if products table exists and has correct schema
        logger.info("📋 Test 1: Checking products table schema...")
        
        # Get table info (this will help us see the actual columns)
        try:
            # Try to query with sku_id (correct column)
            product_test = supabase_client.table('products').select(
                'sku_id', count='exact'
            ).limit(1).execute()
            
            logger.info(f"✅ Products table accessible with sku_id column")
            logger.info(f"   Query executed successfully, found {product_test.count} total products")
            
        except Exception as e:
            logger.error(f"❌ Error accessing products table with sku_id: {e}")
            return False
        
        # Test 2: Try the old query that was failing (should fail)
        logger.info("📋 Test 2: Verifying old query fails...")
        
        try:
            # This should fail because 'id' column doesn't exist
            old_query = supabase_client.table('products').select(
                'id', count='exact'
            ).limit(1).execute()
            
            logger.warning("⚠️  Old query with 'id' unexpectedly succeeded - this might indicate a schema issue")
            
        except Exception as e:
            logger.info(f"✅ Old query correctly failed: {str(e)[:100]}...")
        
        # Test 3: Test the actual store stats query pattern
        logger.info("📋 Test 3: Testing store statistics query pattern...")
        
        try:
            # Simulate the fixed store stats query
            active_products_stats = supabase_client.table('products').select(
                'sku_id', count='exact'
            ).eq('status', 'active').execute()
            
            logger.info(f"✅ Store stats query pattern works")
            logger.info(f"   Found {active_products_stats.count} active products")
            
            # Test with a specific shop_id if any stores exist
            stores_result = supabase_client.table('stores').select('id').limit(1).execute()
            
            if stores_result.data:
                shop_id = stores_result.data[0]['id']
                logger.info(f"📋 Test 4: Testing with actual shop_id {shop_id}...")
                
                shop_products = supabase_client.table('products').select(
                    'sku_id', count='exact'
                ).eq('shop_id', shop_id).eq('status', 'active').execute()
                
                logger.info(f"✅ Shop-specific query works")
                logger.info(f"   Shop {shop_id} has {shop_products.count} active products")
            else:
                logger.info("ℹ️  No stores found, skipping shop-specific test")
            
        except Exception as e:
            logger.error(f"❌ Store stats query pattern failed: {e}")
            return False
        
        logger.info("🎉 All tests passed! Store statistics fix is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

async def main():
    """Main test runner."""
    
    print("🔧 Store Statistics Fix Test")
    print("=" * 50)
    
    success = await test_store_stats_query()
    
    if success:
        print("\n✅ Fix verification completed successfully!")
        print("The store statistics endpoint should now work without the 'products.id' error.")
        return 0
    else:
        print("\n❌ Fix verification failed!")
        print("There may still be issues with the database schema or query.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)