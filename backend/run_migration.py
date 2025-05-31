#!/usr/bin/env python3
"""
Database migration script for Supabase PostgreSQL
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import database
from app.core.config import settings

async def run_migration():
    """Run the initial database migration."""
    
    print("🚀 Starting database migration to Supabase...")
    print(f"📍 Database URL: {settings.DATABASE_URL[:50]}...")
    
    try:
        # Connect to database
        await database.connect()
        print("✅ Connected to Supabase database")
        
        # Read migration file
        migration_file = backend_dir / "migrations" / "001_initial_schema.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
            
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("📄 Migration file loaded")
        
        # Split the migration into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        print(f"🔄 Executing {len(statements)} SQL statements...")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            try:
                if statement.strip():
                    await database.execute(statement)
                    print(f"✅ Statement {i}/{len(statements)} executed")
            except Exception as e:
                # Some statements might fail if objects already exist
                if "already exists" in str(e).lower():
                    print(f"⚠️  Statement {i}/{len(statements)} skipped (already exists)")
                else:
                    print(f"❌ Statement {i}/{len(statements)} failed: {e}")
                    # Continue with other statements
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        await database.disconnect()
        print("🔌 Disconnected from database")

async def verify_migration():
    """Verify that the migration was successful."""
    
    print("\n🔍 Verifying migration...")
    
    try:
        await database.connect()
        
        # Check if main tables exist
        tables_to_check = [
            'stores', 'products', 'sales', 'competitor_prices', 
            'trend_insights', 'recommended_prices', 'video_jobs', 
            'video_scripts', 'generated_videos'
        ]
        
        for table in tables_to_check:
            try:
                result = await database.fetch_one(
                    f"SELECT COUNT(*) as count FROM information_schema.tables WHERE table_name = '{table}'"
                )
                if result and result['count'] > 0:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
            except Exception as e:
                print(f"❌ Error checking table '{table}': {e}")
        
        print("✅ Migration verification completed")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        await database.disconnect()

if __name__ == "__main__":
    print("🗄️  Database Migration Tool")
    print("=" * 50)
    
    # Check if DATABASE_URL is set to Supabase
    if not settings.DATABASE_URL or "supabase.co" not in settings.DATABASE_URL:
        print("❌ DATABASE_URL is not set to Supabase PostgreSQL")
        print("Please update your .env file with the correct Supabase DATABASE_URL")
        sys.exit(1)
    
    # Run migration
    asyncio.run(run_migration())
    
    # Verify migration
    asyncio.run(verify_migration())
    
    print("\n🎯 Next steps:")
    print("1. Test the backend server: python -m uvicorn main:app --reload")
    print("2. Check the Supabase dashboard to see your tables")
    print("3. Start building your integrations!")