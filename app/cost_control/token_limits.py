"""
Token limits for Creative Service (placeholder - not applicable).
"""

from typing import Tuple

def validate_token_limits(input_tokens: int, output_tokens: int = 0) -> Tuple[bool, str]:
    """Creative service doesn't use tokens, but keep interface consistent."""
    return True, ""


def get_token_limits_config() -> dict:
    """Returns token limits config."""
    return {"enabled": False}

