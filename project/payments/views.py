from typing import Dict, Tuple

from rest_framework.response import Response

from .repositories import (
    WalletRepo,
    TransactionRepo,
)
from .serializers import (
    WalletSerializer,
    TransactionSerializer,
    TransactionCreateSerializer,
    InvoicePaySerializer,
)
from .use_cases import (
    CreateTransactionInteractor,
    UpdateTransactionInteractor,
    CreateInvoiceInteractor,
    UpdateWalletBalanceInteractor,
    MakeTransferInteractor,
)
from ..accounts.data import UserData
from ..accounts.repositories import UserRepo
from ..accounts.use_cases import get_user_with_wallet


class BalanceView:
    def get(self, request_user_id: int):
        wallet = WalletRepo.get(user_id=request_user_id)
        serializer = WalletSerializer(wallet)

        return Response(serializer.data)


class TransactionsView:
    def _get_sender_and_receiver_for_transaction(
        self, request_data: Dict, request_user_id: int, is_transfer: bool = False
    ) -> Tuple[UserData, UserData, Dict]:
        sender = get_user_with_wallet(repo=UserRepo, id=request_user_id)
        serializer = TransactionCreateSerializer(
            data=request_data, request_user_email=sender.email, is_transfer=is_transfer
        )
        serializer.is_valid(raise_exception=True)
        receiver = get_user_with_wallet(
            repo=UserRepo, email=serializer.validated_data["user_email"]
        )

        return sender, receiver, serializer.validated_data

    def create_invoice(self, request_data: Dict, request_user_id: int) -> Response:
        (
            sender,
            receiver,
            validated_data,
        ) = self._get_sender_and_receiver_for_transaction(request_data, request_user_id)

        invoice_interactor = CreateInvoiceInteractor(repo=TransactionRepo)
        invoice_interactor.set_params(
            sender.wallet, receiver.wallet, validated_data["sum"], True
        )
        invoice_interactor.execute()
        transaction_obj = invoice_interactor.get_execution_result()

        return Response(TransactionSerializer(transaction_obj).data)

    def make_deposits(self, request_data: Dict, request_user_id: int) -> Response:
        (
            sender,
            receiver,
            validated_data,
        ) = self._get_sender_and_receiver_for_transaction(request_data, request_user_id)

        update_interactor = UpdateWalletBalanceInteractor(repo=WalletRepo)
        update_interactor.set_params(receiver.wallet, validated_data["sum"])
        update_interactor.execute()
        wallet = update_interactor.get_execution_result()

        transaction_interactor = CreateTransactionInteractor(repo=TransactionRepo)
        transaction_interactor.set_params(
            sender.wallet, receiver.wallet, validated_data["sum"], False
        )
        transaction_interactor.execute()

        if sender == receiver:
            # Return wallet balance if user make deposits for himself:
            return Response(WalletSerializer(wallet).data)
        else:
            # Return confirmation if user make deposits for another user:
            return Response({"details": "success"})

    def transfer_to_another_user(
        self, request_data: Dict, request_user_id: int
    ) -> Response:
        (
            sender,
            receiver,
            validated_data,
        ) = self._get_sender_and_receiver_for_transaction(
            request_data, request_user_id, is_transfer=True
        )

        transfer_interactor = MakeTransferInteractor(repo=WalletRepo)
        transfer_interactor.set_params(
            sender.wallet.id, receiver.wallet.id, validated_data["sum"]
        )
        transfer_interactor.execute()
        sender_wallet = transfer_interactor.get_execution_result()

        transaction_interactor = CreateTransactionInteractor(repo=TransactionRepo)
        transaction_interactor.set_params(
            sender.wallet, receiver.wallet, validated_data["sum"], False
        )
        transaction_interactor.execute()

        return Response(WalletSerializer(sender_wallet).data)

    def pay_invoice(self, request_data: Dict, request_user_id: id) -> Response:
        sender = get_user_with_wallet(UserRepo, id=request_user_id)
        serializer = InvoicePaySerializer(
            data=request_data, sender_wallet_id=sender.wallet.id
        )
        serializer.is_valid(raise_exception=True)
        transaction_obj = TransactionRepo.get(uuid=serializer.validated_data["uuid"])

        transfer_interactor = MakeTransferInteractor(repo=WalletRepo)
        transfer_interactor.set_params(
            transaction_obj.sender_id,
            transaction_obj.receiver_id,
            transaction_obj.sum,
        )
        transfer_interactor.execute()
        sender_wallet = transfer_interactor.get_execution_result()

        update_interactor = UpdateTransactionInteractor(repo=TransactionRepo)
        update_interactor.set_params(transaction_obj)
        update_interactor.execute()

        return Response(WalletSerializer(sender_wallet).data)
