from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, generics

from .serializers import UserSerializer, RegistrationUserSerializer
from .views import RegistrationView
from ..core.async_tools import AsyncMixin


class RegistrationViewWrapper(AsyncMixin, generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationUserSerializer

    @swagger_auto_schema(responses={200: UserSerializer})  # noqa
    async def post(self, request, *args, **kwargs):
        return await RegistrationView().post(request.data, *args, **kwargs)
