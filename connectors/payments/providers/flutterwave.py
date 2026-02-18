import logging
from typing import Any, Dict, Optional
from decimal import Decimal
import uuid

from django.conf import settings
from payments.providers.base import BasePaymentProvider
from payments.flutterwave import FlutterwaveClient
from payments.flutterwave.exceptions import FlutterwaveAPIException

# Set up logging
logger = logging.getLogger(__name__)

class FlutterwaveProvider(BasePaymentProvider):
    """
    Flutterwave Payment Provider Implementation.
    """

    def __init__(self):
        """
        Initialize Flutterwave provider using settings.
        """
        flutterwave_settings = settings.PAYMENT_PROVIDER.get("FLUTTERWAVE", {})

        secret_key = flutterwave_settings.get("secret_key")
        self.callback_url = flutterwave_settings.get("callback_url")
        self.webhook_secret = flutterwave_settings.get("webhook_secret")
        
        # Determine if we're in sandbox mode
        self.is_sandbox = secret_key and secret_key.startswith("FLWSECK_TEST")

        if not secret_key:
            logger.error("Flutterwave secret key is missing in settings.")
            raise ValueError("Flutterwave secret key is missing in settings.")

        # Initialize API client
        super().__init__(api_client=FlutterwaveClient(
            secret_key=secret_key, 
            is_sandbox=self.is_sandbox
        ))

        self.name = "flutterwave"

    def initialize_transaction(
        self, 
        email: str, 
        amount: int, 
        currency: str = "NGN",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Initialize a transaction with Flutterwave.

        Args:
            email: Customer email
            amount: Amount in base currency units (e.g., kobo for NGN)
            currency: Currency code
            **kwargs: Additional parameters

        Returns:
            Transaction initialization response
        """
        try:
            # Convert amount from minor units (kobo) to major units (naira) and ensure two decimal places
            amount_decimal = (Decimal(amount) / 100).quantize(Decimal("0.01"))
            amount_str = format(amount_decimal, "f")

            customer_name = kwargs.get("name", "Anonymous")
            phone_number = kwargs.get("phone_number")
            payment_options = kwargs.get("payment_options")
            subaccounts = kwargs.get("subaccounts")
            payment_plan = kwargs.get("payment_plan")
            customizations = kwargs.get("customizations") or {
                "title": kwargs.get("title") or "Titaar Payment"
            }
            redirect_url = kwargs.get("callback_url") or self.callback_url

            if not redirect_url:
                logger.error("Redirect/callback URL is required for Flutterwave payments.")
                raise ValueError("Redirect/callback URL is required for Flutterwave payments.")

            customer_data = {
                "email": email,
                "name": customer_name,
            }
            if phone_number:
                customer_data["phonenumber"] = phone_number

            reference = kwargs.get("reference", f"TITAA-{uuid.uuid4().hex[:12].upper()}")

            metadata = {
                "order_id": kwargs.get("order_id"),
                "customer_email": email,
                "source": "titaa_backend"
            }
            if kwargs.get("metadata"):
                metadata.update(kwargs["metadata"])

            # Remove None values from metadata
            metadata = {key: value for key, value in metadata.items() if value is not None}

            payment_response = self.api_client.payments.create_payment(
                tx_ref=reference,
                amount=amount_str,
                currency=currency.upper(),
                redirect_url=redirect_url,
                customer=customer_data,
                customizations=customizations,
                meta=metadata or None,
                payment_options=payment_options,
                subaccounts=subaccounts,
                payment_plan=payment_plan,
            )
            
            payment_response.setdefault("data", {})
            payment_response["data"].update({
                "tx_ref": reference,
                "amount": amount_str,
                "currency": currency.upper(),
                "redirect_url": redirect_url
            })

            return payment_response

        except FlutterwaveAPIException as e:
            logger.error(f"FlutterwaveAPIException during transaction initialization: {str(e)}")
            logger.error(f"Exception details - Status Code: {e.status_code}, Error Code: {e.error_code}, Response Data: {e.response_data}")
            return {
                "status": "error",
                "message": str(e),
                "error": {
                    "code": e.error_code,
                    "status_code": e.status_code
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error during transaction initialization: {str(e)}", exc_info=True)
            return {
                "status": "error", 
                "message": f"Unexpected error: {str(e)}"
            }

    def verify_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verify a transaction using its ID or reference.

        Args:
            transaction_id: Transaction ID or reference

        Returns:
            Transaction verification response
        """
        try:
            result = self.api_client.payments.verify_payment_by_reference(transaction_id)
            return result

        except FlutterwaveAPIException as e:
            logger.error(f"FlutterwaveAPIException during transaction verification: {str(e)}")
            logger.error(f"Exception details - Status Code: {e.status_code}, Error Code: {e.error_code}, Response Data: {e.response_data}")
            return {
                "status": "error",
                "message": str(e),
                "error": {
                    "code": e.error_code,
                    "status_code": e.status_code
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error during transaction verification: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Verification failed: {str(e)}"
            }

    def clean_init_data(self, init_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and format initialization data for frontend consumption.

        Args:
            init_data: Raw initialization response from Flutterwave

        Returns:
            Cleaned data for frontend
        """
        if init_data.get("status") == "success" and "data" in init_data:
            data = init_data["data"]

            payment_url = data.get("link") or data.get("payment_url")

            if not payment_url:
                logger.warning("Flutterwave initialization successful but no payment link found.")
                return {
                    "error": True,
                    "message": "Payment link not returned by Flutterwave.",
                    "status": "failed"
                }

            cleaned_data = {
                "payment_url": payment_url,
                "access_code": data.get("tx_ref"),
                "reference": data.get("tx_ref"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "status": init_data.get("status")
            }
            return cleaned_data
        else:
            # Return error information
            error_data = {
                "error": True,
                "message": init_data.get("message", "Transaction initialization failed"),
                "status": "failed"
            }
            logger.warning(f"Initialization data cleaning failed - Error Data: {error_data}")
            return error_data

    def process_payment(self, amount: float, currency: str, customer_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a payment request.

        Args:
            amount: Payment amount
            currency: Currency code
            customer_info: Customer information

        Returns:
            Payment processing response
        """
        email = customer_info.get("email") or ""
        result = self.initialize_transaction(
            email=email,
            amount=int(amount * 100),  # Convert to minor units
            currency=currency,
            name=customer_info.get("name"),
            phone_number=customer_info.get("phone")
        )
        return result

    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Refund a payment transaction.

        Args:
            transaction_id: Transaction ID to refund
            amount: Amount to refund (None for full refund)

        Returns:
            Refund response
        """
        # Note: Flutterwave refunds are typically handled through their dashboard
        # or require specific refund endpoints that may not be in the charges API
        # This is a placeholder implementation
        try:
            # In a full implementation, this would call Flutterwave's refund API
            # For now, return a placeholder response
            refund_data = {
                "status": "error",
                "message": "Refunds must be processed through Flutterwave dashboard",
                "data": {
                    "transaction_id": transaction_id,
                    "refund_amount": amount,
                    "refund_method": "dashboard"
                }
            }
            return refund_data
        except Exception as e:
            logger.error(f"Error during refund processing: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Refund failed: {str(e)}"
            }

    def list_banks(self, country: str = "NG") -> Dict[str, Any]:
        """
        List available banks for the given country.

        Args:
            country: Country code (defaults to Nigeria)

        Returns:
            List of available banks
        """
        # Note: This would require a separate banks API endpoint
        # Placeholder implementation
        bank_data = {
            "status": "error",
            "message": "Bank listing not implemented in charges API"
        }
        return bank_data

    def resolve_account(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """
        Resolve account number to get account details.

        Args:
            account_number: Account number to resolve
            bank_code: Bank code

        Returns:
            Account resolution response
        """
        # Note: This would require a separate account resolution endpoint
        # Placeholder implementation
        account_data = {
            "status": "error", 
            "message": "Account resolution not implemented in charges API"
        }
        return account_data
