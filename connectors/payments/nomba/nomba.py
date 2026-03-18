# modules/payments/nomba/client.py

from connectors.payments.nomba.bills import Bills
from connectors.payments.nomba.transfers import Transfers
from connectors.payments.nomba.transactions import Transactions


class NombaClient:
    """
    Main Nomba Client - Paystack-style aggregator
    """

    def __init__(self):
        self.bills = Bills()
        self.transfers = Transfers()
        self.transactions = Transactions()