# modules/payments/nomba/client.py

from connectors.payments.nomba.bills import Bills
from connectors.payments.nomba.transfers import Transfers
from connectors.payments.nomba.transactions import Transactions


class NombaClient:
    """
    Main Nomba Client - Paystack-style aggregator
    """

    def __init__(self, credentials: dict):
        if not credentials:
            raise ValueError("Credentials required")

        self.credentials = credentials

        # initialize modules
        self.bills = Bills(self)
        self.transfers = Transfers(self)
        self.transactions = Transactions(self)