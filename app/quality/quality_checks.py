"""
Quality checks for Creative Service.
"""

from typing import Tuple, Any, Dict, List, Optional
from app.quality.policy import get_quality_policy_loader
from app.logger import get_logger

logger = get_logger()


def check_quality(response: Any, prompt: str = "", endpoint: str = "default") -> Tuple[bool, Optional[str]]:
    """
    Perform quality checks on response.
    
    For creative service, this checks:
    - Image resolution (if applicable)
    - Basic response structure
    
    Returns: (is_valid, error_message)
    """
    policy = get_quality_policy_loader().get_policy()
    
    if not policy.quality_checks.enabled:
        return True, None
    
    # For image generation, check if data exists
    if endpoint == "/v1/images/generate" and isinstance(response, dict):
        if "data" in response and isinstance(response["data"], list):
            if len(response["data"]) == 0:
                error = "No images generated"
                logger.warn("Quality check failed", endpoint=endpoint, reason="empty_data")
                return False, error
            
            # Check image quality if enabled
            if policy.quality_checks.check_image_quality:
                # Basic validation - ensure we have image data
                for item in response["data"]:
                    if not isinstance(item, dict):
                        continue
                    if not (item.get("url") or item.get("b64_json")):
                        error = "Image data missing URL or base64 content"
                        logger.warn("Quality check failed", endpoint=endpoint, reason="missing_image_data")
                        return False, error
    
    # For video generation, similar checks
    if endpoint == "/v1/videos/generate" and isinstance(response, dict):
        if "data" in response:
            if not response["data"]:
                error = "No video generated"
                logger.warn("Quality check failed", endpoint=endpoint, reason="empty_data")
                return False, error
    
    return True, None

