from django.contrib import admin
from .models import Contact, Newsletter, Notification


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "contact_me", "date_created")
    list_filter = ("contact_me", "date_created")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("date_created", "date_modified")
    ordering = ("-date_created",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "date_created")
    list_filter = ("is_active", "date_created")
    search_fields = ("email",)
    readonly_fields = ("date_created", "date_modified")
    ordering = ("-date_created",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "read", "date_created")
    list_filter = ("read", "date_created")
    search_fields = ("title", "message", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("date_created", "date_modified")
    ordering = ("-date_created",)