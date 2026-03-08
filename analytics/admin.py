from django.contrib import admin
from .models import ProviderPerformance


@admin.register(ProviderPerformance)
class ProviderPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "provider",
        "success_rate",
        "failure_rate",
        "avg_latency",
        "total_transactions",
        "successful_transactions",
        "failed_transactions",
        "last_updated",
    )

    search_fields = ("provider",)
    list_filter = ("provider", "last_updated")
    readonly_fields = ("last_updated",)
    ordering = ("-last_updated",)