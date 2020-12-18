from project.core.repos import BaseORMRepo
from project.payments.models import Transaction
from project.payments.data import TransactionData


class TransactionORMRepo(BaseORMRepo):
    data_class = TransactionData
    orm_class = Transaction
