from django.contrib import admin
from billing.models.invoice import Invoice

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    fields = ("reference", "amount_due", "status", "issued_at", "paid_at")
    readonly_fields = ("reference", "issued_at", "paid_at")



@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("reference", "merchant", "amount_due", "status", "issued_at", "paid_at")
    list_filter = ("status", "issued_at")
    search_fields = ("merchant__business_name", "merchant__user__email", "reference")
    readonly_fields = ("reference", "issued_at", "paid_at")
    ordering = ("-issued_at",)