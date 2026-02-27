from django.contrib import admin
from communications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "read", "date_created")
    list_filter = ("read", "date_created")
    search_fields = ("title", "message", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("date_created", "date_modified")
    ordering = ("-date_created",)