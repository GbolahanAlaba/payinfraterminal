from django.contrib import admin
from billing.models.plan import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "transaction_limit", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)