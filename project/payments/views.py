from collections import namedtuple
from typing import Dict, Union

from .data import WalletData, TransactionData
from .repositories import (
    WalletRepo,
    TransactionRepo,
)
from .use_cases import (
    CreateTransactionInteractor,
    UpdateTransactionInteractor,
    CreateInvoiceInteractor,
    UpdateWalletBalanceInteractor,
    MakeTransferInteractor,
)

TransactionCleanedData = namedtuple(
    "TransactionCleanedData", "sender receiver validated_data"
)


class BalanceView:
    async def get(self, request_user_id: int) -> WalletData:
        wallet = await WalletRepo.async_get(user_id=request_user_id)

        return wallet


class TransactionsView:
    async def create_invoice(
        self, cleaned_data: TransactionCleanedData
    ) -> TransactionData:

        invoice_interactor = CreateInvoiceInteractor(repo=TransactionRepo)
        invoice_interactor.set_params(
            cleaned_data.sender.wallet,
            cleaned_data.receiver.wallet,
            cleaned_data.validated_data["sum"],
            True,
        )
        await invoice_interactor.execute()
        transaction_obj = invoice_interactor.get_execution_result()

        return transaction_obj

    async def make_deposits(
        self, cleaned_data: TransactionCleanedData
    ) -> Union[WalletData, Dict]:

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
            response_data = wallet
        else:
            # Return confirmation if user make deposits for another user:
            response_data = {"details": "success"}

        return response_data

    async def transfer_to_another_user(
        self,
        cleaned_data: TransactionCleanedData,
    ) -> WalletData:

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

        return sender_wallet

    async def pay_invoice(self, cleaned_invoice_data: Dict) -> WalletData:
        transaction_obj = await TransactionRepo.async_get(
            uuid=cleaned_invoice_data["uuid"]
        )

        transfer_interactor = MakeTransferInteractor(repo=WalletRepo)
        transfer_interactor.set_params(
            transaction_obj.sender.id,
            transaction_obj.receiver.id,
            transaction_obj.sum,
        )
        await transfer_interactor.execute()
        sender_wallet = transfer_interactor.get_execution_result()

        update_interactor = UpdateTransactionInteractor(repo=TransactionRepo)
        update_interactor.set_params(transaction_obj)
        await update_interactor.execute()

        return sender_wallet
