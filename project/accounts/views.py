from typing import Dict

from .data import UserData
from .repositories import UserRepo
from .use_cases import CreateWalletInteractor, RegisterInteractor
from ..payments.repositories import WalletRepo


class RegistrationView:
    async def post(self, validated_data: Dict, *args, **kwargs) -> UserData:
        user_interactor = RegisterInteractor(repo=UserRepo)
        user_interactor.set_params(validated_data)
        await user_interactor.execute()
        user = user_interactor.get_execution_result()

        wallet_interactor = CreateWalletInteractor(repo=WalletRepo)
        wallet_interactor.set_params(user)
        await wallet_interactor.execute()

        return user
