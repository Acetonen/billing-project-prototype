from asgiref.sync import sync_to_async, async_to_sync
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, generics
from rest_framework import response as drf_response

from .serializers import UserSerializer, RegistrationUserSerializer
from .views import RegistrationView
from ..core.async_tools import AsyncMixin


class RegistrationViewWrapper(AsyncMixin, generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationUserSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Registration data", schema=UserSerializer
            )
        }
    )
    async def post(self, request, *args, **kwargs):
        return await self._post(request, *args, **kwargs)

    @sync_to_async
    def _post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        async_to_sync(serializer.is_valid)(raise_exception=True)

        with transaction.atomic():
            # We can only use sync request with transaction.atomic, so use async_to_sync
            data_to_response = async_to_sync(RegistrationView().post)(
                serializer.validated_data, *args, **kwargs
            )

        return drf_response.Response(
            {
                "user": UserSerializer(data_to_response).data,
                "message": "User Created Successfully.  Now perform Login to get your token",
            }
        )
