# accounts/admin/mfa.py
from django.contrib import admin
from accounts.models import MFADevice

class MFAInline(admin.StackedInline):
    model = MFADevice
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    fields = ("method", "status", "secret", "created_at", "updated_at")

@admin.register(MFADevice)
class MFAAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "status", "created_at")
    list_filter = ("type", "is_active")
    search_fields = ("user__email", "method")
    readonly_fields = ("created_at", "verified_at")
    ordering = ("-created_at",)