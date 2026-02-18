# modules/transactions/services/wallet_withdrawal.py

from decimal import Decimal
from django.db import transaction
from django.contrib.auth.hashers import check_password
from requests.exceptions import HTTPError
from django.core.exceptions import ValidationError
from account.models import Profile
from wallet.models import Wallet, CurrencyWallet, WalletTransaction
from modules.utils.exceptions import WalletWithdrawalError
from modules.utils.utils import TransUtils

class WithdrawalService:
    """
    Handles wallet withdrawal business logic
    """

    def __init__(self, user, provider, currency_code="NGN"):
        self.user = user
        self.provider = provider
        self.currency_code = currency_code

    def _get_currency_wallet(self) -> CurrencyWallet:
        try:
            wallet = Wallet.objects.select_related("user").get(user=self.user)
        except Wallet.DoesNotExist:
            raise ValidationError("Wallet not found")

        if not wallet.is_active:
            raise ValidationError("Wallet is inactive")

        try:
            return CurrencyWallet.objects.select_for_update().get(
                wallet=wallet,
                currency__code=self.currency_code,
            )
        except CurrencyWallet.DoesNotExist:
            raise ValidationError(f"{self.currency_code} wallet not found")
        
    def _validate_transaction_pin(self, pin: str):
        if not pin:
            raise WalletWithdrawalError("Pin is required")

        try:
            profile = self.user.profile
        except Profile.DoesNotExist:
            raise WalletWithdrawalError("Profile doesn't exist")

        if not profile.pin:
            raise WalletWithdrawalError("No pin set")

        if not check_password(pin, profile.pin):
            raise WalletWithdrawalError("Incorrect transaction pin")

    @transaction.atomic
    def withdraw(
        self,
        amount,
        account_number: str,
        account_name: str,
        bank_code: str,
        pin: str = None,
        **kwargs,
    ):
        """
        Withdraw funds from wallet and initiate transfer.
        Always return a generic 'Service unavailable' on failure.
        """

        self._validate_transaction_pin(pin)


        amount = Decimal(amount)

        if amount <= 0:
            raise WalletWithdrawalError("Service unavailable")  # generic

        currency_wallet = self._get_currency_wallet()

        if currency_wallet.balance < amount:
            raise WalletWithdrawalError("Service unavailable")  # generic

        # Deduct first
        total_fee = amount + 100
        currency_wallet.balance -= total_fee
        currency_wallet.save(update_fields=["balance"])

        try:
            transfer_response = self.provider.initiate_transfer(
                amount=int(amount),
                account_number=account_number,
                account_name=account_name,
                bank_code=bank_code,
                **kwargs,
            )

            # If provider explicitly fails
            if isinstance(transfer_response, dict) and transfer_response.get("status") is False:
                raise WalletWithdrawalError("Service unavailable")

            reference = TransUtils.generate_payment_reference(currency_wallet.wallet.user.profile.profile_id)
            WalletTransaction.transaction_data(
                creator_currency_wallet=currency_wallet,
                donation_amount=Decimal(amount),
                description=f"Transaction fee",
                source="withdrawal",
                reference=reference,
                status="successful"
            )
        except Exception:
            # Rollback wallet on **any error**
            currency_wallet.balance += total_fee
            currency_wallet.save(update_fields=["balance"])

            raise WalletWithdrawalError("Service unavailable")

        return {
            "wallet_balance": currency_wallet.balance,
            "provider_response": transfer_response,
        }