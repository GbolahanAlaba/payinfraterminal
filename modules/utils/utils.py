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



        
class PaymentCharges:

    @staticmethod
    def payment_charges(amount: Decimal) -> Decimal:
        """
        Calculate Paystack charges for a given amount.
        Paystack charges 1.5% + ₦100 per transaction for amounts above ₦2500,
        and a flat ₦100 for amounts ₦2500 and below.
        """
        provider = "paystack"
        if provider == "paystack":
            percentage_charge = Decimal(0.015) * amount
            extra_charge = Decimal(100.0) if amount > Decimal(2500) else Decimal(0.0)
            total_charge = percentage_charge + extra_charge
            return round(min(total_charge, Decimal(2000.0)), 2) # capped N2000
        else:
            return 0.0


class ServiceProvidersEnvironment:

    def get_provider(self, provider: str, environment: str):
        """
        Factory function that returns the environment details for a given provider.
        Currently supports 'paystack' and 'nomba'.
        """
        return provider, environment

        

    def get_nomba_environment_details(self):
        
        provider = self.get_provider()
        environment = provider[1]
        log.info(f"Nomba ENV: {environment}")
        
        if environment == "live":
            return {
                "URL": settings.LIVE_NOMBA_BASE_URL,
                "NOMBA_ACCOUNT_ID": settings.NOMBA_ACCOUNT_ID,
                "NOMBA_CLIENT_ID": settings.LIVE_NOMBA_CLIENT_ID,
                "NOMBA_CLIENT_SECRET": settings.LIVE_NOMBA_CLIENT_SECRET
            }
        else:  # Default to sandbox
            log.info(f"Nomba ENV: {environment}")
            return {
                "URL": settings.TEST_NOMBA_BASE_URL,
                "NOMBA_ACCOUNT_ID": settings.NOMBA_ACCOUNT_ID,
                "NOMBA_CLIENT_ID": settings.TEST_NOMBA_CLIENT_ID,
                "NOMBA_CLIENT_SECRET": settings.TEST_NOMBA_CLIENT_SECRET
            }

            
    def get_paystack_environment_details(self):
        """
        Return Paystack environment details (URL, secret key) dynamically.
        Uses the database `ThirdPartyEnvironment` to determine live/test mode.
        Falls back to default sandbox if no active record is found.
        """

        # Fetch active Paystack environment from DB
        provider = "paystack"
        environment = "live"

        if provider == "paystack":
            log.info(f"Active Paystack environment from DB: {environment}")
            if environment.lower() == "live":
                log.info("Using LIVE Paystack environment.")
                secret_key = settings.LIVE_PAYSTACK_SECRET_KEY
            else:
                log.info("Using SANDBOX Paystack environment.")
                secret_key = settings.TEST_PAYSTACK_SECRET_KEY
        else:
            log.warning("No active Paystack environment found in DB. Defaulting to TEST.")
            secret_key = settings.TEST_PAYSTACK_SECRET_KEY

        return {
            "URL": settings.PAYSTACK_BASE_URL,
            "PAYSTACK_SECRET_KEY": secret_key,
        }
    
class ServiceProviders:

    def get_email_provider():
        """
        Factory function that returns an email provider instance
        based on the configured settings.SMS_PROVIDER.
        """
        # sms_provider = getattr(settings, "SMS_PROVIDER", "termii").lower()
        email_provider = "mailgun"
        if email_provider == "mailgun":
            return MailgunGateway()
        # elif sms_provider == "twilio":
        #     return TwilioSMSService(
        #         account_sid=settings.TWILIO_ACCOUNT_SID,
        #         auth_token=settings.TWILIO_AUTH_TOKEN,
        #         from_number=settings.TWILIO_PHONE_NUMBER,
        #     )
        else:
            raise ValueError(f"Unsupported email provider: {email_provider}")



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