"""
Feature flags policy loader for Creative Service.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from app.logger import get_logger

logger = get_logger()


@dataclass
class ProviderFlags:
    openai: bool = True
    stable_diffusion: bool = True
    cipher: bool = True
    replicate: bool = True
    runway: bool = True


@dataclass
class EndpointFlags:
    image_generation: bool = True
    diagram_generation: bool = True
    video_generation: bool = True
    image_animation: bool = True


@dataclass
class FeatureFlagsPolicy:
    version: str = "1.0.0"
    streaming_enabled: bool = True
    caching_enabled: bool = True
    providers: ProviderFlags = field(default_factory=ProviderFlags)
    endpoints: EndpointFlags = field(default_factory=EndpointFlags)
    custom_flags: Dict[str, bool] = field(default_factory=dict)


class FeatureFlagsPolicyLoader:
    def __init__(self, policies_path: str = "/app/policies"):
        self.policies_path = Path(policies_path)
        self.logger = get_logger()
        self._policy: Optional[FeatureFlagsPolicy] = None
        self._load_policy()

    def _load_policy(self):
        policy_file = self.policies_path / "feature_flags.yaml"
        if not policy_file.exists():
            self.logger.warn("Feature flags policy file not found", path=str(policy_file))
            self._policy = FeatureFlagsPolicy()
            return

        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "feature_flags" not in data:
                raise ValueError("Invalid feature flags policy structure")
            
            flags_data = data["feature_flags"]
            
            policy = FeatureFlagsPolicy(
                version=data.get("version", "1.0.0"),
                streaming_enabled=flags_data.get("streaming_enabled", True),
                caching_enabled=flags_data.get("caching_enabled", True),
                providers=ProviderFlags(**flags_data.get("providers", {})),
                endpoints=EndpointFlags(**flags_data.get("endpoints", {})),
                custom_flags=flags_data.get("custom_flags", {}),
            )
            
            self._policy = policy
            self.logger.info("Feature flags policy loaded", file=str(policy_file))
        except Exception as e:
            self.logger.error("Failed to load feature flags policy", error=str(e))
            self._policy = FeatureFlagsPolicy()

    def get_policy(self) -> FeatureFlagsPolicy:
        if self._policy is None:
            self._load_policy()
        return self._policy if self._policy else FeatureFlagsPolicy()

    def reload(self):
        self._policy = None
        self._load_policy()
        self.logger.info("Feature flags policies reloaded")


_feature_flags_policy_loader: Optional[FeatureFlagsPolicyLoader] = None


def get_feature_flags_loader() -> FeatureFlagsPolicyLoader:
    global _feature_flags_policy_loader
    if _feature_flags_policy_loader is None:
        policies_path = os.getenv("FEATURE_FLAGS_POLICIES_PATH", "/app/policies")
        _feature_flags_policy_loader = FeatureFlagsPolicyLoader(policies_path=policies_path)
    return _feature_flags_policy_loader

