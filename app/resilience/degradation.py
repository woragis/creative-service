"""
Graceful degradation logic.
"""

from typing import Optional, Tuple
from app.logger import get_logger
from app.resilience.policy import get_resilience_policy_loader

logger = get_logger()


def get_degradation_strategy() -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Retrieves the degradation strategy from the resilience policy.
    
    Returns: (enabled, degrade_to_provider, degrade_to_model, message)
    """
    policy = get_resilience_policy_loader().get_policy().degradation
    
    if not policy.enabled:
        return False, None, None, None
    
    logger.warn("Degradation policy is active", degrade_to_provider=policy.degrade_to_provider, degrade_to_model=policy.degrade_to_model)
    return True, policy.degrade_to_provider, policy.degrade_to_model, policy.message

