"""
Quality policy loader for Creative Service.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from app.logger import get_logger

logger = get_logger()


@dataclass
class LengthLimitsConfig:
    enabled: bool = True
    min_length: int = 0
    max_length: int = 100000
    per_endpoint: Dict[str, Dict[str, int]] = field(default_factory=dict)


@dataclass
class FormatValidationConfig:
    enabled: bool = True
    required_fields: List[str] = field(default_factory=lambda: ["data", "provider"])
    allowed_formats: List[str] = field(default_factory=lambda: ["json"])
    strict_validation: bool = False


@dataclass
class QualityChecksConfig:
    enabled: bool = True
    min_coherence_score: float = 0.5
    min_relevance_score: float = 0.5
    check_image_quality: bool = True
    min_image_resolution: int = 256


@dataclass
class ToxicityConfig:
    enabled: bool = True
    threshold: float = 0.7
    block_on_toxicity: bool = True


@dataclass
class QualityPolicy:
    version: str = "1.0.0"
    length_limits: LengthLimitsConfig = field(default_factory=LengthLimitsConfig)
    format_validation: FormatValidationConfig = field(default_factory=FormatValidationConfig)
    quality_checks: QualityChecksConfig = field(default_factory=QualityChecksConfig)
    toxicity: ToxicityConfig = field(default_factory=ToxicityConfig)


class QualityPolicyLoader:
    def __init__(self, policies_path: str = "/app/quality/policies"):
        self.policies_path = Path(policies_path)
        self.logger = get_logger()
        self._policy: Optional[QualityPolicy] = None
        self._load_policy()

    def _load_policy(self):
        policy_file = self.policies_path / "quality.yaml"
        if not policy_file.exists():
            self.logger.warn("Quality policy file not found", path=str(policy_file))
            self._policy = QualityPolicy()
            return

        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "quality" not in data:
                raise ValueError("Invalid quality policy structure")
            
            quality_data = data["quality"]
            
            policy = QualityPolicy(
                version=data.get("version", "1.0.0"),
                length_limits=LengthLimitsConfig(**quality_data.get("length_limits", {})),
                format_validation=FormatValidationConfig(**quality_data.get("format_validation", {})),
                quality_checks=QualityChecksConfig(**quality_data.get("quality_checks", {})),
                toxicity=ToxicityConfig(**quality_data.get("toxicity", {})),
            )
            
            self._policy = policy
            self.logger.info("Quality policy loaded", file=str(policy_file))
        except Exception as e:
            self.logger.error("Failed to load quality policy", error=str(e))
            self._policy = QualityPolicy()

    def get_policy(self) -> QualityPolicy:
        if self._policy is None:
            self._load_policy()
        return self._policy if self._policy else QualityPolicy()

    def reload(self):
        self._policy = None
        self._load_policy()
        self.logger.info("Quality policies reloaded")


_quality_policy_loader: Optional[QualityPolicyLoader] = None


def get_quality_policy_loader() -> QualityPolicyLoader:
    global _quality_policy_loader
    if _quality_policy_loader is None:
        policies_path = os.getenv("QUALITY_POLICIES_PATH", "/app/quality/policies")
        _quality_policy_loader = QualityPolicyLoader(policies_path=policies_path)
    return _quality_policy_loader

