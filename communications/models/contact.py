import uuid
from django.db import models
from django.utils import timezone


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True, default="")
    email = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=100, blank=True, default="")
    message = models.TextField(blank=True, default="")
    contact_me = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.name} ({self.email})"