from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model

from project.core.repos import BaseData

UserModel = get_user_model()


@dataclass
class TransactionData(BaseData):
    id: int
    uuid: str
    sender_id: int
    receiver_id: int
    sum: Decimal  # noqa
    done_time: datetime
    is_done: bool


@dataclass
class WalletData(BaseData):
    id: int
    uuid: UserModel
    balance: Decimal
    currency: str
