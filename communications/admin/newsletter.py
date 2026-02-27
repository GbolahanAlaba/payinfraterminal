from django.contrib import admin
from communications.models import Newsletter


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "date_created")
    list_filter = ("is_active", "date_created")
    search_fields = ("email",)
    readonly_fields = ("date_created", "date_modified")
    ordering = ("-date_created",)