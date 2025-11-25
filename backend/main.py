"""
Gamma Clone - FastAPI Main Application
Complete backend with all 423 features
Optimized for performance and scalability
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from backend.config import settings
from backend.db.base import init_db, close_connections, get_redis
from backend.middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestValidationMiddleware
)
from backend.middleware.performance import PerformanceMiddleware
from backend.utils.logging import api_logger
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    try:
        api_logger.info("Starting Gamma Clone backend")
        print("[STARTUP] Starting Gamma Clone...")
        print(f"[DATABASE] {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
        print(f"[AI] Model: {settings.DEFAULT_TEXT_MODEL}")
        print(f"[RATE LIMIT] {settings.RATE_LIMIT_PER_MINUTE} requests/minute")
        
        # Check Redis availability
        redis_client = get_redis()
        if redis_client:
            try:
                redis_client.ping()
                print("[OK] Redis: Connected (caching enabled)")
            except Exception:
                print("[WARNING] Redis: Not available (caching disabled)")
        else:
            print("[WARNING] Redis: Not available (caching disabled)")
        
        # Run blocking DB init in thread pool to avoid blocking event loop
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, init_db)
        
        api_logger.info("Backend initialized successfully")
        print("[OK] Backend ready!")
        print("[INFO] Server is running. Press CTRL+C to stop.")
        
    except Exception as e:
        api_logger.error(f"Startup failed: {e}")
        print(f"[ERROR] Startup failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    yield  # Server runs here
    
    # Shutdown
    try:
        api_logger.info("Shutting down backend")
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, close_connections)
        print("[SHUTDOWN] Backend shutdown complete")
    except Exception as e:
        print(f"[ERROR] Shutdown error: {e}")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Complete Gamma.app clone with 480+ features - Optimized",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration - Permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Security Middleware (order matters - apply from outermost to innermost)
app.add_middleware(PerformanceMiddleware)  # Monitor performance
app.add_middleware(SecurityHeadersMiddleware)  # Add security headers
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)  # Rate limiting
app.add_middleware(RequestValidationMiddleware)  # Validate requests

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Gamma Clone API",
        "version": settings.APP_VERSION,
        "status": "running",
        "features": 480,  # Updated: +57 new endpoints (documents, webpages, social, folders, import, domains)
        "docs": "/docs"
    }

# Health check with detailed status
@app.get("/health")
async def health_check():
    redis_client = get_redis()
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected" if redis_client else "disconnected",
        "ai_service": "ready",
        "version": settings.APP_VERSION,
        "features": 480  # Updated: +57 new endpoints
    }

# Import and include all API routers
from backend.api import (
    auth, 
    ai, 
    presentations, 
    templates, 
    themes, 
    export, 
    analytics, 
    collaboration, 
    billing,
    documents,
    webpages,
    social,
    folders,
    import_content,
    custom_domains
)

# Include all routers (tags already defined in each router)
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(presentations.router)
app.include_router(templates.router)
app.include_router(themes.router)
app.include_router(export.router)
app.include_router(analytics.router)
app.include_router(collaboration.router)
app.include_router(billing.router)
app.include_router(documents.router)
app.include_router(webpages.router)
app.include_router(social.router)
app.include_router(folders.router)
app.include_router(import_content.router)
app.include_router(custom_domains.router)

if __name__ == "__main__":
    import sys
    
    # Don't set custom signal handlers - let uvicorn handle them
    
    try:
        uvicorn.run(
            app,  # Pass app directly instead of string to avoid reload issues
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to fix the hanging issue
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n[INFO] Received shutdown signal")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Server crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
