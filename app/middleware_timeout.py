"""
Request timeout middleware.

This middleware enforces per-request timeouts to prevent long-running requests
from consuming resources indefinitely.
"""

import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.logger import get_logger

logger = get_logger()

# Default timeout per endpoint (in seconds)
# Image/video generation can take longer, so we set higher timeouts
DEFAULT_TIMEOUT = 300  # 5 minutes
ENDPOINT_TIMEOUTS = {
    "/v1/images/generate": 120,  # 2 minutes for image generation
    "/v1/images/generate/thumbnail": 120,  # 2 minutes for thumbnails
    "/v1/diagrams/generate": 60,  # 1 minute for diagrams
    "/v1/diagrams/mermaid": 60,  # 1 minute for mermaid diagrams
    "/v1/videos/generate": 300,  # 5 minutes for video generation
    "/v1/videos/animate": 300,  # 5 minutes for animation
    "/v1/providers/images": 5,  # 5 seconds for provider list
    "/v1/providers/diagrams": 5,  # 5 seconds for provider list
    "/v1/providers/videos": 5,  # 5 seconds for provider list
    "/healthz": 5,  # 5 seconds for health check
}


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeouts."""
    
    def __init__(self, app, default_timeout: float = DEFAULT_TIMEOUT):
        super().__init__(app)
        self.default_timeout = default_timeout
        self.logger = get_logger()
    
    async def dispatch(self, request: Request, call_next):
        """Enforce timeout for request processing."""
        # Get timeout for this endpoint
        path = request.url.path
        timeout = ENDPOINT_TIMEOUTS.get(path, self.default_timeout)
        
        # Skip timeout for metrics endpoint
        if path == "/metrics":
            return await call_next(request)
        
        try:
            # Run request with timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            self.logger.warn(
                "request timeout",
                path=path,
                timeout=timeout,
                method=request.method
            )
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request timeout",
                    "message": f"Request exceeded timeout of {timeout}s",
                    "path": path
                }
            )

