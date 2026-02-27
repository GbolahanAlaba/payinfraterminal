from django.contrib import admin
from merchants.models import MerchantAPIKey

class MerchantAPIKeyInline(admin.TabularInline):
    model = MerchantAPIKey
    extra = 0
    fields = ("provider", "secret_key", "public_key", "is_active")
    readonly_fields = ("provider", "secret_key", "public_key")


@admin.register(MerchantAPIKey)
class MerchantAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("merchant", "provider", "is_active", "created_at")
    list_filter = ("provider", "is_active", "created_at")
    search_fields = ("merchant__business_name", "merchant__user__email", "provider")