#!/usr/bin/env python3
"""
Comprehensive Shopify Sync Testing Script
Tests all aspects of the sync functionality to ensure it works correctly.
"""

import os
import sys
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client
from app.services.shopify_service import ShopifyService

class ShopifySyncTester:
    def __init__(self):
        self.supabase_client = None
        self.shopify_service = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if details and not success:
            print(f"   Details: {details}")
    
    async def setup(self):
        """Initialize services and connections."""
        print("=== SHOPIFY SYNC COMPREHENSIVE TEST ===")
        print(f"Started at: {datetime.utcnow().isoformat()}")
        print()
        
        try:
            # Initialize Supabase client
            self.supabase_client = get_supabase_client()
            self.log_test("Database Connection", True, "Supabase client initialized")
            
            # Initialize Shopify service
            self.shopify_service = ShopifyService()
            self.log_test("Service Initialization", True, "ShopifyService initialized")
            
            return True
            
        except Exception as e:
            self.log_test("Setup", False, "Failed to initialize services", str(e))
            return False
    
    async def test_database_tables(self):
        """Test that all required database tables exist and are accessible."""
        print("\n=== TESTING DATABASE TABLES ===")
        
        tables_to_test = [
            ("stores", "id"),
            ("products", "sku_id"),
            ("sync_jobs", "id"),
            ("webhook_events", "id")
        ]
        
        all_tables_ok = True
        
        for table_name, primary_key in tables_to_test:
            try:
                result = self.supabase_client.table(table_name).select(primary_key).limit(1).execute()
                self.log_test(f"Table: {table_name}", True, f"Table exists and accessible")
            except Exception as e:
                self.log_test(f"Table: {table_name}", False, f"Table not accessible", str(e))
                all_tables_ok = False
        
        return all_tables_ok
    
    async def test_sync_job_operations(self):
        """Test sync job creation, update, and deletion."""
        print("\n=== TESTING SYNC JOB OPERATIONS ===")
        
        try:
            # Create a test sync job
            test_sync_data = {
                "shop_id": 999999,  # Test shop ID
                "sync_type": "product_sync",
                "status": "pending",
                "total_items": 0,
                "processed_items": 0,
                "failed_items": 0,
                "sync_config": {"test": True, "full_sync": False}
            }
            
            # Test creation
            create_result = self.supabase_client.table('sync_jobs').insert(test_sync_data).execute()
            
            if not create_result.data:
                self.log_test("Sync Job Creation", False, "No data returned from insert")
                return False
            
            sync_job_id = create_result.data[0]['id']
            self.log_test("Sync Job Creation", True, f"Created sync job with ID: {sync_job_id}")
            
            # Test update
            update_data = {
                "status": "running",
                "processed_items": 5,
                "sync_details": {"test_update": True}
            }
            
            update_result = self.supabase_client.table('sync_jobs').update(update_data).eq('id', sync_job_id).execute()
            
            if update_result.data:
                self.log_test("Sync Job Update", True, "Successfully updated sync job")
            else:
                self.log_test("Sync Job Update", False, "Update returned no data")
            
            # Test retrieval
            get_result = self.supabase_client.table('sync_jobs').select('*').eq('id', sync_job_id).execute()
            
            if get_result.data and get_result.data[0]['status'] == 'running':
                self.log_test("Sync Job Retrieval", True, "Successfully retrieved and verified sync job")
            else:
                self.log_test("Sync Job Retrieval", False, "Failed to retrieve or verify sync job")
            
            # Test completion
            complete_data = {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "sync_details": {"test_completed": True}
            }
            
            complete_result = self.supabase_client.table('sync_jobs').update(complete_data).eq('id', sync_job_id).execute()
            
            if complete_result.data:
                self.log_test("Sync Job Completion", True, "Successfully marked sync job as completed")
            else:
                self.log_test("Sync Job Completion", False, "Failed to mark sync job as completed")
            
            # Cleanup
            self.supabase_client.table('sync_jobs').delete().eq('id', sync_job_id).execute()
            self.log_test("Sync Job Cleanup", True, "Test sync job cleaned up")
            
            return True
            
        except Exception as e:
            self.log_test("Sync Job Operations", False, "Exception during sync job testing", str(e))
            return False
    
    async def test_product_operations(self):
        """Test product creation, update, and deletion."""
        print("\n=== TESTING PRODUCT OPERATIONS ===")
        
        try:
            # Test product data with core schema only
            test_product_data = {
                "shop_id": 999999,  # Test shop ID
                "shopify_product_id": 888888888,
                "sku_code": f"TEST-SYNC-{int(time.time())}",
                "product_title": "Test Sync Product",
                "variant_title": "Test Variant",
                "current_price": 29.99,
                "inventory_level": 10,
                "cost_price": 15.00,
                "status": "active"
            }
            
            # Test creation
            create_result = self.supabase_client.table('products').insert(test_product_data).execute()
            
            if not create_result.data:
                self.log_test("Product Creation", False, "No data returned from product insert")
                return False
            
            product_id = create_result.data[0]['sku_id']
            self.log_test("Product Creation", True, f"Created product with SKU ID: {product_id}")
            
            # Test update
            update_data = {
                "current_price": 39.99,
                "inventory_level": 15,
                "status": "active"
            }
            
            update_result = self.supabase_client.table('products').update(update_data).eq('sku_id', product_id).execute()
            
            if update_result.data:
                self.log_test("Product Update", True, "Successfully updated product")
            else:
                self.log_test("Product Update", False, "Product update returned no data")
            
            # Test retrieval by SKU code
            sku_lookup = self.supabase_client.table('products').select('*').eq('sku_code', test_product_data['sku_code']).execute()
            
            if sku_lookup.data and sku_lookup.data[0]['current_price'] == 39.99:
                self.log_test("Product SKU Lookup", True, "Successfully found product by SKU code")
            else:
                self.log_test("Product SKU Lookup", False, "Failed to find product by SKU code")
            
            # Test Shopify-specific columns (if they exist)
            try:
                shopify_data = {
                    "shopify_variant_id": 777777777,
                    "handle": "test-sync-product",
                    "vendor": "Test Vendor",
                    "product_type": "Test Type"
                }
                
                shopify_update = self.supabase_client.table('products').update(shopify_data).eq('sku_id', product_id).execute()
                
                if shopify_update.data:
                    self.log_test("Shopify Columns", True, "Shopify-specific columns are available and working")
                else:
                    self.log_test("Shopify Columns", False, "Shopify columns update returned no data")
                    
            except Exception as e:
                self.log_test("Shopify Columns", False, "Shopify-specific columns not available", str(e))
            
            # Cleanup
            self.supabase_client.table('products').delete().eq('sku_id', product_id).execute()
            self.log_test("Product Cleanup", True, "Test product cleaned up")
            
            return True
            
        except Exception as e:
            self.log_test("Product Operations", False, "Exception during product testing", str(e))
            return False
    
    async def test_webhook_operations(self):
        """Test webhook event operations."""
        print("\n=== TESTING WEBHOOK OPERATIONS ===")
        
        try:
            # Test webhook event data
            test_webhook_data = {
                "shop_id": 999999,
                "event_type": "products/create",
                "shopify_id": "test_product_123",
                "event_data": {"test": True, "product_id": 123},
                "processed": False,
                "retry_count": 0
            }
            
            # Test creation
            create_result = self.supabase_client.table('webhook_events').insert(test_webhook_data).execute()
            
            if not create_result.data:
                self.log_test("Webhook Creation", False, "No data returned from webhook insert")
                return False
            
            webhook_id = create_result.data[0]['id']
            self.log_test("Webhook Creation", True, f"Created webhook event with ID: {webhook_id}")
            
            # Test update (mark as processed)
            update_data = {
                "processed": True,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            update_result = self.supabase_client.table('webhook_events').update(update_data).eq('id', webhook_id).execute()
            
            if update_result.data:
                self.log_test("Webhook Update", True, "Successfully updated webhook event")
            else:
                self.log_test("Webhook Update", False, "Webhook update returned no data")
            
            # Cleanup
            self.supabase_client.table('webhook_events').delete().eq('id', webhook_id).execute()
            self.log_test("Webhook Cleanup", True, "Test webhook event cleaned up")
            
            return True
            
        except Exception as e:
            self.log_test("Webhook Operations", False, "Exception during webhook testing", str(e))
            return False
    
    async def test_store_operations(self):
        """Test store-related operations."""
        print("\n=== TESTING STORE OPERATIONS ===")
        
        try:
            # Check for existing active stores
            stores_result = self.supabase_client.table('stores').select(
                'id, shop_domain, shop_name, is_active, access_token'
            ).eq('is_active', True).execute()
            
            if stores_result.data:
                self.log_test("Active Stores", True, f"Found {len(stores_result.data)} active store(s)")
                
                for store in stores_result.data:
                    print(f"   - Store ID: {store['id']}")
                    print(f"     Domain: {store['shop_domain']}")
                    print(f"     Name: {store['shop_name']}")
                    print(f"     Has Token: {'Yes' if store.get('access_token') else 'No'}")
                
                # Test store statistics query
                test_store = stores_result.data[0]
                shop_id = test_store['id']
                
                # Count products for this store
                products_count = self.supabase_client.table('products').select(
                    'sku_id', count='exact'
                ).eq('shop_id', shop_id).execute()
                
                self.log_test("Store Products Count", True, f"Store {shop_id} has {products_count.count or 0} products")
                
                # Count sync jobs for this store
                sync_jobs_count = self.supabase_client.table('sync_jobs').select(
                    'id', count='exact'
                ).eq('shop_id', shop_id).execute()
                
                self.log_test("Store Sync Jobs Count", True, f"Store {shop_id} has {sync_jobs_count.count or 0} sync jobs")
                
                return True
                
            else:
                self.log_test("Active Stores", False, "No active stores found - connect a Shopify store first")
                return False
                
        except Exception as e:
            self.log_test("Store Operations", False, "Exception during store testing", str(e))
            return False
    
    async def test_sync_service_methods(self):
        """Test ShopifyService methods."""
        print("\n=== TESTING SHOPIFY SERVICE METHODS ===")
        
        try:
            # Test service initialization
            if self.shopify_service:
                self.log_test("Service Instance", True, "ShopifyService instance available")
            else:
                self.log_test("Service Instance", False, "ShopifyService instance not available")
                return False
            
            # Test _get_store method with a test store
            stores_result = self.supabase_client.table('stores').select('id').eq('is_active', True).limit(1).execute()
            
            if stores_result.data:
                test_shop_id = stores_result.data[0]['id']
                
                try:
                    store = await self.shopify_service._get_store(test_shop_id)
                    self.log_test("Get Store Method", True, f"Successfully retrieved store {test_shop_id}")
                except Exception as e:
                    self.log_test("Get Store Method", False, f"Failed to get store {test_shop_id}", str(e))
            else:
                self.log_test("Get Store Method", False, "No stores available to test")
            
            return True
            
        except Exception as e:
            self.log_test("Service Methods", False, "Exception during service method testing", str(e))
            return False
    
    async def test_error_handling(self):
        """Test error handling scenarios."""
        print("\n=== TESTING ERROR HANDLING ===")
        
        try:
            # Test invalid shop ID
            try:
                invalid_store = await self.shopify_service._get_store(999999999)
                self.log_test("Invalid Store ID", False, "Should have failed with invalid store ID")
            except Exception:
                self.log_test("Invalid Store ID", True, "Correctly handled invalid store ID")
            
            # Test invalid table query
            try:
                invalid_result = self.supabase_client.table('nonexistent_table').select('*').execute()
                self.log_test("Invalid Table", False, "Should have failed with invalid table")
            except Exception:
                self.log_test("Invalid Table", True, "Correctly handled invalid table query")
            
            # Test invalid column query
            try:
                invalid_column = self.supabase_client.table('products').select('nonexistent_column').limit(1).execute()
                self.log_test("Invalid Column", False, "Should have failed with invalid column")
            except Exception:
                self.log_test("Invalid Column", True, "Correctly handled invalid column query")
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, "Exception during error handling testing", str(e))
            return False
    
    def generate_report(self):
        """Generate a comprehensive test report."""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['message']}")
                    if result['details']:
                        print(f"   Details: {result['details']}")
        
        print(f"\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        with open('shopify_sync_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: shopify_sync_test_report.json")
        
        return failed_tests == 0

async def main():
    """Run all tests."""
    tester = ShopifySyncTester()
    
    # Setup
    if not await tester.setup():
        print("❌ Setup failed, cannot continue with tests")
        return False
    
    # Run all test suites
    test_suites = [
        tester.test_database_tables,
        tester.test_sync_job_operations,
        tester.test_product_operations,
        tester.test_webhook_operations,
        tester.test_store_operations,
        tester.test_sync_service_methods,
        tester.test_error_handling
    ]
    
    all_passed = True
    for test_suite in test_suites:
        try:
            result = await test_suite()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Test suite failed with exception: {e}")
            all_passed = False
    
    # Generate report
    success = tester.generate_report()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Shopify sync functionality is ready to use.")
    else:
        print("\n💥 SOME TESTS FAILED! Check the report above for details.")
    
    return success

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)