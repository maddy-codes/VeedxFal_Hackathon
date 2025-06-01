"""
Add columns for async video processing to the database.
"""

import asyncio
import logging
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

async def add_video_async_columns():
    """Add columns needed for async video processing."""
    
    db_manager = DatabaseManager()
    
    try:
        # Add columns to video_jobs table if they don't exist
        alter_queries = [
            """
            ALTER TABLE video_jobs 
            ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS current_step TEXT DEFAULT 'pending',
            ADD COLUMN IF NOT EXISTS started_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS video_id TEXT
            """,
            
            # Create video_scripts table if it doesn't exist
            """
            CREATE TABLE IF NOT EXISTS video_scripts (
                script_id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                shop_id INTEGER NOT NULL,
                script_content TEXT NOT NULL,
                word_count INTEGER DEFAULT 0,
                estimated_duration FLOAT DEFAULT 0,
                generated_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (job_id) REFERENCES video_jobs(job_id)
            )
            """,
            
            # Add indexes for better performance
            """
            CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_video_jobs_shop_id ON video_jobs(shop_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_video_jobs_user_id ON video_jobs(user_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_video_scripts_job_id ON video_scripts(job_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_generated_videos_job_id ON generated_videos(job_id);
            """
        ]
        
        for query in alter_queries:
            try:
                await db_manager.execute_query(query)
                logger.info(f"Successfully executed: {query[:50]}...")
            except Exception as e:
                logger.warning(f"Query failed (might already exist): {e}")
        
        logger.info("Database schema updated for async video processing")
        
    except Exception as e:
        logger.error(f"Failed to update database schema: {e}")
        raise
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(add_video_async_columns())