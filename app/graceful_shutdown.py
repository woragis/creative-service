"""
Graceful shutdown handling for Creative Service.

This module implements graceful shutdown to ensure:
- In-flight requests complete
- Connections close properly
- Resources are cleaned up
"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.logger import get_logger

logger = get_logger()

# Global shutdown event
shutdown_event = asyncio.Event()


def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info("shutdown signal received", signal=signum)
        shutdown_event.set()
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # On Windows, also handle SIGBREAK
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, signal_handler)


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator:
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown logic.
    """
    # Startup
    logger.info("starting up creative service")
    setup_signal_handlers()
    
    # Create background task to monitor shutdown
    shutdown_task = asyncio.create_task(monitor_shutdown())
    
    yield
    
    # Shutdown
    logger.info("shutting down creative service")
    shutdown_event.set()
    
    # Shutdown tracing
    try:
        from app.tracing import shutdown as shutdown_tracing
        shutdown_tracing()
    except Exception as e:
        logger.warn("Failed to shutdown tracing", error=str(e))
    
    # Wait for shutdown task
    try:
        await asyncio.wait_for(shutdown_task, timeout=5.0)
    except asyncio.TimeoutError:
        logger.warn("shutdown task timeout")
    
    # Give time for in-flight requests to complete
    logger.info("waiting for in-flight requests to complete")
    await asyncio.sleep(2)
    
    logger.info("shutdown complete")


async def monitor_shutdown():
    """Monitor shutdown event and handle graceful shutdown."""
    await shutdown_event.wait()
    logger.info("shutdown event triggered")


def is_shutting_down() -> bool:
    """Check if service is shutting down."""
    return shutdown_event.is_set()

