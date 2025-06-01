"""
Create video generation tables for async processing.
"""

import asyncio
import logging
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

async def create_video_tables():
    """Create video generation tables."""
    
    db_manager = DatabaseManager()
    
    try:
        # Create video_jobs table
        create_video_jobs_query = """
        CREATE TABLE IF NOT EXISTS video_jobs (
            job_id TEXT PRIMARY KEY,
            shop_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            request_data JSONB,
            progress INTEGER DEFAULT 0,
            current_step TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            video_id TEXT
        )
        """
        
        # Create video_scripts table
        create_video_scripts_query = """
        CREATE TABLE IF NOT EXISTS video_scripts (
            script_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            shop_id INTEGER NOT NULL,
            script_content TEXT NOT NULL,
            word_count INTEGER DEFAULT 0,
            estimated_duration FLOAT DEFAULT 0,
            generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (job_id) REFERENCES video_jobs(job_id)
        )
        """
        
        # Create generated_videos table if it doesn't exist
        create_generated_videos_query = """
        CREATE TABLE IF NOT EXISTS generated_videos (
            video_id TEXT PRIMARY KEY,
            shop_id INTEGER NOT NULL,
            job_id TEXT,
            video_url TEXT,
            script_content TEXT,
            audio_url TEXT,
            duration_seconds FLOAT,
            file_size_bytes BIGINT,
            resolution TEXT,
            format TEXT DEFAULT 'mp4',
            generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE,
            view_count INTEGER DEFAULT 0,
            metadata JSONB,
            FOREIGN KEY (job_id) REFERENCES video_jobs(job_id)
        )
        """
        
        # Execute table creation queries
        queries = [
            ("video_jobs", create_video_jobs_query),
            ("video_scripts", create_video_scripts_query),
            ("generated_videos", create_generated_videos_query)
        ]
        
        for table_name, query in queries:
            try:
                await db_manager.execute_query(query)
                logger.info(f"✅ Created/verified table: {table_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create table {table_name}: {e}")
                raise
        
        # Create indexes for better performance
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status)",
            "CREATE INDEX IF NOT EXISTS idx_video_jobs_shop_id ON video_jobs(shop_id)",
            "CREATE INDEX IF NOT EXISTS idx_video_jobs_user_id ON video_jobs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_video_scripts_job_id ON video_scripts(job_id)",
            "CREATE INDEX IF NOT EXISTS idx_video_scripts_shop_id ON video_scripts(shop_id)",
            "CREATE INDEX IF NOT EXISTS idx_generated_videos_job_id ON generated_videos(job_id)",
            "CREATE INDEX IF NOT EXISTS idx_generated_videos_shop_id ON generated_videos(shop_id)",
            "CREATE INDEX IF NOT EXISTS idx_generated_videos_generated_at ON generated_videos(generated_at)"
        ]
        
        for index_query in index_queries:
            try:
                await db_manager.execute_query(index_query)
                logger.info(f"✅ Created index: {index_query.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                logger.warning(f"⚠️ Index creation warning: {e}")
        
        logger.info("🎉 Video tables and indexes created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to create video tables: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_video_tables())