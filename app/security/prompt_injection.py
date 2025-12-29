"""
Prompt injection detection for Creative Service.
"""

import re
from typing import Tuple, Optional
from app.security.policy import get_security_policy_loader
from app.logger import get_logger

logger = get_logger()


def detect_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
    """
    Detect potential prompt injection attempts.
    
    Returns: (is_safe, warning_message)
    """
    policy = get_security_policy_loader().get_policy()
    
    if not policy.prompt_injection.enabled:
        return True, None
    
    text_lower = text.lower()
    suspicious_count = 0
    
    # Check for suspicious patterns
    for pattern in policy.prompt_injection.suspicious_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            suspicious_count += 1
            logger.debug("Suspicious pattern detected", pattern=pattern)
    
    # Calculate risk score (simple heuristic)
    risk_score = min(suspicious_count / len(policy.prompt_injection.suspicious_patterns), 1.0)
    
    if risk_score >= policy.prompt_injection.threshold:
        warning = f"Potential prompt injection detected (risk score: {risk_score:.2f})"
        logger.warn("Prompt injection detected", risk_score=risk_score, text_preview=text[:50])
        return False, warning
    
    return True, None

