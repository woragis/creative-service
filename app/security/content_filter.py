"""
Content filtering for Creative Service.
"""

import re
from typing import Tuple, Optional
from app.security.policy import get_security_policy_loader
from app.logger import get_logger

logger = get_logger()


def check_content_filter(text: str) -> Tuple[bool, Optional[str]]:
    """
    Check if content matches blocked patterns.
    
    Returns: (is_allowed, error_message)
    """
    policy = get_security_policy_loader().get_policy()
    
    if not policy.content_filter.enabled:
        return True, None
    
    text_lower = text.lower()
    
    # Check blocked patterns (regex)
    for pattern in policy.content_filter.blocked_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warn("Content blocked by pattern", pattern=pattern)
            return False, f"Content contains blocked pattern: {pattern}"
    
    # Check blocked keywords
    for keyword in policy.content_filter.blocked_keywords:
        if keyword.lower() in text_lower:
            logger.warn("Content blocked by keyword", keyword=keyword)
            return False, f"Content contains blocked keyword: {keyword}"
    
    return True, None

