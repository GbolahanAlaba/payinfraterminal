# modules/payments/nomba/bills.py

from payments.nomba.base import NombaBase


class Bills(NombaBase):

    def fetch_data_plans(self, telco: str):
        return self.get(f"/bill/data-plan/{telco}")

    def buy_data(self, amount, phone_number, network, reference, sender_name):
        payload = {
            "amount": amount,
            "phoneNumber": phone_number,
            "network": network,
            "merchantTxRef": reference,
            "senderName": sender_name,
        }
        return self.post("/bill/data", json=payload)

    def buy_airtime(self, amount, phone_number, network, reference, sender_name):
        payload = {
            "amount": amount,
            "phoneNumber": phone_number,
            "network": network,
            "merchantTxRef": reference,
            "senderName": sender_name,
        }
        return self.post("/bill/topup", json=payload)

    def electric_discos(self):
        return self.get("/bill/electricity/discos")

    def electric_lookup(self, disco, customer_id):
        return self.get(
            "/bill/electricity/lookup",
            params={"disco": disco, "customerId": customer_id},
        )

    def buy_electricity(
        self, disco, reference, payer_name, amount, customer_id, phone, meter_type
    ):
        payload = {
            "disco": disco,
            "merchantTxRef": reference,
            "payerName": payer_name,
            "amount": amount,
            "customerId": customer_id,
            "phoneNumber": phone,
            "meterType": meter_type,
        }
        return self.post("/bill/electricity", json=payload)
