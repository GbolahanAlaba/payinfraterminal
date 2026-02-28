from django.contrib import admin
from api.models import ProviderAPIKey

class ProviderAPIKeyInline(admin.TabularInline):
    model = ProviderAPIKey
    extra = 0
    fields = ("provider", "secret_key", "public_key", "is_active")
    readonly_fields = ("provider", "secret_key", "public_key")


@admin.register(ProviderAPIKey)
class ProviderAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("client", "provider", "is_active", "created_at")
    list_filter = ("provider", "is_active", "created_at")
    search_fields = ("client__merchant__user__email", "provider")