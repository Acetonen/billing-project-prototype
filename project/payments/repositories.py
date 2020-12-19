from project.core.repos import ORMRepo
from project.payments.data import TransactionData, WalletData
from project.payments.models import Transaction, Wallet


class TransactionRepoFactory:
    @staticmethod
    def get():
        return ORMRepo(database_class=Transaction, data_class=TransactionData)


class WalletIRepoFactory:
    @staticmethod
    def get():
        return ORMRepo(database_class=Wallet, data_class=WalletData)


WalletRepo = WalletIRepoFactory().get()
TransactionRepo = TransactionRepoFactory().get()
