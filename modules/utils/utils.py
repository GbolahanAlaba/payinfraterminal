import logging
import environ
import boto3
import random
import string
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils.timezone import now
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.utils.html import strip_tags
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.conf import settings
from modules.gateways.mailgun import MailgunGateway

env = environ.Env()

log = logging.getLogger('my_logger')

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            return Response({"status": "failed", "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper


class AccountUtils:
    """ """
    def generate_profile_id():
        return str(random.randint(100_000_000, 999_999_999))
    
    def generate_merchant_id():
        return str(random.randint(100_000_000, 999_999_999))
    
    def generate_otp():
        return str(random.randint(1000, 9999))

class TransUtils:
    def generate_payment_reference(profile_id: int) -> str:
        prefix = "TXN"
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{date_str}-{profile_id}-{random_str}"


class KYCUtils:
    @staticmethod
    def is_kyc_verified(merchant):
        return merchant.kyc_documents.filter(verified=True).exists()

class util:
    @staticmethod
    def send_email(data=None, **kwargs):
        """
        Send an email via Mailgun.
        Supports both:
          util.send_email(data={...})
          util.send_email(subject=..., to_email=..., html=..., text=...)
        """
        try:
            # Determine input style
            if data is None:
                subject = kwargs.get("subject")
                to_email = kwargs.get("to_email")
                html = kwargs.get("html")
                text = kwargs.get("text") or strip_tags(html)
                attachments = kwargs.get("attachments")
                template = kwargs.get("template")
                context = kwargs.get("context", {})

            else:
                subject = data["email_subject"]
                to_email = data["to_email"]
                html = data.get("html", "")
                text = data.get("text", strip_tags(html))
                attachments = data.get("attachments")
                template = data.get("template")
                context = data.get("context", {})

            # Render template if provided
            if template:
                try:
                    # If email_body is passed in context, it will be injected
                    html = render_to_string(template, context)
                    text = strip_tags(html)
                except TemplateDoesNotExist:
                    log.warning("Template %s not found, using raw HTML", template)

            provider = kwargs.get("email_provider")
            log.info(f"Sending email to {to_email} via {provider.__class__.__name__}")
            response = provider.send_email(
                to_email=to_email,
                subject=subject,
                text=text,
                html=html,
                attachments=attachments,
            )

            if response.status_code in [200, 202]:
                log.info(f"Mailgun email sent successfully to {to_email}")
            else:
                log.error(
                    f"Mailgun email failed for {to_email}. "
                    f"Status: {response.status_code}, Response: {response.text}"
                )

            return response

        except Exception as e:
            log.error(f"Error sending Mailgun email to {kwargs.get('to_email') or data.get('to_email')}: {e}")