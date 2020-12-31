from typing import Dict

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, permissions
from rest_framework import response as drf_response
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
from .views import BalanceView, TransactionsView, TransactionCleanedData
from ..accounts.repositories import UserRepo
from ..core.async_tools import AsyncMixin

UserModel = get_user_model()


class BalanceViewWrapper(AsyncMixin, APIView):
    permission_classes = (RelatedUserOnly,)
    serializer_class = WalletSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Wallet data", schema=WalletSerializer)
        }
    )
    async def get(self, request):
        response_data = await BalanceView().get(request.user.id)
        serializer = self.serializer_class(response_data)

        return drf_response.Response(serializer.data)


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

    # Support methods
    # ----------------------------------------------------------------------------------------
    async def _get_sender_and_receiver_for_transaction(
        self, request_data: Dict, request_user_id: int, is_transfer: bool = False
    ) -> TransactionCleanedData:
        """"""
        sender = await UserRepo.async_get(id=request_user_id)
        serializer = TransactionCreateSerializer(
            data=request_data, request_user_email=sender.email, is_transfer=is_transfer
        )
        await serializer.is_valid(raise_exception=True)
        receiver = await UserRepo.async_get(
            email=serializer.validated_data["user_email"]
        )

        return TransactionCleanedData(sender, receiver, serializer.validated_data)

    async def _get_invoice_data(self, request) -> Dict:
        sender = await UserRepo.async_get(id=request.user.id)

        serializer = InvoicePaySerializer(
            data=request.data, sender_wallet_id=sender.wallet.id
        )
        await serializer.is_valid(raise_exception=True)

        return serializer.validated_data

    # Actions
    # ----------------------------------------------------------------------------------------
    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={
            200: openapi.Response(
                description="Transaction data", schema=TransactionSerializer
            )
        },
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Create invoice to another user",
        url_path="create-invoice",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def create_invoice(self, request):
        cleaned_data = await self._get_sender_and_receiver_for_transaction(
            request.data, request.user.id
        )
        response_data = await TransactionsView().create_invoice(cleaned_data)

        return drf_response.Response(TransactionSerializer(response_data).data)

    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={
            200: openapi.Response(description="Wallet data", schema=WalletSerializer)
        },
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Make a deposits",
        url_path="make-deposits",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def make_deposits(self, request):
        cleaned_data = await self._get_sender_and_receiver_for_transaction(
            request.data, request.user.id
        )
        response_data = await TransactionsView().make_deposits(cleaned_data)
        if "details" not in response_data:
            # Return wallet balance if user make deposits for himself:
            response_data = WalletSerializer(response_data).data

        return drf_response.Response(response_data)

    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={
            200: openapi.Response(description="Wallet data", schema=WalletSerializer)
        },
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Transfer to another user",
        url_path="make-transfer",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def transfer_to_another_user(self, request):
        cleaned_data = await self._get_sender_and_receiver_for_transaction(
            request.data, request.user.id, is_transfer=True
        )

        return await self._transfer_to_another_user(request, cleaned_data)

    @sync_to_async
    def _transfer_to_another_user(self, request, cleaned_data):
        with transaction.atomic():
            # We can only use sync request with transaction.atomic, so use async_to_sync
            response_data = async_to_sync(TransactionsView().transfer_to_another_user)(
                cleaned_data
            )

            return drf_response.Response(WalletSerializer(response_data).data)

    @swagger_auto_schema(
        methods=["post"],
        request_body=InvoicePaySerializer,
        responses={
            200: openapi.Response(description="Wallet data", schema=WalletSerializer)
        },
    )
    @action(
        detail=False,
        methods=["post"],  # noqa
        name="Pay for invoice",
        url_path="pay-invoice",
        permission_classes=[permissions.IsAuthenticated],
    )
    async def pay_invoice(self, request):
        cleaned_invoice_data = await self._get_invoice_data(request)

        return await self._pay_invoice(request, cleaned_invoice_data)

    @sync_to_async
    def _pay_invoice(self, request, cleaned_invoice_data):
        with transaction.atomic():
            # We can only use sync request with transaction.atomic, so use async_to_sync
            response_data = async_to_sync(TransactionsView().pay_invoice)(
                cleaned_invoice_data
            )
            return drf_response.Response(WalletSerializer(response_data).data)
