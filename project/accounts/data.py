from datetime import datetime

from project.core.data import BaseData
from project.payments.data import WalletData


class UserData(BaseData):
    password: str
    last_login: datetime = None
    is_superuser: bool
    first_name: str
    last_name: str
    email: str
    is_staff: bool
    is_active: bool
    wallet: WalletData = None

    class Config:
        orm_mode = True
