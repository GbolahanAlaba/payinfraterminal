# modules/payments/nomba/client.py

from modules.payments.nomba.bills import Bills
from modules.payments.nomba.transfers import Transfers
from modules.payments.nomba.transactions import Transactions


class NombaClient:
    """
    Main Nomba Client - Paystack-style aggregator
    """

    def __init__(self):
        self.bills = Bills()
        self.transfers = Transfers()
        self.transactions = Transactions()