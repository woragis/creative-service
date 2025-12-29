"""
Resilience policy loader and validator for Creative Service.

Loads retry, circuit breaker, timeout, and graceful degradation policies from YAML.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from app.logger import get_logger

logger = get_logger()


@dataclass
class RetryConfig:
    enabled: bool = True
    max_attempts: int = 3
    initial_delay_seconds: float = 0.5
    backoff_factor: float = 2.0
    max_delay_seconds: float = 10.0
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])
    retry_on_exceptions: List[str] = field(default_factory=lambda: ["httpx.ConnectError", "httpx.TimeoutException"])


@dataclass
class CircuitBreakerConfig:
    enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    minimum_requests: int = 10


@dataclass
class TimeoutConfig:
    enabled: bool = True
    default_timeout_seconds: int = 120  # Image/video generation takes longer
    per_provider_timeouts: Dict[str, int] = field(default_factory=dict)
    per_endpoint_timeouts: Dict[str, int] = field(default_factory=dict)


@dataclass
class DegradationConfig:
    enabled: bool = False
    degrade_to_provider: Optional[str] = None
    degrade_to_model: Optional[str] = None
    message: str = "Service is currently degraded. Please try again later or with a simpler request."


@dataclass
class ResiliencePolicy:
    version: str = "1.0.0"
    retry: RetryConfig = field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    degradation: DegradationConfig = field(default_factory=DegradationConfig)


class ResiliencePolicyLoader:
    def __init__(self, policies_path: str = "/app/resilience/policies"):
        self.policies_path = Path(policies_path)
        self.logger = get_logger()
        self._policy: Optional[ResiliencePolicy] = None
        self._load_policy()

    def _load_policy(self):
        policy_file = self.policies_path / "resilience.yaml"
        if not policy_file.exists():
            self.logger.warn("Resilience policy file not found", path=str(policy_file))
            self._policy = ResiliencePolicy()
            self.logger.info("Default resilience policy loaded")
            return

        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "resilience" not in data:
                raise ValueError("Invalid resilience policy structure: missing 'resilience' key")
            
            resilience_data = data["resilience"]
            
            policy = ResiliencePolicy(
                version=data.get("version", "1.0.0"),
                retry=RetryConfig(**resilience_data.get("retry", {})),
                circuit_breaker=CircuitBreakerConfig(**resilience_data.get("circuit_breaker", {})),
                timeout=TimeoutConfig(**resilience_data.get("timeout", {})),
                degradation=DegradationConfig(**resilience_data.get("degradation", {})),
            )
            
            self._policy = policy
            self.logger.info("Resilience policy loaded", file=str(policy_file))
        except Exception as e:
            self.logger.error("Failed to load resilience policy", error=str(e), file=str(policy_file))
            self._policy = ResiliencePolicy()
            self.logger.info("Default resilience policy loaded due to error")

    def get_policy(self) -> ResiliencePolicy:
        if self._policy is None:
            self._load_policy()
        return self._policy if self._policy else ResiliencePolicy()

    def reload(self):
        self._policy = None
        self._load_policy()
        self.logger.info("Resilience policies reloaded")


_resilience_policy_loader: Optional[ResiliencePolicyLoader] = None


def get_resilience_policy_loader() -> ResiliencePolicyLoader:
    global _resilience_policy_loader
    if _resilience_policy_loader is None:
        policies_path = os.getenv("RESILIENCE_POLICIES_PATH", "/app/resilience/policies")
        _resilience_policy_loader = ResiliencePolicyLoader(policies_path=policies_path)
    return _resilience_policy_loader

