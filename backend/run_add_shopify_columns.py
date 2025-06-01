#!/usr/bin/env python3
"""
Add Shopify-specific columns to products table.
This script adds the missing columns needed for Shopify product sync.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client

async def add_shopify_columns():
    """Add Shopify-specific columns to products table."""
    print("Adding Shopify columns to products table...")
    
    try:
        supabase_client = get_supabase_client()
        
        # List of columns to add
        columns_to_add = [
            "shopify_variant_id BIGINT",
            "handle TEXT",
            "product_type TEXT", 
            "vendor TEXT",
            "tags TEXT",
            "published_at TIMESTAMP WITH TIME ZONE",
            "shopify_created_at TIMESTAMP WITH TIME ZONE",
            "shopify_updated_at TIMESTAMP WITH TIME ZONE"
        ]
        
        # Add each column
        for column_def in columns_to_add:
            column_name = column_def.split()[0]
            try:
                # Try to add the column
                result = supabase_client.rpc('exec_sql', {
                    'sql': f'ALTER TABLE products ADD COLUMN {column_def}'
                }).execute()
                print(f"✅ Added column: {column_name}")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print(f"⚠️  Column {column_name} already exists, skipping")
                else:
                    print(f"❌ Failed to add column {column_name}: {e}")
        
        # Add indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_products_shopify_variant_id ON products(shopify_variant_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_handle ON products(handle)",
            "CREATE INDEX IF NOT EXISTS idx_products_vendor ON products(vendor)"
        ]
        
        for index_sql in indexes:
            try:
                result = supabase_client.rpc('exec_sql', {'sql': index_sql}).execute()
                print(f"✅ Created index: {index_sql.split()[5]}")
            except Exception as e:
                print(f"⚠️  Index creation failed (may already exist): {e}")
        
        print("\n✅ Shopify columns migration completed!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = asyncio.run(add_shopify_columns())
    sys.exit(0 if success else 1)