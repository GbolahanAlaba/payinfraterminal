"""
Analytics Views Package
All views for the Analytics service
"""

from .health import HealthView
from .provider_performance import ProviderPerformanceView


__all__ = [
    "HealthView",
    "ProviderPerformanceView",
]