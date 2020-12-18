import time
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from project.core.abstract_data_types import AbstractUseCase
from project.payments.models import Wallet, Transaction


class GetWalletInteractor(AbstractUseCase):
    """Get user wallet to view balance."""

    def set_params(self, user):
        self.user = user

    def execute(self):
        self.result_of_execution = Wallet.objects.get(user=self.user)

    def get_execution_result(self) -> Wallet:
        return super().get_execution_result()


class CreateTransactionInteractor(AbstractUseCase):
    """Create new transfer, invoice ot transaction."""

    def set_params(self, sender, receiver, sum_: Decimal, invoice: bool):
        self.sender = sender
        self.receiver = receiver
        self.sum = sum_
        self.invoice = invoice

    def execute(self):
        self.result_of_execution = Transaction.objects.create(
            sender=self.sender.wallet,
            receiver=self.receiver.wallet,
            sum=self.sum,
            uuid=uuid.uuid4(),
            done_time=timezone.now() if not self.invoice else None,
            is_done=False if self.invoice else True,
        )  # as it invoice, not payment

    def get_execution_result(self) -> Transaction:
        return super().get_execution_result()


class UpdateTransactionInteractor(AbstractUseCase):
    """Update invoice transaction."""

    def set_params(self, transaction_uuid: uuid.uuid4):
        self.transaction_uuid = transaction_uuid

    def execute(self):
        invoice = Transaction.objects.get(uuid=self.transaction_uuid)
        invoice.is_done = True
        invoice.done_time = timezone.now()
        invoice.save(update_fields=["is_done", "done_time"])

        self.result_of_execution = invoice

    def get_execution_result(self) -> Transaction:
        return super().get_execution_result()


class CreateInvoiceInteractor(CreateTransactionInteractor):
    def set_params(self, *args, **kwargs):
        super().set_params(*args, **kwargs)
        #  We should switch sender and receiver when make deal with invoice:
        if self.invoice:
            self.sender, self.receiver = self.receiver, self.sender


class UpdateWalletBalanceInteractor(AbstractUseCase):
    """Update wallet balance."""

    def set_params(self, receiver_wallet: Wallet, sum_: Decimal):
        self.receiver_wallet = receiver_wallet
        self.sum = sum_

    def execute(self):
        self.receiver_wallet.balance = (
            F("balance") + self.sum
        )  # to prevent race conditions
        self.receiver_wallet.save(update_fields=["balance"])
        self.receiver_wallet.refresh_from_db()

        self.result_of_execution = self.receiver_wallet

    def get_execution_result(self) -> Wallet:
        return super().get_execution_result()


class MakeTransferInteractor(AbstractUseCase):
    """Write off sum from one user and add to another"""

    def set_params(self, sender, receiver, sum_: Decimal):
        self.sender = sender
        self.receiver = receiver
        self.sum = sum_

    def execute(self):
        """
        Use transaction.atomic and select_for_update to lock rows and prevent race conditions.
        Is need to select_for_update only sender wallet to prevent go to 'under zero', receiver will be enough
        with F('balance') + sum.
        """
        with transaction.atomic():
            sender_wallet = Wallet.objects.select_for_update().get(
                user_id=self.sender.id
            )
            if self.sum > sender_wallet.balance:
                raise ValidationError("Not enough money to make transfer.")

            receiver_wallet = Wallet.objects.get(user_id=self.receiver.id)

            # For using in tests as net lag emulation:
            if settings.MAKE_TEST_LAG_IN_TRANSFER:
                time.sleep(2)

            update_interactor = UpdateWalletBalanceInteractor()
            update_interactor.set_params(sender_wallet, -self.sum)
            update_interactor.execute()
            sender_wallet = update_interactor.get_execution_result()

            update_interactor = UpdateWalletBalanceInteractor()
            update_interactor.set_params(receiver_wallet, self.sum)
            update_interactor.execute()

        self.result_of_execution = sender_wallet

    def get_execution_result(self) -> Wallet:
        return super().get_execution_result()
