"""
Merchants Admin Package
Registers all admin interfaces for the Merchants app
"""

from .merchant import MerchantInline, MerchantAdmin
from .account_key import MerchantAccountKeyAdmin, MerchantAccountKeyInline
from .api_key import MerchantAPIKeyAdmin, MerchantAPIKeyInline
from .kyc_document import KYCDocumentAdmin, KYCDocumentInline

__all__ = [
    "MerchantInline",
    "MerchantAdmin",
    "MerchantAccountKeyAdmin",
    "MerchantAccountKeyInline",
    "MerchantAPIKeyAdmin",
    "MerchantAPIKeyInline",
    "KYCDocumentAdmin",
    "KYCDocumentInline",
]