from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model

from project.core.abstract_data_types import AbstractData

UserModel = get_user_model()


@dataclass(init=False)
class TransactionData(AbstractData):
    __slots__ = (
        "id",
        "uuid",
        "sender_id",
        "receiver_id",
        "sum",
        "done_time",
        "is_done",
    )
    id: int
    uuid: str
    sender_id: int
    receiver_id: int
    sum: Decimal
    done_time: datetime
    is_done: bool


@dataclass(init=False)
class WalletData(AbstractData):
    __slots__ = ("id", "balance", "currency", "user_id")
    id: int
    balance: Decimal
    currency: str
    user_id: int
