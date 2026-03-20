from typing import Any
from connectors.payments.nomba.base import NombaBase
import uuid

class Transactions(NombaBase):

    def __init__(self, client):
        super().__init__(client)

    def initialize_transaction(
        self,
        email: str,
        amount: str,
        currency: str = "NGN",
        reference: str = None,
        callback_url: str = None,
        account_id: str = None,
        allowed_payment_methods: list = None,
        tokenize_card: bool = False,
        **kwargs
    ) -> dict[str, Any]:

        url = "/checkout/order"

        payload = {
            "order": {
                "customerEmail": email,
                "amount": amount,
                "currency": currency.upper(),
                "orderReference": reference or str(uuid.uuid4()),
                "allowedPaymentMethods": allowed_payment_methods or ["Card", "Transfer"],
                **({"callbackUrl": callback_url} if callback_url else {}),
                **({"accountId": account_id} if account_id else {}),
                **kwargs,
            },
            "tokenizeCard": tokenize_card,
        }

        return self.post(url, json=payload)

    def verify_transaction(self, order_reference: str) -> dict[str, Any]:

        url = "/transactions/accounts/single"
        response = self.get(url, params={"orderReference": order_reference})

        data = response.get("data")
        return {"status": data.get("status")} if data else {"status": "failed"}

    def fetch(self, merchant_tx_ref: str):

        url = "/transactions/accounts/single"
        response = self.get(url, params={"merchantTxRef": merchant_tx_ref},)
        data = response.get("data")
        return {"status": data.get("status")} if data else {"status": "failed"}

    def fetch_disco(self, merchant_tx_ref: str):
        response = self.fetch(merchant_tx_ref)
        response["token"] = response.get("phcnVendToken")
        return response
