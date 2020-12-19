from rest_framework.response import Response

from .repositories import UserRepoFactory
from .serializers import UserSerializer, RegistrationUserSerializer
from .use_cases import CreateWalletInteractor, RegisterInteractor
from ..payments.repositories import WalletIRepoFactory


class RegistrationView:
    def post(self, request_data, *args, **kwargs):
        serializer = RegistrationUserSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        user_interactor = RegisterInteractor(repo=UserRepoFactory.get())
        user_interactor.set_params(serializer.validated_data)
        user_interactor.execute()
        user = user_interactor.get_execution_result()

        wallet_interactor = CreateWalletInteractor(repo=WalletIRepoFactory.get())
        wallet_interactor.set_params(user)
        wallet_interactor.execute()

        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "User Created Successfully.  Now perform Login to get your token",
            }
        )
