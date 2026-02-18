import os
import requests
import logging
import environ
from django.conf import settings

log = logging.getLogger(__name__)
env = environ.Env()


MAILGUN_BASE_URL = settings.MAILGUN_BASE_URL
MAILGUN_DOMAIN = settings.MAILGUN_DOMAIN
MAILGUN_API_KEY = settings.MAILGUN_API_KEY
DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
EMAIL_PREFIX = settings.EMAIL_PREFIX


class MailgunGateway:
    def __init__(self):
        if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
            raise ValueError("Mailgun API key and domain must be set")

        self.api_key = MAILGUN_API_KEY
        self.domain = MAILGUN_DOMAIN
        self.base_url = MAILGUN_BASE_URL

    def send_email(self, to_email, subject, text, html=None, attachments=None):
        return send_via_mailgun(to_email, subject, text, html, attachments)
    

def send_via_mailgun(to_email, subject, text, html=None, attachments=None):
    """
    Send an email through Mailgun API
    :param to_email: recipient email
    :param subject: subject line
    :param text: plain text body
    :param html: optional HTML body
    :param attachments: list of (filename, file_content, mimetype)
    """
    from_email = f"{EMAIL_PREFIX} <{DEFAULT_FROM_EMAIL}>"

    data = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "text": text,
    }

    if html:
        data["html"] = html

    files = []
    if attachments:
        for filename, file_content, mimetype in attachments:
            files.append(
                ("attachment", (filename, file_content, mimetype))
            )

    response = requests.post(
        f"{MAILGUN_BASE_URL}/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data=data,
        files=files if files else None,
    )
    return response

