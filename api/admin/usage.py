
from django.contrib import admin
from api.models import APIUsageRecord

class UsageRecordInline(admin.TabularInline):
    model = APIUsageRecord
    extra = 0
    readonly_fields = ("endpoint", "method", "status_code", "response_time", "created_at")
    fields = ("endpoint", "method", "status_code", "response_time", "created_at")
    ordering = ("-created_at",)


@admin.register(APIUsageRecord)
class APIUsageRecordAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "endpoint",
        "method",
        "request_count",
        "status_code",
        "response_time",
        "created_at",
    )
    list_filter = ("endpoint", "method", "status_code", "created_at")
    search_fields = ("client__client_name", "endpoint")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    # # Optional: Inline for history if you have a history model
    # class HistoryInline(admin.TabularInline):
    #     model = APIUsageRecordHistory
    #     extra = 0
    #     readonly_fields = (
    #         "client",
    #         "endpoint",
    #         "method",
    #         "request_count",
    #         "status_code",
    #         "response_time",
    #         "recorded_at",
    #     )
    #     can_delete = False

    # inlines = [HistoryInline]