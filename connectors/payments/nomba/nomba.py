# modules/payments/nomba/client.py

from payments.nomba.bills import Bills
from payments.nomba.transfers import Transfers
from payments.nomba.transactions import Transactions


class NombaClient:
    """
    Main Nomba Client - Paystack-style aggregator
    """

    def __init__(self):
        self.bills = Bills()
        self.transfers = Transfers()
        self.transactions = Transactions()