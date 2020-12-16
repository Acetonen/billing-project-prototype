import time
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from project.accounts.use_cases import UserModel
from project.payments.models import Wallet, Transaction


class GetWalletInteractor:
    """Get user wallet to view balance."""

    def set_params(self, user: UserModel) -> "GetWalletInteractor":
        self.user = user

        return self

    def execute(self) -> Wallet:
        return Wallet.objects.get(user=self.user)


class CreateTransactionInteractor:
    """Create new transfer, invoice ot transaction."""

    def set_params(
        self, sender: UserModel, receiver: UserModel, sum_: Decimal, invoice: bool
    ) -> "CreateTransactionInteractor":
        self.sender = sender
        self.receiver = receiver
        self.sum = sum_
        self.invoice = invoice

        return self

    def execute(self) -> Transaction:
        return Transaction.objects.create(
            sender=self.sender.wallet,
            receiver=self.receiver.wallet,
            sum=self.sum,
            uuid=uuid.uuid4(),
            done_time=timezone.now() if not self.invoice else None,
            is_done=False if self.invoice else True,
        )  # as it invoice, not payment


class UpdateTransactionInteractor:
    """Update invoice transaction."""

    def set_params(self, transaction_uuid: uuid) -> "UpdateTransactionInteractor":
        self.transaction_uuid = transaction_uuid

        return self

    def execute(self) -> Transaction:
        invoice = Transaction.objects.get(uuid=self.transaction_uuid)
        invoice.is_done = True
        invoice.done_time = timezone.now()
        invoice.save(update_fields=["is_done", "done_time"])

        return invoice


class CreateInvoiceInteractor(CreateTransactionInteractor):
    def set_params(self, *args, **kwargs) -> "CreateInvoiceInteractor":
        super().set_params(*args, **kwargs)
        #  We should switch sender and receiver when make deal with invoice:
        if self.invoice:
            self.sender, self.receiver = self.receiver, self.sender

        return self


class UpdateWalletBalanceInteractor:
    """Update wallet balance."""

    def set_params(
        self, receiver_wallet: Wallet, sum_: Decimal
    ) -> "UpdateWalletBalanceInteractor":
        self.receiver_wallet = receiver_wallet
        self.sum = sum_

        return self

    def execute(self) -> Wallet:
        self.receiver_wallet.balance = (
            F("balance") + self.sum
        )  # to prevent race conditions
        self.receiver_wallet.save(update_fields=["balance"])
        self.receiver_wallet.refresh_from_db()

        return self.receiver_wallet


class MakeTransferInteractor:
    """Write off sum from one user and add to another"""

    def set_params(
        self, sender: UserModel, receiver: UserModel, sum_: Decimal
    ) -> "MakeTransferInteractor":
        self.sender = sender
        self.receiver = receiver
        self.sum = sum_

        return self

    def execute(self) -> Wallet:
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

            sender_wallet = (
                UpdateWalletBalanceInteractor()
                .set_params(sender_wallet, -self.sum)
                .execute()
            )
            receiver_wallet = (
                UpdateWalletBalanceInteractor()
                .set_params(receiver_wallet, self.sum)
                .execute()
            )

        return sender_wallet
