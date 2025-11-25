"""  
Security Middleware
Adds security headers and protections
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
from backend.db.base import get_redis
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        # Allow CDN for Swagger UI docs
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://cdn.jsdelivr.net; "
            "connect-src 'self' https://api.openai.com https://api.anthropic.com; "
            "frame-ancestors 'none'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting with Redis support for production
    Falls back to in-memory if Redis unavailable
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)  # Fallback in-memory storage
        self.redis_client = get_redis()
        # Check if Redis is actually working
        self.use_redis = False
        if self.redis_client:
            try:
                self.redis_client.ping()
                self.use_redis = True
            except Exception:
                self.use_redis = False
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP (handle None for TestClient)
        client_ip = "127.0.0.1"  # Default
        if request.client and hasattr(request.client, 'host'):
            client_ip = request.client.host
        
        if self.use_redis:
            # Redis-based rate limiting (production)
            is_limited = await self._check_redis_rate_limit(client_ip)
        else:
            # In-memory rate limiting (development)
            is_limited = self._check_memory_rate_limit(client_ip)
        
        if is_limited:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        if self.use_redis:
            try:
                key = f"rate_limit:{client_ip}"
                count = int(self.redis_client.get(key) or 0)
                remaining = max(0, self.requests_per_minute - count)
            except Exception:
                remaining = self.requests_per_minute
        else:
            remaining = self.requests_per_minute - len(self.requests[client_ip])
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
    
    async def _check_redis_rate_limit(self, client_ip: str) -> bool:
        """Check rate limit using Redis"""
        try:
            key = f"rate_limit:{client_ip}"
            count = self.redis_client.incr(key)
            
            if count == 1:
                # First request, set expiry
                self.redis_client.expire(key, 60)
            
            return count > self.requests_per_minute
        except Exception:
            # Redis error, allow request
            return False
    
    def _check_memory_rate_limit(self, client_ip: str) -> bool:
        """Check rate limit using in-memory storage"""
        now = datetime.now()
        
        # Clean old requests (older than 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return True
        
        # Add current request
        self.requests[client_ip].append(now)
        return False


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate and sanitize requests
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check content length to prevent large payload attacks
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request payload too large"}
                )
        
        # Check for suspicious patterns in URL
        path = request.url.path
        suspicious_patterns = ["../", "..\\\\", "<script", "javascript:", "onerror="]
        if any(pattern in path.lower() for pattern in suspicious_patterns):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request"}
            )
        
        response = await call_next(request)
        return response
