from django.contrib import admin
from merchants.models import Merchant
from .account_key import MerchantAccountKeyInline
from .api_key import MerchantAPIKeyInline
from .kyc_document import KYCDocumentInline

class MerchantInline(admin.StackedInline):
    model = Merchant
    extra = 0
    fields = (
        'merchant_id',
        'business_name',
        'business_email',
        'business_phone',
        'merchant_type',
        'website',
        'address',
        'country',
        'state',
        'is_verified',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('merchant_id', 'created_at', 'updated_at')
    inlines = [KYCDocumentInline]

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "merchant_type", "is_verified", "created_at")
    list_filter = ("merchant_type", "is_verified", "created_at")
    search_fields = ("business_name", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("merchant_id", "created_at", "updated_at")
    inlines = [MerchantAccountKeyInline, MerchantAPIKeyInline, KYCDocumentInline]

    fieldsets = (
        (None, {"fields": ("user", "merchant_id", "business_name", "business_email", "business_phone")}),
        ("Business Details", {"fields": ("merchant_type", "website", "address", "country", "state")}),
        ("Status", {"fields": ("is_verified",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )