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

UserModel = get_user_model()


class BalanceViewWrapper(APIView):
    permission_classes = (RelatedUserOnly,)
    serializer_class = WalletSerializer

    @swagger_auto_schema(responses={200: WalletSerializer})  # noqa
    def get(self, request):
        return BalanceView().get(request.user.id)


class TransactionsViewSetWrapper(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
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
        methods=["post"],
        name="Create invoice to another user",
        url_path="create-invoice",
        permission_classes=[permissions.IsAuthenticated],
    )  # noqa
    def create_invoice(self, request):
        return TransactionsView().create_invoice(request.data, request.user.id)

    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={200: WalletSerializer},  # noqa
    )
    @action(
        detail=False,
        methods=["post"],
        name="Make a deposits",
        url_path="make-deposits",
        permission_classes=[permissions.IsAuthenticated],
    )  # noqa
    def make_deposits(self, request):
        return TransactionsView().make_deposits(request.data, request.user.id)

    @swagger_auto_schema(
        methods=["post"],
        request_body=TransactionCreateSerializer,
        responses={200: WalletSerializer},  # noqa
    )
    @action(
        detail=False,
        methods=["post"],
        name="Transfer to another user",
        url_path="make-transfer",
        permission_classes=[permissions.IsAuthenticated],
    )  # noqa
    def transfer_to_another_user(self, request):
        with transaction.atomic():
            return TransactionsView().transfer_to_another_user(
                request.data, request.user.id
            )

    @swagger_auto_schema(
        methods=["post"],
        request_body=InvoicePaySerializer,
        responses={200: WalletSerializer},  # noqa
    )
    @action(
        detail=False,
        methods=["post"],
        name="Pay for invoice",
        url_path="pay-invoice",
        permission_classes=[permissions.IsAuthenticated],
    )  # noqa
    def pay_invoice(self, request):
        with transaction.atomic():
            return TransactionsView().pay_invoice(request.data, request.user.id)
