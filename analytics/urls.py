# urls.py
from django.urls import path
from .views import (HealthView, 
        ProviderPerformanceView, 
        ProviderSuccessGraphView, 
        OverviewView,
        OverviewGraphView,
        )

urlpatterns = [
    path("health-check/", HealthView.as_view()),
    path("overview/", OverviewView.as_view(), name="overview-data"),
    path("overview/graph/", OverviewGraphView.as_view(), name="overview-graph"),
    path("provider-performance/", ProviderPerformanceView.as_view(), name="provider-performance"),
    path("success-rate/", ProviderSuccessGraphView.as_view(), name="success-rate-graph"),
]
