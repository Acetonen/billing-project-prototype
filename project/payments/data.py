from datetime import datetime
from decimal import Decimal
from uuid import UUID

from django.contrib.auth import get_user_model

from project.core.data import BaseData

UserModel = get_user_model()


class WalletData(BaseData):
    balance: Decimal
    currency: str

    class Config:
        orm_mode = True


class TransactionData(BaseData):
    uuid: UUID
    sender: WalletData
    receiver: WalletData
    sum: Decimal
    done_time: datetime = None
    is_done: bool

    class Config:
        orm_mode = True
