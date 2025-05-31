"""
FastAPI application entry point for Retail AI Advisor backend.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.middleware.auth import AuthMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.v1 import analytics, auth, products, sync, upload, video
from app.core.config import settings
from app.core.database import database
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logging.warning("Starting Retail AI Advisor API...")
    try:
        await database.connect()
        logging.warning("Database connected successfully")
    except Exception as e:
        logging.error(f"Database connection failed, continuing without it: {e}")
    
    yield
    
    # Shutdown
    logging.warning("Shutting down Retail AI Advisor API...")
    try:
        await database.disconnect()
        logging.warning("Database disconnected")
    except Exception as e:
        logging.error(f"Database disconnect failed: {e}")


# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Retail AI Advisor API",
    description="AI-powered retail analytics and pricing optimization platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Add security middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["retail-ai-advisor.azurewebsites.net", "*.azurewebsites.net"]
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["Data Synchronization"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(video.router, prefix="/api/v1/video", tags=["Video Generation"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["File Upload"])


@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/v1/health/supabase", include_in_schema=False)
async def supabase_health_check():
    """Supabase connection health check endpoint."""
    from app.core.database import check_database_health
    
    try:
        health_status = await check_database_health()
        return {
            "service": "supabase",
            "timestamp": datetime.utcnow().isoformat(),
            "database": health_status,
            "supabase_url": settings.SUPABASE_URL,
            "connection_status": "connected" if health_status.get("connected") else "disconnected"
        }
    except Exception as e:
        return {
            "service": "supabase",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            },
            "supabase_url": settings.SUPABASE_URL,
            "connection_status": "disconnected"
        }


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": "Retail AI Advisor API",
        "version": "1.0.0",
        "docs_url": "/docs" if settings.ENVIRONMENT == "development" else None,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )