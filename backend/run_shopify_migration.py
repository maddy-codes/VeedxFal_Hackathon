#!/usr/bin/env python3
"""
Run Shopify tables migration.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.logging import setup_logging
from migrations.create_shopify_tables import run_migration


async def main():
    """Main migration runner."""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Shopify tables migration...")
    
    try:
        success = await run_migration()
        
        if success:
            logger.info("✅ Shopify tables migration completed successfully!")
            return 0
        else:
            logger.error("❌ Shopify tables migration failed!")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Migration failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)