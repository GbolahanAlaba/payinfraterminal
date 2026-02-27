"""
Accounts Admin Package
Registers all admin interfaces for the Accounts app
"""

from .user import UserAdmin
from .profile import ProfileInline
from .account import AccountTypeAdmin
from .otp import OTPAdmin

__all__ = [
    'UserAdmin',
    'ProfileInline',
    'AccountTypeAdmin',
    'OTPAdmin',
]