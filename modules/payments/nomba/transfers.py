# modules/payments/nomba/transfers.py

from modules.payments.nomba.base import NombaBase


class Transfers(NombaBase):

    def banks(self):
        return self.get("/transfers/banks")

    def resolve_account(self, account_number, bank_code):
        payload = {
            "accountNumber": account_number,
            "bankCode": bank_code,
        }
        return self.post("/transfers/bank/lookup", json=payload)

    def transfer(
        self,
        amount,
        account_number,
        account_name,
        bank_code,
        reference,
        sender_name,
        narration,
    ):
        payload = {
            "amount": amount,
            "accountNumber": account_number,
            "accountName": account_name,
            "bankCode": bank_code,
            "merchantTxRef": reference,
            "senderName": sender_name,
            "narration": narration,
        }
        return self.post("/transfers/bank", json=payload)
