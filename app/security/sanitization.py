"""
Response sanitization for Creative Service.
"""

import re
from typing import Any, Dict
from app.security.policy import get_security_policy_loader
from app.logger import get_logger

logger = get_logger()


def sanitize_response(response: Any) -> Any:
    """
    Sanitize response content to remove potentially dangerous elements.
    """
    policy = get_security_policy_loader().get_policy()
    
    if not policy.sanitization.enabled:
        return response
    
    if isinstance(response, str):
        sanitized = response
        
        # Remove HTML tags if enabled
        if policy.sanitization.remove_html_tags:
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Remove script tags if enabled
        if policy.sanitization.remove_script_tags:
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
        
        # Enforce max length
        if policy.sanitization.max_length and len(sanitized) > policy.sanitization.max_length:
            sanitized = sanitized[:policy.sanitization.max_length]
            logger.debug("Response truncated to max length")
        
        return sanitized
    
    elif isinstance(response, dict):
        sanitized = {}
        for key, value in response.items():
            sanitized[key] = sanitize_response(value)
        return sanitized
    
    elif isinstance(response, list):
        return [sanitize_response(item) for item in response]
    
    return response

