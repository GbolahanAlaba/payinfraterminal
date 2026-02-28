from django.contrib import admin
from api.models.client import APIClient
from api.admin import RateLimitInline

@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    list_display = ("client_name", "merchant", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("client_name", "merchant__business_name", "merchant__user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [RateLimitInline, UsageRecordInline]