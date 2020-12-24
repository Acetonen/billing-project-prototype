from django.contrib.auth.hashers import make_password

from project.accounts.data import UserData
from project.core.abstract_data_types import AbstractUseCase
from project.payments.data import WalletData
from project.payments.repositories import WalletIRepoFactory


class CreateWalletInteractor(AbstractUseCase):
    """
    Create user wallet.
    """

    def set_params(self, user: UserData):
        self.user = user

    async def execute(self):
        obj_id = await self.repo.async_create(user_id=self.user.id)
        self.result_of_execution = await self.repo.async_get(id=obj_id)

    def get_execution_result(self) -> WalletData:
        return super().get_execution_result()


class RegisterInteractor(AbstractUseCase):
    """
    Register User.
    """

    def set_params(self, registration_serializer_data):
        self.registration_serializer_data = registration_serializer_data
        self.registration_serializer_data["is_staff"] = True
        self.registration_serializer_data["password"] = make_password(
            self.registration_serializer_data["password"]
        )

    async def execute(self):
        object_id = await self.repo.async_create(**self.registration_serializer_data)
        self.result_of_execution = await self.repo.async_get(id=object_id)

    def get_execution_result(self) -> UserData:
        return super().get_execution_result()


class GetUserWithWalletInteractor(AbstractUseCase):
    """
    Get User with nested Wallet field.
    """

    def set_params(self, **kwargs):
        self.search_fields = kwargs

    async def execute(self):
        user_data = await self.repo.async_get(**self.search_fields)
        user_data.wallet = (
            await WalletIRepoFactory().get().async_get(user_id=user_data.id)
        )
        self.result_of_execution = user_data

    def get_execution_result(self) -> UserData:
        return super().get_execution_result()


async def get_user_with_wallet(repo, **kwargs) -> UserData:
    user_with_wallet_interactor = GetUserWithWalletInteractor(repo=repo)
    user_with_wallet_interactor.set_params(**kwargs)
    await user_with_wallet_interactor.execute()

    return user_with_wallet_interactor.get_execution_result()
