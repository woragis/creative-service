"""
Feature flags utilities for Creative Service.
"""

from typing import Optional, Any
from app.features.policy import get_feature_flags_loader
from app.logger import get_logger

logger = get_logger()


def is_feature_enabled(feature_name: str) -> bool:
    """
    Check if a feature is enabled.
    
    Supports:
    - streaming_enabled
    - caching_enabled
    - providers.{provider_name} (e.g., providers.openai)
    - endpoints.{endpoint_name} (e.g., endpoints.image_generation)
    - custom_flags.{flag_name}
    """
    policy = get_feature_flags_loader().get_policy()
    
    # Direct flags
    if feature_name == "streaming_enabled":
        return policy.streaming_enabled
    if feature_name == "caching_enabled":
        return policy.caching_enabled
    
    # Provider flags
    if feature_name.startswith("providers."):
        provider_name = feature_name.split(".", 1)[1]
        return getattr(policy.providers, provider_name, False)
    
    # Endpoint flags
    if feature_name.startswith("endpoints."):
        endpoint_name = feature_name.split(".", 1)[1]
        return getattr(policy.endpoints, endpoint_name, False)
    
    # Custom flags
    if feature_name.startswith("custom_flags."):
        flag_name = feature_name.split(".", 1)[1]
        return policy.custom_flags.get(flag_name, False)
    
    # Direct custom flag access
    if feature_name in policy.custom_flags:
        return policy.custom_flags[feature_name]
    
    logger.warn("Unknown feature flag", feature=feature_name)
    return False


def get_feature_flag(feature_name: str, default: Any = False) -> Any:
    """
    Get feature flag value with default.
    """
    try:
        return is_feature_enabled(feature_name)
    except Exception as e:
        logger.warn("Error getting feature flag", feature=feature_name, error=str(e))
        return default

