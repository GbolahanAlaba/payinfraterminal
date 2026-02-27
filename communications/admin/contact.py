from django.contrib import admin
from communications.models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "contact_me", "date_created")
    list_filter = ("contact_me", "date_created")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("date_created", "date_modified")
    ordering = ("-date_created",)