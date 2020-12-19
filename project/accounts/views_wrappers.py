from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, generics

from .serializers import UserSerializer, RegistrationUserSerializer
from .views import RegistrationView


class RegistrationViewWrapper(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationUserSerializer

    @swagger_auto_schema(responses={200: UserSerializer})  # noqa
    def post(self, request, *args, **kwargs):
        return RegistrationView().post(request.data, *args, **kwargs)
