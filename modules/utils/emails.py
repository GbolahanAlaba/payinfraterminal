from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from accounts.models import User
from modules.services.notification_service import NotificationService



@shared_task
def contact_us_email_autoresponder(message, email, name):
    subject = "Thank you for contacting us — iGospel"
    body = (
        f"Hi {name}! <br><br>"
        "Thank you for reaching out to us through the <b>Contact Us</b> page.<br><br>"
        "We've successfully received your message, and our team is currently reviewing it. "
        "One of our representatives will get back to you as soon as possible.<br><br>"
        f"<b>Message from: {email}</b><br>"
        "<b>Content:</b><br>"
        "<div style='padding:10px; border-left:3px solid #e0e0e0; margin:10px 0;'>"
        f"{message}"
        "</div><br>"
        "If you have any additional information you'd like to share, feel free to reply directly to this email.<br><br>"
        "Thank you for contacting us. We appreciate your time and trust.<br><br>"
        "<b>iGospel Team</b>"
    )

    service = NotificationService()
    service.send(
    channels=["email"],
    email_data={
        "email_subject": subject,
        "email_body": body,
        "to_email": email
        },
    )


@shared_task
def send_verify_email(user, otp):
    subject = "Verify Your Email Address - Welcome to PayInfra Terminal!"

    body = (
        f"Dear {user.first_name or 'Valued Partner'},<br><br>"
        "Welcome to <b>[Your Payment Infra Name]</b> — your infrastructure layer for reliable, "
        "intelligent, and seamless payment orchestration.<br><br>"
        "To complete your registration and activate your account, please verify your email address "
        "using the One-Time Password (OTP) below:<br><br>"
        f"<div style='font-size:22px; font-weight:bold; letter-spacing:3px;'>{otp}</div><br>"
        "This OTP is valid for <b>10 minutes</b>. For security reasons, please do not share this code with anyone.<br><br>"
        "Email verification helps us protect your account and ensures secure access to your dashboard, "
        "transaction monitoring tools, failover configurations, and performance analytics.<br><br>"
        "If you did not initiate this registration, please ignore this email. "
        "Your account will not be activated without verification.<br><br>"
        "We look forward to powering your payment reliability.<br><br>"
        "Best regards,<br>"
        "<b>The [Your Payment Infra Name] Team</b><br>"
        "<i>Resilient Infrastructure for Modern Payments</i>"
    )

    service = NotificationService()
    service.send(
    channels=["email"],
    email_data={
        "email_subject": subject,
        "email_body": body,
        "to_email": user.email
        },
    )


@shared_task
def send_email_verification_confirmation(user):
    subject = "Account Activated - Complete Your KYC Verification"

    body = (
        f"Dear {user.first_name or 'Valued Partner'},<br><br>"
        "Your email has been successfully verified and your "
        "<b>[Your Payment Infra Name] account is now active</b>.<br><br>"
        "To unlock full access to the platform and begin integrating your payment providers, "
        "please log in to your dashboard and proceed with the <b>KYC verification process</b>.<br><br>"
        "KYC verification is required to ensure compliance, secure infrastructure access, "
        "and safe transaction orchestration across connected gateways.<br><br>"
        "Once your verification is completed and approved, you will be able to configure "
        "payment routing, enable failover logic, and monitor transactions in real time.<br><br>"
        "If you need any assistance during verification or integration, our team is available to support you.<br><br>"
        "We look forward to powering your payment reliability.<br><br>"
        "Best regards,<br>"
        "<b>The [Your Payment Infra Name] Team</b><br>"
        "<i>Resilient Infrastructure for Modern Payments</i>"
    )

    service = NotificationService()
    service.send(
    channels=["email"],
    email_data={
        "email_subject": subject,
        "email_body": body,
        "to_email": user.email
        },
    )

@shared_task
def send_otp_email(user, otp, purpose):
    subject = f"Reset Your Account {purpose.capitalize()}"
    body = (
        f"Dear {user.full_name},<br><br>"
        f"We received a request to reset the {purpose.capitalize()} for your <b>iGospel</b> account.<br><br>"
        f"To proceed, please use the One-Time Password (OTP) below to reset your {purpose.capitalize()}:<br><br>"
        f"<div style='font-size:22px; font-weight:bold; letter-spacing:3px;'>{otp}</div><br>"
        "This OTP is valid for <b>10 minutes</b>. For your security, please do not share this code with anyone.<br><br>"
        "If you did not request a password reset, please ignore this email. Your account remains safe "
        "and no changes will be made.<br><br>"
        "If you continue to receive these emails without initiating a request, please contact our support team immediately.<br><br>"
        "May God grant you peace and assurance as you continue your journey with us.<br><br>"
        "With care,<br>"
        "<b>The iGospel Team</b><br>"
        "<i>Spreading the Gospel through digital media</i>"
    )

    service = NotificationService()
    service.send(
    channels=["email"],
    email_data={
        "email_subject": subject,
        "email_body": body,
        "to_email": user.email
        },
    )


@shared_task
def givers_email_autoresponder(email, name):
    giver = name if name else "Generous Supporter"
    giver_email = email if email else settings.DEFAULT_EMAIL
    subject = "Thank You for Supporting iGospel ❤️"
    body = (
        f"Dear {giver},<br><br>"
        "Thank you so much for your generous support of <b>iGospel</b>.<br><br>"
        "We are truly grateful for your giving. Your contribution helps us continue spreading the Gospel, "
        "sharing inspiring messages, and building content that uplifts lives across the world.<br><br>"
        "Every seed you sow enables us to improve our blog, reach more people, and remain consistent in "
        "delivering faith-based content that blesses and encourages believers daily.<br><br>"
        "Please know that your support does not go unnoticed — we deeply appreciate your kindness and "
        "partnership in this mission.<br><br>"
        "May God bless you abundantly for your generosity and reward you openly.<br><br>"
        "With gratitude,<br>"
        "<b>The iGospel Team</b><br>"
        "<i>Spreading the Gospel through digital media</i>"
    )

    service = NotificationService()
    service.send(
    channels=["email"],
    email_data={
        "email_subject": subject,
        "email_body": body,
        "to_email": giver_email
        },
    )



@shared_task
def support_gift_email(user, net_amount):
    subject = "You've Received a Gift on iGospel!"
    body = (
        f"Dear {user.full_name},<br><br>"
        f"You've received a support gift on <b>iGospel</b>!<br><br>"
        f"<b>Amount:</b> ₦{net_amount}<br>"
        "Thank you for sharing your talent and ministry with the world. Every gift helps you continue "
        "to inspire and impact lives.<br><br>"
        "Keep creating and sharing—your audience is listening and supporting you!<br><br>"
        "With gratitude,<br>"
        "<b>The iGospel Team</b><br>"
        "<i>Spreading the Gospel through digital media</i>"
    )

    service = NotificationService()
    service.send(
    channels=["email"],
    email_data={
        "email_subject": subject,
        "email_body": body,
        "to_email": user.email
        },
    )
