import logging
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from support.models import Notification
from modules.interfaces.notification import BaseNotification
from modules.utils.utils import util


logger = logging.getLogger(__name__)


class NotificationService(BaseNotification):
    """
    Concrete implementation of BaseNotificationService.
    """

    def __init__(self, sms_provider=None, email_provider=None):
        # If no provider passed in, use the default from factory
        from modules.utils.utils import ServiceProviders
        # self.sms_provider = sms_provider or ServiceProviders.get_sms_provider()
        self.email_provider = email_provider or ServiceProviders.get_email_provider()

    def send_email(self, data: dict) -> bool:
        """
        Send an email using util.send_email (Mailgun + template support).
        Expects data dict with:
            - email_subject
            - to_email
            - email_body
            - attachments (optional)
        """
        try:
            subject = data["email_subject"]
            to_email = data["to_email"]
            email_body = data["email_body"]
            attachments = data.get("attachments")

            # Pass email_body into the template context
            context = {
                "email_subject": subject,
                "email_body": email_body,
            }

            # Call your util function
            util.send_email(
                email_provider=self.email_provider,
                subject=subject,
                to_email=to_email,
                template="emails/generic_email.html",
                context=context,
                attachments=attachments,
                text=None,  # util will generate plain text from template automatically
            )

            logger.info("Email sent successfully to: %s", to_email)
            return True

        except Exception as e:
            logger.error("Failed to send email to %s: %s", data.get("to_email"), str(e))
            return False


    def send_sms(self, to: str, message: str) -> bool:
        try:
            sender_id = getattr(self.sms_provider, "sender_id", None)
            channel = getattr(self.sms_provider, "channel", None)
            logger.info(f"Sending SMS to {to} via {self.sms_provider.__class__.__name__}") 
            response = self.sms_provider.send_sms(
                to=to,
                sender_id=sender_id,
                message=message,
                channel=channel
            )

            if response.get("code") == "ok" or response.get("status") == "success":
                logger.debug(f"SMS sent successfully to {to}")
                return True
            else:
                logger.error(f"Failed to send SMS to {to}: {response}")
                return False

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False

    def send_inapp(self, user, title: str, message: str) -> bool:
        try:
            logger.info(message)
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                read=False,
                date_created=timezone.now(),
            )
            logger.info(f"In-app notification created for {user}")
            return True
        except Exception as e:
            logger.error(f"Error creating in-app notification: {e}")
            return False

    def send_push(self, device_token: str, title: str, body: str) -> bool:
        try:
            # TODO: Add FCM / OneSignal integration
            logger.info(f"Push notification sent to {device_token}")
            return True
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False

    def send(self, channels: list, **kwargs) -> dict:
        results = {}
        for channel in channels:
            if channel == "email":
                results["email"] = self.send_email(kwargs.get("email_data"))
            elif channel == "sms":
                results["sms"] = self.send_sms(kwargs.get("to"), kwargs.get("message"))
            elif channel == "inapp":
                results["inapp"] = self.send_inapp(
                    kwargs.get("user"), kwargs.get("title"), kwargs.get("inapp_message")
                )
            elif channel == "push":
                results["push"] = self.send_push(
                    kwargs.get("device_token"), kwargs.get("title"), kwargs.get("inapp_message")
                )
        return results
