"""
Toxicity detection for Creative Service.
"""

from typing import Tuple, Optional
from app.quality.policy import get_quality_policy_loader
from app.logger import get_logger

logger = get_logger()


def check_toxicity(text: str) -> Tuple[bool, Optional[str], float]:
    """
    Check text for toxicity.
    
    Returns: (is_safe, warning_message, toxicity_score)
    """
    policy = get_quality_policy_loader().get_policy()
    
    if not policy.toxicity.enabled:
        return True, None, 0.0
    
    # Simple keyword-based toxicity detection
    # In production, use a proper toxicity detection model
    toxic_keywords = [
        "hate", "violence", "harassment", "abuse",
        "discrimination", "offensive", "inappropriate"
    ]
    
    text_lower = text.lower()
    toxic_count = sum(1 for keyword in toxic_keywords if keyword in text_lower)
    
    # Simple scoring: ratio of toxic keywords found
    toxicity_score = min(toxic_count / len(toxic_keywords), 1.0)
    
    if toxicity_score >= policy.toxicity.threshold:
        warning = f"Potential toxicity detected (score: {toxicity_score:.2f})"
        logger.warn("Toxicity detected", score=toxicity_score, text_preview=text[:50])
        
        if policy.toxicity.block_on_toxicity:
            return False, warning, toxicity_score
        
        return True, warning, toxicity_score
    
    return True, None, toxicity_score

