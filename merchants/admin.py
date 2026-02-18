from django.contrib import admin
from .models import Merchant, MerchantAPIKey, KYCDocument


class MerchantAPIKeyInline(admin.TabularInline):
    model = MerchantAPIKey
    extra = 0
    fields = ("provider", "secret_key", "public_key", "is_active")
    readonly_fields = ("provider", "secret_key", "public_key",) 


class KYCDocumentInline(admin.TabularInline):
    model = KYCDocument
    extra = 0
    fields = ("document_type", "document_file", "verified", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "merchant_type", "is_verified", "created_at")
    list_filter = ("merchant_type", "is_verified", "created_at")
    search_fields = ("business_name", "user__email", "user__first_name", "user__last_name")
    inlines = [MerchantAPIKeyInline, KYCDocumentInline]
    readonly_fields = ("merchant_id", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("user", "merchant_id", "business_name", "business_email", "business_phone")}),
        ("Business Details", {"fields": ("merchant_type", "website", "address", "country", "state")}),
        ("Status", {"fields": ("is_verified",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(MerchantAPIKey)
class MerchantAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("merchant", "provider", "is_active", "created_at")
    list_filter = ("provider", "is_active", "created_at")
    search_fields = ("merchant__business_name", "merchant__user__email", "provider")


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ("merchant", "document_type", "verified", "uploaded_at")
    list_filter = ("document_type", "verified", "uploaded_at")
    search_fields = ("merchant__business_name",)
    readonly_fields = ("uploaded_at",)
