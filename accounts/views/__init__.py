"""
Accounts Views Package
All views for the Accounts service
"""

from .register import RegisterView
from .login import LoginView
from .verify_otp import VerifyOTPView
from .forgot_password import ForgotPasswordView
from .reset_password import ResetPasswordView
from .user import UserDetailView, UpdateProfileAPIView

__all__ = [
    "RegisterView",
    "LoginView",
    "VerifyOTPView",
    "ForgotPasswordView",
    "ResetPasswordView",
    "UserDetailView",
    "UpdateProfileAPIView",
]