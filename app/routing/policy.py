"""
Routing policy loader for Creative Service.

Simplified routing for image/video/diagram providers.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from app.logger import get_logger

logger = get_logger()


@dataclass
class ProviderConfig:
    name: str
    enabled: bool = True
    priority: int = 1
    cost_tier: str = "medium"  # low, medium, high
    quality_tier: str = "medium"  # low, medium, high
    fallback_to: List[str] = field(default_factory=list)


@dataclass
class RoutingPolicy:
    version: str = "1.0.0"
    default_provider: str = "openai"
    providers: List[ProviderConfig] = field(default_factory=list)


class RoutingPolicyLoader:
    def __init__(self, policies_path: str = "/app/routing/policies"):
        self.policies_path = Path(policies_path)
        self.logger = get_logger()
        self._policy: Optional[RoutingPolicy] = None
        self._load_policy()

    def _load_policy(self):
        policy_file = self.policies_path / "routing.yaml"
        if not policy_file.exists():
            self.logger.warn("Routing policy file not found", path=str(policy_file))
            self._policy = RoutingPolicy()
            return

        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "routing" not in data:
                raise ValueError("Invalid routing policy structure")
            
            routing_data = data["routing"]
            policy = RoutingPolicy(
                version=data.get("version", "1.0.0"),
                default_provider=routing_data.get("default_provider", "openai"),
            )

            if "providers" in routing_data:
                for provider_data in routing_data["providers"]:
                    provider_config = ProviderConfig(
                        name=provider_data["name"],
                        enabled=provider_data.get("enabled", True),
                        priority=provider_data.get("priority", 99),
                        cost_tier=provider_data.get("cost_tier", "medium"),
                        quality_tier=provider_data.get("quality_tier", "medium"),
                        fallback_to=provider_data.get("fallback_to", []),
                    )
                    policy.providers.append(provider_config)
            
            self._policy = policy
            self.logger.info("Routing policy loaded", file=str(policy_file))
        except Exception as e:
            self.logger.error("Failed to load routing policy", error=str(e))
            self._policy = RoutingPolicy()

    def get_policy(self) -> RoutingPolicy:
        if self._policy is None:
            self._load_policy()
        return self._policy if self._policy else RoutingPolicy()

    def reload(self):
        self._policy = None
        self._load_policy()
        self.logger.info("Routing policies reloaded")


_routing_policy_loader: Optional[RoutingPolicyLoader] = None


def get_routing_policy_loader() -> RoutingPolicyLoader:
    global _routing_policy_loader
    if _routing_policy_loader is None:
        policies_path = os.getenv("ROUTING_POLICIES_PATH", "/app/routing/policies")
        _routing_policy_loader = RoutingPolicyLoader(policies_path=policies_path)
    return _routing_policy_loader

