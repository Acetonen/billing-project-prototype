from collections import namedtuple
from typing import Dict

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
from ..accounts.repositories import UserRepo
from ..accounts.use_cases import get_user_with_wallet

TransactionCleanedData = namedtuple(
    "TransactionCleanedData", "sender receiver validated_data"
)


class BalanceView:
    async def get(self, request_user_id: int):
        wallet = await WalletRepo.async_get(user_id=request_user_id)
        serializer = WalletSerializer(wallet)

        return Response(serializer.data)


class TransactionsView:
    async def _get_sender_and_receiver_for_transaction(
        self, request_data: Dict, request_user_id: int, is_transfer: bool = False
    ) -> TransactionCleanedData:
        sender = await get_user_with_wallet(repo=UserRepo, id=request_user_id)
        serializer = TransactionCreateSerializer(
            data=request_data, request_user_email=sender.email, is_transfer=is_transfer
        )
        await serializer.is_valid(raise_exception=True)
        receiver = await get_user_with_wallet(
            repo=UserRepo, email=serializer.validated_data["user_email"]
        )

        return TransactionCleanedData(sender, receiver, serializer.validated_data)

    async def create_invoice(
        self, request_data: Dict, request_user_id: int
    ) -> Response:
        cleaned_data = await self._get_sender_and_receiver_for_transaction(
            request_data, request_user_id
        )

        invoice_interactor = CreateInvoiceInteractor(repo=TransactionRepo)
        invoice_interactor.set_params(
            cleaned_data.sender.wallet,
            cleaned_data.receiver.wallet,
            cleaned_data.validated_data["sum"],
            True,
        )
        await invoice_interactor.execute()
        transaction_obj = invoice_interactor.get_execution_result()

        return Response(TransactionSerializer(transaction_obj).data)

    async def make_deposits(self, request_data: Dict, request_user_id: int) -> Response:
        cleaned_data = await self._get_sender_and_receiver_for_transaction(
            request_data, request_user_id
        )

        update_interactor = UpdateWalletBalanceInteractor(repo=WalletRepo)
        update_interactor.set_params(
            cleaned_data.receiver.wallet, cleaned_data.validated_data["sum"]
        )
        await update_interactor.execute()
        wallet = update_interactor.get_execution_result()

        transaction_interactor = CreateTransactionInteractor(repo=TransactionRepo)
        transaction_interactor.set_params(
            cleaned_data.sender.wallet,
            cleaned_data.receiver.wallet,
            cleaned_data.validated_data["sum"],
            False,
        )
        await transaction_interactor.execute()

        if cleaned_data.sender == cleaned_data.receiver:
            # Return wallet balance if user make deposits for himself:
            return Response(WalletSerializer(wallet).data)
        else:
            # Return confirmation if user make deposits for another user:
            return Response({"details": "success"})

    async def transfer_to_another_user(
        self, request_data: Dict, request_user_id: int
    ) -> Response:
        cleaned_data = await self._get_sender_and_receiver_for_transaction(
            request_data, request_user_id, is_transfer=True
        )

        transfer_interactor = MakeTransferInteractor(repo=WalletRepo)
        transfer_interactor.set_params(
            cleaned_data.sender.wallet.id,
            cleaned_data.receiver.wallet.id,
            cleaned_data.validated_data["sum"],
        )
        await transfer_interactor.execute()
        sender_wallet = transfer_interactor.get_execution_result()

        transaction_interactor = CreateTransactionInteractor(repo=TransactionRepo)
        transaction_interactor.set_params(
            cleaned_data.sender.wallet,
            cleaned_data.receiver.wallet,
            cleaned_data.validated_data["sum"],
            False,
        )
        await transaction_interactor.execute()

        return Response(WalletSerializer(sender_wallet).data)

    async def pay_invoice(self, request_data: Dict, request_user_id: id) -> Response:
        sender = await get_user_with_wallet(UserRepo, id=request_user_id)
        serializer = InvoicePaySerializer(
            data=request_data, sender_wallet_id=sender.wallet.id
        )
        await serializer.is_valid(raise_exception=True)
        transaction_obj = await TransactionRepo.async_get(
            uuid=serializer.validated_data["uuid"]
        )

        transfer_interactor = MakeTransferInteractor(repo=WalletRepo)
        transfer_interactor.set_params(
            transaction_obj.sender_id,
            transaction_obj.receiver_id,
            transaction_obj.sum,
        )
        await transfer_interactor.execute()
        sender_wallet = transfer_interactor.get_execution_result()

        update_interactor = UpdateTransactionInteractor(repo=TransactionRepo)
        update_interactor.set_params(transaction_obj)
        await update_interactor.execute()

        return Response(WalletSerializer(sender_wallet).data)
