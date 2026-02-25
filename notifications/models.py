from django.db import models
import uuid
from django.db import models
from django.utils import timezone
from accounts.models import User


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True, default="")
    email = models.CharField(max_length=100, blank=True, null=True, default="")
    phone = models.CharField(max_length=100, blank=True, null=True, default="")
    message = models.TextField(max_length=100, blank=True, null=True, default="")
    contact_me = models.BooleanField(default=True)
    date_created = models.DateField(default=timezone.now)
    date_modified = models.DateField(default=timezone.now)


class Newsletter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=100, blank=True, null=True, default="")
    is_active = models.BooleanField(default=True)
    date_created = models.DateField(default=timezone.now)
    date_modified = models.DateField(default=timezone.now)



class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField(max_length=255)
    read = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.title