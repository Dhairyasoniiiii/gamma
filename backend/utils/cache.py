"""
Response caching utilities
"""

from functools import wraps
from typing import Optional, Callable, Any
import hashlib
import json
from backend.db.base import get_redis


def cache_response(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator to cache API responses in Redis
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_prefix: Prefix for cache keys
    
    Usage:
        @cache_response(ttl=600, key_prefix="templates")
        async def get_templates():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            redis_client = get_redis()
            
            # If Redis not available, skip caching
            if not redis_client:
                return await func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)
            
            # Try to get from cache
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass  # Cache miss or error
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            try:
                redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
            except Exception:
                pass  # Cache write failed, not critical
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str, pattern: Optional[str] = None):
    """
    Invalidate cache entries by prefix or pattern
    
    Args:
        key_prefix: Cache key prefix
        pattern: Optional pattern for matching keys (e.g., "user:123:*")
    """
    redis_client = get_redis()
    if not redis_client:
        return
    
    try:
        if pattern:
            search_pattern = f"{key_prefix}:{pattern}"
        else:
            search_pattern = f"{key_prefix}:*"
        
        # Find and delete matching keys
        keys = redis_client.keys(search_pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass  # Cache invalidation failed, not critical


def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate unique cache key from function arguments"""
    # Filter out non-cacheable arguments (like database sessions)
    cacheable_args = [
        arg for arg in args
        if not hasattr(arg, '__module__') or 'sqlalchemy' not in arg.__module__
    ]
    
    # Create key from arguments
    key_data = {
        "func": func_name,
        "args": str(cacheable_args),
        "kwargs": {k: v for k, v in kwargs.items() if k not in ['db', 'current_user']}
    }
    
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"{prefix}:{func_name}:{key_hash}"
