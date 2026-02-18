
from django.core.exceptions import ValidationError


class WalletWithdrawalError(ValidationError):
    def __init__(self, message):
        # Pass message as a string, not a list
        super().__init__(message, code="wallet_withdrawal")