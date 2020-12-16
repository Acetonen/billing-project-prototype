from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, generics
from rest_framework.response import Response

from . import serializers
from .serializers import UserSerializer
from .use_cases import CreateWalletInteractor

UserModel = get_user_model()


class RegistrationView(generics.CreateAPIView):
    serializer_class = serializers.RegistrationUserSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(responses={200: UserSerializer})  # noqa
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        CreateWalletInteractor().set_params(user).execute()

        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": "User Created Successfully.  Now perform Login to get your token",
            }
        )
