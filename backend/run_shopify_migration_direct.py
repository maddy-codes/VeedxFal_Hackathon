#!/usr/bin/env python3
"""
Run Shopify tables migration using direct database connection.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.logging import setup_logging
from app.core.database import get_database


async def create_shopify_tables():
    """Create Shopify integration tables using direct SQL execution."""
    
    database = await get_database()
    
    # SQL statements for creating tables (adapted for SQLite/PostgreSQL compatibility)
    sql_statements = [
        # Create shopify_stores table
        """
        CREATE TABLE IF NOT EXISTS shopify_stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            shop_domain VARCHAR(255) NOT NULL UNIQUE,
            shop_name VARCHAR(255) NOT NULL,
            shop_id BIGINT,
            access_token TEXT NOT NULL,
            scope TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            shop_config TEXT DEFAULT '{}',
            last_sync_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Create indexes for shopify_stores
        "CREATE INDEX IF NOT EXISTS idx_shopify_stores_user_id ON shopify_stores(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_stores_shop_domain ON shopify_stores(shop_domain);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_stores_is_active ON shopify_stores(is_active);",
        
        # Create shopify_products table
        """
        CREATE TABLE IF NOT EXISTS shopify_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            sku_id INTEGER NOT NULL,
            shopify_product_id BIGINT NOT NULL,
            shopify_variant_id BIGINT,
            handle VARCHAR(255) NOT NULL,
            product_type VARCHAR(255),
            vendor VARCHAR(255),
            tags TEXT,
            published_at TIMESTAMP,
            shopify_created_at TIMESTAMP,
            shopify_updated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shopify_stores(id) ON DELETE CASCADE,
            UNIQUE(shop_id, shopify_product_id, shopify_variant_id)
        );
        """,
        
        # Create indexes for shopify_products
        "CREATE INDEX IF NOT EXISTS idx_shopify_products_shop_id ON shopify_products(shop_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_products_sku_id ON shopify_products(sku_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_products_shopify_product_id ON shopify_products(shopify_product_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_products_handle ON shopify_products(handle);",
        
        # Create shopify_orders table
        """
        CREATE TABLE IF NOT EXISTS shopify_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            shopify_order_id BIGINT NOT NULL,
            order_number VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            total_price DECIMAL(10,2) NOT NULL,
            subtotal_price DECIMAL(10,2) NOT NULL,
            total_tax DECIMAL(10,2) DEFAULT 0,
            currency VARCHAR(3) NOT NULL,
            financial_status VARCHAR(50) NOT NULL,
            fulfillment_status VARCHAR(50),
            order_status_url TEXT,
            customer_data TEXT DEFAULT '{}',
            line_items TEXT NOT NULL DEFAULT '[]',
            shipping_address TEXT DEFAULT '{}',
            billing_address TEXT DEFAULT '{}',
            shopify_created_at TIMESTAMP NOT NULL,
            shopify_updated_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shopify_stores(id) ON DELETE CASCADE,
            UNIQUE(shop_id, shopify_order_id)
        );
        """,
        
        # Create indexes for shopify_orders
        "CREATE INDEX IF NOT EXISTS idx_shopify_orders_shop_id ON shopify_orders(shop_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_orders_shopify_order_id ON shopify_orders(shopify_order_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_orders_order_number ON shopify_orders(order_number);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_orders_financial_status ON shopify_orders(financial_status);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_orders_created_at ON shopify_orders(shopify_created_at);",
        
        # Create shopify_webhook_events table
        """
        CREATE TABLE IF NOT EXISTS shopify_webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            shopify_id VARCHAR(255) NOT NULL,
            webhook_id VARCHAR(255),
            event_data TEXT NOT NULL,
            processed BOOLEAN DEFAULT FALSE,
            processed_at TIMESTAMP,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shopify_stores(id) ON DELETE CASCADE
        );
        """,
        
        # Create indexes for shopify_webhook_events
        "CREATE INDEX IF NOT EXISTS idx_shopify_webhook_events_shop_id ON shopify_webhook_events(shop_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_webhook_events_event_type ON shopify_webhook_events(event_type);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_webhook_events_processed ON shopify_webhook_events(processed);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_webhook_events_created_at ON shopify_webhook_events(created_at);",
        
        # Create shopify_sync_jobs table
        """
        CREATE TABLE IF NOT EXISTS shopify_sync_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            sync_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            total_items INTEGER,
            processed_items INTEGER DEFAULT 0,
            failed_items INTEGER DEFAULT 0,
            sync_config TEXT DEFAULT '{}',
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT,
            sync_details TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shopify_stores(id) ON DELETE CASCADE
        );
        """,
        
        # Create indexes for shopify_sync_jobs
        "CREATE INDEX IF NOT EXISTS idx_shopify_sync_jobs_shop_id ON shopify_sync_jobs(shop_id);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_sync_jobs_sync_type ON shopify_sync_jobs(sync_type);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_sync_jobs_status ON shopify_sync_jobs(status);",
        "CREATE INDEX IF NOT EXISTS idx_shopify_sync_jobs_created_at ON shopify_sync_jobs(created_at);",
    ]
    
    try:
        # Connect to database
        await database.connect()
        
        # Execute each SQL statement
        for i, sql in enumerate(sql_statements):
            try:
                logger.info(f"Executing migration step {i + 1}/{len(sql_statements)}")
                await database.execute(sql.strip())
                logger.info(f"Step {i + 1} completed successfully")
                    
            except Exception as e:
                logger.error(f"Error executing migration step {i + 1}: {e}")
                # Continue with other statements for non-critical errors
                continue
        
        logger.info("Shopify tables migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        try:
            await database.disconnect()
        except:
            pass


async def verify_tables():
    """Verify that the Shopify tables were created successfully."""
    
    database = await get_database()
    
    tables_to_check = [
        'shopify_stores',
        'shopify_products', 
        'shopify_orders',
        'shopify_webhook_events',
        'shopify_sync_jobs'
    ]
    
    try:
        await database.connect()
        
        for table in tables_to_check:
            try:
                # Try to query the table to verify it exists
                result = await database.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                logger.info(f"✅ Table '{table}' exists and is accessible (count: {result['count'] if result else 0})")
            except Exception as e:
                logger.error(f"❌ Table '{table}' verification failed: {e}")
                return False
        
        logger.info("✅ All Shopify tables verified successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Table verification failed: {e}")
        return False
    finally:
        try:
            await database.disconnect()
        except:
            pass


async def main():
    """Main migration runner."""
    
    # Setup logging
    setup_logging()
    global logger
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Shopify tables migration...")
    
    try:
        # Create tables
        success = await create_shopify_tables()
        
        if not success:
            logger.error("❌ Shopify tables migration failed!")
            return 1
        
        # Verify tables were created
        verification_success = await verify_tables()
        
        if verification_success:
            logger.info("✅ Shopify tables migration completed successfully!")
            return 0
        else:
            logger.error("❌ Table verification failed!")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Migration failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)