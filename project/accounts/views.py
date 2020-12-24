from rest_framework.response import Response

from .repositories import UserRepoFactory, UserRepo
from .serializers import UserSerializer, RegistrationUserSerializer
from .use_cases import CreateWalletInteractor, RegisterInteractor
from ..payments.repositories import WalletIRepoFactory, WalletRepo


class RegistrationView:
    async def post(self, request_data, *args, **kwargs):
        serializer = RegistrationUserSerializer(data=request_data)
        await serializer.is_valid(raise_exception=True)

        user_interactor = RegisterInteractor(repo=UserRepo)
        user_interactor.set_params(serializer.validated_data)
        await user_interactor.execute()
        user = user_interactor.get_execution_result()

        wallet_interactor = CreateWalletInteractor(repo=WalletRepo)
        wallet_interactor.set_params(user)
        await wallet_interactor.execute()

        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "User Created Successfully.  Now perform Login to get your token",
            }
        )
