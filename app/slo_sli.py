"""
SLO/SLI (Service Level Objective/Indicator) tracking for Creative Service.

This module implements SLO/SLI metrics tracking to measure service reliability
and performance against defined objectives.

SLOs:
- Availability: 99.9% (3 nines)
- Latency: P95 < 2000ms, P99 < 5000ms (image generation can be slower)
- Error Rate: < 0.1% (1 error per 1000 requests)
"""

from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import REGISTRY
import time
from typing import Optional
from app.logger import get_logger

logger = get_logger()

# SLO/SLI Metrics
# Availability metrics
slo_requests_total = Counter(
    'slo_requests_total',
    'Total number of requests',
    ['endpoint', 'status']
)

slo_availability = Gauge(
    'slo_availability',
    'Current availability percentage (0-100)',
    ['window']
)

# Latency metrics
slo_latency_histogram = Histogram(
    'slo_latency_seconds',
    'Request latency in seconds',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

slo_latency_p95 = Gauge(
    'slo_latency_p95_seconds',
    'P95 latency in seconds',
    ['endpoint', 'window']
)

slo_latency_p99 = Gauge(
    'slo_latency_p99_seconds',
    'P99 latency in seconds',
    ['endpoint', 'window']
)

# Error rate metrics
slo_errors_total = Counter(
    'slo_errors_total',
    'Total number of errors',
    ['endpoint', 'error_type']
)

slo_error_rate = Gauge(
    'slo_error_rate',
    'Current error rate percentage (0-100)',
    ['endpoint', 'window']
)

# Error budget tracking
slo_error_budget_remaining = Gauge(
    'slo_error_budget_remaining',
    'Remaining error budget percentage (0-100)',
    ['slo_name', 'window']
)

# SLO targets (configurable)
SLO_TARGETS = {
    'availability': 99.9,  # 99.9% availability
    'latency_p95': 2.0,    # 2000ms P95 (image generation is slower)
    'latency_p99': 5.0,    # 5000ms P99
    'error_rate': 0.1,     # 0.1% error rate
}


class SLOTracker:
    """Tracks SLO/SLI metrics for the service."""
    
    def __init__(self):
        self.logger = get_logger()
    
    def record_request(self, endpoint: str, status_code: int, duration: float):
        """
        Record a request for SLO tracking.
        
        Args:
            endpoint: The endpoint path (e.g., '/v1/images/generate')
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        # Record total requests
        status = 'success' if 200 <= status_code < 400 else 'error'
        slo_requests_total.labels(endpoint=endpoint, status=status).inc()
        
        # Record latency
        slo_latency_histogram.labels(endpoint=endpoint).observe(duration)
        
        # Record errors
        if status_code >= 400:
            error_type = self._classify_error(status_code)
            slo_errors_total.labels(endpoint=endpoint, error_type=error_type).inc()
    
    def _classify_error(self, status_code: int) -> str:
        """Classify error by status code."""
        if 400 <= status_code < 500:
            return 'client_error'
        elif 500 <= status_code < 600:
            return 'server_error'
        else:
            return 'unknown_error'
    
    def calculate_availability(self, endpoint: str, window: str = '1h') -> float:
        """
        Calculate availability percentage for a given window.
        
        Note: This is a simplified calculation. In production, you'd want
        to query Prometheus for actual time-series data.
        """
        # This would typically query Prometheus for actual metrics
        # For now, return a placeholder
        return 99.9
    
    def calculate_error_rate(self, endpoint: str, window: str = '1h') -> float:
        """
        Calculate error rate percentage for a given window.
        
        Note: This is a simplified calculation. In production, you'd want
        to query Prometheus for actual time-series data.
        """
        # This would typically query Prometheus for actual metrics
        # For now, return a placeholder
        return 0.05
    
    def check_slo_compliance(self, endpoint: str) -> dict:
        """
        Check if current metrics meet SLO targets.
        
        Returns:
            dict with SLO compliance status for each metric
        """
        availability = self.calculate_availability(endpoint)
        error_rate = self.calculate_error_rate(endpoint)
        
        return {
            'availability': {
                'current': availability,
                'target': SLO_TARGETS['availability'],
                'compliant': availability >= SLO_TARGETS['availability']
            },
            'error_rate': {
                'current': error_rate,
                'target': SLO_TARGETS['error_rate'],
                'compliant': error_rate <= SLO_TARGETS['error_rate']
            },
            'overall_compliant': (
                availability >= SLO_TARGETS['availability'] and
                error_rate <= SLO_TARGETS['error_rate']
            )
        }


# Global SLO tracker instance
slo_tracker = SLOTracker()


def record_request_metric(endpoint: str, status_code: int, duration: float):
    """Convenience function to record request metrics."""
    slo_tracker.record_request(endpoint, status_code, duration)

