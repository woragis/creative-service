"""
Cost control policy loader for Creative Service.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from app.logger import get_logger

logger = get_logger()


@dataclass
class BudgetConfig:
    enabled: bool = True
    daily_limit_usd: float = 100.0
    monthly_limit_usd: float = 3000.0
    per_request_limit_usd: float = 1.0
    reset_hour_utc: int = 0


@dataclass
class CostControlPolicy:
    version: str = "1.0.0"
    budget: BudgetConfig = field(default_factory=BudgetConfig)


class CostControlPolicyLoader:
    def __init__(self, policies_path: str = "/app/cost_control/policies"):
        self.policies_path = Path(policies_path)
        self.logger = get_logger()
        self._policy: Optional[CostControlPolicy] = None
        self._load_policy()

    def _load_policy(self):
        policy_file = self.policies_path / "cost_control.yaml"
        if not policy_file.exists():
            self.logger.warn("Cost control policy file not found", path=str(policy_file))
            self._policy = CostControlPolicy()
            return

        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data or "cost_control" not in data:
                raise ValueError("Invalid cost control policy structure")
            
            cost_control_data = data["cost_control"]
            
            policy = CostControlPolicy(
                version=data.get("version", "1.0.0"),
                budget=BudgetConfig(**cost_control_data.get("budget", {})),
            )
            
            self._policy = policy
            self.logger.info("Cost control policy loaded", file=str(policy_file))
        except Exception as e:
            self.logger.error("Failed to load cost control policy", error=str(e))
            self._policy = CostControlPolicy()

    def get_policy(self) -> CostControlPolicy:
        if self._policy is None:
            self._load_policy()
        return self._policy if self._policy else CostControlPolicy()

    def reload(self):
        self._policy = None
        self._load_policy()
        self.logger.info("Cost control policies reloaded")


_cost_control_policy_loader: Optional[CostControlPolicyLoader] = None


def get_cost_control_policy_loader() -> CostControlPolicyLoader:
    global _cost_control_policy_loader
    if _cost_control_policy_loader is None:
        policies_path = os.getenv("COST_CONTROL_POLICIES_PATH", "/app/cost_control/policies")
        _cost_control_policy_loader = CostControlPolicyLoader(policies_path=policies_path)
    return _cost_control_policy_loader

