"""
Rate limiting middleware using a simple in-memory sliding window algorithm.
For production with multiple workers, consider using Redis-based rate limiting.
"""
import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    Note: This implementation uses in-memory storage and is suitable for
    single-worker deployments. For multi-worker/distributed deployments,
    consider using Redis-based rate limiting via the Redis client in app.state.
    """
    
    def __init__(self, app, requests_per_minute: int = 60, burst_size: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_size = 60  # 1 minute window
        self._requests: dict[str, list[float]] = defaultdict(list)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers or connection."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, client_ip: str, current_time: float) -> None:
        """Remove requests older than the window size."""
        cutoff = current_time - self.window_size
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > cutoff
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and metrics
        if request.url.path in ("/health", "/metrics"):
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(client_ip, current_time)
        
        # Check if rate limit exceeded
        request_count = len(self._requests[client_ip])
        if request_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self._requests[client_ip].append(current_time)
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - request_count - 1
        )
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))
        
        return response
