"""
Length limits validation for Creative Service.
"""

from typing import Tuple, Any, Dict, Optional
from app.quality.policy import get_quality_policy_loader
from app.logger import get_logger

logger = get_logger()


def check_length_limits(content: Any, endpoint: str = "default") -> Tuple[bool, Optional[str]]:
    """
    Check if content meets length requirements.
    
    Returns: (is_valid, error_message)
    """
    policy = get_quality_policy_loader().get_policy()
    
    if not policy.length_limits.enabled:
        return True, None
    
    # Get limits for endpoint or use defaults
    endpoint_config = policy.length_limits.per_endpoint.get(endpoint, {})
    min_length = endpoint_config.get("min_length", policy.length_limits.min_length)
    max_length = endpoint_config.get("max_length", policy.length_limits.max_length)
    
    # Calculate content length
    if isinstance(content, str):
        content_length = len(content)
    elif isinstance(content, (list, dict)):
        content_length = len(str(content))
    else:
        content_length = len(str(content))
    
    if content_length < min_length:
        error = f"Content length {content_length} is below minimum {min_length}"
        logger.warn("Length limit violation", endpoint=endpoint, length=content_length, min=min_length)
        return False, error
    
    if content_length > max_length:
        error = f"Content length {content_length} exceeds maximum {max_length}"
        logger.warn("Length limit violation", endpoint=endpoint, length=content_length, max=max_length)
        return False, error
    
    return True, None

