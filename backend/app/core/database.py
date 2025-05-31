"""
Database configuration and connection management.
"""

import logging
from typing import Any, Dict, Optional

import asyncpg
from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=0,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

# Async database connection
# SQLite doesn't support connection pooling parameters
if settings.DATABASE_URL.startswith('sqlite'):
    database = Database(settings.DATABASE_URL)
else:
    # PostgreSQL connection with pooling
    database = Database(
        settings.DATABASE_URL,
        min_size=5,
        max_size=20,
        ssl="prefer" if settings.is_production else None,
    )


async def get_database() -> Database:
    """Get database connection."""
    return database


class DatabaseManager:
    """Database connection and query manager."""
    
    def __init__(self):
        self.database = database
        self._connection_pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Connect to database."""
        try:
            await self.database.connect()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
        try:
            await self.database.disconnect()
            logger.info("Database disconnected successfully")
        except Exception as e:
            logger.error(f"Failed to disconnect from database: {e}")
            raise
    
    async def execute_query(
        self,
        query: str,
        values: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a database query."""
        try:
            if values:
                return await self.database.execute(query, values)
            else:
                return await self.database.execute(query)
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    async def fetch_one(
        self,
        query: str,
        values: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch one record from database."""
        try:
            if values:
                return await self.database.fetch_one(query, values)
            else:
                return await self.database.fetch_one(query)
        except Exception as e:
            logger.error(f"Database fetch_one failed: {e}")
            raise
    
    async def fetch_all(
        self,
        query: str,
        values: Optional[Dict[str, Any]] = None
    ) -> list[Dict[str, Any]]:
        """Fetch all records from database."""
        try:
            if values:
                return await self.database.fetch_all(query, values)
            else:
                return await self.database.fetch_all(query)
        except Exception as e:
            logger.error(f"Database fetch_all failed: {e}")
            raise
    
    async def execute_transaction(self, queries: list[tuple[str, Dict[str, Any]]]) -> None:
        """Execute multiple queries in a transaction."""
        async with self.database.transaction():
            for query, values in queries:
                await self.database.execute(query, values)


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_manager() -> DatabaseManager:
    """Get database manager instance."""
    return db_manager


# Database health check
async def check_database_health() -> Dict[str, Any]:
    """Check database connection health."""
    try:
        result = await database.fetch_one("SELECT 1 as health_check")
        return {
            "status": "healthy",
            "connected": True,
            "result": dict(result) if result else None
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }


# Database initialization queries
INIT_QUERIES = [
    # Enable Row Level Security
    "ALTER TABLE IF EXISTS stores ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE IF EXISTS products ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE IF EXISTS sales ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE IF EXISTS competitor_prices ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE IF EXISTS trend_insights ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE IF EXISTS recommended_prices ENABLE ROW LEVEL SECURITY;",
]


async def initialize_database() -> None:
    """Initialize database with required settings."""
    try:
        for query in INIT_QUERIES:
            try:
                await database.execute(query)
            except Exception as e:
                # Log but don't fail if table doesn't exist yet
                logger.warning(f"Init query failed (may be expected): {query} - {e}")
        
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise