"""
Performance monitoring middleware
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from backend.utils.logging import api_logger


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Monitor API endpoint performance
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(duration_ms)
        
        # Log slow requests (>1 second)
        if duration > 1.0:
            api_logger.warning(
                "Slow request detected",
                path=request.url.path,
                method=request.method,
                duration_ms=duration_ms,
                status_code=response.status_code
            )
        
        # Log all requests in debug mode
        api_logger.debug(
            "Request completed",
            path=request.url.path,
            method=request.method,
            duration_ms=duration_ms,
            status_code=response.status_code
        )
        
        return response
