from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
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
from .use_cases import (
    GetWalletInteractor,
    CreateTransactionInteractor,
    UpdateTransactionInteractor,
    CreateInvoiceInteractor,
    UpdateWalletBalanceInteractor,
    MakeTransferInteractor,
)

UserModel = get_user_model()


class BalanceView(APIView):
    permission_classes = (RelatedUserOnly,)
    serializer_class = WalletSerializer

    @swagger_auto_schema(responses={200: WalletSerializer})  # noqa
    def get(self, request):
        wallet_interactor = GetWalletInteractor()
        wallet_interactor.set_params(request.user)
        wallet_interactor.execute()
        wallet = wallet_interactor.get_execution_result()
        serializer = WalletSerializer(wallet)

        return Response(serializer.data)


class TransactionsViewSet(
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
        serializer = TransactionCreateSerializer(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        receiver = UserModel.objects.get(email=serializer.validated_data["user_email"])

        invoice_interactor = CreateInvoiceInteractor()
        invoice_interactor.set_params(
            request.user, receiver, serializer.validated_data["sum"], True
        )
        invoice_interactor.execute()
        transaction_obj = invoice_interactor.get_execution_result()

        return Response(TransactionSerializer(transaction_obj).data)

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
        serializer = TransactionCreateSerializer(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        receiver = UserModel.objects.get(email=serializer.validated_data["user_email"])

        with transaction.atomic():
            update_interactor = UpdateWalletBalanceInteractor()
            update_interactor.set_params(
                receiver.wallet, serializer.validated_data["sum"]
            )
            update_interactor.execute()
            wallet = update_interactor.get_execution_result()

            transaction_interactor = CreateTransactionInteractor()
            transaction_interactor.set_params(
                request.user, receiver, serializer.validated_data["sum"], False
            )
            transaction_interactor.execute()

        if request.user == receiver:
            # Return wallet balance if user make deposits for himself:
            return Response(WalletSerializer(wallet).data)
        else:
            # Return confirmation if user make deposits for another user:
            return Response({"details": "success"})

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
        serializer = TransactionCreateSerializer(
            data=request.data, is_transfer=True, request=request
        )
        serializer.is_valid(raise_exception=True)
        receiver = UserModel.objects.get(email=serializer.validated_data["user_email"])

        with transaction.atomic():
            transfer_interactor = MakeTransferInteractor()
            transfer_interactor.set_params(
                request.user, receiver, serializer.validated_data["sum"]
            )
            transfer_interactor.execute()
            sender_wallet = transfer_interactor.get_execution_result()

            transaction_interactor = CreateTransactionInteractor()
            transaction_interactor.set_params(
                request.user, receiver, serializer.validated_data["sum"], False
            )
            transaction_interactor.execute()

        return Response(WalletSerializer(sender_wallet).data)

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
        serializer = InvoicePaySerializer(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        transaction_obj = Transaction.objects.select_related("sender__user").get(
            uuid=serializer.validated_data["uuid"]
        )

        with transaction.atomic():
            transfer_interactor = MakeTransferInteractor()
            transfer_interactor.set_params(
                transaction_obj.sender.user,
                transaction_obj.receiver.user,
                transaction_obj.sum,
            )
            transfer_interactor.execute()
            sender_wallet = transfer_interactor.get_execution_result()

            update_interactor = UpdateTransactionInteractor()
            update_interactor.set_params(transaction_obj.uuid)
            update_interactor.execute()

        return Response(WalletSerializer(sender_wallet).data)
