"""Redis-based rate limiting middleware"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from redis import Redis
from redis.exceptions import RedisError
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware with multiple time windows.
    Uses sliding window algorithm for accurate rate limiting.
    """
    
    def __init__(
        self,
        app,
        redis_url: str,
        enabled: bool = True,
        requests_per_minute: int = 100,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
    ):
        super().__init__(app)
        self.enabled = enabled
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        
        # Initialize Redis connection
        try:
            self.redis_client = Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis rate limiter initialized successfully")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis for rate limiting: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client.
        Uses IP address, but can be extended to use API keys or user IDs.
        """
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # For authenticated endpoints, you could also use user ID
        # user_id = request.state.user_id if hasattr(request.state, 'user_id') else None
        # return f"user:{user_id}" if user_id else f"ip:{client_ip}"
        
        return f"ip:{client_ip}"
    
    def _check_rate_limit(
        self,
        client_id: str,
        window_seconds: int,
        max_requests: int,
    ) -> tuple[bool, int, int]:
        """
        Check if client has exceeded rate limit for given window.
        
        Returns:
            tuple: (is_allowed, current_count, remaining)
        """
        if not self.redis_client or not self.enabled:
            return True, 0, max_requests
        
        try:
            current_time = time.time()
            window_start = current_time - window_seconds
            
            # Create unique key for this client and window
            key = f"rate_limit:{client_id}:{window_seconds}"
            
            # Use Redis sorted set with timestamps as scores
            pipe = self.redis_client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry on the key
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            current_count = results[1]
            
            # Check if limit exceeded
            is_allowed = current_count < max_requests
            remaining = max(0, max_requests - current_count - 1)
            
            return is_allowed, current_count, remaining
            
        except RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Fail open - allow request if Redis is down
            return True, 0, max_requests
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limits for different windows
        limits = [
            (60, self.requests_per_minute, "minute"),
            (3600, self.requests_per_hour, "hour"),
            (86400, self.requests_per_day, "day"),
        ]
        
        for window_seconds, max_requests, window_name in limits:
            is_allowed, current_count, remaining = self._check_rate_limit(
                client_id, window_seconds, max_requests
            )
            
            if not is_allowed:
                # Calculate retry after time
                retry_after = window_seconds
                
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {max_requests} requests per {window_name}. "
                           f"Please try again in {retry_after} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                        "Retry-After": str(retry_after),
                    }
                )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        # Get remaining for the strictest limit (per minute)
        _, _, remaining = self._check_rate_limit(client_id, 60, self.requests_per_minute)
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        
        return response


# Legacy class for backward compatibility
class RateLimitMiddleware(RedisRateLimitMiddleware):
    """Backward compatible rate limit middleware"""
    pass
