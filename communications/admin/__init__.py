"""
Communications Admin Package
Registers all admin interfaces for the Communications app
"""

from .contact import ContactAdmin
from .newsletter import NewsletterAdmin
from .notification import NotificationAdmin

__all__ = [
    "ContactAdmin",
    "NewsletterAdmin",
    "NotificationAdmin",
]