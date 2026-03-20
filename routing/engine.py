import logging

from connectors.payments.services.payment_services import PaymentService
from api.models import ClientProvider, ClientProviderCredential


log = logging.getLogger(__name__)

class PaymentRouteEngine:
    def __init__(self, client):
        self.client = client
        self.environment = getattr(client, "environment", "live")

    def route_payment(
        self,
        *,
        provider: str,
        amount,
        currency: str | None,
        email: str,
        reference: str | None = None,
        credentials: str,
        callback_url: str,
    ):
        service = PaymentService(
            provider_name=provider,
            credentials=credentials,
            environment=self.environment,
            callback_url=callback_url,
        )
        return service.initialize_payment(
            amount=amount,
            currency=currency,
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
            client_provider_credentials = client_provider.credentials
            if client_provider_credentials.is_encrypted:
                credentials = client_provider_credentials.decrypt_credentials()
                credential = credentials
            else:
                credentials = client_provider_credentials.credentials
                credential = credentials
                log.info(credential)

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