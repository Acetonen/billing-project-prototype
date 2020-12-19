from dataclasses import dataclass
from datetime import datetime
from typing import List

from project.core.abstract_data_types import AbstractData
from project.payments.data import WalletData


@dataclass(init=False)
class UserData(AbstractData):
    __slots__ = (
        "id",
        "password",
        "last_login",
        "is_superuser",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "groups",
        "user_permissions",
    )
    id: int
    password: str
    last_login: datetime
    is_superuser: bool
    first_name: str
    last_name: str
    email: str
    is_staff: bool
    is_active: bool
    groups: List
    user_permissions: List
    wallet: WalletData = None
