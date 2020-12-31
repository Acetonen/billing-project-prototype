from django.contrib.auth.hashers import make_password

from project.accounts.data import UserData
from project.core.abstract_data_types import AbstractUseCase
from project.payments.data import WalletData


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
