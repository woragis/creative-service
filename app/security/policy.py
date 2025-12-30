"""
Security policy loader for Creative Service.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from app.logger import get_logger

logger = get_logger()


@dataclass
class ContentFilterConfig:
    enabled: bool = True
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onload=",
    ])
    blocked_keywords: List[str] = field(default_factory=lambda: [])


@dataclass
class PIIDetectionConfig:
    enabled: bool = True
    mask_email: bool = True
    mask_phone: bool = True
    mask_ssn: bool = True
    mask_credit_card: bool = True
    mask_pattern: str = "***REDACTED***"


@dataclass
class PromptInjectionConfig:
    enabled: bool = True
    suspicious_patterns: List[str] = field(default_factory=lambda: [
        r"ignore previous instructions",
        r"forget everything",
        r"system:",
        r"assistant:",
        r"you are now",
    ])
    threshold: float = 0.7


@dataclass
class SanitizationConfig:
    enabled: bool = True
    remove_html_tags: bool = True
    remove_script_tags: bool = True
    max_length: int = 100000


@dataclass
class SecurityPolicy:
    version: str = "1.0.0"
    content_filter: ContentFilterConfig = field(default_factory=ContentFilterConfig)
    pii_detection: PIIDetectionConfig = field(default_factory=PIIDetectionConfig)
    prompt_injection: PromptInjectionConfig = field(default_factory=PromptInjectionConfig)
    sanitization: SanitizationConfig = field(default_factory=SanitizationConfig)


class SecurityPolicyLoader:
    def __init__(self, policies_path: str = "/app/policies")
        self.policies_path = Path(policies_path)
        self.logger = get_logger()
        self._policy: Optional[SecurityPolicy] = None
        self._load_policy()

    def _load_policy(self):
        policy_file = self.policies_path / "security.yaml"
        if not policy_file.exists():
            self.logger.warn("Security policy file not found", path=str(policy_file))
            self._policy = SecurityPolicy()
            return

        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "security" not in data:
                raise ValueError("Invalid security policy structure")
            
            security_data = data["security"]
            
            policy = SecurityPolicy(
                version=data.get("version", "1.0.0"),
                content_filter=ContentFilterConfig(**security_data.get("content_filter", {})),
                pii_detection=PIIDetectionConfig(**security_data.get("pii_detection", {})),
                prompt_injection=PromptInjectionConfig(**security_data.get("prompt_injection", {})),
                sanitization=SanitizationConfig(**security_data.get("sanitization", {})),
            )
            
            self._policy = policy
            self.logger.info("Security policy loaded", file=str(policy_file))
        except Exception as e:
            self.logger.error("Failed to load security policy", error=str(e))
            self._policy = SecurityPolicy()

    def get_policy(self) -> SecurityPolicy:
        if self._policy is None:
            self._load_policy()
        return self._policy if self._policy else SecurityPolicy()

    def reload(self):
        self._policy = None
        self._load_policy()
        self.logger.info("Security policies reloaded")


_security_policy_loader: Optional[SecurityPolicyLoader] = None


def get_security_policy_loader() -> SecurityPolicyLoader:
    global _security_policy_loader
    if _security_policy_loader is None:
        policies_path = os.getenv("SECURITY_POLICIES_PATH", "/app/policies")
        _security_policy_loader = SecurityPolicyLoader(policies_path=policies_path)
    return _security_policy_loader

