from django.contrib import admin
from billing.models import UsageRecord

class UsageRecordInline(admin.TabularInline):
    model = UsageRecord
    extra = 0
    fields = ("transaction_count", "total_amount", "month")
    readonly_fields = ("transaction_count", "total_amount", "month")

@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("merchant", "transaction_count", "total_amount", "month")
    list_filter = ("month",)
    search_fields = ("merchant__business_name", "merchant__user__email")
    readonly_fields = ("transaction_count", "total_amount", "month")
    ordering = ("-month",)