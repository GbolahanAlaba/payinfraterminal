from django.contrib import admin
from api.models import ProviderAPIKey, ClientProvider, ClientProviderCredential

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
    ordering = ("-created_at",)


class MerchantProviderCredentialInline(admin.StackedInline):
    model = ClientProviderCredential
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("credentials", "credential_type", "is_encrypted")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(ClientProvider)
class ClientProviderAdmin(admin.ModelAdmin):
    list_display = ("client", "provider", "is_active", "created_at")
    list_filter = ("provider", "is_active")
    search_fields = ("client__merchant__name", "provider")
    ordering = ("-created_at",)
    inlines = [MerchantProviderCredentialInline]


@admin.register(ClientProviderCredential)
class MerchantProviderCredentialAdmin(admin.ModelAdmin):
    list_display = ("client_provider", "credential_type", "is_encrypted", "created_at", "updated_at")
    search_fields = ("client_provider__client__merchant__name", "credential_type")
    readonly_fields = ("created_at", "updated_at")
    ordering = ('-created_at',)