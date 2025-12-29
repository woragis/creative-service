"""
PII detection and masking for Creative Service.
"""

import re
from typing import Tuple
from app.security.policy import get_security_policy_loader
from app.logger import get_logger

logger = get_logger()


def detect_and_mask_pii(text: str) -> Tuple[str, bool]:
    """
    Detect and mask PII in text.
    
    Returns: (masked_text, pii_detected)
    """
    policy = get_security_policy_loader().get_policy()
    
    if not policy.pii_detection.enabled:
        return text, False
    
    masked_text = text
    pii_detected = False
    
    # Email pattern
    if policy.pii_detection.mask_email:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, masked_text):
            masked_text = re.sub(email_pattern, policy.pii_detection.mask_pattern, masked_text)
            pii_detected = True
            logger.debug("PII detected: email")
    
    # Phone pattern (US format)
    if policy.pii_detection.mask_phone:
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, masked_text):
            masked_text = re.sub(phone_pattern, policy.pii_detection.mask_pattern, masked_text)
            pii_detected = True
            logger.debug("PII detected: phone")
    
    # SSN pattern
    if policy.pii_detection.mask_ssn:
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        if re.search(ssn_pattern, masked_text):
            masked_text = re.sub(ssn_pattern, policy.pii_detection.mask_pattern, masked_text)
            pii_detected = True
            logger.debug("PII detected: SSN")
    
    # Credit card pattern (simplified)
    if policy.pii_detection.mask_credit_card:
        cc_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
        if re.search(cc_pattern, masked_text):
            masked_text = re.sub(cc_pattern, policy.pii_detection.mask_pattern, masked_text)
            pii_detected = True
            logger.debug("PII detected: credit card")
    
    if pii_detected:
        logger.warn("PII detected and masked in content")
    
    return masked_text, pii_detected

