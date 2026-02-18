# modules/payments/nomba/transactions.py

from modules.payments.nomba.base import NombaBase


class Transactions(NombaBase):

    def fetch(self, merchant_tx_ref: str):
        response = self.get(
            "/transactions/accounts/single",
            params={"merchantTxRef": merchant_tx_ref},
        )
        data = response.get("data")
        return {"status": data.get("status")} if data else {"status": "failed"}

    def fetch_disco(self, merchant_tx_ref: str):
        response = self.fetch(merchant_tx_ref)
        response["token"] = response.get("phcnVendToken")
        return response
