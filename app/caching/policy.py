"""
Caching policy loader for Creative Service.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from app.logger import get_logger

logger = get_logger()


@dataclass
class TTLConfig:
    enabled: bool = True
    default_seconds: int = 3600
    per_endpoint_seconds: Dict[str, int] = field(default_factory=dict)


@dataclass
class EvictionPolicyConfig:
    policy: str = "lru"
    max_entries: int = 10000
    max_size_mb: int = 500


@dataclass
class CachingPolicy:
    version: str = "1.0.0"
    enabled: bool = True
    ttl: TTLConfig = field(default_factory=TTLConfig)
    size_limits: EvictionPolicyConfig = field(default_factory=EvictionPolicyConfig)


class CachingPolicyLoader:
    def __init__(self, policies_path: str = "/app/caching/policies"):
        self.policies_path = Path(policies_path)
        self.logger = get_logger()
        self._policy: Optional[CachingPolicy] = None
        self._load_policy()

    def _load_policy(self):
        policy_file = self.policies_path / "caching.yaml"
        if not policy_file.exists():
            self.logger.warn("Caching policy file not found", path=str(policy_file))
            self._policy = CachingPolicy()
            return

        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "caching" not in data:
                raise ValueError("Invalid caching policy structure")
            
            caching_data = data["caching"]
            
            policy = CachingPolicy(
                version=data.get("version", "1.0.0"),
                enabled=caching_data.get("enabled", True),
                ttl=TTLConfig(**caching_data.get("ttl", {})),
                size_limits=EvictionPolicyConfig(**caching_data.get("size_limits", {})),
            )
            
            self._policy = policy
            self.logger.info("Caching policy loaded", file=str(policy_file))
        except Exception as e:
            self.logger.error("Failed to load caching policy", error=str(e))
            self._policy = CachingPolicy()

    def get_policy(self) -> CachingPolicy:
        if self._policy is None:
            self._load_policy()
        return self._policy if self._policy else CachingPolicy()

    def reload(self):
        self._policy = None
        self._load_policy()
        self.logger.info("Caching policies reloaded")


_caching_policy_loader: Optional[CachingPolicyLoader] = None


def get_caching_policy_loader() -> CachingPolicyLoader:
    global _caching_policy_loader
    if _caching_policy_loader is None:
        policies_path = os.getenv("CACHING_POLICIES_PATH", "/app/caching/policies")
        _caching_policy_loader = CachingPolicyLoader(policies_path=policies_path)
    return _caching_policy_loader

