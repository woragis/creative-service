"""
Budget tracking for Creative Service.
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from app.logger import get_logger
from app.cost_control.policy import get_cost_control_policy_loader

logger = get_logger()


class BudgetTracker:
    def __init__(self):
        self.policy = get_cost_control_policy_loader().get_policy().budget
        self._daily_spent = 0.0
        self._monthly_spent = 0.0
        self._last_daily_reset = datetime.now(timezone.utc).replace(
            hour=self.policy.reset_hour_utc, minute=0, second=0, microsecond=0
        )
        self._last_monthly_reset = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        self._ensure_resets()
        logger.info("BudgetTracker initialized", policy=self.policy)

    def _ensure_resets(self):
        now = datetime.now(timezone.utc)
        
        # Daily reset
        next_daily_reset = self._last_daily_reset + timedelta(days=1)
        if now >= next_daily_reset:
            self._daily_spent = 0.0
            self._last_daily_reset = now.replace(
                hour=self.policy.reset_hour_utc, minute=0, second=0, microsecond=0
            )
            logger.info("Daily budget reset")

        # Monthly reset
        next_month = self._last_monthly_reset.replace(day=1) + timedelta(days=32)
        next_monthly_reset = next_month.replace(day=1)
        if now >= next_monthly_reset:
            self._monthly_spent = 0.0
            self._last_monthly_reset = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            logger.info("Monthly budget reset")

    def record_spend(self, amount_usd: float):
        if not self.policy.enabled:
            return
        self._ensure_resets()
        self._daily_spent += amount_usd
        self._monthly_spent += amount_usd
        logger.debug("Recorded spend", amount_usd=amount_usd, daily_spent=self._daily_spent, monthly_spent=self._monthly_spent)

    def check_budget(self, estimated_cost_usd: float) -> Tuple[bool, str]:
        if not self.policy.enabled:
            return True, ""
        
        self._ensure_resets()
        
        if estimated_cost_usd > self.policy.per_request_limit_usd:
            return False, f"Estimated cost ${estimated_cost_usd:.2f} exceeds per-request limit of ${self.policy.per_request_limit_usd:.2f}"
        
        if (self._daily_spent + estimated_cost_usd) > self.policy.daily_limit_usd:
            return False, f"Estimated cost ${estimated_cost_usd:.2f} would exceed daily budget of ${self.policy.daily_limit_usd:.2f}"
        
        if (self._monthly_spent + estimated_cost_usd) > self.policy.monthly_limit_usd:
            return False, f"Estimated cost ${estimated_cost_usd:.2f} would exceed monthly budget of ${self.policy.monthly_limit_usd:.2f}"
        
        return True, ""

    def get_status(self) -> dict:
        self._ensure_resets()
        return {
            "enabled": self.policy.enabled,
            "daily_spent_usd": round(self._daily_spent, 4),
            "daily_limit_usd": self.policy.daily_limit_usd,
            "monthly_spent_usd": round(self._monthly_spent, 4),
            "monthly_limit_usd": self.policy.monthly_limit_usd,
            "per_request_limit_usd": self.policy.per_request_limit_usd,
        }


_budget_tracker: Optional[BudgetTracker] = None


def get_budget_tracker() -> BudgetTracker:
    global _budget_tracker
    if _budget_tracker is None:
        _budget_tracker = BudgetTracker()
    return _budget_tracker


def estimate_and_check_cost(provider: str, endpoint: str) -> Tuple[float, bool, str]:
    """Estimates cost and checks against budget limits."""
    from app.cost_tracking import estimate_request_cost
    estimated_cost = estimate_request_cost(provider, endpoint)
    
    tracker = get_budget_tracker()
    allowed, error_msg = tracker.check_budget(estimated_cost)
    
    return estimated_cost, allowed, error_msg


def validate_token_limits(input_tokens: int, output_tokens: int = 0) -> Tuple[bool, str]:
    """For creative service, we don't use tokens, but keep interface consistent."""
    return True, ""


def get_token_limits_config() -> dict:
    """Returns token limits config (not applicable for creative service)."""
    return {"enabled": False}

