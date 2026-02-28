from django.contrib import admin
from merchants.models import Merchant
from billing.admin.invoice import InvoiceInline
from billing.admin.subscription import MerchantSubscriptionInline
from billing.admin.usage import UsageRecordInline
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
    inlines = [KYCDocumentInline]  # keep KYC inline if needed


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    def get_inlines(self, request, obj=None):
        # from merchants.admin.rate_limit import RateLimitInline

        return [
            MerchantAccountKeyInline,
            MerchantAPIKeyInline,
            KYCDocumentInline,
            MerchantSubscriptionInline,
            UsageRecordInline,
            InvoiceInline,
            # RateLimitInline,
        ]

    list_display = ("business_name", "user", "merchant_type", "is_verified", "created_at")
    list_filter = ("merchant_type", "is_verified", "created_at")
    search_fields = ("business_name", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("merchant_id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "merchant_id", "business_name", "business_email", "business_phone")}),
        ("Business Details", {"fields": ("merchant_type", "website", "address", "country", "state")}),
        ("Status", {"fields": ("is_verified",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )