"""
Provider selection and routing for Creative Service.
"""

from typing import Optional, Tuple, List, Callable, Awaitable, Any
from app.routing.policy import get_routing_policy_loader
from app.logger import get_logger

logger = get_logger()


def select_provider(
    requested_provider: Optional[str] = None,
    cost_mode: str = "balanced",  # cost_optimized, balanced, quality_optimized
) -> Tuple[str, List[str]]:
    """
    Select provider based on routing policies.
    
    Returns: (selected_provider, fallback_chain)
    """
    policy_loader = get_routing_policy_loader()
    policy = policy_loader.get_policy()
    
    if not policy.providers:
        return policy.default_provider, []
    
    # If explicit provider requested and enabled, use it
    if requested_provider:
        for p_config in policy.providers:
            if p_config.name.lower() == requested_provider.lower() and p_config.enabled:
                fallback_chain = p_config.fallback_to
                logger.info("Explicit provider selected", provider=p_config.name)
                return p_config.name, fallback_chain
    
    # Auto-select based on cost mode
    available_providers = [p for p in policy.providers if p.enabled]
    if not available_providers:
        return policy.default_provider, []
    
    if cost_mode == "cost_optimized":
        # Prefer low cost tier
        available_providers.sort(key=lambda p: (p.cost_tier == "low", p.priority))
    elif cost_mode == "quality_optimized":
        # Prefer high quality tier
        available_providers.sort(key=lambda p: (p.quality_tier == "high", p.priority))
    else:  # balanced
        # Sort by priority
        available_providers.sort(key=lambda p: p.priority)
    
    selected = available_providers[0]
    logger.info("Auto-selected provider", provider=selected.name, cost_mode=cost_mode)
    return selected.name, selected.fallback_to


async def execute_with_fallback(
    provider: str,
    fallback_chain: List[str],
    execution_function: Callable[[str], Awaitable[Any]],
    endpoint: str = "default"
) -> Any:
    """
    Execute function with provider fallback chain.
    """
    attempts = [provider] + fallback_chain
    
    for i, attempt_provider in enumerate(attempts):
        try:
            logger.info("Attempting execution", attempt=i+1, provider=attempt_provider, endpoint=endpoint)
            result = await execution_function(attempt_provider)
            logger.info("Execution successful", provider=attempt_provider)
            return result
        except Exception as e:
            logger.warn("Execution failed, attempting fallback", provider=attempt_provider, error=str(e))
            if i == len(attempts) - 1:
                raise
    
    raise RuntimeError("All execution attempts failed.")

