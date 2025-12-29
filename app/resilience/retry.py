"""
Retry logic with exponential backoff.
"""

import asyncio
import time
from typing import Callable, Any, Awaitable
from app.logger import get_logger
from app.resilience.policy import get_resilience_policy_loader

logger = get_logger()


async def retry_with_backoff(
    func: Callable[..., Awaitable[Any]],
    *args,
    retry_policy_name: str = "default",
    **kwargs
) -> Any:
    """
    Retries an asynchronous function with exponential backoff based on policy.
    """
    policy = get_resilience_policy_loader().get_policy().retry
    
    if not policy.enabled:
        return await func(*args, **kwargs)

    max_attempts = policy.max_attempts
    initial_delay = policy.initial_delay_seconds
    backoff_factor = policy.backoff_factor
    max_delay = policy.max_delay_seconds
    
    attempt = 0
    delay = initial_delay

    while attempt < max_attempts:
        attempt += 1
        try:
            logger.debug("Attempting function execution", attempt=attempt, max_attempts=max_attempts)
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            error_str = str(e).lower()
            is_retryable = any(
                code in error_str or 
                str(code) in error_str or
                any(exc_type in error_str for exc_type in policy.retry_on_exceptions)
                for code in policy.retry_on_status_codes
            )
            
            if attempt < max_attempts and is_retryable:
                logger.warn("Function failed, retrying...", attempt=attempt, max_attempts=max_attempts, delay=delay, error=str(e))
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error("Function failed after multiple attempts or with non-retryable error", attempt=attempt, max_attempts=max_attempts, error=str(e))
                raise
    
    raise RuntimeError("Max retry attempts exceeded.")

