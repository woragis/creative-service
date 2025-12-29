"""
Timeout wrapper for async functions.
"""

import asyncio
from typing import Callable, Any, Awaitable
from app.logger import get_logger
from app.resilience.policy import get_resilience_policy_loader

logger = get_logger()


async def apply_timeout(
    func: Callable[..., Awaitable[Any]],
    *args,
    provider_name: str = "default",
    endpoint: str = "default",
    **kwargs
) -> Any:
    """
    Applies a timeout to an asynchronous function based on resilience policy.
    """
    policy = get_resilience_policy_loader().get_policy().timeout
    
    if not policy.enabled:
        return await func(*args, **kwargs)

    timeout_seconds = policy.default_timeout_seconds
    
    # Check for per-endpoint timeout
    if endpoint in policy.per_endpoint_timeouts:
        timeout_seconds = policy.per_endpoint_timeouts[endpoint]
    # Check for per-provider timeout
    elif provider_name in policy.per_provider_timeouts:
        timeout_seconds = policy.per_provider_timeouts[provider_name]

    try:
        logger.debug("Applying timeout to function", timeout=timeout_seconds, provider=provider_name, endpoint=endpoint)
        return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error("Function timed out", timeout=timeout_seconds, provider=provider_name, endpoint=endpoint)
        raise TimeoutException(f"Operation timed out after {timeout_seconds} seconds for provider '{provider_name}', endpoint '{endpoint}'")


class TimeoutException(asyncio.TimeoutError):
    """Custom exception for operation timeouts."""
    pass

