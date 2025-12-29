"""
Output format validation for Creative Service.
"""

from typing import Tuple, Any, Dict, List, Optional
from app.quality.policy import get_quality_policy_loader
from app.logger import get_logger

logger = get_logger()


def validate_output_format(response: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate response format against policy requirements.
    
    Returns: (is_valid, error_message)
    """
    policy = get_quality_policy_loader().get_policy()
    
    if not policy.format_validation.enabled:
        return True, None
    
    # Check required fields
    if isinstance(response, dict):
        for field in policy.format_validation.required_fields:
            if field not in response:
                error = f"Missing required field: {field}"
                logger.warn("Format validation failed", missing_field=field)
                return False, error
    
    # For creative service, we mainly validate structure
    # Format validation is more relevant for text-based responses
    if policy.format_validation.strict_validation:
        if not isinstance(response, dict):
            error = "Response must be a dictionary"
            logger.warn("Format validation failed", response_type=type(response).__name__)
            return False, error
    
    return True, None

