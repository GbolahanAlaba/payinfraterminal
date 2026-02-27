from django.contrib import admin
from accounts.models import OTP

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("code", "user", "purpose", "is_used", "created_at", "expired_status")
    list_filter = ("purpose", "is_used", "created_at")
    search_fields = ("code", "user__email")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)

    def expired_status(self, obj):
        return obj.is_expired()
    expired_status.boolean = True
    expired_status.short_description = "Expired"