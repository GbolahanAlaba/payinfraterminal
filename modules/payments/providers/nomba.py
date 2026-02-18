import logging
import uuid
from typing import Any
from modules.payments.providers.base import BaseProvider
from modules.payments.nomba.nomba import NombaClient
from modules.utils.utils import ServiceProvidersEnvironment

log = logging.getLogger("my_logger")


class NombaProvider(BaseProvider):
    """
    Nomba Payment Provider Implementation
    """

    def __init__(self):
        """
        Initializes Nomba provider using environment-based credentials.
        """
        env_details = ServiceProvidersEnvironment.get_nomba_environment_details()

        if not env_details:
            raise ValueError("Nomba environment configuration is missing.")

        super().__init__(api_client=NombaClient())
        self.name = "Nomba"
    # =========================
    # Airtime & Data
    # =========================

    def fetch_data_plans(self, telco: str):
        return self.api_client.bills.fetch_data_plans(telco)

    def buy_data(
        self,
        amount: int,
        phone_number: str,
        network: str,
        reference: str,
        sender_name: str,
    ):
        return self.api_client.bills.buy_data(
            amount=amount,
            phone_number=phone_number,
            network=network,
            reference=reference,
            sender_name=sender_name,
        )

    def buy_airtime(
        self,
        amount: int,
        phone_number: str,
        network: str,
        reference: str,
        sender_name: str,
    ):
        return self.api_client.bills.buy_airtime(
            amount=amount,
            phone_number=phone_number,
            network=network,
            reference=reference,
            sender_name=sender_name,
        )

    # =========================
    # Electricity
    # =========================

    def list_electricity_discos(self):
        return self.api_client.bills.electric_discos()

    def resolve_electricity_customer(
        self,
        disco: str,
        customer_id: str,
    ):
        return self.api_client.bills.electric_lookup(
            disco=disco,
            customer_id=customer_id,
        )

    def buy_electricity(
        self,
        disco: str,
        reference: str,
        payer_name: str,
        amount: int,
        customer_id: str,
        phone_number: str,
        meter_type: str,
    ):
        return self.api_client.bills.buy_electricity(
            disco=disco,
            reference=reference,
            payer_name=payer_name,
            amount=amount,
            customer_id=customer_id,
            phone=phone_number,
            meter_type=meter_type,
        )

    # =========================
    # Cable TV
    # =========================

    def list_cable_packages(self, cable_tv_type: str):
        return self.api_client.bills.cable_packages(cable_tv_type)

    def resolve_cable_customer(
        self,
        customer_id: str,
        cable_tv_type: str,
    ):
        return self.api_client.bills.cable_customer_details(
            customer_id=customer_id,
            cable_tv_type=cable_tv_type,
        )

    def subscribe_cable(
        self,
        cable_tv_type: str,
        reference: str,
        payer_name: str,
        amount: int,
        customer_id: str,
    ):
        return self.api_client.bills.cable_subscription(
            cable_tv_type=cable_tv_type,
            merchant_tx_ref=reference,
            payer_name=payer_name,
            amount=amount,
            customer_id=customer_id,
        )

    # =========================
    # Transfers
    # =========================

    def list_banks(self):
        return self.api_client.transfers.banks()

    def resolve_account(self, account_number: str, bank_code: str) -> dict[str, Any]:
        result = self.api_client.transfers.resolve_account(
            account_number=account_number,
            bank_code=bank_code,
        )

        data = result.get("data", {})
        return {
            "accountName": data.get("accountName"),
            "accountNumber": data.get("accountNumber"),
        }

    def initiate_transfer(
        self,
        amount: int,
        account_number: str,
        account_name: str,
        bank_code: str,
        reference: str | None = None,
        sender_name: str | None = None,
        narration: str | None = None,
    ):
        """
        Initiate bank transfer via Nomba.
        Amount is in NAIRA.
        """

        reference = reference or f"NOMBA-{uuid.uuid4().hex[:12]}"
        sender_name = sender_name or "iGospel"
        narration = narration or "Withdrawal"

        return self.api_client.transfers.transfer(
            amount=int(amount),
            account_number=account_number,
            account_name=account_name,
            bank_code=bank_code,
            reference=reference,
            sender_name=sender_name,
            narration=narration,
        )

    # =========================
    # Transactions
    # =========================

    def verify_transaction(self, reference: str):
        return self.api_client.transactions.fetch(reference)

    def verify_electricity_transaction(self, reference: str):
        return self.api_client.transactions.fetch_disco(reference)
