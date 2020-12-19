import time
import uuid
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from project.core.abstract_data_types import AbstractUseCase
from project.payments.data import WalletData, TransactionData


class CreateTransactionInteractor(AbstractUseCase):
    """Create new transfer, invoice ot transaction."""

    def set_params(
        self,
        sender_wallet: WalletData,
        receiver_wallet: WalletData,
        sum_: Decimal,
        invoice: bool,
    ):
        self.sender_wallet = sender_wallet
        self.receiver_wallet = receiver_wallet
        self.sum = sum_
        self.invoice = invoice

    def execute(self):
        object_id = self.repo.create(
            sender_id=self.sender_wallet.id,
            receiver_id=self.receiver_wallet.id,
            sum=self.sum,
            uuid=uuid.uuid4(),
            done_time=timezone.now() if not self.invoice else None,
            is_done=False if self.invoice else True,
        )  # as it invoice, not payment
        self.result_of_execution = self.repo.get(id=object_id)

    def get_execution_result(self) -> TransactionData:
        return super().get_execution_result()


class UpdateTransactionInteractor(AbstractUseCase):
    """Update invoice transaction."""

    def set_params(self, transaction_data: TransactionData):
        self.transaction_data = transaction_data

    def execute(self):
        self.transaction_data.is_done = True
        self.transaction_data.done_time = timezone.now()
        object_id = self.repo.update(self.transaction_data)

        self.result_of_execution = self.repo.get(id=object_id)

    def get_execution_result(self) -> TransactionData:
        return super().get_execution_result()


class CreateInvoiceInteractor(CreateTransactionInteractor):
    def set_params(self, *args, **kwargs):
        super().set_params(*args, **kwargs)
        #  We should switch sender and receiver when make deal with invoice:
        if self.invoice:
            self.sender_wallet, self.receiver_wallet = (
                self.receiver_wallet,
                self.sender_wallet,
            )


class UpdateWalletBalanceInteractor(AbstractUseCase):
    """Update wallet balance."""

    def set_params(self, receiver_wallet: WalletData, sum_: Decimal):
        self.receiver_wallet = receiver_wallet
        self.sum = sum_

    def execute(self):
        self.repo.update_incrementally(self.receiver_wallet, "balance", self.sum)
        self.result_of_execution = self.repo.get(id=self.receiver_wallet.id)

    def get_execution_result(self) -> WalletData:
        return super().get_execution_result()


class MakeTransferInteractor(AbstractUseCase):
    """Write off sum from one user and add to another"""

    def set_params(self, sender_wallet_id: int, receiver_wallet_id: int, sum_: Decimal):
        self.sender_wallet_id = sender_wallet_id
        self.receiver_wallet_id = receiver_wallet_id
        self.sum = sum_

    def execute(self):
        """
        Use with_lock=True (select_for_update in repo) to lock rows and prevent race conditions.
        Is need to select_for_update only sender wallet to prevent go to 'under zero', receiver will be enough
        with F('balance') + sum.
        """
        sender_wallet = self.repo.get(id=self.sender_wallet_id, with_lock=True)

        if self.sum > sender_wallet.balance:
            raise ValidationError("Not enough money to make transfer.")

        receiver_wallet = self.repo.get(
            id=self.receiver_wallet_id,
        )

        # For using in tests as net lag emulation:
        if settings.MAKE_TEST_LAG_IN_TRANSFER:
            time.sleep(2)

        update_interactor = UpdateWalletBalanceInteractor(repo=self.repo)
        update_interactor.set_params(sender_wallet, -self.sum)
        update_interactor.execute()
        sender_wallet = update_interactor.get_execution_result()

        update_interactor = UpdateWalletBalanceInteractor(repo=self.repo)
        update_interactor.set_params(receiver_wallet, self.sum)
        update_interactor.execute()

        self.result_of_execution = sender_wallet

    def get_execution_result(self) -> WalletData:
        return super().get_execution_result()
