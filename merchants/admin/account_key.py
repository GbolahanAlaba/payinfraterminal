from django.contrib import admin
from merchants.models import MerchantAccountKey

class MerchantAccountKeyInline(admin.StackedInline):
    model = MerchantAccountKey
    can_delete = False
    max_num = 1
    readonly_fields = ('merchant_api_key', 'created_at', 'updated_at')
    fields = ('account_id', 'merchant_api_key', 'environment', 'is_active', 'created_at', 'updated_at')


@admin.register(MerchantAccountKey)
class MerchantAccountKeyAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'merchant_api_key', 'account_id', 'environment', 'is_active', 'created_at')
    list_filter = ('environment', 'is_active', 'created_at')
    search_fields = ('merchant__business_name', 'merchant_api_key', 'account_id')
    readonly_fields = ('merchant_api_key', 'created_at', 'updated_at')