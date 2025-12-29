"""
Cost tracking and optimization metrics for Creative Service.

This module tracks resource usage and cost-related metrics to help optimize
deployment costs.
"""

from prometheus_client import Gauge, Counter, Histogram
from app.logger import get_logger

logger = get_logger()

# Cost-related metrics
cost_cpu_usage = Gauge(
    'cost_cpu_usage_cores',
    'Current CPU usage in cores',
    ['pod', 'node']
)

cost_memory_usage = Gauge(
    'cost_memory_usage_bytes',
    'Current memory usage in bytes',
    ['pod', 'node']
)

cost_request_cost = Histogram(
    'cost_request_cost_usd',
    'Estimated cost per request in USD',
    ['endpoint', 'provider'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

cost_total_requests = Counter(
    'cost_total_requests',
    'Total number of requests (for cost calculation)',
    ['endpoint']
)

cost_provider_api_calls = Counter(
    'cost_provider_api_calls_total',
    'Total API calls to external providers',
    ['provider', 'model']
)

# Resource utilization metrics
resource_utilization = Gauge(
    'resource_utilization_percent',
    'Resource utilization percentage',
    ['resource_type']  # cpu, memory
)


class CostTracker:
    """Tracks cost and resource usage metrics."""
    
    def __init__(self):
        self.logger = get_logger()
    
    def record_request(self, endpoint: str, provider: str = None, cost_usd: float = 0.0):
        """
        Record a request for cost tracking.
        
        Args:
            endpoint: The endpoint path
            provider: Provider used (e.g., 'openai', 'replicate', 'cipher')
            cost_usd: Estimated cost in USD
        """
        cost_total_requests.labels(endpoint=endpoint).inc()
        
        if provider and cost_usd > 0:
            cost_request_cost.labels(
                endpoint=endpoint,
                provider=provider
            ).observe(cost_usd)
    
    def record_api_call(self, provider: str, model: str = "default"):
        """Record an API call to external provider."""
        cost_provider_api_calls.labels(
            provider=provider,
            model=model
        ).inc()
    
    def update_resource_usage(self, cpu_cores: float, memory_bytes: int, pod: str = "unknown", node: str = "unknown"):
        """
        Update resource usage metrics.
        
        Note: In Kubernetes, this would typically be scraped by cAdvisor.
        This is for manual tracking if needed.
        """
        cost_cpu_usage.labels(pod=pod, node=node).set(cpu_cores)
        cost_memory_usage.labels(pod=pod, node=node).set(memory_bytes)


# Global cost tracker instance
cost_tracker = CostTracker()


def estimate_request_cost(provider: str, endpoint: str, **kwargs) -> float:
    """
    Estimate cost per request based on provider and endpoint.
    
    Note: These are example pricing. Update with actual provider pricing.
    """
    # Example pricing (update with actual pricing)
    pricing = {
        "openai": {
            "/v1/images/generate": 0.04,  # DALL-E 3 standard
            "/v1/images/generate/thumbnail": 0.04,
        },
        "stable-diffusion": {
            "/v1/images/generate": 0.002,  # Replicate pricing (per second)
        },
        "cipher": {
            "/v1/images/generate": 0.01,  # Estimated
        },
        "replicate": {
            "/v1/videos/generate": 0.05,  # Stable Video Diffusion
            "/v1/videos/animate": 0.05,
        },
        "runway": {
            "/v1/videos/generate": 0.10,  # Estimated
            "/v1/videos/animate": 0.10,
        },
    }
    
    provider_pricing = pricing.get(provider, {})
    cost = provider_pricing.get(endpoint, 0.0)
    
    return cost

