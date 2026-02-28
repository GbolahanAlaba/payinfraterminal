from django.contrib import admin
from .client import APIClient


class APIClientInline(admin.StackedInline):
    model = APIClient
    extra = 0
    readonly_fields = ('client_id', 'client_secret', 'created_at', 'updated_at')
    fields = ('client_name', 'client_id', 'client_secret', 'environment', 'status', 'created_at', 'updated_at')


@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'merchant', 'environment', 'status', 'created_at')
    list_filter = ('environment', 'status', 'created_at')
    search_fields = ('client_name', 'merchant__business_name', 'merchant__user__email')
    readonly_fields = ('client_id', 'client_secret', 'created_at', 'updated_at')