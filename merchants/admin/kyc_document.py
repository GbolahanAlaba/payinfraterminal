from django.contrib import admin
from merchants.models import KYCDocument

class KYCDocumentInline(admin.TabularInline):
    model = KYCDocument
    extra = 0
    fields = ("document_type", "document_file", "verified", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ("merchant", "document_type", "verified", "uploaded_at")
    list_filter = ("document_type", "verified", "uploaded_at")
    search_fields = ("merchant__business_name",)
    readonly_fields = ("uploaded_at",)