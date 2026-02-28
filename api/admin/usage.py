
from django.contrib import admin
from api.models import APIUsageRecord

class UsageRecordInline(admin.TabularInline):
    model = APIUsageRecord
    extra = 0
    readonly_fields = ("endpoint", "method", "status_code", "response_time", "created_at")
    fields = ("endpoint", "method", "status_code", "response_time", "created_at")
    ordering = ("-created_at",)