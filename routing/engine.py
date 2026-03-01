from modules.services.payment_services import PaymentService


class PaymentRouteEngine:

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
        )

        return service.initialize_payment(
            amount=amount,
            email=email,
            reference=reference,
        )
        


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