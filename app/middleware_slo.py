"""
Middleware for SLO/SLI tracking.

This middleware automatically tracks request metrics for SLO/SLI calculations.
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.slo_sli import record_request_metric
from app.logger import get_logger

logger = get_logger()


class SLOTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track SLO/SLI metrics for all requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Track request metrics for SLO/SLI."""
        start_time = time.time()
        
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Extract endpoint (normalize path)
        endpoint = request.url.path
        
        # Record metrics
        try:
            record_request_metric(
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )
        except Exception as e:
            logger.warn("Failed to record SLO metrics", error=str(e))
        
        return response

