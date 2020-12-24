from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView

from project.core.permissions import RelatedUserOnly, ReceiverOrSenderOnly
from .models import Transaction
from .pagination import TransactionsPagination
from .serializers import (
    WalletSerializer,
    TransactionSerializer,
    TransactionCreateSerializer,
    InvoicePaySerializer,
)
from .views import BalanceView, TransactionsView
from ..core.async_tools import AsyncMixin

UserModel = get_user_model()


class BalanceViewWrapper(AsyncMixin, APIView):
    permission_classes = (RelatedUserOnly,)
    serializer_class = WalletSerializer

    @swagger_auto_schema(responses={200: WalletSerializer})  # noqa
    async def get(self, request):
        return await BalanceView().get(request.user.id)


class TransactionsViewSetWrapper(
    AsyncMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (ReceiverOrSenderOnly,)
    pagination_class = TransactionsPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["is_done"]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={200: TransactionSerializer},  # noqa
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Create invoice to another user",
        url_path="create-invoice",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def create_invoice(self, request):
        return await TransactionsView().create_invoice(request.data, request.user.id)

    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={200: WalletSerializer},  # noqa
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Make a deposits",
        url_path="make-deposits",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def make_deposits(self, request):
        return await TransactionsView().make_deposits(request.data, request.user.id)

    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={200: WalletSerializer},  # noqa
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Transfer to another user",
        url_path="make-transfer",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def transfer_to_another_user(self, request):
        return await self._transfer_to_another_user(request)

    @sync_to_async
    def _transfer_to_another_user(self, request):
        with transaction.atomic():
            # We can only use sync request with transaction.atomic, so use async_to_sync
            return async_to_sync(TransactionsView().transfer_to_another_user)(
                request.data, request.user.id
            )

    @swagger_auto_schema(
        methods=["post"],
        request_body=InvoicePaySerializer,
        responses={200: WalletSerializer},  # noqa
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Pay for invoice",
        url_path="pay-invoice",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def pay_invoice(self, request):
        return await self._pay_invoice(request)

    @sync_to_async
    def _pay_invoice(self, request):
        with transaction.atomic():
            # We can only use sync request with transaction.atomic, so use async_to_sync
            return async_to_sync(TransactionsView().pay_invoice)(
                request.data, request.user.id
            )