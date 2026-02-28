from django.contrib import admin
from billing.models import MerchantSubscription

class MerchantSubscriptionInline(admin.TabularInline):
    model = MerchantSubscription
    extra = 0
    fields = ("plan", "start_date", "end_date", "is_active")
    readonly_fields = ("start_date",)


@admin.register(MerchantSubscription)
class MerchantSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("merchant", "plan", "start_date", "end_date", "is_active")
    list_filter = ("plan", "is_active", "start_date")
    search_fields = ("merchant__business_name", "merchant__user__email", "plan__name")
    readonly_fields = ("start_date",)
    ordering = ("-start_date",)