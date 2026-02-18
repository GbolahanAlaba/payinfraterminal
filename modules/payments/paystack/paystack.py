from modules.payments.paystack.transactions import Transactions
from modules.payments.paystack.misc import Miscellaneous
from modules.payments.paystack.verification import Verification
from modules.payments.paystack.transfer import Transfers
from modules.payments.paystack.subaccounts import Subaccounts


class PaystackClient:
    """
    Main Paystack Client that exposes all API functionalities.
    """

    def __init__(self, secret_key):
        self.transactions = Transactions(secret_key)
        self.miscellaneous = Miscellaneous(secret_key)
        self.verification = Verification(secret_key)
        self.transfer = Transfers(secret_key)
        self.subaccounts = Subaccounts(secret_key)
        
        


if __name__ == "__main__":
    client = PaystackClient("sk_test_14b2d6c00593454cc65e22eeafa03f141d484b54")
    # response = client.transactions.initialize_transaction(
    #     email="test@mail.com", amount="1000000", callback_url="http://localhost:8000/"
    # )
    # print(response)

    response = client.transactions.verify_transaction("sg7iupn2xm")
    print(response)
