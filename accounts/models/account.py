import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountTypeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class AccountType(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountTypeQuerySet.as_manager()

    class Meta:
        verbose_name = _("Account Type")
        verbose_name_plural = _("Account Types")
        ordering = ["name"]

    def __str__(self):
        return self.name