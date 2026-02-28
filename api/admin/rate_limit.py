from django.contrib import admin
from api.models import APIRateLimit

class RateLimitInline(admin.StackedInline):
    model = APIRateLimit
    max_num = 1
    can_delete = False
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "requests_per_minute",
        "requests_per_hour",
        "requests_per_day",
        "burst_allowance",
        "created_at",
        "updated_at",
    )


@admin.register(APIRateLimit)
class RateLimitAdmin(admin.ModelAdmin):
    list_display = ("merchant", "requests_per_minute", "requests_per_hour", "requests_per_day", "burst_allowance")
    search_fields = ("merchant__user__email",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)