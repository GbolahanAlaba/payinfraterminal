import logging

from modules.services.payment_services import PaymentService
from api.models import ClientProvider, ClientProviderCredential


log = logging.getLogger(__name__)

# class PaymentRouteEngine:

#     def route_payment(
#         self,
#         *,
#         provider: str,
#         amount,
#         email: str,
#         reference: str | None = None,
#         secret_key: str,
#         callback_url: str,
#     ):

#         service = PaymentService(
#             provider_name=provider,
#             secret_key=secret_key,
#             callback_url=callback_url,
#         )

#         return service.initialize_payment(
#             amount=amount,
#             email=email,
#             reference=reference,
#         )
class PaymentRouteEngine:
    def __init__(self, client):
        self.client = client

    def route_payment(
        self,
        *,
        provider: str,
        amount,
        email: str,
        reference: str | None = None,
        secret_key: str,
        callback_url: str,
    ):
        service = PaymentService(
            provider_name=provider,
            secret_key=secret_key,
            callback_url=callback_url,
        )
        return service.initialize_payment(
            amount=amount,
            email=email,
            reference=reference,
        )
    
    def get_provider_credentials(self, provider_name: str):
        try:
            client_provider = ClientProvider.objects.get(
                client=self.client,
                provider=provider_name,
                is_active=True
            )
            log.info(f"Found provider config for {provider_name} and client {self.client.merchant.business_name}")
        except ClientProvider.DoesNotExist:
            raise ValueError(f"Provider '{provider_name}' is not configured for this merchant.")

        try:
            merchant_credentials = client_provider.credentials
            if merchant_credentials.is_encrypted:
                credentials = merchant_credentials.decrypt_credentials()
                credential = credentials.get("secret_key") # To be used for paystack and flutterwave. Adjust if you have different keys for different providers
            else:
                credentials = merchant_credentials.credentials
                credential = credentials.get("secret_key") # To be used for paystack and flutterwave. Adjust if you have different keys for different providers

            return credential
        except ClientProviderCredential.DoesNotExist:
            raise ValueError(f"No credentials found for provider '{provider_name}'.")
        


class PaymentSwitchEngine:

    def route_payment(self, providers: list, amount: float, email: str, merchant_keys: dict):

        for provider in providers:
            try:
                payment_provider = PaymentService(
                    provider=provider,
                    secret_key=merchant_keys.get(provider)
                )

                response = payment_provider.initialize_payment({
                    "amount": amount,
                    "email": email
                })

                if response.get("status") == "success":
                    return response

            except Exception:
                continue

        return {
            "status": "failed",
            "message": "All providers failed"
        }